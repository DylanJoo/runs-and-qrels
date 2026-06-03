#!/usr/bin/env python3
"""
Fetch run files from HuggingFace bucket storage and evaluate against local qrels.

The HF bucket stores run files mirroring the local structure:
  runs/{subdir}/run.{benchmark}.{model}.{dataset}.txt

Qrel files remain local at:
  qrels/{subdir}/qrels.{benchmark}.{dataset}.txt

Usage:
    python scripts/fetch_and_evaluate.py
    python scripts/fetch_and_evaluate.py --metrics nDCG@10,R@100
    python scripts/fetch_and_evaluate.py --prefix runs/beir/
"""

import argparse
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path

import requests

BUCKET_OWNER = "DylanJHJ"
BUCKET_NAME = "runs-and-qrels"
HF_API_BASE = f"https://huggingface.co/api/buckets/{BUCKET_OWNER}/{BUCKET_NAME}"
HF_BUCKET_BASE = f"https://huggingface.co/buckets/{BUCKET_OWNER}/{BUCKET_NAME}"


def list_bucket_objects(prefix="runs/", token=None):
    """List all object paths in the HF bucket, filtered client-side by prefix."""
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    resp = requests.get(f"{HF_API_BASE}/tree", headers=headers, timeout=60)
    if not resp.ok:
        print(
            f"Error listing bucket objects (HTTP {resp.status_code}): {resp.text}",
            file=sys.stderr,
        )
        print(f"  API URL: {HF_API_BASE}/tree", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    # Response is a flat list of {"type": "file"|"directory", "path": "...", ...}
    return [
        obj["path"]
        for obj in data
        if isinstance(obj, dict) and obj.get("path", "").startswith(prefix)
    ]


def download_to_temp(key, token=None):
    """Stream a run file from HF bucket into a temp file, validating on the fly.
    Returns (tmp_path, warnings) or (None, []) on error."""
    url = f"{HF_BUCKET_BASE}/resolve/{key}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp = requests.get(url, headers=headers, stream=True)
    if not resp.ok:
        print(
            f"Error downloading {key} (HTTP {resp.status_code}): {resp.text}",
            file=sys.stderr,
        )
        return None, []

    warnings = []
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    try:
        for i, line in enumerate(resp.iter_lines(decode_unicode=True), 1):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) == 6:
                tmp.write(line + "\n")
            elif len(parts) == 5:
                warnings.append(f"  line {i}: only 5 fields, appending dummy run_id: {line[:80]}")
                tmp.write(line + " run\n")
            else:
                warnings.append(f"  line {i}: expected 6 fields, got {len(parts)}, skipping: {line[:80]}")
    finally:
        tmp.close()
    return tmp.name, warnings


def evaluate_run(run_path, qrel_path, parsed_metrics):
    """Evaluate a run file against a qrel file. Returns dict of metric scores."""
    try:
        import ir_measures
    except ImportError:
        print("Error: ir-measures not installed. Run: pip install ir-measures", file=sys.stderr)
        sys.exit(1)

    qrels = ir_measures.read_trec_qrels(str(qrel_path))
    run = ir_measures.read_trec_run(str(run_path))
    results = ir_measures.calc_aggregate(parsed_metrics, qrels, run)
    return {str(k): v for k, v in results.items()}


def main():
    parser = argparse.ArgumentParser(description="Fetch runs from HF bucket and evaluate")
    parser.add_argument("--metrics", default="nDCG@10,R@100",
                        help="Comma-separated ir-measures metrics (default: nDCG@10,R@100)")
    parser.add_argument("--prefix", default="runs/",
                        help="Bucket prefix to list (default: runs/)")
    parser.add_argument("--token", default=os.environ.get("HF_TOKEN"),
                        help="HF token (for private buckets; reads HF_TOKEN env var by default)")
    parser.add_argument("--output-dir", default="results",
                        help="Directory to write result JSON files (default: results)")
    parser.add_argument("--force", action="store_true",
                        help="Re-evaluate even if result JSON already exists")
    args = parser.parse_args()

    try:
        from ir_measures import parse_measure
    except ImportError:
        print("Error: ir-measures not installed. Run: pip install ir-measures", file=sys.stderr)
        sys.exit(1)

    metric_list = [m.strip() for m in args.metrics.split(",")]
    try:
        parsed_metrics = [parse_measure(m) for m in metric_list]
    except Exception as e:
        print(f"Error parsing metrics: {e}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"Listing run files from bucket: {BUCKET_OWNER}/{BUCKET_NAME} (prefix={args.prefix})")
    all_keys = list_bucket_objects(prefix=args.prefix, token=args.token)
    run_keys = [k for k in all_keys if k.endswith(".txt") and "gitkeep" not in k]
    print(f"Found {len(run_keys)} run file(s)")

    evaluated = 0
    skipped_no_qrel = 0
    skipped_cached = 0
    errors = 0

    for key in run_keys:
        path = Path(key)
        # Expected: runs/{subdir}/run.{benchmark}.{model}.{dataset}.txt
        parts = path.parts  # ('runs', 'beir', 'run.beir.bm25.arguana.txt')

        if len(parts) < 3 or parts[0] != "runs":
            # Root-level or unexpected depth — skip
            print(f"Skipping: {key} (unexpected path structure)")
            continue

        subdir = parts[1]
        filename_stem = path.stem  # run.beir.bm25.arguana

        if not filename_stem.startswith("run."):
            print(f"Skipping: {key} (filename doesn't start with 'run.')")
            continue

        run_parts = filename_stem[len("run."):].split(".")
        if len(run_parts) < 3:
            print(f"Skipping: {key} (need at least benchmark.model.dataset in name)")
            continue

        benchmark = run_parts[0]
        model = run_parts[1]
        dataset = ".".join(run_parts[2:])

        qrel_file = Path(f"qrels/{subdir}/qrels.{benchmark}.{dataset}.txt")
        if not qrel_file.exists():
            print(f"Skipping: {key} (no qrel at {qrel_file})")
            skipped_no_qrel += 1
            continue

        output_name = f"{benchmark}.{model}.{dataset}"
        output_json = output_dir / f"{output_name}_results.json"

        if output_json.exists() and not args.force:
            print(f"Cached:  {key} -> {output_json}")
            skipped_cached += 1
            continue

        print(f"Evaluating: {key}")
        tmp_path, run_warnings = download_to_temp(key, token=args.token)
        if tmp_path is None:
            errors += 1
            continue

        for w in run_warnings:
            print(f"  Warning [{key}]: {w}", file=sys.stderr)

        try:
            results = evaluate_run(tmp_path, qrel_file, parsed_metrics)
            with open(output_json, "w") as f:
                json.dump(results, f, indent=2)
            print(f"  -> {output_json}: {results}")
            evaluated += 1
        except Exception as e:
            print(f"  Error evaluating {key}: {type(e).__name__}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            errors += 1
        finally:
            os.unlink(tmp_path)

    print(
        f"\nDone. evaluated={evaluated}, cached={skipped_cached}, "
        f"no_qrel={skipped_no_qrel}, errors={errors}"
    )
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()

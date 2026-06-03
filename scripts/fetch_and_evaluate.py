#!/usr/bin/env python3
""" Fetch run files from HuggingFace bucket storage and evaluate against local qrels.

The HF bucket stores run files mirroring the local structure:
  runs/{subdir}/run.{benchmark}.{model}.{dataset}.txt
"""

import argparse
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path
import requests

from huggingface_hub import list_bucket_tree, download_bucket_files
import ir_datasets
import ir_measures
from ir_measures import nDCG

BUCKET_OWNER = "DylanJHJ"
BUCKET_NAME = "runs-and-qrels"

def main():
    parser = argparse.ArgumentParser(description="Fetch runs from HF bucket and evaluate")
    parser.add_argument("--result-file", default="temp.tsv")
    args = parser.parse_args()

    print(f"Listing run files from bucket: {BUCKET_OWNER}/{BUCKET_NAME}")
    run_paths = [k.path for k in list_bucket_tree(f"{BUCKET_OWNER}/{BUCKET_NAME}") if k.path.endswith(".txt") and "gitkeep" not in k.path]
    print(f"Found {len(run_paths)} run file(s)")

    # First pass: collect all jobs and build deduplicated download list
    jobs = []
    for run_path in run_paths:
        parts = Path(run_path).parts
        if len(parts) < 3 or parts[0] != "runs":
            print(f"Skipping: {run_path} (unexpected path structure)")
            continue

        benchmark = parts[1]
        run_parts = parts[-1].split(".")
        model = run_parts[2]
        dataset = run_parts[3]
        qrels_path = f"qrels/{benchmark}/qrels.{benchmark}.{dataset}.txt"
        jobs.append((run_path, qrels_path, model, dataset))

    temp_dir = Path("./temp")
    temp_dir.mkdir(exist_ok=True)

    download_list = []
    run_local_map = {}
    qrels_local_map = {}

    for run_path, qrels_path, model, dataset in jobs:
        if run_path not in run_local_map:
            local = temp_dir / Path(run_path).name
            run_local_map[run_path] = local
            download_list.append((run_path, str(local)))
        if qrels_path not in qrels_local_map:
            local = temp_dir / Path(qrels_path).name
            qrels_local_map[qrels_path] = local
            download_list.append((qrels_path, str(local)))

    print(f"Downloading {len(download_list)} files in batch...")
    download_bucket_files(f"{BUCKET_OWNER}/{BUCKET_NAME}", files=download_list)
    print("Download complete.")

    evaluated = 0
    with open(args.result_file, "w") as f:
        for run_path, qrels_path, model, dataset in jobs:
            try:
                run = ir_measures.read_trec_run(str(run_local_map[run_path]))
                qrels = ir_measures.read_trec_qrels(str(qrels_local_map[qrels_path]))
                ndcg = ir_measures.calc_aggregate([nDCG@10], qrels, run)[nDCG@10]
                f.write(f"{benchmark}\t{model}\t{dataset}\t{ndcg}\n")
                evaluated += 1
            except Exception as e:
                print(f"Error evaluating {run_path}: {e}")

    print(f"\nDone. evaluated={evaluated}")

    for _, local_path in download_list:
        try:
            Path(local_path).unlink(missing_ok=True)
        except Exception as e:
            print(f"Warning: could not remove {local_path}: {e}")
    try:
        temp_dir.rmdir()
    except OSError:
        pass  # not empty, leave it

if __name__ == "__main__":
    main()

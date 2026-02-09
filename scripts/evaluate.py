#!/usr/bin/env python3
"""
Evaluation Script for Retrieval Results

This script evaluates retrieval runs against qrels (ground truth) using ir-measures.
Optionally, nugget-level ratings can be provided for more fine-grained evaluation.

Usage:
    python evaluate.py --run <run_file> --qrel <qrel_file> [--rating_jsonl <rating_file>] [--metrics <metrics>]

Example:
    python evaluate.py --run runs/my_run.txt --qrel qrels/my_qrel.txt --metrics nDCG@10,AP,R@1000
    python evaluate.py --run runs/my_run.txt --qrel qrels/my_qrel.txt --rating_jsonl ratings/my_rating.jsonl
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import ir_measures
    from ir_measures import parse_measure
    IR_MEASURES_AVAILABLE = True
except ImportError:
    IR_MEASURES_AVAILABLE = False


def load_run(run_path):
    """
    Load a run file in TREC format.
    
    Format: <query_id> Q0 <doc_id> <rank> <score> <run_name>
    
    Returns:
        dict: {query_id: [(doc_id, score), ...]}
    """
    run = {}
    skipped = 0
    with open(run_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 6:
                skipped += 1
                continue
            query_id, _, doc_id, rank, score, _ = parts
            if query_id not in run:
                run[query_id] = []
            run[query_id].append((doc_id, float(score)))
    
    if skipped > 0:
        print(f"  Warning: Skipped {skipped} invalid lines")
    
    # Sort by score descending
    for query_id in run:
        run[query_id] = sorted(run[query_id], key=lambda x: x[1], reverse=True)
    
    return run


def load_qrel(qrel_path):
    """
    Load a qrel file in TREC format.
    
    Format: <query_id> 0 <doc_id> <relevance>
    
    Returns:
        dict: {query_id: {doc_id: relevance}}
    """
    qrel = {}
    skipped = 0
    with open(qrel_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 4:
                skipped += 1
                continue
            query_id, _, doc_id, relevance = parts
            if query_id not in qrel:
                qrel[query_id] = {}
            qrel[query_id][doc_id] = int(relevance)
    
    if skipped > 0:
        print(f"  Warning: Skipped {skipped} invalid lines")
    
    return qrel


def load_rating(rating_path):
    """
    Load a rating file in JSONL format containing nugget-level judgments.
    
    Format: {"qid": "query_id", "ratings": {"docid": [score1, score2, ...], ...}}
    
    Each line is a JSON object with:
    - qid: Query identifier
    - ratings: Dictionary mapping document IDs to lists of nugget-level scores
    
    Returns:
        dict: {query_id: {doc_id: [score1, score2, ...]}}
    """
    rating = {}
    skipped = 0
    with open(rating_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                qid = data.get('qid')
                ratings = data.get('ratings', {})
                if qid is not None:
                    rating[qid] = ratings
                else:
                    print(f"  Warning: Line {line_num}: Missing 'qid' field")
                    skipped += 1
            except json.JSONDecodeError as e:
                print(f"  Warning: Line {line_num}: Invalid JSON - {e}")
                skipped += 1
    
    if skipped > 0:
        print(f"  Warning: Skipped {skipped} invalid lines")
    
    return rating


def calculate_metrics_with_ir_measures(run_path, qrel_path, metrics):
    """
    Calculate evaluation metrics using ir-measures library.
    
    Args:
        run_path: Path to run file
        qrel_path: Path to qrel file
        metrics: List of metric names to calculate
    
    Returns:
        dict: Metric scores (aggregated means)
    """
    # Parse metrics
    parsed_metrics = []
    for metric in metrics:
        try:
            parsed_metrics.append(parse_measure(metric))
        except Exception as e:
            print(f"  Warning: Could not parse metric '{metric}': {e}. "
                  f"See https://ir-measur.es/ for valid metric formats (e.g., nDCG@10, AP, P@10, RR).")
    
    if not parsed_metrics:
        print("Error: No valid metrics to calculate. "
              "Please specify valid ir-measures metrics (e.g., nDCG@10, AP, P@10, RR). "
              "See https://ir-measur.es/ for documentation.", file=sys.stderr)
        return {}
    
    # Load run and qrel using ir-measures
    qrels = ir_measures.read_trec_qrels(str(qrel_path))
    run = ir_measures.read_trec_run(str(run_path))
    
    # Calculate metrics
    results = ir_measures.calc_aggregate(parsed_metrics, qrels, run)
    
    # Convert to simple dict with string keys
    return {str(k): v for k, v in results.items()}


def calculate_metrics(run, qrel, metrics, rating=None):
    """
    Calculate evaluation metrics (fallback without ir-measures).
    
    Args:
        run: Dictionary of retrieval results
        qrel: Dictionary of ground truth relevance
        metrics: List of metric names to calculate
        rating: Optional dictionary of nugget-level ratings (currently unused,
                reserved for future implementation of nugget-based evaluation)
    
    Returns:
        dict: Metric scores
    """
    results = {}
    
    print("Note: ir-measures not installed. Install with: pip install ir-measures")
    
    # Placeholder for metrics
    for metric in metrics:
        results[metric] = 0.0
        print(f"  {metric}: Not calculated (ir-measures not available)")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate retrieval runs against qrels using ir-measures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python evaluate.py --run runs/bm25.txt --qrel qrels/dev.txt
  python evaluate.py --run runs/bm25.txt --qrel qrels/dev.txt --metrics nDCG@10,AP,R@1000
  python evaluate.py --run runs/bm25.txt --qrel qrels/dev.txt --rating_jsonl ratings/my_rating.jsonl
  
Metrics (ir-measures format):
  Common metrics include: AP, nDCG@10, nDCG@20, R@1000, P@10, P@20, RR
  Multiple metrics can be specified as comma-separated values.
  See https://ir-measur.es/ for full list of supported metrics.
        """
    )
    
    parser.add_argument('--run', required=True, help='Path to run file (TREC format)')
    parser.add_argument('--qrel', required=True, help='Path to qrel file (TREC format)')
    parser.add_argument('--rating_jsonl', help='Path to rating file (JSONL format with nugget-level judgments)')
    parser.add_argument('--metrics', default='nDCG@10,AP,R@1000',
                        help='Comma-separated list of metrics to calculate (ir-measures format)')
    parser.add_argument('--output', help='Output file for results (default: stdout)')
    parser.add_argument('--output_json', help='Output file for results in JSON format')
    
    args = parser.parse_args()
    
    # Validate input files
    run_path = Path(args.run)
    qrel_path = Path(args.qrel)
    
    if not run_path.exists():
        print(f"Error: Run file not found: {args.run}", file=sys.stderr)
        sys.exit(1)
    
    if not qrel_path.exists():
        print(f"Error: Qrel file not found: {args.qrel}", file=sys.stderr)
        sys.exit(1)
    
    rating_path = None
    if args.rating_jsonl:
        rating_path = Path(args.rating_jsonl)
        if not rating_path.exists():
            print(f"Error: Rating file not found: {args.rating_jsonl}", file=sys.stderr)
            sys.exit(1)
    
    # Parse metrics
    metric_list = [m.strip() for m in args.metrics.split(',')]
    
    print(f"Loading run: {args.run}")
    print(f"Loading qrel: {args.qrel}")
    
    # Load optional rating file
    rating = None
    if rating_path:
        print(f"Loading rating: {args.rating_jsonl}")
        rating = load_rating(rating_path)
        print(f"  Loaded {len(rating)} queries")
    
    # Calculate metrics
    print(f"\nCalculating metrics: {', '.join(metric_list)}")
    
    if IR_MEASURES_AVAILABLE:
        results = calculate_metrics_with_ir_measures(run_path, qrel_path, metric_list)
    else:
        run = load_run(run_path)
        qrel = load_qrel(qrel_path)
        results = calculate_metrics(run, qrel, metric_list, rating)
    
    # Output results
    output_lines = []
    output_lines.append("\nEvaluation Results:")
    output_lines.append("-" * 50)
    for metric, score in results.items():
        output_lines.append(f"{metric:20s}: {score:.4f}")
    
    output_text = "\n".join(output_lines)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_text + "\n")
        print(f"\nResults written to: {args.output}")
    else:
        print(output_text)
    
    # Output JSON if requested
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"JSON results written to: {args.output_json}")


if __name__ == '__main__':
    main()

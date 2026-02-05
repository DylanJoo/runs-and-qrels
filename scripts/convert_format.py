#!/usr/bin/env python3
"""
Convert between different run/qrel formats

This script converts between TREC format and other common formats for runs and qrels.

Usage:
    python convert_format.py --input <input_file> --output <output_file> --format <format>

Example:
    python convert_format.py --input runs/my_run.txt --output runs/my_run.json --format json
"""

import argparse
import json
import sys
from pathlib import Path


def read_trec_run(filepath):
    """Read TREC format run file."""
    run = {}
    skipped = 0
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 6:
                skipped += 1
                continue
            query_id, _, doc_id, rank, score, run_name = parts
            if query_id not in run:
                run[query_id] = []
            run[query_id].append({
                'doc_id': doc_id,
                'rank': int(rank),
                'score': float(score),
                'run_name': run_name
            })
    if skipped > 0:
        print(f"Warning: Skipped {skipped} invalid lines")
    return run


def read_trec_qrel(filepath):
    """Read TREC format qrel file."""
    qrel = {}
    skipped = 0
    with open(filepath, 'r') as f:
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
        print(f"Warning: Skipped {skipped} invalid lines")
    return qrel


def write_json(data, filepath):
    """Write data to JSON format."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Converted to JSON: {filepath}")


def write_trec_run(data, filepath):
    """Write data to TREC run format."""
    with open(filepath, 'w') as f:
        for query_id, docs in data.items():
            for doc in docs:
                run_name = doc.get('run_name', 'run')
                f.write(f"{query_id} Q0 {doc['doc_id']} {doc['rank']} {doc['score']} {run_name}\n")
    print(f"Converted to TREC run format: {filepath}")


def write_trec_qrel(data, filepath):
    """Write data to TREC qrel format."""
    with open(filepath, 'w') as f:
        for query_id, docs in data.items():
            for doc_id, relevance in docs.items():
                f.write(f"{query_id} 0 {doc_id} {relevance}\n")
    print(f"Converted to TREC qrel format: {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert between different run/qrel formats',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--input', required=True, help='Input file path')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--format', required=True, choices=['json', 'trec'],
                        help='Output format')
    parser.add_argument('--type', choices=['run', 'qrel'], default='run',
                        help='Type of file (run or qrel)')
    
    args = parser.parse_args()
    
    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Read input
    if args.type == 'run':
        print(f"Reading run file: {args.input}")
        data = read_trec_run(input_path)
    else:
        print(f"Reading qrel file: {args.input}")
        data = read_trec_qrel(input_path)
    
    print(f"Loaded {len(data)} queries")
    
    # Write output
    output_path = Path(args.output)
    if args.format == 'json':
        write_json(data, output_path)
    elif args.format == 'trec':
        if args.type == 'run':
            write_trec_run(data, output_path)
        else:
            write_trec_qrel(data, output_path)
    
    print("Conversion complete!")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Validate TREC format files

This script validates that run and qrel files conform to the TREC format standard.

Usage:
    python validate.py --input <file> --type <run|qrel>

Example:
    python validate.py --input runs/my_run.txt --type run
    python validate.py --input qrels/my_qrel.txt --type qrel
"""

import argparse
import sys
from pathlib import Path


def validate_run(filepath):
    """
    Validate TREC run format.
    
    Expected format: <query_id> Q0 <doc_id> <rank> <score> <run_name>
    """
    errors = []
    warnings = []
    line_count = 0
    query_ids = set()
    
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line_count += 1
            line = line.strip()
            
            if not line:
                warnings.append(f"Line {line_num}: Empty line")
                continue
            
            parts = line.split()
            
            # Check number of fields
            if len(parts) != 6:
                errors.append(f"Line {line_num}: Expected 6 fields, found {len(parts)}")
                continue
            
            query_id, q0, doc_id, rank, score, run_name = parts
            query_ids.add(query_id)
            
            # Validate Q0 field
            if q0 != 'Q0':
                errors.append(f"Line {line_num}: Second field should be 'Q0', found '{q0}'")
            
            # Validate rank is integer
            try:
                rank_int = int(rank)
                if rank_int < 1:
                    errors.append(f"Line {line_num}: Rank should be positive (1-based), found {rank_int}")
            except ValueError:
                errors.append(f"Line {line_num}: Rank should be an integer, found '{rank}'")
            
            # Validate score is float
            try:
                float(score)
            except ValueError:
                errors.append(f"Line {line_num}: Score should be a number, found '{score}'")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'stats': {
            'total_lines': line_count,
            'unique_queries': len(query_ids)
        }
    }


def validate_qrel(filepath):
    """
    Validate TREC qrel format.
    
    Expected format: <query_id> 0 <doc_id> <relevance>
    """
    errors = []
    warnings = []
    line_count = 0
    query_ids = set()
    
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line_count += 1
            line = line.strip()
            
            if not line:
                warnings.append(f"Line {line_num}: Empty line")
                continue
            
            parts = line.split()
            
            # Check number of fields
            if len(parts) != 4:
                errors.append(f"Line {line_num}: Expected 4 fields, found {len(parts)}")
                continue
            
            query_id, zero, doc_id, relevance = parts
            query_ids.add(query_id)
            
            # Validate second field is 0
            if zero != '0':
                errors.append(f"Line {line_num}: Second field should be '0', found '{zero}'")
            
            # Validate relevance is integer
            try:
                rel_int = int(relevance)
            except ValueError:
                errors.append(f"Line {line_num}: Relevance should be an integer, found '{relevance}'")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'stats': {
            'total_lines': line_count,
            'unique_queries': len(query_ids)
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Validate TREC format files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--input', required=True, help='Input file to validate')
    parser.add_argument('--type', required=True, choices=['run', 'qrel'],
                        help='Type of file to validate')
    
    args = parser.parse_args()
    
    # Validate input exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Validate file
    print(f"Validating {args.type} file: {args.input}")
    print("-" * 60)
    
    if args.type == 'run':
        result = validate_run(input_path)
    else:
        result = validate_qrel(input_path)
    
    # Print results
    print(f"\nStatistics:")
    for key, value in result['stats'].items():
        print(f"  {key}: {value}")
    
    if result['warnings']:
        print(f"\nWarnings ({len(result['warnings'])}):")
        for warning in result['warnings'][:10]:  # Show first 10
            print(f"  {warning}")
        if len(result['warnings']) > 10:
            print(f"  ... and {len(result['warnings']) - 10} more warnings")
    
    if result['errors']:
        print(f"\nErrors ({len(result['errors'])}):")
        for error in result['errors'][:10]:  # Show first 10
            print(f"  {error}")
        if len(result['errors']) > 10:
            print(f"  ... and {len(result['errors']) - 10} more errors")
        print(f"\n❌ Validation FAILED")
        sys.exit(1)
    else:
        print(f"\n✓ Validation PASSED")


if __name__ == '__main__':
    main()

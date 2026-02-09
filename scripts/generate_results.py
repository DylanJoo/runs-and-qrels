#!/usr/bin/env python3
"""
Generate RESULTS.md from evaluation JSON files.

This script scans the results/ directory for JSON files and generates
a markdown file with all evaluation results, grouped by benchmark type.

The script expects result files to be named following this pattern:
    <benchmark>.<model>.<dataset>_results.json
    
For example:
    beir.bm25.arguana_results.json
    msmarco-passage.bm25.trec-dl-2019_results.json

Usage:
    python scripts/generate_results.py
    python scripts/generate_results.py --metrics nDCG@10
    python scripts/generate_results.py --metrics "nDCG@10,R@100"
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path


def parse_result_filename(filename):
    """
    Parse result filename to extract benchmark, model, and dataset.
    
    Expected format: <benchmark>.<model>.<dataset>_results.json
    Returns: (benchmark, model, dataset) or None if parsing fails
    """
    # Remove _results suffix and .json extension
    stem = filename.replace("_results.json", "")
    
    # Split by dots to get components
    parts = stem.split(".")
    
    if len(parts) >= 3:
        benchmark = parts[0]
        model = parts[1]
        dataset = ".".join(parts[2:])  # Handle datasets with dots in name
        return benchmark, model, dataset
    elif len(parts) == 2:
        # Fallback: assume benchmark.dataset (legacy format)
        return parts[0], "legacy", parts[1]
    else:
        return None, None, stem


def format_score(score):
    """Format score for display in markdown table."""
    if score is None:
        return "-"
    return f"{score:.4f}"


def generate_benchmark_table(benchmark_data, metrics_order, selected_metrics=None):
    """
    Generate markdown tables for a benchmark.
    
    For single model: Dataset | Metric1 | Metric2 | ...
    For multiple models: Create per-metric tables with Model as columns
    
    Args:
        benchmark_data: dict of {dataset: {model: {metric: score}}}
        metrics_order: list of metrics to display in preferred order
        selected_metrics: optional list of specific metrics to include (filters output)
    
    Returns:
        list of markdown lines
    """
    lines = []
    
    # Collect all models across all datasets
    all_models = set()
    for dataset_data in benchmark_data.values():
        all_models.update(dataset_data.keys())
    models = sorted(all_models)
    
    if not models:
        return ["No results available.", ""]
    
    # Determine which metrics we have
    available_metrics = set()
    for dataset_data in benchmark_data.values():
        for model_data in dataset_data.values():
            available_metrics.update(model_data.keys())
    
    # Use provided order, filter to available
    display_metrics = [m for m in metrics_order if m in available_metrics]
    if not display_metrics:
        display_metrics = sorted(available_metrics)
    
    # If specific metrics are selected, filter further
    if selected_metrics:
        display_metrics = [m for m in display_metrics if m in selected_metrics]
        if not display_metrics:
            # Fall back to available selected metrics
            display_metrics = [m for m in selected_metrics if m in available_metrics]
    
    if not display_metrics:
        return ["No matching metrics found.", ""]
    
    datasets = sorted(benchmark_data.keys())
    
    if len(models) == 1:
        # Single model: simple table with metrics as columns
        model = models[0]
        header = "| Dataset | " + " | ".join(display_metrics) + " |"
        separator = "|:---|" + "|".join([":---:" for _ in display_metrics]) + "|"
        lines.append(header)
        lines.append(separator)
        
        for dataset in datasets:
            row_parts = [dataset]
            model_data = benchmark_data[dataset].get(model, {})
            for metric in display_metrics:
                score = model_data.get(metric)
                row_parts.append(format_score(score))
            lines.append("| " + " | ".join(row_parts) + " |")
        lines.append("")
    else:
        # Multiple models: create a table with models as columns
        # Format: Dataset | Model1 | Model2 | Model3 | ...
        # One table per metric
        
        # When specific metrics are selected, show them directly without categorization
        if selected_metrics:
            # Just display all selected metrics as simple tables
            for metric in display_metrics:
                lines.append(f"**{metric}**")
                lines.append("")
                header = "| Dataset | " + " | ".join(models) + " |"
                separator = "|:---|" + "|".join([":---:" for _ in models]) + "|"
                lines.append(header)
                lines.append(separator)
                
                for dataset in datasets:
                    row_parts = [dataset]
                    for model in models:
                        model_data = benchmark_data[dataset].get(model, {})
                        score = model_data.get(metric)
                        row_parts.append(format_score(score))
                    lines.append("| " + " | ".join(row_parts) + " |")
                lines.append("")
        else:
            # Default behavior: Key metrics shown prominently, others in expandable section
            # Select key metrics for the main table (nDCG@10, RR, R@1000 are common)
            key_metrics = ["nDCG@10", "AP", "RR"]
            key_metrics = [m for m in key_metrics if m in display_metrics]
            
            if key_metrics:
                lines.append("### Key Metrics")
                lines.append("")
                
                for metric in key_metrics:
                    lines.append(f"**{metric}**")
                    lines.append("")
                    header = "| Dataset | " + " | ".join(models) + " |"
                    separator = "|:---|" + "|".join([":---:" for _ in models]) + "|"
                    lines.append(header)
                    lines.append(separator)
                    
                    for dataset in datasets:
                        row_parts = [dataset]
                        for model in models:
                            model_data = benchmark_data[dataset].get(model, {})
                            score = model_data.get(metric)
                            row_parts.append(format_score(score))
                        lines.append("| " + " | ".join(row_parts) + " |")
                    lines.append("")
            
            # Full details in expandable section
            other_metrics = [m for m in display_metrics if m not in key_metrics]
            
            if other_metrics:
                lines.append("<details>")
                lines.append("<summary>All Metrics (click to expand)</summary>")
                lines.append("")
                
                for metric in other_metrics:
                    lines.append(f"**{metric}**")
                    lines.append("")
                    header = "| Dataset | " + " | ".join(models) + " |"
                    separator = "|:---|" + "|".join([":---:" for _ in models]) + "|"
                    lines.append(header)
                    lines.append(separator)
                    
                    for dataset in datasets:
                        row_parts = [dataset]
                        for model in models:
                            model_data = benchmark_data[dataset].get(model, {})
                            score = model_data.get(metric)
                            row_parts.append(format_score(score))
                        lines.append("| " + " | ".join(row_parts) + " |")
                    lines.append("")
                
                lines.append("</details>")
                lines.append("")
    
    return lines


def main():
    parser = argparse.ArgumentParser(
        description='Generate RESULTS.md from evaluation JSON files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_results.py
  python scripts/generate_results.py --metrics nDCG@10
  python scripts/generate_results.py --metrics "nDCG@10,R@100"
  python scripts/generate_results.py --output custom_results.md
        """
    )
    parser.add_argument('--metrics', 
                        help='Comma-separated list of metrics to include (e.g., nDCG@10 or "nDCG@10,R@100"). '
                             'If not specified, all available metrics are shown.')
    parser.add_argument('--output', default='RESULTS.md',
                        help='Output markdown file path (default: RESULTS.md)')
    
    args = parser.parse_args()
    
    # Parse selected metrics if provided
    selected_metrics = None
    if args.metrics:
        selected_metrics = [m.strip() for m in args.metrics.split(',')]
    
    results_dir = Path("results")
    output_file = Path(args.output)
    
    # Preferred metrics order for display
    metrics_order = ["nDCG@10", "nDCG@20", "AP", "RR", "R@100", "R@1000", "P@10", "P@20"]
    
    # Collect all JSON result files
    result_files = sorted(results_dir.glob("*.json"))
    
    # Group results by benchmark
    # Structure: {benchmark: {dataset: {model: {metric: score}}}}
    benchmarks = defaultdict(lambda: defaultdict(dict))
    
    # Also track any files that couldn't be parsed
    unparsed_results = []
    
    for result_file in result_files:
        benchmark, model, dataset = parse_result_filename(result_file.name)
        
        try:
            with open(result_file, 'r') as f:
                results = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            unparsed_results.append((result_file.name, str(e)))
            continue
        
        if benchmark is None:
            # Couldn't parse filename, use as-is
            unparsed_results.append((result_file.name, "Could not parse filename"))
            continue
        
        benchmarks[benchmark][dataset][model] = results
    
    # Generate markdown
    lines = []
    lines.append("# Evaluation Results")
    lines.append("")
    lines.append("This file is automatically generated by the evaluation pipeline.")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    if not benchmarks and not unparsed_results:
        lines.append("No evaluation results found.")
    else:
        # Table of contents
        if len(benchmarks) > 1:
            lines.append("## Table of Contents")
            lines.append("")
            for benchmark in sorted(benchmarks.keys()):
                # Create anchor-friendly name
                anchor = benchmark.lower().replace(" ", "-").replace("_", "-")
                lines.append(f"- [{benchmark.upper()}](#{anchor})")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Generate table for each benchmark
        for benchmark in sorted(benchmarks.keys()):
            benchmark_data = benchmarks[benchmark]
            
            # Section header
            lines.append(f"## {benchmark.upper()}")
            lines.append("")
            
            # Count datasets and models
            num_datasets = len(benchmark_data)
            all_models = set()
            for dataset_data in benchmark_data.values():
                all_models.update(dataset_data.keys())
            
            lines.append(f"*{num_datasets} dataset(s), {len(all_models)} model(s)*")
            lines.append("")
            
            # Generate table
            table_lines = generate_benchmark_table(benchmark_data, metrics_order, selected_metrics)
            lines.extend(table_lines)
            
            lines.append("---")
            lines.append("")
        
        # Handle unparsed results (legacy format)
        if unparsed_results:
            lines.append("## Other Results")
            lines.append("")
            lines.append("*Results that could not be grouped by benchmark:*")
            lines.append("")
            for filename, error in unparsed_results:
                lines.append(f"- `{filename}`: {error}")
            lines.append("")
    
    # Write the markdown file
    with open(output_file, 'w') as f:
        f.write("\n".join(lines))
    
    print(f"Generated {output_file}")
    print(f"  - {len(benchmarks)} benchmark(s)")
    for benchmark, data in sorted(benchmarks.items()):
        print(f"    - {benchmark}: {len(data)} dataset(s)")


if __name__ == '__main__':
    main()

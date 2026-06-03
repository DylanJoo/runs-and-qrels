#!/usr/bin/env bash
# Run files are stored in the HuggingFace bucket (DylanJHJ/runs-and-qrels).
# This script fetches them from the bucket, evaluates against local qrels,
# and writes JSON results to results/. Then regenerates RESULTS.md.

set -euo pipefail

# python scripts/fetch_and_evaluate.py
python scripts/generate_results.py

echo "Done. See RESULTS.md for a summary."

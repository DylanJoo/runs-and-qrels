#!/usr/bin/env bash
# Run files are stored in the HuggingFace bucket (DylanJHJ/runs-and-qrels).
# This script fetches them from the bucket, evaluates against local qrels,
# and writes JSON results to results/. Then regenerates RESULTS.md.
#
# Usage:
#   ./autorun.sh                  # evaluate all; skip already-cached results
#   ./autorun.sh --force          # re-evaluate everything
#   ./autorun.sh --prefix runs/beir/  # only a specific subdirectory

set -euo pipefail

METRICS="nDCG@10,R@100"

python scripts/fetch_and_evaluate.py \
  --metrics "$METRICS" \
  "$@"

python scripts/generate_results.py

echo "Done. See RESULTS.md for a summary."

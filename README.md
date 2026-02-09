# runs-and-qrels

Storing runs, qrels, and ratings for IR evaluation.

## Structure

```
runs/       # TREC run files
qrels/      # TREC qrel files  
ratings/    # Nugget-level ratings (JSONL)
scripts/    # Evaluation utilities
results/    # Evaluation results (JSON)
```

## File Naming Convention

For automatic evaluation and result grouping, use the following naming patterns:

**Run files**: `run.<benchmark>.<model>.<dataset>.txt`
```
run.beir.bm25.arguana.txt
run.msmarco-passage.contriever.trec-dl-2019.txt
```

**Qrel files**: `qrel.<benchmark>.<dataset>.txt`
```
qrel.beir.arguana.txt
qrel.msmarco-passage.trec-dl-2019.txt
```

**Result files**: `<benchmark>.<model>.<dataset>_results.json` (auto-generated)
```
beir.bm25.arguana_results.json
msmarco-passage.contriever.trec-dl-2019_results.json
```

## Examples

**Run** (`runs/example_run.txt`):
```
1 Q0 doc123 1 0.95 BM25
1 Q0 doc456 2 0.87 BM25
2 Q0 doc234 1 0.92 BM25
```

**Qrel** (`qrels/example_qrel.txt`):
```
1 0 doc123 2
1 0 doc456 1
2 0 doc234 1
```

**Rating** (`ratings/example_rating.jsonl`):
```json
{"qid": "1", "ratings": {"doc123": [0, 0, 2, 3, 3], "doc456": [1, 2, 4, 5, 2]}}
{"qid": "2", "ratings": {"doc234": [1, 1, 1, 2], "doc567": [2, 3, 4, 4, 5]}}
```

## Usage

```bash
# Evaluate (requires ir-measures: pip install ir-measures)
python scripts/evaluate.py --run runs/example_run.txt --qrel qrels/example_qrel.txt --metrics "nDCG@10,AP,R@1000"

# Validate
python scripts/validate.py --input runs/example_run.txt --type run

# Convert formats
python scripts/convert_format.py --input runs/example_run.txt --output runs/example.json --format json --type run

# Generate RESULTS.md from JSON results
python scripts/generate_results.py
```

## Automatic Evaluation

This repository includes a GitHub Actions workflow that automatically evaluates runs when changes are pushed. The workflow:

1. Triggers on pushes to `main`/`master` branches when run, qrel, rating, or evaluation files change
2. Installs `ir-measures` and runs evaluation on all run/qrel pairs
3. Updates `RESULTS.md` with the latest metric results grouped by benchmark
4. Commits the updated results back to the repository

The workflow automatically matches run files with qrel files based on the naming convention:
- `run.<benchmark>.<model>.<dataset>.txt` → `qrel.<benchmark>.<dataset>.txt`

See [RESULTS.md](RESULTS.md) for the latest evaluation metrics.

## Resources

- [pytrec_eval](https://github.com/cvangysel/pytrec_eval)
- [ir_measures](https://ir-measur.es/)

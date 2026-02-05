# runs-and-qrels

Storing runs, qrels, and ratings for IR evaluation.

## Structure

```
runs/       # TREC run files
qrels/      # TREC qrel files  
ratings/    # Nugget-level ratings (JSONL)
scripts/    # Evaluation utilities
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
# Evaluate
python scripts/evaluate.py --run runs/example_run.txt --qrel qrels/example_qrel.txt

# Validate
python scripts/validate.py --input runs/example_run.txt --type run

# Convert formats
python scripts/convert_format.py --input runs/example_run.txt --output runs/example.json --format json --type run
```

## Resources

- [pytrec_eval](https://github.com/cvangysel/pytrec_eval)
- [ir_measures](https://ir-measur.es/)

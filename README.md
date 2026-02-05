# runs-and-qrels

A repository for storing and managing information retrieval (IR) results and evaluation ground truth (qrels).

## Overview

This repository provides a structured way to organize:
- **Runs**: Retrieval results from various IR systems (e.g., BM25, neural retrievers)
- **Qrels**: Ground truth relevance judgments for evaluation
- **Ratings**: Nugget-level judgments for fine-grained evaluation (JSONL format)
- **Scripts**: Utilities for evaluating, validating, and converting IR data

## Repository Structure

```
runs-and-qrels/
├── runs/              # Retrieval results in TREC format
│   └── .gitkeep
├── qrels/             # Ground truth relevance judgments
│   └── .gitkeep
├── ratings/           # Nugget-level judgments in JSONL format
│   └── .gitkeep
├── scripts/           # Evaluation and utility scripts
│   ├── evaluate.py    # Evaluate runs against qrels
│   ├── validate.py    # Validate TREC format files
│   └── convert_format.py  # Convert between formats
└── README.md
```

## File Formats

### Run Format (TREC)

Retrieval results should be stored in the standard TREC run format:

```
<query_id> Q0 <doc_id> <rank> <score> <run_name>
```

**Example:**
```
1 Q0 doc123 1 0.95 BM25
1 Q0 doc456 2 0.87 BM25
2 Q0 doc789 1 0.92 BM25
```

**Fields:**
- `query_id`: Query identifier
- `Q0`: Literal string (unused, kept for historical reasons)
- `doc_id`: Document identifier
- `rank`: Rank position (1-based)
- `score`: Retrieval score (higher is better)
- `run_name`: Name of the retrieval system/run

### Qrel Format (TREC)

Relevance judgments should be stored in the standard TREC qrel format:

```
<query_id> 0 <doc_id> <relevance>
```

**Example:**
```
1 0 doc123 2
1 0 doc456 1
2 0 doc789 0
```

**Fields:**
- `query_id`: Query identifier
- `0`: Literal string (iteration number, usually 0)
- `doc_id`: Document identifier
- `relevance`: Relevance label (typically 0=non-relevant, 1+=relevant)

### Rating Format (JSONL)

Nugget-level judgments should be stored in JSONL (JSON Lines) format, with one JSON object per line:

```json
{"qid": "<query_id>", "ratings": {"<doc_id>": [<score1>, <score2>, ...], ...}}
```

**Example:**
```json
{"qid": "1", "ratings": {"doc123": [0, 0, 2, 3, 3], "doc456": [1, 2, 4, 5, 2]}}
{"qid": "2", "ratings": {"doc234": [1, 1, 1, 2], "doc567": [2, 3, 4, 4, 5]}}
```

**Fields:**
- `qid`: Query identifier
- `ratings`: Dictionary mapping document IDs to lists of nugget-level scores
  - Each document ID maps to an array of scores representing judgments for individual nuggets

## Usage

### Storing Runs, Qrels, and Ratings

Place your retrieval results, qrels, and ratings in their respective directories:

```bash
# Add a run file
cp my_retrieval_results.txt runs/bm25_baseline.txt

# Add a qrel file
cp my_ground_truth.txt qrels/test_set.txt

# Add a rating file (JSONL format)
cp my_nugget_ratings.jsonl ratings/test_ratings.jsonl
```

### Evaluating Runs

Use the `evaluate.py` script to evaluate retrieval results:

```bash
# Basic evaluation
python scripts/evaluate.py --run runs/bm25_baseline.txt --qrel qrels/test_set.txt

# Specify custom metrics
python scripts/evaluate.py \
    --run runs/bm25_baseline.txt \
    --qrel qrels/test_set.txt \
    --metrics ndcg_cut_10,map,recall_1000

# Evaluation with nugget-level ratings
python scripts/evaluate.py \
    --run runs/bm25_baseline.txt \
    --qrel qrels/test_set.txt \
    --rating_jsonl ratings/test_ratings.jsonl

# Save results to file
python scripts/evaluate.py \
    --run runs/bm25_baseline.txt \
    --qrel qrels/test_set.txt \
    --output results.txt
```

**Note:** The evaluation script is a placeholder. For production use, consider integrating with [pytrec_eval](https://github.com/cvangysel/pytrec_eval):

```bash
pip install pytrec_eval
```

### Validating Files

Ensure your files conform to TREC format:

```bash
# Validate a run file
python scripts/validate.py --input runs/bm25_baseline.txt --type run

# Validate a qrel file
python scripts/validate.py --input qrels/test_set.txt --type qrel
```

### Converting Formats

Convert between TREC format and JSON:

```bash
# Convert run to JSON
python scripts/convert_format.py \
    --input runs/bm25_baseline.txt \
    --output runs/bm25_baseline.json \
    --format json \
    --type run

# Convert JSON back to TREC format
python scripts/convert_format.py \
    --input runs/bm25_baseline.json \
    --output runs/bm25_baseline.txt \
    --format trec \
    --type run
```

## Common Metrics

The evaluation script supports common IR metrics:

- **MAP (Mean Average Precision)**: Overall ranking quality
- **NDCG@k (Normalized Discounted Cumulative Gain)**: Ranking quality at top-k positions
- **Recall@k**: Coverage of relevant documents in top-k
- **P@k (Precision at k)**: Proportion of relevant documents in top-k
- **MRR (Mean Reciprocal Rank)**: Average inverse rank of first relevant document

Common metric specifications:
- `ndcg_cut_10`, `ndcg_cut_20`: NDCG at positions 10 and 20
- `map`: Mean Average Precision
- `recall_1000`: Recall at 1000 documents
- `P_10`, `P_20`: Precision at 10 and 20 documents

## Best Practices

1. **Naming Convention**: Use descriptive names for runs and qrels
   - `runs/bm25_k1-1.2_b-0.75.txt`
   - `qrels/msmarco_dev.txt`

2. **Versioning**: Track different versions of runs
   - `runs/neural_retriever_v1.txt`
   - `runs/neural_retriever_v2.txt`

3. **Validation**: Always validate files before evaluation
   ```bash
   python scripts/validate.py --input runs/new_run.txt --type run
   ```

4. **Documentation**: Add a comment or metadata file describing each run
   - What system/model was used
   - What parameters were set
   - What dataset was used

## Requirements

The scripts require Python 3.6+. No additional dependencies are required for basic functionality.

For full evaluation capabilities, install:

```bash
pip install pytrec_eval
```

## Contributing

When adding new runs or qrels:

1. Ensure files follow TREC format
2. Validate files using `validate.py`
3. Use descriptive filenames
4. Document any special characteristics

## Resources

- [TREC Format Documentation](https://trec.nist.gov/)
- [pytrec_eval](https://github.com/cvangysel/pytrec_eval) - Python interface to trec_eval
- [ir_measures](https://ir-measur.es/) - Modern IR evaluation library

## License

This repository structure is provided as-is for organizing IR experimental results.

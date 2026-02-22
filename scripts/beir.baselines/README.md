# Retrieval Baselines

This folder contains scripts for encoding documents and queries using various retrieval models. These scripts are designed to run on SLURM clusters with GPU support.

## Prerequisites

- SLURM-based cluster with GPU nodes
- Conda environment with the following packages:
  - [Tevatron](https://github.com/texttron/tevatron) - for dense and sparse retrieval encoding
  - [Pyserini](https://github.com/castorini/pyserini) - for SPLADE indexing

## Models

| Script | Model | Type |
|--------|-------|------|
| `encode.nomic-embed.sh` | [nomic-ai/modernbert-embed-base](https://huggingface.co/nomic-ai/modernbert-embed-base) | Dense |
| `encode.qwen3-embed-600m.sh` | [Qwen/Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) | Dense |
| `encode.splade-v3.sh` | [naver/splade-v3](https://huggingface.co/naver/splade-v3) | Sparse |

## Document Encoding

### Dense Retrieval (Nomic Embed / Qwen3)

The dense retrieval scripts encode both corpus documents and queries into dense vector embeddings.

**Submit the job:**
```bash
# For Nomic Embed
sbatch encode.nomic-embed.sh

# For Qwen3
sbatch encode.qwen3-embed-600m.sh
```

**What these scripts do:**
1. Encode corpus documents from `DylanJHJ/beir-corpus` (sharded for parallelization)
2. Encode queries from `DylanJHJ/beir-subset`
3. Output embeddings are saved as pickle files to `$HOME/indices/beir-corpus/<model_name>/`

**Output files:**
- Corpus embeddings: `corpus_emb.<dataset>-<shard_id>.pkl`
- Query embeddings: `query_emb.<dataset>.pkl`

### Sparse Retrieval (SPLADE-v3)

SPLADE produces sparse lexical representations for documents.

**Step 1: Encode documents**
```bash
sbatch encode.splade-v3.sh
```

This encodes documents and outputs sparse vectors to:
- `$HOME/indices/beir-corpus/splade-v3/<dataset>/vectors.jsonl`

**Step 2: Build the index**
```bash
sbatch index.splade-v3.sh
```

This creates a Lucene index using Pyserini for efficient sparse retrieval.

## Getting Run Files

After encoding is complete, you need to perform retrieval to generate run files.

### Dense Retrieval

Use Tevatron's search functionality to retrieve documents:

```bash
python -m tevatron.retriever.driver.search \
    --query_emb_path $output_dir/query_emb.<dataset>.pkl \
    --passage_emb_path "$output_dir/corpus_emb.<dataset>-*.pkl" \
    --depth 1000 \
    --save_ranking_to runs/run.beir.<model>.<dataset>.txt
```

### Sparse Retrieval (SPLADE)

Use Pyserini to search the indexed documents:

```bash
python -m pyserini.search.lucene \
    --index $output_dir/<dataset> \
    --topics <query_file> \
    --output runs/run.beir.splade-v3.<dataset>.txt \
    --impact \
    --hits 1000
```

## Datasets

The scripts are configured to process the following BEIR datasets:

- `beir.arguana`
- `beir.climate_fever`
- `beir.dbpedia_entity`
- `beir.fever`
- `beir.fiqa`
- `beir.hotpotqa`
- `beir.nfcorpus`
- `beir.nq`
- `beir.quora`
- `beir.scidocs`
- `beir.scifact`
- `beir.trec_covid`
- `beir.webis_touche2020`

## Configuration Notes

- **SLURM Array Jobs**: The scripts use array jobs (`--array`) to process multiple datasets in parallel
- **GPU Resources**: Each job requests 1 NVIDIA RTX A6000 GPU
- **Memory**: 32GB RAM per job

## Customization

To use a different model or dataset:

1. Modify the `model_dir` variable to point to your model
2. Update the `DATASETS` array with your target datasets
3. Adjust encoding parameters (batch size, max length, etc.) based on your model's requirements

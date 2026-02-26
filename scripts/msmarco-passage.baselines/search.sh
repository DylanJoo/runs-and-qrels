#!/bin/bash -l
#SBATCH --job-name=search
#SBATCH --output=logs/result.%a
#SBATCH --partition=cpu
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=2:00:00

# ENV
source ${HOME}/.bashrc
initconda
conda activate inference 

# nomic-ai/modernbert-embed-base
# Qwen/Qwen3-Embedding-0.6B

MODEL_DIR=$1
output_dir=${HOME}/scratch/msmarco-passage/${MODEL_DIR##*/}
for year in 19 20;do
python -m tevatron.retriever.driver.search \
    --query_reps $output_dir/query_emb.dl${year}.pkl \
    --passage_reps "$output_dir/corpus_emb*" \
    --depth 100 \
    --batch_size -1 \
    --save_text \
    --save_ranking_to ${year}.run

python -m tevatron.utils.format.convert_result_to_trec \
    --input ${year}.run \
    --output ${HOME}/runs-and-qrels/runs/msmarco-passage/run.msmarco-passage.${MODEL_DIR##*/}.trec-dl-20${year}.txt

done

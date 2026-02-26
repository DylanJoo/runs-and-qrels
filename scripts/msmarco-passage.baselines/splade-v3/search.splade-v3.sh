#!/bin/bash -l
#SBATCH --job-name=lsr-search
#SBATCH --output=logs/search.out
#SBATCH --error=logs/search.err
#SBATCH --nodes=1                
#SBATCH --partition=gpu
#SBATCH --gres=gpu:nvidia_rtx_a6000:1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=64G
#SBATCH --time=10:00:00

# ENV
source /ivi/ilps/personal/dju/miniconda3/etc/profile.d/conda.sh
conda activate inference

model_dir=naver/splade-v3
output_dir=${HOME}/indices/msmarco-passage/${model_dir##*/}
output_dir=${HOME}/scratch/msmarco-passage/${model_dir##*/}
export HF_HOME=${HOME}/scratch/hf
mkdir -p $output_dir

for subset in trec-dl-2019 trec-dl-2020;do
    topic_tsv=${HOME}/runs-and-qrels/queries/msmarco-passage/queries.msmarco-passage.${subset}.tsv
    python -m pyserini.search.lucene \
        --threads 36 --batch-size 32 \
        --index ${output_dir} \
        --topics ${topic_tsv} \
        --encoder ${model_dir} \
        --output ${HOME}/runs-and-qrels/runs/msmarco-passage/run.msmarco-passage.splade-v3.${subset}.txt \
        --hits 100 --impact
done

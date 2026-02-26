#!/bin/bash -l
#SBATCH --job-name=colbert
#SBATCH --output=logs/encode.out
#SBATCH --error=logs/encode.err
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=32
#SBATCH --nodes=1
#SBATCH --mem=512G
#SBATCH --time=1-00:00:00

# ENV
source ${HOME}/.bashrc
initconda
conda activate colbert

model_dir=answerdotai/answerai-colbert-small-v1
output_dir=${HOME}/indices/msmarco-passage/${model_dir##*/}
output_dir=${HOME}/scratch/msmarco-passage/${model_dir##*/}
export HF_HOME=${HOME}/scratch/hf
mkdir -p $output_dir

cd ${HOME}/tevatron/examples/colbert
# for step in prepare encode finalize;do
for step in prepare-cpu;do
    echo Start $step
    python index.py \
        --output_dir=temp \
        --model_name_or_path answerdotai/answerai-colbert-small-v1 \
        --dataset_name Tevatron/msmarco-passage-corpus-new \
        --exclude_title \
        --dataset_split train \
        --passage_max_len 256 \
        --per_device_eval_batch_size 512 \
        --encode_output_path $output_dir  \
        --nbits 1 \
        --dataset_shard_index 0 \
        --dataset_number_of_shards 1 \
        --n_gpus 1 \
        --step $step
    echo End $step
done

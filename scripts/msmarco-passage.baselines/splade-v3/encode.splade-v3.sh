#!/bin/bash -l
#SBATCH --job-name=lsr
#SBATCH --output=logs/lsr.out.%a
#SBATCH --error=logs/lsr.err.%a
#SBATCH --partition=gpu
#SBATCH --gres=gpu:nvidia_rtx_a6000:1
#SBATCH --ntasks-per-node=1        
#SBATCH --nodes=1                
#SBATCH --mem=32G
#SBATCH --time=1-00:00:00

# ENV
source ${HOME}/.bashrc
initconda
conda activate inference

model_dir=naver/splade-v3
output_dir=${HOME}/indices/msmarco-passage/${model_dir##*/}
output_dir=${HOME}/scratch/msmarco-passage/${model_dir##*/}
export HF_HOME=${HOME}/scratch/hf
mkdir -p $output_dir

python -m tevatron.retriever.driver.encode_lsr \
    --exclude_title \
    --model_name_or_path $model_dir \
    --dataset_name Tevatron/msmarco-passage-corpus-new \
    --collection_output ${output_dir}/$DATASET/vectors.jsonl \
    --batch_size 512 \
    --max_length 256 \
    --quantization_factor 100

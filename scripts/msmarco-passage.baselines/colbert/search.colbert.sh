#!/bin/bash -l
#SBATCH --job-name=colbert
#SBATCH --output=logs/search.out
#SBATCH --error=logs/search.err
#SBATCH --partition=gpu
#SBATCH --gres=gpu:nvidia_rtx_a6000:1
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1                
#SBATCH --mem=32G
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
for year in 2019 2020;do
    python search.py \
        --output_dir=temp \
        --model_name_or_path answerdotai/answerai-colbert-small-v1 \
        --encode_output_path $output_dir  \
        --dataset_name DylanJHJ/msmarco-passage-trec \
        --dataset_split  msmarco_passage.trec_dl_${year} \
        --query_max_len 32 \
        --encode_is_query \
        --run_path ${HOME}/runs-and-qrels/runs/msmarco-passage/run.msmarco-passage.colbert-small.trec-dl-${year}.txt
done

#!/bin/bash -l
#SBATCH --job-name=colbert
#SBATCH --output=logs/encode.out.%a
#SBATCH --error=logs/encode.err.%a
#SBATCH --partition=gpu
#SBATCH --gres=gpu:nvidia_rtx_a6000:2
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --array=0-12%2
#SBATCH --mem=96G
#SBATCH --time=1-00:00:00

# ENV
source ${HOME}/.bashrc
initconda
conda activate colbert

model_dir=answerdotai/answerai-colbert-small-v1
output_dir=${HOME}/indices/beir-corpus/${model_dir##*/}
output_dir=${HOME}/scratch/beir-corpus/${model_dir##*/}
export HF_HOME=${HOME}/scratch/hf
mkdir -p $output_dir

DATASETS=(
"beir.arguana"
"beir.climate_fever"
"beir.dbpedia_entity"
"beir.fever"
"beir.fiqa"
"beir.hotpotqa"
"beir.nfcorpus"
"beir.nq"
"beir.quora"
"beir.scidocs"
"beir.scifact"
"beir.trec_covid"
"beir.webis_touche2020"
)
DATASET=${DATASETS[$SLURM_ARRAY_TASK_ID]}

cd ${HOME}/tevatron/examples/colbert
echo Encoding $DATASET corpus
python index.py \
    --output_dir=temp \
    --model_name_or_path $model_dir \
    --dataset_name DylanJHJ/beir-corpus \
    --dataset_split $DATASET \
    --passage_max_len 512 \
    --per_device_eval_batch_size 3840 \
    --encode_output_path $output_dir/$DATASET

# python index.py \
#     --output_dir=temp \
#     --model_name_or_path answerdotai/answerai-colbert-small-v1 \
#     --dataset_name Tevatron/msmarco-passage-corpus-new \
#     --exclude_title \
#     --dataset_split train \
#     --passage_max_len 256 \
#     --per_device_eval_batch_size 512 \
#     --encode_output_path $output_dir  \
#     --nbits 1 \
#     --dataset_shard_index 0 \
#     --dataset_number_of_shards 10 \
#     --step $step

#!/bin/bash -l
#SBATCH --job-name=colbert
#SBATCH --output=logs/search.out.%a
#SBATCH --error=logs/search.err.%a
#SBATCH --partition=gpu
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:nvidia_rtx_a6000:1
#SBATCH --nodes=1                
#SBATCH --array=0-12%1
#SBATCH --mem=200G
#SBATCH --time=1-00:00:00

# ENV
source ${HOME}/.bashrc
initconda
conda activate colbert

model_dir=answerdotai/answerai-colbert-small-v1
output_dir=${HOME}/indices/beir-corpus/${model_dir##*/}
output_dir=${HOME}/scratch/beir-corpus/${model_dir##*/}
export HF_HOME=${HOME}/scratch/hf
export COLLBERT_LOAD_TORCH_EXTENSION_VERBOSE=True
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
subset=${DATASET/beir./}
python search.py \
    --output_dir=temp \
    --model_name_or_path answerdotai/answerai-colbert-small-v1 \
    --encode_output_path $output_dir/$DATASET \
    --dataset_name DylanJHJ/beir-subset \
    --dataset_split $DATASET \
    --per_device_eval_batch_size 4 \
    --query_max_len 64 \
    --encode_is_query \
    --run_path ${HOME}/runs-and-qrels/runs/beir/run.beir.colbert-small.${subset/_/-}.txt

#!/bin/bash -l
#SBATCH --job-name=qwen3
#SBATCH --output=logs/qwen3.out.%a
#SBATCH --error=logs/qwen3.err.%a
#SBATCH --partition=gpu
#SBATCH --gres=gpu:nvidia_rtx_a6000:1
#SBATCH --ntasks-per-node=1        
#SBATCH --nodes=1                
#SBATCH --array=5
#SBATCH --mem=32G
#SBATCH --time=1-00:00:00

# ENV
source ${HOME}/.bashrc
initconda
conda activate inference 

model_dir=Qwen/Qwen3-Embedding-0.6B
output_dir=${HOME}/indices/beir-corpus/${model_dir##*/}
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

for SHARD_ID in 3;do
    echo Encoding $DATASET corpus $SHARD_ID
    python -m tevatron.retriever.driver.encode \
        --output_dir=temp \
        --model_name_or_path $model_dir \
        --bf16 \
        --per_device_eval_batch_size 256 \
        --normalize \
        --pooling last \
        --padding_side left \
        --passage_prefix "" \
        --passage_max_len 384 \
        --dataset_name DylanJHJ/beir-corpus \
        --dataset_split $DATASET \
        --encode_output_path $output_dir/corpus_emb.${DATASET}-${SHARD_ID}.pkl \
        --dataset_number_of_shards 4 \
        --dataset_shard_index ${SHARD_ID}
done

echo Encoding $DATASET queries
python -m tevatron.retriever.driver.encode \
    --output_dir=temp \
    --model_name_or_path $model_dir \
    --bf16 \
    --per_device_eval_batch_size 128 \
    --normalize \
    --pooling last \
    --padding_side left \
    --query_prefix "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery:" \
    --dataset_name  DylanJHJ/beir-subset \
    --dataset_split $DATASET \
    --encode_output_path $output_dir/query_emb.${DATASET}.pkl \
    --query_max_len 128 \
    --encode_is_query

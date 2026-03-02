#!/bin/bash -l
#SBATCH --job-name=qwen3
#SBATCH --output=logs/qwen3.out
#SBATCH --error=logs/qwen3.err
#SBATCH --partition=gpu
#SBATCH --gres=gpu:nvidia_rtx_a6000:1
#SBATCH --ntasks-per-node=1        
#SBATCH --nodes=1                
#SBATCH --array=0
#SBATCH --mem=32G
#SBATCH --time=1-00:00:00

# ENV
source ${HOME}/.bashrc
initconda
conda activate inference

model_dir=Qwen/Qwen3-Embedding-0.6B
output_dir=${HOME}/indices/msmarco-passage/${model_dir##*/}
output_dir=${HOME}/scratch/msmarco-passage/${model_dir##*/}
export HF_HOME=${HOME}/scratch/hf
mkdir -p $output_dir

SHARD_ID=$SLURM_ARRAY_TASK_ID
echo Encoding msmarco-passage corpus $SHARD_ID
# python -m tevatron.retriever.driver.encode \
#     --exclude_title \
#     --output_dir=temp \
#     --tokenizer_name $model_dir \
#     --model_name_or_path $model_dir \
#     --bf16 \
#     --per_device_eval_batch_size 256 \
#     --normalize \
#     --pooling last \
#     --padding_side left \
#     --passage_prefix "" \
#     --passage_max_len 266 \
#     --dataset_name Tevatron/msmarco-passage-corpus-new \
#     --encode_output_path $output_dir/corpus_emb.${SHARD_ID}.pkl \
#     --dataset_shard_index ${SHARD_ID} \
#     --dataset_number_of_shards 4

if [[ $SLURM_ARRAY_TASK_ID -eq 0 ]]; then
    for SPLIT in dl19 dl20;do
        python -m tevatron.retriever.driver.encode \
            --output_dir=temp \
            --tokenizer_name $model_dir \
            --model_name_or_path $model_dir \
            --per_device_eval_batch_size 128 \
            --bf16 \
            --normalize \
            --pooling last \
            --padding_side left \
            --query_prefix "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery:" \
            --corpus_name Tevatron/msmarco-passage-new \
            --dataset_name Tevatron/msmarco-passage-new \
            --dataset_split $SPLIT \
            --encode_output_path $output_dir/query_emb.${SPLIT}.pkl \
            --query_max_len 48 \
            --encode_is_query
    done
fi

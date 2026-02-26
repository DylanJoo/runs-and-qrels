#!/bin/bash -l
#SBATCH --job-name=search
#SBATCH --output=logs/result.%a
#SBATCH --partition=cpu
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --array=0-12
#SBATCH --mem=128G
#SBATCH --time=2:00:00

# ENV
source ${HOME}/.bashrc
initconda
conda activate inference 

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
# nomic-ai/modernbert-embed-base

export HF_HOME=${HOME}/scratch/hf

MODEL_DIR=$1
output_dir=${HOME}/scratch/${MODEL_DIR##*/}
# output_dir=${HOME}/indices/beir-corpus/${MODEL_DIR##*/}
python -m tevatron.retriever.driver.search \
    --query_reps $output_dir/query_emb.${DATASET}.pkl \
    --passage_reps "$output_dir/corpus_emb.${DATASET}*pkl" \
    --depth 100 \
    --batch_size -1 \
    --save_text \
    --save_ranking_to ${DATASET}.run

python -m tevatron.utils.format.convert_result_to_trec \
    --input ${DATASET}.run \
    --output $output_dir/${DATASET/_/-}.txt

echo "Finished searching ${DATASET} with model ${MODEL_DIR}"

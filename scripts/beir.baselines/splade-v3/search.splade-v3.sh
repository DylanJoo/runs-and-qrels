#!/bin/bash -l
#SBATCH --job-name=lsr-search
#SBATCH --output=logs/lsr.out.%a
#SBATCH --error=logs/lsr.err.%a
#SBATCH --nodes=1                
#SBATCH --partition=gpu
#SBATCH --gres=gpu:nvidia_rtx_a6000:1
#SBATCH --ntasks-per-node=1
#SBATCH --array=0-12%2
#SBATCH --mem=64G
#SBATCH --time=10:00:00

# ENV
source /ivi/ilps/personal/dju/miniconda3/etc/profile.d/conda.sh
conda activate inference

model_dir=naver/splade-v3
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

topic_tsv=${HOME}/runs-and-qrels/queries/beir/queries.${DATASET/_/-}.tsv
subset=${DATASET/beir./}
python -m pyserini.search.lucene \
    --threads 36 --batch-size 32 \
    --index ${output_dir}/$DATASET \
    --topics ${topic_tsv} \
    --encoder ${model_dir} \
    --output ${HOME}/runs-and-qrels/runs/beir/run.beir.splade-v3.${subset/_/-}.txt \
    --hits 100 --impact

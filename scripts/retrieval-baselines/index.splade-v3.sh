#!/bin/bash -l
#SBATCH --job-name=lsr-index
#SBATCH --output=logs/lsr.out.%a
#SBATCH --error=logs/lsr.err.%a
#SBATCH --partition=gpu
#SBATCH --gres=gpu:nvidia_rtx_a6000:1
#SBATCH --ntasks-per-node=1        
#SBATCH --nodes=1                
#SBATCH --array=0-12
#SBATCH --mem=32G
#SBATCH --time=1-00:00:00

# ENV
source /ivi/ilps/personal/dju/miniconda3/etc/profile.d/conda.sh
conda activate inference

model_dir=naver/splade-v3
corpus_name=beir-corpus
output_dir=${HOME}/indices/${corpus_name}/${model_dir##*/}
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

python -m pyserini.index.lucene \
    --collection JsonVectorCollection \
    --input ${output_dir}/$DATASET \
    --index ${output_dir}/$DATASET \
    --generator DefaultLuceneDocumentGenerator \
    --threads 36 \
    --impact --pretokenized

#!/bin/bash -l
#SBATCH --job-name=lsr-index
#SBATCH --output=logs/index.out
#SBATCH --error=logs/index.err
#SBATCH --ntasks-per-node=1        
#SBATCH --nodes=1                
#SBATCH --mem=64G
#SBATCH --time=10:00:00

# ENV
source ${HOME}/.bashrc
initconda
conda activate inference

model_dir=naver/splade-v3
output_dir=${HOME}/indices/msmarco-passage/${model_dir##*/}
output_dir=${HOME}/scratch/msmarco-passage/${model_dir##*/}
export HF_HOME=${HOME}/scratch/hf
mkdir -p $output_dir

python -m pyserini.index.lucene \
    --collection JsonVectorCollection \
    --input ${output_dir} \
    --index ${output_dir} \
    --generator DefaultLuceneDocumentGenerator \
    --threads 36 \
    --impact --pretokenized

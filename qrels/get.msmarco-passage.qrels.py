import csv
import json
import logging
import os
import ir_datasets
from collections import defaultdict, OrderedDict
from typing import Optional 
logger = logging.getLogger(__name__)

def save_qrel(benchmark: str, dataset_name: str, path: Optional[str] = None):

    dataset = ir_datasets.load(f"{benchmark}/{dataset_name}")

    njudge = 0
    nqueries = set()
    dataset_name = dataset_name.split("/")[0]
    with open(os.path.join(path, f"qrels.msmarco-passage.{dataset_name}.txt"), "w") as f:
        for qrel in dataset.qrels_iter():
            f.write(f"{qrel.query_id} 0 {qrel.doc_id} {qrel.relevance}\n")
            njudge += 1
            nqueries.add(qrel.query_id)

    print(f"{dataset_name} | {njudge} | {njudge / len(nqueries)}")
    return 0

DATASETS=["trec-dl-2019/judged", "trec-dl-2020/judged"]

for dataset_name in DATASETS:
    save_qrel(
        benchmark="msmarco-passage",
        dataset_name=dataset_name,
        path="/home/dju/runs-and-qrels/qrels/msmarco-passage"
    )

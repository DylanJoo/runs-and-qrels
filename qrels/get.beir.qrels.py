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
    with open(os.path.join(path, f"qrels.beir.{dataset_name}.txt"), "w") as f:
        for qrel in dataset.qrels_iter():
            f.write(f"{qrel.query_id} 0 {qrel.doc_id} {qrel.relevance}\n")
            njudge += 1
            nqueries.add(qrel.query_id)

    print(f"{dataset_name} | {njudge} | {njudge / len(nqueries)}")
    return 0

DATASETS=[
    "arguana",
    "climate-fever",
    "dbpedia-entity/test",
    "fever/test",
    "fiqa/test",
    "hotpotqa/test",
    "nfcorpus/test",
    "nq",
    "quora/test",
    "scidocs",
    "scifact/test",
    "trec-covid",
    "webis-touche2020/v2",
]

for dataset_name in DATASETS:
    save_qrel(
        benchmark="beir",
        dataset_name=dataset_name,
        path="/home/dju/runs-and-qrels/qrels/beir"
    )

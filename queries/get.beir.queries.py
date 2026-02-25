import logging
import os
import ir_datasets
from typing import Optional

logger = logging.getLogger(__name__)

def save_queries(benchmark: str, dataset_name: str, path: Optional[str] = None):

    dataset = ir_datasets.load(f"{benchmark}/{dataset_name}")

    judged_qids = {qrel.query_id for qrel in dataset.qrels_iter()}

    dataset_name = dataset_name.split("/")[0]
    out_path = os.path.join(path, f"queries.beir.{dataset_name}.tsv")
    n = 0
    with open(out_path, "w") as f:
        for query in dataset.queries_iter():
            if query.query_id in judged_qids:
                f.write(f"{query.query_id}\t{query.text}\n")
                n += 1

    print(f"{dataset_name} | {n} queries saved")
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
    save_queries(
        benchmark="beir",
        dataset_name=dataset_name,
        path="/home/dju/runs-and-qrels/queries/beir"
    )

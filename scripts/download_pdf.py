import os
import subprocess

from pymongo import MongoClient

from ..config import DATA_PATH

client = MongoClient("localhost:27017")
db = client.arxiv
col_papers = db.papers

for paper in col_papers.find():

    latest_pdf = "{}{}.pdf".format(paper["id"], paper["versions"][-1]["version"])
    ym = paper["id"].split(".")[0]
    local_path = os.path.join(DATA_PATH, ym)
    
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    if os.path.isfile(os.path.join(local_path, latest_pdf)):
        continue

    paper_path = "gs://arxiv-dataset/arxiv/arxiv/pdf/{}/{}{}.pdf".format(ym, latest_pdf)
    r = subprocess.run(["gsutil", "cp", paper_path, local_path])

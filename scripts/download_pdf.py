import os
import sys
sys.path.append("..")
from glob import glob
import subprocess

from pymongo import MongoClient

from config import DATA_PATH

PDF_PATH = os.path.join(DATA_PATH, "pdf")
if not os.path.exists(PDF_PATH):
    os.makedirs(PDF_PATH)

client = MongoClient("localhost:27017")
db = client.arxiv
col_papers = db.papers

paper_total = col_papers.count()
pdf_count = len(glob(os.path.join(PDF_PATH, "*/*.pdf")))

for paper in col_papers.find():
    ym = paper["id"].split(".")[0]
    ym_path = os.path.join(PDF_PATH, ym)
    latest_pdf = "{}{}.pdf".format(paper["id"], paper["versions"][-1]["version"])

    if not os.path.exists(ym_path):
        os.makedirs(ym_path)

    if os.path.isfile(os.path.join(ym_path, latest_pdf)):
        continue

    paper_path = "gs://arxiv-dataset/arxiv/arxiv/pdf/{}/{}".format(ym, latest_pdf)
    try:
        subprocess.run(["gsutil", "cp", paper_path, ym_path])
    except Exception as e:
        continue
    pdf_count = pdf_count + 1
    print("{}/{}".format(pdf_count, paper_total))

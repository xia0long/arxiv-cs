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

def download_pdf(paper):
    """
    If the downloads fails, then download the previous version.
    """
    global pdf_count
    ym = paper["id"].split(".")[0]
    ym_path = os.path.join(PDF_PATH, ym)
    
    for v in paper["versions"][::-1]:

        pdf = "{}{}.pdf".format(paper["id"], v["version"])
        if not os.path.exists(ym_path):
            os.makedirs(ym_path)

        if os.path.isfile(os.path.join(ym_path, pdf)):
            continue

        paper_path = "gs://arxiv-dataset/arxiv/arxiv/pdf/{}/{}".format(ym, pdf)
        r = subprocess.run(["gsutil", "cp", paper_path, ym_path], capture_output=True)

        if "No URLs matched" in r.stderr.decode():
            print("Download fails, download the previous version.")
            continue
        elif "Operation completed over" in r.stderr.decode():
            print("Download {} successful.".format(pdf))
            pdf_count = pdf_count + 1
            print("{}/{}".format(pdf_count, paper_total))
            break
        else:
            print(r.stderr)


for paper in col_papers.find().skip(9000):
    
    download_pdf(paper)
    

import os
import sys
sys.path.append("..")
from glob import glob
import subprocess

from pymongo import MongoClient

from config import DATA_PATH

TXT_PATH = os.path.join(DATA_PATH, "txt")
if not os.path.exists(TXT_PATH):
    os.makedirs(TXT_PATH)

client = MongoClient("localhost:27017")
db = client.arxiv
col_papers = db.papers

paper_total = col_papers.count()
txt_count = len(glob(os.path.join(TXT_PATH, "*/*.txt")))

PDF_PATH = os.path.join(DATA_PATH, "pdf")
pdf_path_list = glob(os.path.join(PDF_PATH, "*/*.pdf"))

for pdf_path in pdf_path_list:
    
    ym = pdf_path.split("/")[-2]
    ym_path = os.path.join(TXT_PATH, ym)
    
    if not os.path.exists(ym_path):
        os.makedirs(ym_path)

    txt_path = pdf_path.replace("pdf", "txt", 1) + ".txt"
    if os.path.isfile(txt_path):
        continue
    
    subprocess.run(["pdftotext", pdf_path, txt_path])


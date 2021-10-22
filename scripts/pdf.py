import os
import sys
sys.path.append("..")
import json
from glob import glob
import subprocess

from tqdm import tqdm

from config import DATA_PATH, col_papers

PDF_PATH = os.path.join(DATA_PATH, "pdf")
if not os.path.exists(PDF_PATH):
    os.makedirs(PDF_PATH)

paper_total = col_papers.estimated_document_count()
pdf_count = len(glob(os.path.join(PDF_PATH, "*/*.pdf")))

def get_pdf_list():

    D = {}
    paper_id_list = col_papers.find({}, {"_id": 0, "id": 1})
    paper_id_list = [i["id"] for i in paper_id_list]

    with open(os.path.join(DATA_PATH, "arxiv-dataset_list-of-files.txt")) as f:
        for line in tqdm(f):
            if not "arxiv/arxiv/pdf" in line:
                continue
            if not line.strip().endswith(".pdf"):
                continue
            pid = line.split("/")[-1].split("v")[0]
            ym = line.split("/")[-2]
            if not pid:
                continue
            
            print(line)
            print(D)
            if pid in paper_id_list:
                if ym not in D.keys():
                    D[ym] = {pid: [line.strip()]}
                else:

                    D[ym][pid].append(line.strip())

    json.dump(D, open(os.path.join(DATA_PATH, "pdf_path_list.json"), "w"), indent=4)


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
            print("Download {} fails, download the previous version.".format(pdf))
            continue
        elif "Operation completed over" in r.stderr.decode():
            print("Download {} successful.".format(pdf))
            pdf_count = pdf_count + 1
            print("{}/{}".format(pdf_count, paper_total))
            break
        else:
            print(r.stderr)

def pdf2txt():

    TXT_PATH = os.path.join(DATA_PATH, "txt")
    if not os.path.exists(TXT_PATH):
        os.makedirs(TXT_PATH)

    txt_count = len(glob(os.path.join(TXT_PATH, "*/*.txt")))

    PDF_PATH = os.path.join(DATA_PATH, "pdf")
    pdf_path_list = glob(os.path.join(PDF_PATH, "*/*.pdf"))

    for pdf_path in tqdm(pdf_path_list):
        
        ym = pdf_path.split("/")[-2]
        ym_path = os.path.join(TXT_PATH, ym)
        
        if not os.path.exists(ym_path):
            os.makedirs(ym_path)

        txt_path = pdf_path.replace("pdf", "txt", 1) + ".txt"
        if os.path.isfile(txt_path):
            continue
        
        subprocess.run(["pdftotext", pdf_path, txt_path])



if __name__ == "__main__":
    
    # import time
    # while 1:
    #     try:
    #         for paper in col_papers.find().skip(100000):
    #             download_pdf(paper)
    #     except:
    #         time.sleep(5)
    #         continue
    get_pdf_list()

import os
import sys
sys.path.append("..")
import json
from glob import glob

from tqdm import tqdm

from config import DATA_PATH, col_papers

PDF_PATH = os.path.join(DATA_PATH, "cs", "pdf")
if not os.path.exists(PDF_PATH):
    os.makedirs(PDF_PATH)

TXT_PATH = os.path.join(DATA_PATH, "cs", "txt")
if not os.path.exists(TXT_PATH):
    os.makedirs(TXT_PATH)

REMOTE_PDF_PATH = json.load(open(os.path.join(DATA_PATH, "pdf_path_list2.json"), "r"))

def get_pdf_list():

    D = {}
    paper_id_list = col_papers.find({}, {"_id": 0, "id": 1})
    paper_id_list = set([i["id"] for i in paper_id_list])

    if not os.path.isfile("/tmp/remote_pdf_path_list.txt"):
        print("/tmp/remote_pdf_path_list.txt not exists, please run `get_remote_pdf_path.sh` first.")
        return
    with open("/tmp/remote_pdf_path_list.txt", "r") as f:
        for line in tqdm(f):
            if "arxiv/cs/pdf" in line:
                pid = "cs/" + line.split("/")[-1].split("v")[0]
            else:
                pid = line.split("/")[-1].split("v")[0]
            
            ym = line.split("/")[-2]
            if pid in paper_id_list:
                if ym not in D.keys():
                    D[ym] = {}
                if pid not in D[ym].keys():
                    D[ym][pid] = [line.strip()]
                else:
                    D[ym][pid].append(line.strip())

    json.dump(D, open(os.path.join(DATA_PATH, "pdf_path_list.json"), "w"), indent=4)

    D2 = {} # Compared to D1, only the latest version of the paper is kept
    for ym, data in tqdm(D.items()):
        if ym not in D2.keys():
            D2[ym] = []
        for pid, paper_path_list in data.items():
            D2[ym].append(paper_path_list[-1])

    json.dump(D2, open(os.path.join(DATA_PATH, "pdf_path_list2.json"), "w"), indent=4)


def parse_paper_id(paper_id):
    
    paper = col_papers.find_one({"id": paper_id})
    cate = paper["categories"][0]
    if "cs" in paper_id:
        ym = paper_id.split("/")[1][:4]
        index = paper_id.split("/")[1][4:]
    else:
        ym, index = paper_id.split(".")

    return cate, ym, index

def get_pdf_remote_path(paper_id):

    _, ym, index = parse_paper_id(paper_id)
    for remote_pdf_path in REMOTE_PDF_PATH[ym]:
        if "cs" in paper_id:
            if ym+index in remote_pdf_path:
                return remote_pdf_path
        elif "." in paper_id:
            if ".".join(ym, index) in remote_pdf_path:
                return remote_pdf_path
        else:
            print("Wrong paper id: {}".format(paper_id))

def download_one(paper_id):

    remote_path = get_pdf_remote_path(paper_id)
    if "cs" in paper_id:
        ym = paper_id.split("/")[1][:4]
    else:
        ym = paper_id.split(".")[0]

    local_dir = os.path.join(DATA_PATH, "cs", ym)
    cmd = "gsutil cp {} {}".format(remote_path, local_dir)
    os.system(cmd)

def download_by_month(ym):

    local_dir = os.path.join(DATA_PATH, "cs", "pdf", ym)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    with open("/tmp/tmp.txt", "w") as f:
        f.writelines("%s\n" % l for l in REMOTE_PDF_PATH[ym])

    cmd = "cat {} | gsutil -m cp -I {}".format("/tmp/tmp.txt", local_dir)
    os.system(cmd)

def download_all():

    for ym in tqdm(REMOTE_PDF_PATH.keys()):
        if os.path.exists(os.path.join(DATA_PATH, "cs", "pdf", ym)):
            continue
        download_by_month(ym)

def pdf2txt():

    pdf_path_list = glob(os.path.join(PDF_PATH, "*/*.pdf"))
    for pdf_path in tqdm(pdf_path_list):
        ym = pdf_path.split("/")[-2]  # a string short for year and month, e.g. 2110(2021.10)
        ym_path = os.path.join(TXT_PATH, ym)
        
        if not os.path.exists(ym_path):
            os.makedirs(ym_path)

        txt_path = pdf_path.replace("pdf", "txt", 1) + ".txt"
        if os.path.isfile(txt_path):
            continue
        
        os.system("pdftotext {} {}".format(pdf_path, txt_path))

if __name__ == "__main__":

    # get_pdf_list()
    # download_all()
    pdf2txt()

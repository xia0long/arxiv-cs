import os
import sys
sys.path.append("..")
import re
from glob import glob

from pymongo import MongoClient

from config import DATA_PATH
from regex_arxiv import REGEX_ARXIV_FLEXIBLE, clean


client = MongoClient("localhost:27017")
db = client.arxiv
col_papers = db.papers

RE_FLEX = re.compile(REGEX_ARXIV_FLEXIBLE)
def extract_references(filename, pattern=RE_FLEX):

    out = []
    with open(filename, "r") as f:
        txt = f.read()

        for matches in pattern.findall(txt):
            out.extend([clean(a) for a in matches if a])
    return list(set(out))

TXT_PATH = os.path.join(DATA_PATH, "txt")

paper_txt_path_list = glob(os.path.join(TXT_PATH, "*/*.txt"))
for paper_txt_path in paper_txt_path_list:

    citations = extract_references(paper_txt_path)
    if not citations:
        continue
    
    paper_id = paper_txt_path.split("/")[-1][:9]

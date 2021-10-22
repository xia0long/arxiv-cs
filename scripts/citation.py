import os
import sys
sys.path.append("..")
import re
from glob import glob

from tqdm import tqdm

from config import DATA_PATH, col_papers
from regex_arxiv import REGEX_ARXIV_FLEXIBLE, clean

TXT_PATH = os.path.join(DATA_PATH, "txt")
RE_FLEX = re.compile(REGEX_ARXIV_FLEXIBLE)

def extract_references(filename, pattern=RE_FLEX):

    out = []
    with open(filename, "r") as f:
        txt = f.read()

        for matches in pattern.findall(txt):
            out.extend([clean(a) for a in matches if a])
    return list(set(out))


def update_citations():
    paper_txt_path_list = glob(os.path.join(TXT_PATH, "*/*.txt"))
    for paper_txt_path in paper_txt_path_list:

        citations = extract_references(paper_txt_path)
        if not citations:
            continue
    
        paper_id = paper_txt_path.split("/")[-1][:9]
        print(paper_id, citations)
    
        col_papers.update_one({"id": paper_id}, {"$set": {"citations": citations}})


def update_inner_reference():
    
    for paper in col_papers.find():
        if "citations" not in paper.keys():
            continue
        
        for citation in paper["citations"]:
            p = col_papers.find_one({"id": citation})
            if not p:
                continue
            print(p)
            # TODO: need better method
            r = col_papers.update_one(
                    {"id": citation, "referenced_in": {"$exists": "false"}},
                    {"$set": {"referenced_in": [paper["id"]]}})
            
            print(r.raw_result)
            # col_papers.update_one({"id": citation, "inner_citations":{"$exists": true}}, {"$addToSet": {"inner_citations": paper_id}})

        
if __name__ == "__main__":

    # updtae_citations()
    update_inner_reference()


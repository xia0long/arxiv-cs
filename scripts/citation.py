import os
import sys
sys.path.append("..")
import re
from glob import glob

from tqdm import tqdm

from config import DATA_PATH, col_papers
from regex_arxiv import REGEX_ARXIV_FLEXIBLE, clean

TXT_PATH = os.path.join(DATA_PATH, "cs", "txt")
RE_FLEX = re.compile(REGEX_ARXIV_FLEXIBLE)

paper_id_list = col_papers.find({}, {"_id": 0, "id": 1})
paper_id_list = set([i["id"] for i in paper_id_list])

def extract_references(filename, pattern=RE_FLEX):

    out = []
    with open(filename, "r") as f:
        txt = f.read()
        for matches in pattern.findall(txt):
            out.extend([clean(a) for a in matches if a])
    
    out = [i for i in set(out) if i in paper_id_list]

    return out

def update_references():
    paper_txt_path_list = glob(os.path.join(TXT_PATH, "*/*.txt"))
    for paper_txt_path in tqdm(paper_txt_path_list):
        paper_id = paper_txt_path.split("/")[-1].split("v")[0]
        references = extract_references(paper_txt_path)
        if paper_id in references:
            references.remove(paper_id)
        if not references:
            continue
    
        print(paper_id, references)
    
        col_papers.update_one({"id": paper_id}, {"$set": {"references": references}})


def update_citations():
    
    D = {}
    for paper in tqdm(col_papers.find()):
        if "references" not in paper.keys():
            continue
        
        for reference in paper["references"]:
            if reference not in D.keys():
                D[reference] = [paper["id"]]
            else:
                D[reference].append(paper["id"])

    # json.dump(D, open(os.path.join(DATA_PATH, "citations.json"), "w"), indent=4)

    for paper_id, citations in tqdm(D.items()):

        col_papers.update_one({"id": paper_id}, {"$set": {"citations": citations}})

if __name__ == "__main__":

    update_references()
    update_citations()

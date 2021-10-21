import os
import sys
sys.path.append("..")

from tqdm import tqdm
from pymongo import MongoClient

client = MongoClient("localhost:27017")
db = client.arxiv
col_papers = db.papers
col_authors = db.authors

D = {}
for paper in tqdm(col_papers.find()):

    for author in paper["authors"]:
        if author not in D.keys():
            D[author] = [paper["id"]]
        elif paper["id"] not in D[author]:
            D[author].append(paper["id"])

# import json
# json.dump(D, open("../data/author.json", "w"), indent=4)

for author, paper_list in tqdm(D.items()):

    col_authors.insert_one({
        "name": author,
        "papers": paper_list
    })

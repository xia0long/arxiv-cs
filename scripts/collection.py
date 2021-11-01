import os
import json
import time
import datetime
import sys
sys.path.append("..")

from tqdm import tqdm

from config import DATA_PATH, col_raw_data, col_papers, col_authors

# STEP 1: Insert raw data
def insert_raw_data():
    with open(os.path.join(DATA_PATH, 'arxiv-metadata-oai-snapshot.json')) as f:
        for line in tqdm(f):
            paper=json.loads(line)
            col_raw_data.insert_one(paper)

# STEP 2: Build collections
def build_collection_papers():
    paper_id_list = set()
    for paper in tqdm(col_raw_data.find()):

        categories = paper["categories"]
        categories = [c.strip() for c in categories.split()]
        # if not (any([c.startswith("cs.") for c in categories])==True or "stat.ML" in categories):
        #     continue
        if not categories[0].startswith("cs"):
            continue
        
        y, m, d = [int(i) for i in paper["update_date"].split("-")]
        p = {
            "id": paper["id"],
            "doi": paper["doi"],
            "title": paper["title"],
            "abstract": paper["abstract"],
            "authors": [" ".join(author[::-1]).strip() for author in paper["authors_parsed"]],
            "categories": categories,
            "versions": paper["versions"],
            "update_date": paper["update_date"],
            "update_date_dict": {"year": y, "month": m, "day": d},
            # "update_timestamp": time.mktime(datetime.datetime.strptime(paper["update_date"], "%Y-%m-%d").timetuple())
        }

        # col_papers.update({"id": paper["id"]}, p, upsert=True)  # too slow
        if p["id"] not in paper_id_list:
            col_papers.insert_one(p)
            paper_id_list.add(p["id"])

    col_papers.create_index("id")


def build_collection_authors():

    D = {}
    for paper in tqdm(col_papers.find()):

        for author in paper["authors"]:
            if author not in D.keys():
                D[author] = [paper["id"]]
            elif paper["id"] not in D[author]:
                D[author].append(paper["id"])

    # import json
    # json.dump(D, open(os.path.join(DATA_PATH, "author.json"), "w"), indent=4)

    for author, paper_list in tqdm(D.items()):
        col_authors.insert_one({"name": author, "papers": paper_list})

    col_authors.create_index("name")

if __name__ == "__main__":
    
    # insert_raw_data()
    # build_collection_papers()
    build_collection_authors()

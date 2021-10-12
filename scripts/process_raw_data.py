import time
import datetime

from tqdm import tqdm
from pymongo import MongoClient

client = MongoClient("localhost:27017")
db = client.arxiv
col_row_data = db.raw_data
col_papers = db.papers

for paper in tqdm(col_row_data.find()):

    categories = paper["categories"]
    categories = [c.strip() for c in categories.split()]

    if not (any([c.startswith("cs.") for c in categories])==True or "stat.ML" in categories):
        continue

    p = {
        "id": paper["id"],
        "doi": paper["doi"],
        "title": paper["title"],
        "abstract": paper["abstract"],
        "authors": [" ".join(author[::-1]).strip() for author in paper["authors_parsed"]],
        "categories": categories,
        "update_date": paper["update_date"],
        "update_timestamp": time.mktime(datetime.datetime.strptime(paper["update_date"], "%Y-%m-%d").timetuple())
    }

    col_papers.insert_one(p)

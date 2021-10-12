import json
from tqdm import tqdm

from pymongo import MongoClient

client = MongoClient("localhost:27017")
db = client.arxiv
col_raw_data = db.raw_data

with open('data/arxiv-metadata-oai-snapshot.json') as f:
    for line in tqdm(f):
        paper=json.loads(line)
        col_raw_data.insert_one(paper)

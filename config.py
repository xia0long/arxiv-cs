from pymongo import MongoClient

DATA_PATH = "/Users/xiaolong/Workspace/arxiv-cs/data"

client = MongoClient("localhost:27017")
db = client.arxiv
col_raw_data = db.raw_data
col_papers = db.papers
col_authors = db.authors

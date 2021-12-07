from pymongo import MongoClient

DATA_PATH = "/media/xiaolong/9bbdf31a-3238-4691-845c-7f9126769abe/Dataset/arxiv-cs/data"

client = MongoClient("localhost:27017")
db = client.arxiv
col_raw_data = db.raw_data
col_papers = db.papers
col_authors = db.authors

CATEGORY = {
    "cs": ["AI", "AR", "CC", "CE", "CG", "CL", "CR", "CV", "CY", "DB", "DC", "DL",
           "DM", "DS", "ET", "FL", "GL", "GR", "GT", "HC", "IR", "IT", "LG", "LO",
           "MA", "MM", "MS", "NA", "NE", "NI", "OH", "OS", "PF", "PL", "RO", "SC",
           "SD", "SE", "SI", "SY"],
}
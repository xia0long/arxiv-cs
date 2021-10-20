import numpy as np
import matplotlib.pyplot as plt

from pymongo import MongoClient

client = MongoClient("localhost:27017")
db = client.arxiv
col_papers = db.papers

paper_counts_by_year = db.papers.aggregate([
        {"$group" : {"_id" : "$update_date_dict.year", "count" : {"$sum" : 1}}},
        {"$sort": {"_id": 1}}
    ])

x, y = [], []
for i in paper_counts_by_year:
    x.append(i["_id"])
    y.append(i["count"])


plt.figure(figsize=(10,5))
plt.bar(x, y)
plt.xticks(x, x)
plt.title("Paper Counts by Year")
# plt.show()
plt.savefig("../static/images/paper_counts_by_year.png")


paper_counts_by_month = db.papers.aggregate([
        {"$group" : {"_id" : {"year": "$update_date_dict.year", "month": "$update_date_dict.month"}, "count" : {"$sum" : 1}}},
        {"$sort": {"_id": 1}}
    ])

x, y = [], []
for i in paper_counts_by_month:
    x.append("{}.{}".format(*i["_id"].values()))
    y.append(i["count"])

plt.figure(figsize=(10,5))
plt.plot(x, y)
plt.xticks(x[::3], rotation='vertical', fontsize=5)
plt.title("Paper Counts by Month")
# plt.show()
plt.savefig("../static/images/paper_counts_by_month.png")

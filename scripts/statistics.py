import os
import sys

sys.path.append("..")

import matplotlib.pyplot as plt

from config import col_papers

STATS_IMAGES_PATH = os.path.join("..", "static/images/stats")
if not os.path.exists(STATS_IMAGES_PATH):
    os.makedirs(STATS_IMAGES_PATH)


def paper_counts_by_year():
    data = col_papers.aggregate(
        [
            {"$group": {"_id": "$update_date_dict.year", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
    )

    x, y = [], []
    for i in data:
        x.append(i["_id"])
        y.append(i["count"])

    plt.figure(figsize=(10, 5))
    plt.bar(x, y)
    plt.xticks(x, x)
    plt.title("Paper Counts by Year")
    # plt.show()
    plt.savefig("../static/images/stats/paper_counts_by_year.png")


def paper_counts_by_month():
    data = col_papers.aggregate(
        [
            {
                "$group": {
                    "_id": {
                        "year": "$update_date_dict.year",
                        "month": "$update_date_dict.month",
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]
    )

    x, y = [], []
    for i in data:
        x.append("{}.{}".format(*i["_id"].values()))
        y.append(i["count"])

    plt.figure(figsize=(10, 5))
    plt.plot(x, y)
    plt.xticks(x[::3], rotation="vertical", fontsize=5)
    plt.title("Paper Counts by Month")
    # plt.show()
    plt.savefig("../static/images/stats/paper_counts_by_month.png")


def paper_counts_by_author(topn=20):
    data = col_papers.aggregate(
        [
            {"$unwind": "$authors"},
            {"$group": {"_id": "$authors", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": topn},
        ]
    )

    x, y = [], []
    for i in data:
        x.append(i["_id"])
        y.append(i["count"])

    plt.figure(figsize=(16, 8))
    plt.bar(x, y)
    plt.xticks(x, x)
    plt.title("Paper Counts by Author TOP20")
    plt.xticks(rotation=45, fontsize=6)
    # plt.show()
    plt.savefig("../static/images/stats/paper_counts_by_author_top20.png")


def paper_counts_by_categories():
    data = col_papers.aggregate(
        [
            {"$unwind": "$categories"},
            {"$group": {"_id": "$categories", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
    )

    x, y = [], []
    for i in data:
        if i["_id"].startswith("cs.") or i["_id"] == "stat.ML":
            x.append(i["_id"])
            y.append(i["count"])

    plt.figure(figsize=(10, 5))
    plt.bar(x, y)
    plt.xticks(x, x)
    plt.title("Paper Counts by Categories")
    plt.xticks(rotation=45, fontsize=6)
    # plt.show()
    plt.savefig("../static/images/stats/paper_counts_by_categories.png")


if __name__ == "__main__":

    paper_counts_by_year()
    paper_counts_by_month()
    paper_counts_by_author()
    paper_counts_by_categories()

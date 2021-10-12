from pymongo import MongoClient
from flask import Flask, request, jsonify, render_template

client = MongoClient("localhost:27017")
db = client.arxiv
col_papers = db.papers

API_ENDPOINT = '/api/v0.1'

app = Flask(__name__)

@app.route("/")
def index():
    papers = col_papers.aggregate([{"$unset": ["_id"] }, {"$sample": {"size": 5}}])
    papers = [paper for paper in papers]

    return render_template("index.html", papers=papers)

@app.route("/paper/<id>")
def paper(id):
    paper = col_papers.find_one({"id": id})
    paper.pop("_id")

    return render_template("paper.html", paper=paper)


@app.route("/statistics")
def statistics():
    paper_count = col_papers.find().count()
    parper_counts_group_by_date = col_papers.aggregate(
            [{"$group": {"_id": "$update_date", "count_by_day": {"$sum": 1}}}])
    
    return render_template("statistics.html",
                            paper_count=paper_count,
                            parper_counts_group_by_date=parper_counts_group_by_date)

if __name__ == "__main__":

    app.run(host='0.0.0.0', debug=True)

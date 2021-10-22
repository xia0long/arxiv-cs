import os
import json
from time import time

from flask import Flask, request, jsonify, render_template

from config import col_papers, col_authors, DATA_PATH

search_dict = json.load(open(os.path.join(DATA_PATH, "search.json"), "r"))

app = Flask(__name__)

@app.route("/")
def index():

    return render_template("index.html")

@app.route("/random")
def random():
    papers = col_papers.aggregate([
            {"$unset": ["_id"] },
            {"$sample": {"size": 5}}
        ])
    papers = [paper for paper in papers]
    return render_template("random.html", papers=papers)

@app.route("/paper/<id>")
def paper(id):
    paper = col_papers.find_one({"id": id})
    paper.pop("_id")

    return render_template("paper.html", paper=paper)

@app.route("/author/<id>")
def author(id):
    author = col_authors.find_one({"name": id})
    papers = col_papers.aggregate([
            {"$unset": ["_id"] },
            {"$match": {"id": { "$in": author["papers"] }}}
        ])
    papers = [paper for paper in papers]

    return render_template("author.html", papers=papers)

@app.route("/search/", methods=["GET", "POST"])
def search():
    if request.method == 'POST':
        qraw = request.form["input"]
    elif request.method == 'GET':
        qraw = request.args.get('query')
    qparts = qraw.lower().strip().split()
    # accumulate scores
    scores = []
    for paper_id, sd in search_dict.items():
        score = sum(sd.get(q, 0) for q in qparts)
        if score == 0:
            continue
        scores.append((score, paper_id))

    scores.sort(reverse=True, key=lambda x: x[0])  # descending
    papers = []
    for s in scores[:10]:
        paper = col_papers.find_one({"id": s[1]})
        paper.pop("_id")
        papers.append(paper)

    return render_template("search.html", papers=papers)

@app.route("/statistics")
def statistics():
    
    return render_template("statistics.html", paper_count=col_papers.estimated_document_count())

if __name__ == "__main__":

    app.run(host='0.0.0.0', debug=True)

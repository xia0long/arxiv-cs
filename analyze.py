import os
import json

from tqdm import tqdm
import numpy as np
from sklearn.feature_extraction import _stop_words
from sklearn.feature_extraction.text import TfidfVectorizer

from config import col_papers, DATA_PATH

max_features = 5000
v_abs = TfidfVectorizer(
    input="content",
    encoding="utf-8",
    decode_error="replace",
    strip_accents="unicode",
    lowercase=True,
    analyzer="word",
    stop_words="english",
    token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9_-]+\b",
    ngram_range=(1, 1),
    max_features=max_features,
    norm="l2",
    use_idf=True,
    smooth_idf=True,
    sublinear_tf=True,
    max_df=1.0,
    min_df=1,
)

papers = col_papers.aggregate([{"$unset": ["_id"]}, {"$sample": {"size": 20000}}])
corpus_abs = [paper["abstract"] for paper in papers]
v_abs.fit(corpus_abs)

vocab = v_abs.vocabulary_
idf = v_abs.idf_

english_stop_words = _stop_words.ENGLISH_STOP_WORDS
punc = "'!\"#$%&'()*+,./:;<=>?@[\\]^_`{|}~'"  # removed hyphen from string.punctucation
trans_table = {ord(c): None for c in punc}


def makedict(s, forceidf=None, scale=1.0):
    words = set(s.lower().translate(trans_table).strip().split())
    words = set(w for w in words if len(w) > 1 and (not w in english_stop_words))
    idfd = {}
    for (
        w
    ) in (
        words
    ):  # todo: if we're using bigrams in vocab then this won't search over them
        if forceidf is None:
            if w in vocab:
                idfval = idf[vocab[w]] * scale  # we have idf for this
            else:
                idfval = 1.0 * scale  # assume idf 1.0(low)
        else:
            idfval = forceidf
        idfd[w] = idfval

    return idfd


def merge_dicts(dlist):
    m = {}
    for d in dlist:
        for k, v in d.items():
            m[k] = m.get(k, 0) + v

    return m


search_dict = {}
for paper in tqdm(col_papers.find()):
    dict_title = makedict(paper["title"], forceidf=10, scale=3)
    dict_authors = makedict(" ".join(paper["authors"]), forceidf=5)
    dict_abstract = makedict(paper["abstract"])
    q_dict = merge_dicts([dict_title, dict_authors, dict_abstract])

    search_dict[paper["id"]] = q_dict

json.dump(search_dict, open(os.path.join(DATA_PATH, "search.json"), "w"))

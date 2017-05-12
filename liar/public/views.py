# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

import itertools

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import current_app

from liar.utils import flash_errors
from liar.extensions import mongo, cache

import scipy
from sklearn import manifold
from scipy.spatial.distance import squareform, pdist

#wordcloud imports
import pandas as pd
from collections import Counter
import re
from collections import defaultdict
from nltk.corpus import stopwords
import nltk
import operator

blueprint = Blueprint('public', __name__, static_folder='../static')

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


gag_list=["EX","RP","TO","VB","WP","PRP","DT","VBP","IN","POS",".","CD","``"]

def split_sentence(text):
    sentence=nltk.word_tokenize(text)
    tagged = nltk.pos_tag(sentence)
    tagged=[tag for tag in tagged if tag[1] not in gag_list]
    pass_list=[tag[0] for tag in tagged]
    return pass_list




def gen_dict(statement_text):
    words=[split_sentence(sentence) for sentence in statement_text]
    word_dict=defaultdict(int)
    for word_list in words:
        temp_dict=dict(Counter(word_list))
        word_dict={**word_dict,**temp_dict}
    return word_dict


def nodes():
    statements = mongo.db.statements
    return statements.aggregate([
        {
            "$unwind": {
                "path": "$subjects"
            }
        },
        {
            "$group": {
                "_id": "$subjects",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ])

def points():
    statements = mongo.db.statements
    subjects = tuple(sorted(statements.distinct("subjects")))
    subjectLists = tuple(s["subjects"] for s in statements.find({}, {"subjects": True, "_id": False}))
    combos = frozenset(itertools.chain.from_iterable(itertools.combinations(l, 2) for l in subjectLists))

    length = len(subjects)
    matrix = scipy.zeros((length, length))

    def numberCommon(x, y):
        if x == y:
            return 0
        else:
            return statements.find({
                '$and': [{'subjects': x}, {'subjects': y}]
            }).count()

    for i, j in combos:
        i_index = subjects.index(i)
        j_index = subjects.index(j)
        common = numberCommon(i, j)
        matrix[i_index, j_index] = common
        matrix[j_index, i_index] = common

    most = matrix.max()

    mds = manifold.MDS(n_components=2, n_init=4, max_iter=300, eps=1e-6, dissimilarity="precomputed", n_jobs=-1)
    return scipy.array(mds.fit_transform(most - matrix))

def edges():
    pass

def make_data(nodes, points):
    pass


#######################Word cloud#####################
def word_cloud():
    statements=mongo.db.statements
    statement_text=statements_df['statement'].tolist()
    wordcount=defaultdict(int)
    word_dict=gen_dict(statement_text)
    word_dict=dict(sorted(word_dict.items(), key=operator.itemgetter(1), reverse=True)[:100])
    return word_cloud
#####################################################



@blueprint.route('/', methods=['GET'])
#@cache.cached(timeout=10)
def home():
    """Home page."""
    return render_template('public/home.html', nodes=nodes(), points=points())


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')

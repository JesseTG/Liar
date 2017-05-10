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

blueprint = Blueprint('public', __name__, static_folder='../static')


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



@blueprint.route('/', methods=['GET'])
#@cache.cached(timeout=10)
def home():
    """Home page."""
    return render_template('public/home.html', nodes=nodes(), points=points())


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')

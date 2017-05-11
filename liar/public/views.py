# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

import itertools
import math

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import current_app

from liar.utils import flash_errors
from liar.extensions import mongo, cache

import scipy
from sklearn import manifold
from scipy.interpolate import interp1d
from scipy.spatial.distance import squareform, pdist

from numpy import amin, amax

from colour import Color

blueprint = Blueprint('public', __name__, static_folder='../static')

COLORS = tuple(map(Color, ("#661a00", "#E71F28", "#EE9022", "#FFD503", "#C3D52D", "#83BF44")))
interval = tuple(i/(len(COLORS) - 1) for i in range(len(COLORS)))
red = interp1d(interval, [c.red for c in COLORS])
green = interp1d(interval, [c.green for c in COLORS])
blue = interp1d(interval, [c.blue for c in COLORS])

def gradient(i):
    return Color(rgb=(red(i), green(i), blue(i)))

def nodes():
    statements = mongo.db.statements
    r = ["$PantsOnFire", "$False", "$MostlyFalse", "$HalfTrue", "$MostlyTrue", "$True"]
    one = 1
    zero = 0
    return statements.aggregate([
        {
            "$unwind": {
                "path": "$subjects"
            }
        },
        {
            "$group": {
                "_id": "$subjects",

                "PantsOnFire": {"$sum": { "$cond": [ { "$eq": [ "$ruling", "Pants on Fire!" ] }, one, zero ] } },
                "False": {"$sum": { "$cond": [ { "$eq": [ "$ruling", "False" ] }, one, zero ] } },
                "MostlyFalse": {"$sum": { "$cond": [ { "$eq": [ "$ruling", "Mostly False" ] }, one, zero ] } },
                "HalfTrue": {"$sum": { "$cond": [ { "$eq": [ "$ruling", "Half-True" ] }, one, zero ] } },
                "MostlyTrue": {"$sum": { "$cond": [ { "$eq": [ "$ruling", "Mostly True" ] }, one, zero ] } },
                "True": {"$sum": { "$cond": [ { "$eq": [ "$ruling", "True" ] }, one, zero ] } },
                "numberOfRulings": {"$sum": one}
            }
        },
        {
            "$project": {
                "_id": True,
                "rulings": r,
                "numberOfRulings": True,
                "averageRuling": {
                    "$divide": [
                        {
                            "$sum": [
                                {"$multiply": ["$PantsOnFire", 0]},
                                {"$multiply": ["$False", 1]},
                                {"$multiply": ["$MostlyFalse", 2]},
                                {"$multiply": ["$HalfTrue", 3]},
                                {"$multiply": ["$MostlyTrue", 4]},
                                {"$multiply": ["$True", 5]}
                            ]
                        },
                        "$numberOfRulings"
                    ]
                }
            }
        },
        {
            "$project": {
                "_id": True,
                "rulings": True,
                "numberOfRulings": True,
                "averageRuling": True,
                "normalizedAverageRuling": {
                    "$divide": ["$averageRuling", 5.0]
                }
            }
        },
        {
            "$sort": { "_id": 1 }
        }
    ])

@cache.cached(timeout=300)
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

    def radius(subject):
        return math.sqrt(statements.count({"subjects": {"$in": [subject]}}))

    for i, j in combos:
        i_index = subjects.index(i)
        j_index = subjects.index(j)
        common = numberCommon(i, j)
        matrix[i_index, j_index] = common
        matrix[j_index, i_index] = common

    for i in range(length):
        i_radius = radius(subjects[i])
        for j in range(length):
            j_radius = radius(subjects[j])
            matrix[i, j] += i_radius + j_radius
            matrix[j, i] += i_radius + j_radius

    most = matrix.max()

    mds = manifold.MDS(n_components=2, n_init=4, max_iter=300, eps=1e-6, dissimilarity="precomputed", n_jobs=-1)
    return scipy.array(mds.fit_transform(most - matrix))

def viewbox(points):
    am = amax(points)
    return "{0} {1} {2} {3}".format(-am, -am, am * 2, am * 2)


@blueprint.route('/', methods=['GET'])
#@cache.cached(timeout=10)
def home():
    n = nodes()
    p = points()
    v = viewbox(p)

    """Home page."""
    return render_template('layout.html', nodes=n, points=p, viewbox=v, gradient=gradient)


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')

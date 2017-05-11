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

from numpy import amax

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
    return statements.aggregate([
        {
            "$unwind": {
                "path": "$subjects"
            }
        },
        {
            "$group": {
                "_id": "$subjects",

                "PantsOnFire": {"$sum": { "$cond": [ { "$eq": [ "$ruling", "Pants on Fire!" ] }, 1, 0 ] } },
                "False": {"$sum": { "$cond": [ { "$eq": [ "$ruling", "False" ] }, 1, 0 ] } },
                "MostlyFalse": {"$sum": { "$cond": [ { "$eq": [ "$ruling", "Mostly False" ] }, 1, 0 ] } },
                "HalfTrue": {"$sum": { "$cond": [ { "$eq": [ "$ruling", "Half-True" ] }, 1, 0 ] } },
                "MostlyTrue": {"$sum": { "$cond": [ { "$eq": [ "$ruling", "Mostly True" ] }, 1, 0 ] } },
                "True": {"$sum": { "$cond": [ { "$eq": [ "$ruling", "True" ] }, 1, 0 ] } },
                "numberOfRulings": {"$sum": 1}
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

    # combos = tuple(statements.aggregate([
    #     {
    #         '$project': { "subjects": True }
    #     },
    #     {
    #         '$addFields': { "subjects2" : "$subjects" }
    #     },
    #     {
    #         '$unwind': "$subjects"
    #     },
    #     {
    #         '$unwind': "$subjects2"
    #     },
    #     {
    #       '$group': {
    #         '_id': {
    #             "$cond": {
    #                 "if": {'$gt': ["$subjects", "$subjects2"]},
    #                 "then": ["$subjects", "$subjects2"],
    #                 "else": ["$subjects2", "$subjects"]
    #             }
    #         }
    #       }
    #     },
    #     {
    #         '$group': {
    #             '_id': None,
    #             'pairs': {'$push': "$_id"}
    #         }
    #     }
    # ]))[0]
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
        return math.sqrt(statements.count({"subjects": {"$elemMatch": { "$eq": subject}}}))

    for i, j in combos:
        i_index = subjects.index(i)
        j_index = subjects.index(j)
        common = numberCommon(i, j)
        matrix[i_index, j_index] = common
        matrix[j_index, i_index] = common

    most = matrix.max()

    mds = manifold.MDS(n_components=2, n_init=10, max_iter=1000, eps=1e-9, dissimilarity="precomputed", n_jobs=-1)
    return scipy.array(mds.fit_transform(most - matrix))

def viewbox(points):
    am = amax(points)
    margin = am * 0.05
    return "{0} {1} {2} {3}".format(-am - margin, -am - margin, am*2 + margin, am*2 + margin)


@blueprint.route('/', methods=['GET'])
#@cache.cached(timeout=10)
def home():
    n = tuple(nodes())
    p = points()
    v = viewbox(p)

    """Home page."""
    return render_template('layout.html', nodes=n, points=p, viewbox=v, gradient=gradient, colors=COLORS)


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')

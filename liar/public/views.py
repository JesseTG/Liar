# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

import itertools
import math

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import current_app

from liar.utils import flash_errors
from liar.extensions import cache
from .. import queries

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

@cache.cached(timeout=300)
def points():
    subjects = tuple(sorted(queries.subjects()))

    length = len(subjects)
    matrix = scipy.zeros((length, length))

    def radius(subject):
        return math.sqrt(queries.subjectMentions(subject))

    for c in queries.combos():
        _id = c['_id']
        count = c['count']
        i_index = subjects.index(_id[0])
        j_index = subjects.index(_id[1])
        matrix[i_index, j_index] = count
        matrix[j_index, i_index] = count

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
    n = tuple(queries.nodes())
    p = points()
    v = viewbox(p)

    """Home page."""
    return render_template('layout.html', nodes=n, points=p, viewbox=v, gradient=gradient, colors=COLORS)


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')

# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

from collections import Counter, defaultdict
import operator
import re
import itertools
import math

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import current_app

from nltk.corpus import stopwords
import nltk

from liar.utils import flash_errors
from liar.extensions import cache
from .. import queries

import scipy
import pandas as pd
from sklearn import manifold
from scipy.interpolate import interp1d
from scipy.spatial.distance import squareform, pdist

from numpy import amax

from colour import Color


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

blueprint = Blueprint('public', __name__, static_folder='../static')

COLORS = tuple(map(Color, ("#661a00", "#E71F28", "#EE9022", "#FFD503", "#C3D52D", "#83BF44")))
interval = tuple(i/(len(COLORS) - 1) for i in range(len(COLORS)))
red = interp1d(interval, [c.red for c in COLORS])
green = interp1d(interval, [c.green for c in COLORS])
blue = interp1d(interval, [c.blue for c in COLORS])


def gradient(i):
    return Color(rgb=(red(i), green(i), blue(i)))

@cache.cached(timeout=300)
def compute_points(combos):
    subjects = tuple(sorted(tuple(queries.subjects())))

    length = len(subjects)
    matrix = scipy.zeros((length, length))

    def radius(subject):
        return math.sqrt(queries.subjectMentions(subject))

    for c in combos:
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

def build_data(points):
    nodes = tuple(queries.nodes())

    assert len(nodes) == len(points)
    # The MDS should provide one 2D point for each topic...

    for i in range(len(nodes)):
        node = nodes[i]
        point = points[i]
        node['x'] = point[0]
        node['y'] = point[1]
        node['radius'] = math.sqrt(node['numberOfRulings'])


#######################Word cloud#####################
def word_cloud():
    statements=mongo.db.statements
    statement_text=statements_df['statement'].tolist()
    wordcount=defaultdict(int)
    word_dict=gen_dict(statement_text)
    word_dict=dict(sorted(word_dict.items(), key=operator.itemgetter(1), reverse=True)[:100])
    return word_cloud
#####################################################



    return { n['_id'] : n for n in nodes}

def compute_edges(nodes, combos):
    def make_edge(combo):
        return {
            'a': nodes[combo['_id'][0]],
            'b': nodes[combo['_id'][1]],
            'count': combo['count']
        }

    def allow_edge(edge):
        a = edge['a']
        b = edge['b']
        count = edge['count']

        return (count / a['numberOfRulings'] >= 0.05) or (count / b['numberOfRulings'] >= 0.05)

    return tuple(e for e in map(make_edge, combos) if allow_edge(e))


@blueprint.route('/', methods=['GET'])
#@cache.cached(timeout=10)
def home():
    combos = tuple(queries.combos())
    points = compute_points(combos)
    nodes = build_data(points)
    edges = compute_edges(nodes, combos)
    v = viewbox(points)

    """Home page."""
    return render_template('layout.html', nodes=nodes, edges=edges, viewbox=v, gradient=gradient, colors=COLORS)


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')

import pymongo
from pymongo import MongoClient
import itertools
import scipy
from sklearn import manifold
from scipy.spatial.distance import squareform, pdist


def numberCommon(x, y):
    if x == y:
        return 0
    else:
        return statements.find({
            '$and': [{'subjects': x}, {'subjects': y}]
        }).count()

def nodes():
    liar_db=connection.liar
    statements=liar_db.statements
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


def edges():

    liar_db=connection.liar
    statements=liar_db.statements
    subjects = tuple(sorted(statements.distinct("subjects")))
    subjectLists = tuple(s["subjects"] for s in statements.find({}, {"subjects": True, "_id": False}))
    combos = frozenset(itertools.chain.from_iterable(itertools.combinations(l, 2) for l in subjectLists))
    length = len(subjects)
    matrix = scipy.zeros((length, length))
    for i, j in combos:
        i_index = subjects.index(i)
        j_index = subjects.index(j)
        common = numberCommon(i, j)
        matrix[i_index, j_index] = common
        matrix[j_index, i_index] = common

    most = matrix.max()

    mds = manifold.MDS(n_components=2, n_init=4, max_iter=300, eps=1e-6, dissimilarity="precomputed", n_jobs=-1)

def add_coordinates():
    n=nodes()
    coords=manifold.MDS(n_components=2, n_init=4, max_iter=300, eps=1e-6, dissimilarity="precomputed", n_jobs=-1)



connection=MongoClient()

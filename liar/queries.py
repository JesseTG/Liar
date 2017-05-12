
from liar.extensions import mongo, cache


def nodes():
    return mongo.db.statements.aggregate([
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
                "rulings": ["$PantsOnFire", "$False", "$MostlyFalse", "$HalfTrue", "$MostlyTrue", "$True"],
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


def combos():
    return tuple(mongo.db.statements.aggregate([
        {
            '$project': { "subjects": True }
        },
        {
            '$addFields': { "subjects2" : "$subjects" }
        },
        {
            '$unwind': "$subjects"
        },
        {
            '$unwind': "$subjects2"
        },
        {
            '$group': {
                '_id': '$_id',
                'pairs': {
                    "$addToSet": {
                        "$cond": {
                            "if": {'$gt': ["$subjects", "$subjects2"]},
                            "then": ["$subjects2", "$subjects"],
                            "else": ["$subjects", "$subjects2"]
                        }
                    }
                }
            }
        },
        {
            '$project': {
                '_id': True,
                'pairs': {
                    '$filter': {
                        'input': "$pairs",
                        'as': "pair",
                        'cond': {
                            '$ne': [
                                {
                                    '$arrayElemAt': ["$$pair", 0]
                                },
                                {
                                    '$arrayElemAt': ["$$pair", 1]
                                }
                            ]
                        }
                    }
                }
            }
        },
        {
            '$match': {
                'pairs': {
                    '$ne': []
                }
            }
        },
        {
            '$unwind': "$pairs"
        },
        {
            '$group': {
                '_id': "$pairs",
                'count': { '$sum': 1 }
            }
        }
    ]))


def subjects():
    return mongo.db.statements.distinct("subjects")

def subjectMentions(subject:str):
    return mongo.db.statements.count({
        "subjects": {
            "$elemMatch": {
                "$eq": subject
            }
        }
    })
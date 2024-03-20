from bson import ObjectId

from pymongo import MongoClient
client = MongoClient('mongodb://test:test@3.34.179.28', 27017)
db = client.tarzan

db.article.insert_one({'state':'미처리', 'title':'방가방', 'text':'방', 'date':'24/03/18', 'house':418, 'name':'박덕기'})

print(db.article.find_one({'name':'박덕기'}))
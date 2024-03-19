from bson import ObjectId

from pymongo import MongoClient
client = MongoClient('mongodb://test:test@3.34.179.28', 27017)
db = client.tarzan

db.comment.insert_one({'article_id':ObjectId('65f85d24013f75d980bc17e5'), 'name':'박덕기', 'house':418, 'text':'저도 반갑습니다.'})

print(db.comment.find_one({'name':'박덕기'}))
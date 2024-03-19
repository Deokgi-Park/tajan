from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider
from flask_jwt_extended import *
from werkzeug.security import *

import json
import sys

# JWT 설정
app = Flask(__name__, instance_relative_config=True)
app.config.update(
    DEBUG = True,
    JWT_SECRET_KEY = 'X3FH9ei1LT2yhfx6nI4FpXml9Z4lXvVH0AfLIfPkIiZVjiwb'
)
jwt = JWTManager(app)


# DB 연결
client = MongoClient('mongodb://test:test@3.34.179.28', 27017)
db = client.tarzan


# MongoDB ObjectID값을 jsonify로 return하기 위한 커스텀 인코더
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)
    
app.json = CustomJSONProvider(app)


# API 시작, 로그인 페이지(메인 페이지)
@app.route('/')
def home():
        return render_template('index.html')

# 로그인 기능
@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['number']  # 기수-학번으로 입력받는다. ex)5-25
    pw = request.form['pw']

    # 입력받은 값을 기수, 학번으로 나눈다
    user = user_id.split('-')
    grade = int(user[0])
    number = int(user[1])

    # 일치하는 회원 찾기
    user = db.user.find_one({'grade':grade, 'number':number, 'pw':pw})

    # 일치하는 회원이 있을 때 로그인, 성공하면 토큰 발행
    if user:
        userData = [user['name'], user['house']]
        name = user['name']
        house = user['house']

        return jsonify({
            'result':'success',
            'access_token': create_access_token(identity=userData,
                                                expires_delta=False) # 토큰 만료시간
        })
    else:
        return jsonify({'result':'failure'})



# 로그인 성공 시 게시글 리스트로 이동
@app.route('/listAuth', methods = ['GET'])
# @jwt_required()
def list():
    # current_user = get_jwt_identity() # 토큰 값 가져오기
    # name = current_user[0]
    # house = current_user[1]

    # print(name, house)

    # user = db.user.find_one({'name':name, 'house':int(house)})
    # print(user)
    # print('good')

    return render_template('boardList.html')

    # else:
    #     return jsonify({'result':'failure'})

@app.route('/boardList')
def good():
    return render_template('boardList.html')





# 직접 실행될 때만(이 코드가 import당하는게 아닐 때) 서버를 가동한다
# 다른 파일에서 이 코드를 import하여 모듈을 이용할 수 있게 한다
if __name__ == '__main__':
    print(sys.executable)  # 이걸 실행하는 파이썬 인터프리터 경로 출력
    app.run('0.0.0.0', port=33333, debug=True) # 모든 IP에 대한, 웹으로의 접근을 허용함(정확히는 리스닝 함)
from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider
from flask_jwt_extended import *
from werkzeug.security import *

from datetime import datetime
from jinja2 import Template


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

# API 시작, 회원가입 페이지 이동
@app.route('/addUser')
def addUser():
        return render_template('addUser.html')

# API 시작, 회원가입 체크
@app.route('/regiUser', methods=['POST'])
def regiUser():
    grade = int(request.form['grade'])
    number = int(request.form['number'])  # 기수-학번으로 입력받는다. ex)5-25
    name = request.form['name']
    pw = request.form['pw']
    print(grade,name,number,pw)
    user = db.user.find_one({'grade':grade, 'number':number, 'name':name })
    print(user)
    if user:
        update_query = {'$set': {'pw':pw}}  # 특정 필드 이름과 값을 수정하세요
        db.user.update_one({'grade':grade, 'number':number, 'name':name}, update_query)  # 필드 이름에 맞게 수정하세요
        return "success"
    else:
        return "failed"


# 로그인 기능
@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['number']  # 기수-학번으로 입력받는다. ex)5-25
    pw = request.form['password']
    print(user_id, pw)

    # 입력받은 값을 기수, 학번으로 나눈다
    user = user_id.split('-')
    grade = int(user[0])
    number = int(user[1])
    print(grade,number)

    # 일치하는 회원 찾기
    user = db.user.find_one({'grade':grade, 'number':number, 'pw':pw})
    print(user)

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
    

@app.route('/add_article', methods=['POST'])
@jwt_required()
def add_article():
    project_list = []
    current_user = get_jwt_identity() 
    name =current_user[0]
    house = str(current_user[1])

    title = request.form['title']
    content = request.form['content']

    year = str(datetime.today().year)
    month = str(datetime.today().month)
    date = str(datetime.today().day)
    time = year + "/" + month + "/" + date

    # 중복된 글이 없을때만 DB에 저장한다
    writeGo = db.article.find_one({'title':title, 'text':content})
    if not writeGo and title != '' and content != '': 
        db.article.insert_one({'state':'0','title':title,'text':content,'date':time,'house':house,'name':name})

    house_list = db.article.find({'house':house,'name':name})

    # if title and content:
    for i in house_list :           # house_list 값이 비어 있을 경우?
        project_list.append({'title': i['title'],'date':i['date'], 'house':i['house']})

    return jsonify({'status': 'success', 'project_list':project_list})
    # else:
        # return jsonify({'status': 'error', 'message': '제목과 내용을 입력하세요.'})
    

# 로그인 성공 시 게시글 리스트로 이동
@app.route('/listAuth', methods = ['POST'])
@jwt_required()
def list():
    current_user = get_jwt_identity()

    name = current_user[0]
    house = current_user[1]

    user = db.user.find_one({'name':name, 'house':house})

    if user:    
        return jsonify({'result':'success'})
    else:
        return jsonify({'result':'failure'})

@app.route('/boardList')
def good():
    return render_template('boardList.html', userName='양선규')
    
# @app.route('/test')
# def test(userName):
#     return render_template('jinjaTest.html')





# 직접 실행될 때만(이 코드가 import당하는게 아닐 때) 서버를 가동한다
# 다른 파일에서 이 코드를 import하여 모듈을 이용할 수 있게 한다
if __name__ == '__main__':
    print(sys.executable)  # 이걸 실행하는 파이썬 인터프리터 경로 출력
    app.run('0.0.0.0', port=33333, debug=True) # 모든 IP에 대한, 웹으로의 접근을 허용함(정확히는 리스닝 함)
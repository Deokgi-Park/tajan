from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request, make_response, session
from flask.json.provider import JSONProvider
from flask_jwt_extended import *
from werkzeug.security import *

from datetime import datetime, timedelta

from datetime import datetime
from jinja2 import Template

from datetime import timedelta

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
    grade = request.form['grade']
    number = request.form['number']  # 기수-학번으로 입력받는다. ex)5-25
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
    # 입력받은 값을 기수, 학번으로 나눈다
    user = user_id.split('-')
    grade = user[0]
    number = user[1]
    # 일치하는 회원 찾기
    user = db.user.find_one({'grade':grade, 'number':number, 'pw':pw})
    # 일치하는 회원이 있을 때 로그인, 성공하면 토큰 발행
    if user:
        userData = [user['name'], user['house']]
        access_token = create_access_token(identity=userData, expires_delta=timedelta(minutes=60))
        response = make_response(jsonify({'result': 'success', "grade": grade, "number":number }))
        response.set_cookie('access_token', access_token)
        return response
    else:
        response = make_response(jsonify({'result': 'failed'}))
        return response


@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    current_user = get_jwt_identity()
    name = current_user[0]
    response = make_response(jsonify({'message': name + '님 로그아웃 되었습니다.',"tokenname": "access_token"}))
    unset_jwt_cookies(response)
    return response


@app.route('/loginManager')
def loginManager():
        return render_template('managerPage.html', name='test')


@app.route('/loginUser')
def loginUser():
        return render_template('mainPage.html')


#모니터링 템플렛 호출 페이지
@app.route('/batchHouse', methods=['POST'])
@jwt_required()
def batchHouse():
    current_user = get_jwt_identity()
    houselist = db.user.distinct('house')
    houseAddCnt =[]
    for house in houselist :
        CNT = db.article.count_documents({"house": house, "state": "0"})
        houseAddCnt.append({house : CNT})
    print(houseAddCnt)
    return render_template('managerPageMoniterTmp.html', houseList = houselist, houseAddCnt=houseAddCnt)


# 문의글 리스팅 + 등록
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
        project_list.append({'title': i['title'],'date':i['date'], 'house':i['house'], 'articleId':i['_id'], 'name':i['name'], 'state':i['state']})

    return render_template('mainPageListTmp.html', project_list=project_list)
    #return jsonify({'status': 'success', 'project_list':project_list})
    # else:
        # return jsonify({'status': 'error', 'message': '제목과 내용을 입력하세요.'})


# 검색 기능, 대소문자 구분 안함
@app.route('/searchArticle', methods = ['POST'])
@jwt_required()
def searchArticle():
    current_user = get_jwt_identity()

    name = current_user[0]
    house = current_user[1]

    # 토큰에 해당하는 유저가 존재할 경우 로직 실행
    user = db.user.find_one({'name':name, 'house':house})
    if user:
        title = request.form['title'] # 검색어

        if name != '타잔' and house != '0': # 일반 유저일 경우 자신의 호실만 검색
            article = db.article.find({'house':house, 'title':{'$regex':title, '$options':'i'}})
        else: # 관리자일 경우 호실 구분없이 검색
            article = db.article.find({'title':{'$regex':title, '$options':'i'}})

        articleList = []
        for i in article:
            if i not in articleList:
                articleList.append({'title': i['title'],'date':i['date'], 'house':i['house'], 'articleId':i['_id'], 'name':i['name'], 'state':i['state']})
        return render_template('mainPageListTmp.html', project_list=articleList)


# 문의글 상세 페이지(제목, 내용, 처리상태 조회,수정 / 댓글 작성)
# 문의글 상세 페이지 조회(글, 댓글리스트)
@app.route('/joinArticle', methods = ['POST'])
@jwt_required()
def joinArticle():
    articleId = ObjectId(request.form['articleId']) # _id값 수신

    article = db.article.find_one({'_id':articleId}) # 글 찾기
    comment = db.comment.find({'article_id':articleId}) # 댓글 찾기(커서 객체)

    commentList = []
    for i in comment:
        commentList.append({'name':i['name'], 'text':i['text'], 'date':i['date']})
    return render_template('mainPageModalTmp.html', article=article, comment=commentList)
 

# 문의글 수정 기능(제목, 내용, 처리상태)
@app.route('/modifyArticle', methods = ['POST'])
@jwt_required()
def modifyArticle():
    articleId = ObjectId(request.form['articleId']) # _id값 수신
    changeTitle = request.form['title'] # 제목, 내용, 처리상태 수신
    changeText = request.form['text']
    changeState = request.form['state']
    
    if changeState == '미처리':
        changeState = '0'
    elif changeState == '진행중':
        changeState = '1'
    else:
        changeState = '2'

    result = db.article.update_one({'_id':articleId}, {'$set':{'title':changeTitle, 'text':changeText, 'state':changeState}})

    if result.modified_count == 1 :
        return jsonify({'result' : 'success'})
    else :
        return jsonify({'result' : 'failure'})


# 문의글 삭제 기능, 댓글까지 함께 삭제된다
@app.route('/deleteArticle', methods = ['POST'])
@jwt_required()
def deleteArticle():
    current_user = get_jwt_identity()

    name = current_user[0]
    house = current_user[1]

    # 토큰에 해당하는 유저가 존재할 경우
    user = db.user.find_one({'name':name, 'house':house})
    if user:

        articleId = ObjectId(request.form['articleId']) # 삭제할 글의 id값을 가져온다
        result = db.article.delete_one({'_id':articleId}) # id에 해당하는 글을 삭제
        result2 = db.comment.delete_many({'article_id':articleId}) # 댓글도 함께 삭제

        if result.deleted_count == 1 and result2.acknowledged :
            return jsonify({'result' : 'success'})
        else :
            return jsonify({'result' : 'failure'})


# 댓글 작성 기능
@app.route('/makeComment', methods = ['POST'])
@jwt_required()
def makeComment():
    current_user = get_jwt_identity()

    name = current_user[0]
    house = current_user[1]

    # 토큰에 해당하는 유저가 존재할 경우
    user = db.user.find_one({'name':name, 'house':house})
    if user:
        year = str(datetime.today().year)
        month = str(datetime.today().month)
        date = str(datetime.today().day)

        time = year + "/" + month + "/" + date # 작성일자
        articleId = ObjectId(request.form['articleId']) # _id값
        text = request.form['text'] # 댓글내용
        
        # 댓글 작성
        result = db.comment.insert_one({'article_id':articleId, 'name':name, 'house':house, 'text':text, 'date':time})

        if result.acknowledged == 1:
            return jsonify({'result':'success'})
        else:
            return jsonify({'result':'failure'})


# 로그인 성공 시 게시글 리스트로 이동
@app.route('/listAuth', methods = ['POST'])
@jwt_required()
def list():
    current_user = get_jwt_identity()
    name = current_user[0]
    house = current_user[1]
    user = db.user.find_one({'name':name, 'house':house})

    if user:
        grade = user.get('grade')  # grade 필드 값 가져오기
        number = user.get('number')  # number 필드 값 가져오기
        if grade == '0' and number  == '0':
            return jsonify({'result':'admin'})
        else:
            return jsonify({'result':'success'})
    else:
        return jsonify({'result':'failure'})

@app.route('/boardList')
def good():
    return render_template('boardList.html', userName='양선규')
    

# 모든 호실 미처리 문의 리스트
@app.route('/noList', methods = ['POST'])
@jwt_required()
def noList():
    current_user = get_jwt_identity()

    name = current_user[0]
    house = current_user[1]

    # 관리자일 경우 로직 실행
    if name == '타잔' and house == '0':
        noList = db.article.find({'state':'0'}) # 미처리 문의 전부 가져오기
        
        if noList: # 미처리 문의가 1개 이상 존재할 경우
            return jsonify({'result':'success', 'noList':noList})
        else:
            return jsonify({'result':'failure'})
        

# 관리자 페이지 호실 인원 리스트
@app.route('/joinHouse', methods =['POST'])
@jwt_required()
def joinHouse():        # 관리자가 로그인 했을 경우
    current_user = get_jwt_identity()
    name = current_user[0]
    house = current_user[1]
    
    if name == "타잔" and house == "0":
        # 호실 선택 시
        user_house = request.form['house']

        home = db.user.find({'house':user_house})

        return jsonify({'result':'success','home':home})
    else:
        return jsonify({'result':'failure'})

# 관리자 페이지 "호실 문의 리스트 확인"
@app.route('/checkList', methods =['POST'])
@jwt_required()
def checkList():        # 관리자가 로그인 했을 경우
    current_user = get_jwt_identity()
    name = current_user[0]
    house = current_user[1]
    
    if name == "타잔" and house == "0":
        # 호실 선택 시
        user_house = request.form['house']

        home = db.comment.find({'house':user_house})

        return jsonify({'result':'success','home':home})
    else:
        return jsonify({'result':'failure'})
    
# 관리자 페이지 "체크 인원 수정 처리"
@app.route('/modifyUser', methods =['POST'])
@jwt_required()
def modifyUser():        # 관리자가 로그인 했을 경우
    current_user = get_jwt_identity()
    name = current_user[0]
    house = current_user[1]
    
    if name == "타잔" and house == "0":
        # 호실 선택 시
        user_house = request.form['house']
        user_name = request.form['name']

        user_grade = request.form['grade']
        user_number = request.form['number']
        new_user_name = request.form['new_name']
        home = db.user.find_one({'house':user_house,'name':user_name})
        if home :    
            db.user.update_one({'house':user_house,'name':user_name},{"$set": {"grade": user_grade, "number": user_number, "name": new_user_name}})
        return jsonify({'result':'success'})
    else:
        return jsonify({'result':'failure'})

# 관리자 페이지 "체크 인원 퇴사 처리"
@app.route('/deleteUser', methods =['POST'])
@jwt_required()
def deleteUser():        # 관리자가 로그인 했을 경우
    current_user = get_jwt_identity()
    name = current_user[0]
    house = current_user[1]
    
    if name == "타잔" and house == "0":
        # 호실 선택 시
        user_house = request.form['house']
        user_name = request.form['name']
        home = db.user.find_one({'house':user_house,'name':user_name})
        if home :    
            db.user.delete_one({'name':user_name})
        return jsonify({'result':'success'})    
    else:
        return jsonify({'result':'failure'})

# 직접 실행될 때만(이 코드가 import당하는게 아닐 때) 서버를 가동한다
# 다른 파일에서 이 코드를 import하여 모듈을 이용할 수 있게 한다
if __name__ == '__main__':
    print(sys.executable)  # 이걸 실행하는 파이썬 인터프리터 경로 출력
    app.run('0.0.0.0', port=33333, debug=True) # 모든 IP에 대한, 웹으로의 접근을 허용함(정확히는 리스닝 함)
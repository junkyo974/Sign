from flask import Flask, render_template, jsonify, request, session, redirect, url_for
app = Flask(__name__)


from pymongo import MongoClient
client = MongoClient('mongodb+srv://sparta:test@sparta.1hlyrob.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

import certifi

ca=certifi.where()


import jwt
# 토근 만료시간 부여를 위한 datetime 사용
import datetime
# 회원가입시 비밀번호 데이터 암호화
import hashlib

SECRET_KEY = 'BOOKREVIEW'

@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')

# [회원가입 API]
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']
    
    # 패스워드 암호화 / sha256 방법(=단방향 암호화. 풀어볼 수 없음)
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.users.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    
    return jsonify({'result': 'success'})
    
# [로그인 API]
# id, pw를 받아서 맞춰 본 뒤 토큰 발급
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.users.find_one({'id': id_receive, 'pw': pw_hash})
# --------------------------------------------------------------------- 작업중>
    if result is not None:
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token 발급
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

        
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    

    try:
        # token을 시크릿키로 디코딩
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
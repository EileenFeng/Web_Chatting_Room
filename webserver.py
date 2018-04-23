# Starter code for 311 Project 3I.
#
# First, install flask
# pip install flask
#
# Then, to initialize the database, run the following:
#     python app.py init
# Then run the app itself as:
#     python app.py
#
# Largely taken from https://gist.github.com/hackeris/fa2bfd20e6bec08c8d5240efe87d4687
import os
import sqlite3
import sys
import time
import bcrypt
import ssl

from bcrypt import hashpw, gensalt 

from flask import Flask
from flask import redirect
from flask import jsonify
from flask import request
from flask import session
from flask import render_template
from flask import send_from_directory
from jinja2 import Template
from jinja2 import utils

app = Flask(__name__)

app.secret_key = 'schrodinger cat'

default_channel_topic = "default topic"

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def connect_db():
    return sqlite3.connect(DATABASE_PATH)

def create_tables():
    conn = connect_db()
    cur = conn.cursor()
    #banned: channels
    cur.execute('''
            CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(32),
            password VARCHAR(32),
            channels TEXT,
            blocked TEXT,
            banned TEXT,
            uploadedfiles TEXT,
            channeladmin TEXT, 
            unique(username)
            )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS channels(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channelname VARCHAR(32),
        members TEXT,
        admin VARCHAR(32),
        topics TEXT,
        banned TEXT, 
        filenames TEXT,
        unique(channelname)
        )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channelname VARCHAR(32),
        user_id INTEGER,
        context TEXT,
        FOREIGN KEY (`user_id`) REFERENCES `user`(`id`)
        )''')
    conn.commit()
    conn.close()

def init_data():
    '''
    users = [
        ('user1', '123456'),
        ('user2', '123456')
    ]
    lines = [
        (1, 'First Post'),
        (1, 'Another Post'),
        (2, 'Here\'s my third post'),
        (2, 'Last post here.')
    ]
    '''
    conn = connect_db()
    cur = conn.cursor()
    #cur.executemany('INSERT INTO `user` VALUES(NULL,?,?)', users)
    #cur.executemany('INSERT INTO `chats` VALUES(NULL,?,?)', lines)
    conn.commit()
    conn.close()

def init():
    create_tables()
    init_data()

def get_user_from_username_and_password(username, password):
    conn = connect_db()
    cur = conn.cursor()
    print(username,password)
    #cur.execute('SELECT id, username FROM `user` WHERE username=\'%s\' AND password=\'%s\'' % (username, password))
    cur.execute('SELECT id, password FROM `user` WHERE username= ?', (username,))
    row = cur.fetchone()
    print (row)
    if row is not None:
        verify_pw = row[1].encode()
        try:
            if bcrypt.checkpw(password.encode(), verify_pw):
                return {'id': row[0], 'username': username}
            else:
                return None
        except Exception, e:
            return None
    else:
        return None

def create_user(username, password):
    conn = connect_db()
    cur = conn.cursor()
    encrypted_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    print("encrypted")
    print(encrypted_pw)
    try: 
        cur.execute('INSERT INTO `user` VALUES(NULL,?,?, NULL, NULL, NULL, NULL, NULL)', (username, encrypted_pw))
        cur.execute('SELECT id FROM `user` WHERE username= ?', (username,))
        row = cur.fetchone()
        conn.commit()
        conn.close()
        if row is not None:
            print("here")
            return {'id': row[0], 'username': username} 
        else:
            return None
    except sqlite3.IntegrityError:
        conn.commit()
        conn.close()
        print("failed")
        return None


def get_user_from_id(uid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM `user` WHERE id=%d' % uid)
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return {'id': row[0], 'username': row[1]}

def create_chat(uid, content):
    conn = connect_db()
    cur = conn.cursor()
    # ...
    stmt = 'INSERT INTO `chats` VALUES (NULL,' + str(uid) + ",\'" + content + '\')'
    print(stmt)
    try:
        cur.executescript(stmt)
    except Exception as e:
        return None
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return row

def get_chats(n):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, user_id, content FROM `chats` WHERE id>=%d ORDER BY id ASC' % n)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return list(map((lambda row: {'id': row[0],
                       'user_id': row[1],
                       'content': utils.escape(row[2]),
                       'username': get_user_from_id(row[1])['username']}),
                    rows))



def user_delete_chat_of_id(uid, tid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM `chat` WHERE  user_id=%s AND id=%s' % (uid, tid))
    conn.commit()
    conn.close()

def render_login_page():
    return render_template('login.html')

def render_create_account():
    return render_template('create_acc.html')

def render_change_pwd():
    return render_template('change_pwd.html')

@app.route('/change_pwd', methods=['GET', 'POST'])
def change_pwd():
    if request.method == 'GET':
        return render_change_pwd()
    elif request.method == 'POST':
        username = request.form['username']
        old_pwd = request.form['old_password']
        new_pwd = request.form['new_password']
    
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT password FROM `user` WHERE username= ?', (username,))
        db_pwd = cur.fetchone()[0].encode()
        #TO-DO: add encryption here
        #encrypted_oldpwd = bcrypt.hashpw(old_pwd.encode(), bcrypt.gensalt())
        encrypted_newpwd = bcrypt.hashpw(new_pwd.encode(), bcrypt.gensalt())

        try:
            if bcrypt.checkpw(old_pwd.encode(), db_pwd):
                cur.execute('UPDATE `user` SET password=? WHERE username=?', (encrypted_newpwd, username))            
            else:
                conn.commit()
                conn.close()
                return render_change_pwd()
        except Exception, e:
            conn.commit()
            conn.close()
            return render_change_pwd()
        conn.commit()
        conn.close()
        return redirect('/login')

# @app.route('/changepassword/<newpassword>')
# def changepassword(newpassword):
#     conn = connect_db()
#     cur = conn.cursor()
#     cur.execute('UPDATE `user` SET password=\'%s\' WHERE id=\'%d\'' % (newpassword, session['uid']))
#     conn.commit()
#     conn.close()
#     return "success", 200

# @app.route('/getpassword')
# def getpassword():
#     print("here123123")
#     if 'uid' in session:
#         conn = connect_db()
#         cur = conn.cursor()
#         cur.execute('SELECT password FROM `user` WHERE id=\'%d\'' % (session['uid']))
#         row = cur.fetchone()
#         conn.commit()
#         conn.close()
#         print("----")
#         print(row)
#         print("----")
#         return jsonify({'password': row[0]})
#     else:
#         return jsonify("Not logged in")

@app.route('/chats', methods=['GET'])
def chats():
    if 'uid' in session:
        return jsonify(get_chats(0))
    else:
        return jsonify("Error: not logged in!")

@app.route('/chats/from/<n>', methods=['GET'])
def chats_from(n):
    if 'uid' in session:
        return jsonify(get_chats(int(n)))
    else:
        return jsonify("Error: not logged in!")

def render_home_page(uid):
    user = get_user_from_id(uid)
    return render_template('chats.html', uid=uid, user=user['username'])

def render_channel_table(uid):
    user = get_user_from_id(uid)
    return render_template('table.html', uid=uid, user=user['username'])

def do_login(user):
    if user is not None:
        print("not null")
        session['uid'] = user['id']
        return redirect('/')
    else:
        print("User is none")
        if 'uid' in session:
            session.pop('uid')
        return redirect('/create_account')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'GET':
        print("create account render")
        return render_create_account()
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        user = create_user(username, password)
        print(user)
        return do_login(user)


@app.route('/create_channel/<channame>/<topic>')
def create_channel(channame, topic):
    print('in create channel')
    print(channame)
    print(topic)
    conn = connect_db()
    cur = conn.cursor()
    try:
        uid = session['uid']
        cur.execute('SELECT username FROM `user` WHERE id=\'%s\'' % uid)
        row = cur.fetchone()
        print(len(row))
        admin_name = row[0]
        print(admin_name)
        channame = '#' + channame
        cur.execute('INSERT INTO `channels` VALUES(NULL,?, ?, ?, ?, NULL, NULL);', (channame, admin_name, admin_name, topic))
        cur.execute('SELECT channels FROM `user` where username= ?', (admin_name,))
        row =cur.fetchone()
        new_channels = ""
        print(row)
        if row[0] is None:
            new_channels = channame
        else:
            new_channels = row[0] + channame
        print("new channel is")
        print(new_channels)
        cur.execute('UPDATE `user` SET channels=? WHERE username=?',(new_channels, admin_name))
        cur.execute('UPDATE `user` SET channeladmin=? WHERE username=?',(new_channels, admin_name))
        print("done")
        cur.execute('SELECT * FROM `user` WHERE channels=? AND username=?', (new_channels,admin_name))
        row = cur.fetchall()
        print(row)
        if row[0] is not None:
            cur.execute('SELECT * FROM `channels` WHERE channelname= ?', (channame,))
            row = cur.fetchall()
            print("channels")
            print(row)
            if row[0] is not None:
                conn.commit()
                conn.close()
                return "success", 200
        else:
            conn.commit()
            conn.close()
            return "forbidden", 403
    except sqlite3.IntegrityError:
        return "forbidden", 403

@app.route('/change_topic/<channel_name>/<new_topic>')
def change_topics(channel_name, new_topic):
    print("in change tocpics")
    print(channel_name)
    print(new_topic)
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute('UPDATE `channels` SET topics=? WHERE channelname=?',(new_topic, channel_name))
        cur.execute('SELECT topics FROM `channels` WHERE channelname=?', (channel_name,))
        row = cur.fetchone()
        print("after update topic")
        if row[0] == new_topic:
            conn.commit()
            conn.close() 
            return "success", 200      
        else:
            conn.commit()
            conn.close() 
            return "forbidden", 403     
    except sqlite3.IntegrityError:
        return "forbidden", 403

@app.route('/')
def index():
    if 'uid' in session:
        #return render_home_page(session['uid'])
        print("in uid in session index")
        return render_channel_table(session['uid'])
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_login_page()
    elif request.method == 'POST':
        print("IN LOGIN")
        username = request.form['username']
        password = request.form['password']
        user = get_user_from_username_and_password(username, password)
        return do_login(user)

@app.route('/chat', methods=['POST'])
def chat():
    if 'uid' in session:
        uid = session['uid']
        json = request.get_json()
        print(json)
        result = create_chat(json['uid'], json['content'])
        if result is None:
            return "forbidden", 403
        else:
            return "success", 200
    return redirect('/')

@app.route('/chat/<cid>/delete')
def delete_chat(cid):
    user_delete_chat_of_id(session['uid'], cid)
    return redirect('/')

@app.route('/logout')
def logout():
    if 'uid' in session:
        session.pop('uid')
    return redirect('/login')

# Static files
@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory('css', path)

if len(sys.argv) > 1 and sys.argv[1] == "init":
    init()
    exit(0)

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
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
import glob
import sys
import string
import ssl
import requests
import struct
import random
import json
import base64
import keyconfig
import cryptography
from Crypto.Cipher import AES
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from bcrypt import hashpw, gensalt 
from flask import Flask
from flask import redirect
from flask import jsonify
from flask import request
from flask import session
from flask import flash
from flask import render_template
from flask import send_from_directory
from werkzeug.utils import secure_filename
from jinja2 import Template
from jinja2 import utils


app = Flask(__name__)

BUFFER_SIZE = 1024
app.secret_key = 'schrodinger cat'
default_channel_topic = "default topic"
file_key = b'&%#$_9Gjns{]H6s_'

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def connect_db():
    return sqlite3.connect(DATABASE_PATH)

def create_tables():
    conn = connect_db()
    cur = conn.cursor()
    #banned: channels that banned this user
    #blocked: users that this user blocked
    # status 0 stands for not logged in, 1 stands for logged in
    cur.execute('''
            CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(32),
            password VARCHAR(32),
            status INTEGER,
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
        admins TEXT,
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
        content BLOB,
        FOREIGN KEY (`user_id`) REFERENCES `user`(`id`)
        )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS files(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename VARCHAR(32),
        uploader INTEGER,
        channelname VARCHAR(32)
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
        print("1")
        verify_pw = row[1].encode()
        print("2")
        print(verify_pw)
        try:
            if bcrypt.checkpw(password.encode(), verify_pw):
                print("here?")
                cur.execute('UPDATE `user` SET status=? WHERE username=?', (1, username)) 
                conn.commit()
                conn.close()
                return {'id': row[0], 'username': username}
            else:
                print("noooo")
                flash(u'Username or password error!', 'error')
                conn = connect_db()
                cur = conn.cursor()
                return None
        except Exception, e:
            print(e)
            conn = connect_db()
            cur = conn.cursor()
            return None
    else:
        flash(u'Username or password error!', 'error')
        conn = connect_db()
        cur = conn.cursor()
        return None

def get_members(channel_name):
    conn = connect_db()
    cur = conn.cursor()
    channel_name = '#' + channel_name
    print("????? in get members %s", channel_name)
    try:
        cur.execute('SELECT members FROM `channels` WHERE channelname=?', (channel_name,))
        row = cur.fetchone()
        if row is not None:
            if row[0] is None:
                conn.commit()
                conn.close()
                return list()
            else:
                memberlist = row[0].split(';')
                print("members for %s" % channel_name)
                print(memberlist)
                conn.commit()
                conn.close()
                return memberlist
        else:
            return list()
            conn.commit()
            conn.close()
    except sqlite3.IntegrityError as e:
        print(e)
        return list()
        conn.commit()
        conn.close()
            

def create_user(username, password):
    conn = connect_db()
    cur = conn.cursor()
    encrypted_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    print("encrypted")
    print(encrypted_pw)
    try: 
        cur.execute('INSERT INTO `user` VALUES(NULL,?,?, ?, NULL, NULL, NULL, NULL, NULL)', (username, encrypted_pw, 1))
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
        flash(u'Username have already been registered!', 'error')
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


def check_not_block(chat_list, msgblock):
    uid = session['uid']
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT username FROM `user` WHERE id=? ', (uid,))
    row = cur.fetchone()
    username = row[0]
    print("username is %s" % username)
    msgs = msgblock.split('\n', 19)
    print("messages")
    print(msgs)
    for msg in msgs:
        print("single msg")
        print(msg)
        split = msg.split('>', 1)
        print("split")
        print(split)
        if len(split) == 2:
            sentuser = split[0]
            chat = split[1]
            print("sent by %s" % sentuser)
            print("msg is %s" % chat)
            cur.execute('SELECT blocked FROM `user` WHERE username = ?', (username,))
            row2 = cur.fetchone()
            print("row2")
            print(row2[0])
            if row2[0] is None:
                chat_list.append(msg)
                continue
            blocked_list = row2[0].split(';')
            print("blocked list of %s is" % sentuser)
            if sentuser in blocked_list:
                continue
            else:
                chat_list.append(msg)
    return chat_list


def get_chats(channel_name, n):
    conn = connect_db()
    conn.text_factory = str
    cur = conn.cursor()
    channel_name = '#' + channel_name
    print("getcha")
    print(channel_name)
    try: 
        cur.execute('SELECT content FROM `chats` WHERE channelname = ? AND id>=? ORDER BY id ASC', (channel_name, 0))
        #cur.execute('SELECT content FROM `chats` WHERE channelname = ? AND id>=? ORDER BY id ASC', (channel_name,))
        print("wata")
        rows = cur.fetchall()
        print("2getcha %d" % len(rows))
        print(rows)
        conn.commit()
        conn.close()
        result_list = list()
        #did not write salt!!!
        if len(rows) != 0:
            for r in rows:
                print("lenth of cur is %d" % len(r))
                print(r[0])
                splits = r[0].split('\n', 2)
                print("after split")
                print(splits)
                salt = str.strip(splits[0])
                msg_encrypted = splits[1]
                signature = splits[2]
                print("encrypted")
                print(msg_encrypted)
                print("3")
                msg_decrypted = ''
                try:
                    kdf = PBKDF2HMAC(
                                    algorithm=hashes.SHA256(),
                                    length=32,
                                    salt=salt,
                                    iterations=100000,
                                    backend=default_backend()
                                    )
                    key = base64.urlsafe_b64encode(kdf.derive(keyconfig.part3_password.encode()))
                    fernet = Fernet(key)
                    msg_decrypted = fernet.decrypt(msg_encrypted)
                    print("?")
                    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
                    try:
                        h.update(msg_decrypted)
                        h.verify((signature))
                        print("Message authenticity confirmed! Message log is as follows: ")
                        print(msg_decrypted)
                        #result_list.append(msg_decrypted)
                        check_not_block(result_list, msg_decrypted)
                    except cryptography.exceptions.InvalidSignature:
                        print("Invalid signature!")
                except cryptography.fernet.InvalidToken as e:
                    print(e)
                    print("Not permitted to read channel logs")
            print("result chats")
            print(result_list)
            return result_list
        else:
            return list()
        '''
        return list(map((lambda row: {'id': row[0],
                            'content': utils.escape(msg_decrypted)}),
                            rows))
                
        return list(map((lambda row: {'id': row[0],
                        'user_id': row[1],
                        'content': utils.escape(row[2]),
                        'username': get_user_from_id(row[1])['username']}),
                        rows))
        '''
    except sqlite3.IntegrityError:
        conn.commit()
        conn.close()
        return list()

def get_channels(uid):
    #TO-DO: get channel list from sql similarly to get_chats
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT channelname, topics, members, admins FROM `channels` WHERE id>=? ORDER BY id ASC', (0, ))
    channels = cur.fetchall()
    cur.execute('SELECT username FROM `user` WHERE id=?', (session['uid'], ))
    row = cur.fetchone()
    try:
        username = row[0]
    except TypeError, e:
        return redirect('/logout')
    print("username is %s" % username)
    print("channels length")
    print(len(channels))
    print("channels")
    print(channels)
    print("done with channels")
    return_list = list()
    for chan in channels:
        print("cur")
        print(chan)
        channel_name = chan[0]
        print("cur channel name is %s" % channel_name)
        topics = chan[1]
        members = chan[2].split(';')
        admins = chan[3].split(';')
        print("topics")
        print(topics)
        print("members are")
        print(members)
        print("admins")
        print(admins)
        is_member = 0
        if username in members:
            is_member = 1
        return_list.append((channel_name, topics, is_member, admins))
    conn.commit()
    conn.close()
    print(return_list)
    return return_list

    '''
    cur.execute('SELECT channels FROM `user` WHERE id = ?', (uid,))
    row = cur.fetchone()
    if row[0] is None:
        conn.commit()
        conn.close()
        return list()
    else:
        print(row[0])
        res = row[0].split('#')
        chanlist = list()
        for chan in res:
            print(chan)
            if chan != '':
                print("appending")
                chan = '#' + chan
                cur.execute('SELECT topics FROM `channels` WHERE channelname = ?', (chan,))
                row = cur.fetchone()
                topic = row[0]
                chanlist.append((chan, topic))
        print(isinstance(chanlist, list))
        print(chanlist)
        conn.commit()
        conn.close()
        return chanlist
    '''

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

@app.route('/leave/<channel_name>')
def leave_channel(channel_name):
    conn = connect_db()
    cur = conn.cursor()
    channel_name = '#' + channel_name
    try:
        cur.execute('SELECT username FROM `user` WHERE id=?', (session['uid'],))
        row = cur.fetchone()
        username = row[0]
        print("username is %s" % username)
        cur.execute('SELECT members FROM `channels` WHERE channelname=?', (channel_name,))
        row2 = cur.fetchone()
        if row2 is not None:
            print("members in leave is")
            print(row2[0])
            if row2[0] is None:
                return 'Fail', 404
            else:
                cur_members = row2[0].split(';')
                new_members = ""
                for cm in cur_members:
                    if cm != username:
                        new_members += cm
                        new_members += ';'
                if new_members ==  ';':
                    new_members = ''
                print("new members are %s" % new_members)
                cur.execute('UPDATE `channels` SET members=? WHERE channelname=?', (new_members, channel_name))
                conn.commit()
                conn.close()
                return 'Success', 200
    except sqlite3.IntegrityError as e:
        print(e)
        conn.commit()
        conn.close()
        return 'Fail', 404

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

@app.route('/chats/<channel_name>', methods=['GET'])
def chats(channel_name):
    if 'uid' in session:
        ch = get_chats("chann", 0)
        print("-----")
        print(ch)
        print("-----")
        #channel_name = request.form['channel_name']
        return jsonify(get_chats(channel_name, 0))
    else:
        return jsonify("Error: not logged in!")

@app.route('/channels', methods=['GET'])
def channels():
    if 'uid' in session:
        listchan = get_channels(session['uid'])
        print(listchan)
        return jsonify(get_channels(session['uid']))
    else:
        return jsonify("Error: not logged in!")

@app.route('/get_list/<channel_name>', methods=['GET'])
def get_list(channel_name):
    member_list = get_members(channel_name)
    channel_name = '#' + channel_name
    print(member_list)
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT id FROM `files` WHERE channelname=?', (channel_name,))   
        rows = cur.fetchall()
        if rows is None:
            conn.commit()
            conn.close()
            ret = (member_list, list())
            return jsonify(ret)
        get_req = requests.get("http://localhost:8080/" + channel_name)
        if (get_req.ok):
            print("Got file list from Tiny Web Server!")
            #send data back to client
            file_list = list()
            filechunk = ""
            for chunk in get_req.iter_content(chunk_size=BUFFER_SIZE):
                filechunk += chunk
            print("file chunk is %s" % filechunk)
            file_list = filechunk.split('\t')
            print("file list is ")
            print(file_list)
            conn.commit()
            conn.close()
            ret = (member_list, file_list)
            print("return value is ")
            print(ret)
            print("end of return value")
            return jsonify(ret)
        else:
            print("Error: Failed to get file from Tiny Web Server!")
            conn.commit()
            conn.close()
            ret = (member_list, list())
            return jsonify(ret)
    except sqlite3.IntegrityError as e:
        print(e)
        ret = (member_list, list())
        return jsonify(ret)
        

@app.route('/delete_file/<channel_name>/<file_name>')
def delete_file(channel_name, file_name):
    channel_name = '#' + channel_name
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT username FROM `user` WHERE id=?', (session['uid'],))
        row = cur.fetchone()
        cur_user = row[0]
        cur.execute('SELECT uploader FROM `files` WHERE channel_name=? AND file_name=?', (channel_name, file_name))
        row2 = cur.fetchone()
        if row2 is None:
            conn.commit()
            conn.close()
            return 'File not found', 404
        if row2[0] is not None:
            if row2[0] == cur_user:
                filepath = os.path.join(channel_name, file_name)
                filepath += '.crypt'
                delete_req = requests.delete("http://localhost:8080/" + filepath)
                if (delete_req.ok):
                    print("Deleted file from Tiny Web Server!")
                    conn.commit()
                    conn.close()
                    return 'Success', 404
                else:
                    print("Error: Failed to delete file from Tiny Web Server!")
                    conn.commit()
                    conn.close()
                    return 'Failed to delete files', 404
            else:
                conn.commit()
                conn.close()
                return 'Only uploaders can delete files', 403
        else:
            return 'Failed to obtain file uploader info', 404
    except sqlite3.IntegrityError as e:
        print(e)
        return 'Fail', 404

@app.route('/channel/<channel_name>')
def channel(channel_name):
    if 'uid' in session:
        #chanlist = get_list(channel_name)
        #print("lists for %s is" % channel_name)
        #print(chanlist)
        user = get_user_from_id(session['uid'])
        
        return render_template("channel.html", channel_name = channel_name, user=user['username'])
    else:
        return redirect('/login')

def render_home_page(uid):
    user = get_user_from_id(uid)
    return render_template('table.html', uid=uid, user=user['username'])

def render_channel_table(uid, channel_data):
    user = get_user_from_id(uid)
    #print("BZ channel_data: " + channel_data)
    return render_template('table.html', uid=uid, user=user['username'], channel_data=json.dumps(channel_data))

def do_login(user):
    if user is not None:
        print("not null")
        session['uid'] = user['id']
        #get_chats('chan', 0)
        return redirect('/')
    else:
        print("User is none")
        if 'uid' in session:
            session.pop('uid')
        return redirect('/login')

#referrence: http://flask.pocoo.org/docs/1.0/patterns/fileuploads/ 

UPLOAD_FOLDER = './upload/transits'
ALLOWED_EXTENSIONS = set(['out', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['POST'])
def upload_file():
    print("hahah")
    if not os.path.exists('./upload/transits/'):
        print("not exists")
        os.mkdir('./upload')
        print("???")
        os.mkdir('./upload/transits')
    print("waatatta")
    print(request.method)
    if request.method == 'POST':
        print("1")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return 'Failed', 404
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        print("filename is %s" % file.filename)
        if file.filename == '':
            flash('No selected file')
            return 'Failed', 404
        if file and allowed_file(file.filename):
            print("2")
            filename = secure_filename(file.filename)
            print("3")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print("4 %s" % filepath)
            print(file)
            if not os.path.exists(filepath):
                print("file not exists")
                try:
                    with open(filepath, 'w'):
                        print("yes")
                except Exception as e:
                    print(e)
                print("???? watattaat?")
            file.save(filepath)
            print("5")
            channel_name = request.form['channel_name']
            print("6")
            outpath = ""
            try:
                outpath = encrypt_file(file_key, filepath)
                #POST to Tiny Web Server
                try:
                    file_to_post = {'file': open(outpath, 'rb')}
                    try:
                        print("posting")
                        post_req = requests.post("http://localhost:8080/" + outpath, files=file_to_post)
                        print("posting for upload")
                        if (post_req.ok):
                            try:
                                conn = connect_db()
                                cur = conn.cursor()
                                print("dbdbdbd")
                                cur.execute('SELECT filenames FROM `channels` where channelname = ?', (channel_name,))
                                row = cur.fetchone()
                                chanfiles = row[0]
                                print("chanfile ahhahaha")
                                print(chanfiles)
                                if chanfiles is None:
                                    chanfiles = filename
                                else:
                                    chanfiles = chanfiles + ';' + filename
                                cur.execute('UPDATE `channels` SET filenames=? WHERE channelname=?', (chanfiles, channel_name))
                                cur.execute('SELECT username FROM `user` WHERE id=?', (session['uid'], ))
                                row = cur.fetchone()
                                cur_user = row[0]
                                print("cur user")
                                print(cur_user)
                                cur.execute('INSERT INTO `files` VALUES(NULL, ?, ?, ?)', (filename, cur_user, channel_name))
                                conn.commit()
                                conn.close()
                                print("upload usccess")
                                return '''                                     
                                <!doctype html>
                                <title>Upload new File</title>
                                <h1>Upload new File</h1>
                                <form method=post enctype=multipart/form-data>
                                   <input type=file name=file>
                                   <input type=submit value=Upload>
                                </form>
                                '''
                                #return 'Success', 200
                            except sqlite3.IntegrityError as e:
                                print(e)
                                return 'Fail', 404
                        else:
                            print("Error: Failed to post file to Tiny Web Server!")
                            print(post_req.status_code)
                            return 'Fail', 404
                    except Exception as e:
                        print("Error: post request in 'upload' failed")
                        print(e)
                        return 'Fail', 404
                except Exception as e:
                    print("Error: opening file %s in 'upload' failed" % outpath)
                    print(e)
                    return 'Fail', 404
                except OSError as e:
                    print("Socket error: %d." % e.errno)
                    return 'Fail', 404
            except Exception as e:
                print("Error: encrypting file in 'upload' failed")
                print(e)
                return 'Fail', 404          
         
#return '''
'''
<!doctype html>
<title>Upload new File</title>
<h1>Upload new File</h1>
<form method=post enctype=multipart/form-data>
    <input type=file name=file>
    <input type=submit value=Upload>
</form>
'''
'''
def upload_file(channelname, filename):
    if 'uid' not in session:
        return "Forbidden", 403
    usr = session['uid']
    conn = 
'''

# needs to adapt to requests form
@app.route('/download_file/<channelname>/<filename>', methods=['GET'])
def download_file(channelname, filename):
    if 'uid' not in session:
        return "Not Found", 404
    usr = session['uid']
    conn = connect_db()
    cur = conn.cursor()
    print(filename)
    channelname = '#'+channelname
    try:
        cur.execute('SELECT channelname, filename FROM `files` WHERE channelname=? AND filename = filename', (channelname, filename))
        row = cur.fetchone()
        if row is not None:
            print(row[0])
            print(row[1])
            if row[1] is not None:
                filepath = channelname + '/'+filename
                if filepath in row[1]:
                    try:
                        #GET to Tiny Web Server
                        outputfile = filepath
                        filepath += ".crypt"
                        dirs = outputfile.split("/")
                        dir_num = 0
                        if outputfile.endswith("/"):
                            dir_num = len(dirs)
                        else:
                            dir_num = len(dirs) - 1
                        cwd = os.getcwd()
                        count = 0
                        while (count < dir_num):
                            if not os.path.exists(dirs[count]):
                                os.makedirs(dirs[count])
                            os.chdir(dirs[count])
                            count += 1
                        os.chdir(cwd)
                        get_req = requests.get("http://localhost:8080/" + filepath)
                        if (get_req.ok):
                            try:
                                print("Got file from Tiny Web Server!")
                                with open(filepath, 'wb') as in_file:
                                    for chunk in get_req.iter_content(chunk_size=BUFFER_SIZE):
                                        in_file.write(chunk)
                                try:
                                    decrypt_file(file_key, usr, filepath)
                                    return "Success", 200
                                except IOError as e:
                                    print ("Error: sending decrypted file in download failed")
                                    conn.commit()
                                    conn.close()
                                    return "Not Found", 404             
                            except IOError as e:
                                print("Error: read in file from stream in download failed")
                                print(e)
                                conn.commit()
                                conn.close()
                                return "Not Found", 404
                        else:
                            print("Error: Failed to get file from Tiny Web Server!")
                            conn.commit()
                            conn.close()
                            return "Not Found", 404
                    except IOError:
                        print("Error: Open file %s failed." % filepath)
                        conn.commit()
                        conn.close()
                        return "Not Found", 404
        conn.commit()
        conn.close()
        return "Not Found", 404
    except sqlite3.IntegrityError:
        conn.commit()
        conn.close()
        return "Not Found", 404

@app.route('/test_chat')
def test_chat():
    return render_template("channel.html")

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
        if user != None:
            return do_login(user)
        else:
            return redirect('/create_account')

@app.route('/add_admin', methods=['POST'])
def add_admin():
    channel_nohash = request.form['channel_name']
    channel_name =  '#' + channel_nohash
    padmin = request.form['username']
    conn = connect_db()
    cur = conn.cursor()
    try: 
        cur.execute('SELECT username FROM `user` WHERE username=?', (padmin, ))
        row = cur.fetchone()
        if row == None:
            flash(u'User does not exist!', 'error')
            conn.commit()
            conn.close()
            return redirect('/channel/' + channel_nohash)
        cur.execute('SELECT username FROM `user` WHERE id=?', (session['uid'],))
        row = cur.fetchone()
        cur_user = row[0]
        cur.execute('SELECT admins FROM `channels` WHERE channelname=?',(channel_name,))
        row2 = cur.fetchone()
        # admins should never be NULL
        oldadmin = row2[0]
        admins = row2[0].split(';')
        if (cur_user in admins) and (padmin not in admins):
            newadmin = oldadmin + ';' + padmin
            cur.execute('UPDATE `channels` SET admins=? WHERE channelname=?', (newadmin, channel_name))
            cur.execute('SELECT channeladmin FROM `user` WHERE username=?', (cur_user,))
            row = cur.fetchone()
            oldpachan = row[0].split(';')
            newchannel_admin = row[0]+channel_name
            cur.execute('UPDATE `user` SET channeladmin=? WHERE username=?', (newchannel_admin, padmin))
            conn.commit()
            conn.close()
            flash(u'Successfully added admin!', 'success')
            return redirect('/channel/' + channel_nohash)
        else:
            conn.commit()
            conn.close()
            if cur_user not in admins:
                flash(u'Not permitted to add admin!', 'error')
            else:
                flash(u'User is already an admin!', 'error')
            return redirect('/channel/' + channel_nohash)
    except Exception, e:
        flash(u'Cannot add admin!', 'error')
        print(e)
        conn.commit()
        conn.close()
        return redirect('/channel/' + channel_nohash)

@app.route('/ban_user', methods=['POST'])
def ban_user():
    channel_nohash = request.form['channel_name']
    channel_name =  channel_nohash
    banned_user = request.form['username']
    conn = connect_db()
    cur = conn.cursor()
    cur_user = ""
    adminlist = list()
    try: 
        cur.execute('SELECT username FROM `user` WHERE username=?', (banned_user, ))
        row = cur.fetchone()
        if row == None:
            flash(u'User does not exist!', 'error')
            conn.commit()
            conn.close()
            return redirect('/channel/' + channel_nohash)
        cur.execute('SELECT username FROM `user` WHERE id=?', (session['uid'], ))
        row = cur.fetchone()
        cur_user = row[0]
        channel_name = '#' + channel_name
        cur.execute('SELECT admins FROM `channels` WHERE channelname=?', (channel_name,))
        row = cur.fetchone()
        adminlist = row[0].split(';')
        if (cur_user in adminlist) and (banned_user not in adminlist):
            cur.execute('SELECT banned FROM `channels` WHERE channelname = ?', (channel_name,))
            row = cur.fetchone()
            old_banlist = list()
            if row[0] is not None:
                old_banlist = row[0].split(';')
            if banned_user not in old_banlist:
                banlist = ""
                if row[0] is None:
                    banlist = banned_user
                else:
                    banlist = row[0] + ';' + banned_user
                cur.execute('UPDATE `channels` SET banned = ? WHERE channelname=?', (banlist, channel_name))
                #update banned in user
                cur.execute('SELECT banned FROM `user` WHERE username = ?', (banned_user,))
                row2 = cur.fetchone()
                bannedlist = ""
                if row2[0] is None:
                    bannedlist = channel_name
                else:
                    bannedlist = row2[0] + channel_name
                cur.execute('UPDATE `user` SET banned = ? WHERE username=?', (bannedlist, banned_user))
                cur.execute('SELECT members FROM `channels` WHERE channelname = ?', (channel_name,))
                mem = cur.fetchone()
                members = ""
                if mem[0] is not None:
                    mem_list = members.split(';')
                    for m in mem_list:
                        if m != banned_user and len(m) != 0:
                            members = members + m + ';'
                cur.execute('UPDATE `channels` SET members = ? WHERE channelname=?', (members, channel_name))
                conn.commit()
                conn.close()
                flash(u'Successfully banned user!', 'success')
                return redirect('/channel/' + channel_nohash)
            else:
                conn.commit()
                conn.close()
                flash(u'User is already banned from channel!', 'error')
                return redirect('/channel/' + channel_nohash)
        else:
            conn.commit()
            conn.close()
            if cur_user not in adminlist:
                flash(u'Not permitted to ban user!', 'error')
            else:
                flash(u'Cannot ban an admin!', 'error')
            return redirect('/channel/' + channel_nohash)
    except sqlite3.IntegrityError:
        conn.commit()
        conn.close()
        flash(u'Cannot ban user!', 'error')
        return redirect('/channel/' + channel_nohash)

@app.route('/create_channel', methods=['POST'])
def create_channel():
    print('in create channel')
    channame = request.form['channel_name']
    topic = request.form['channel_topic']
    print(channame)
    print(topic)
    channame = utils.escape(channame)
    topic = utils.escape(topic)
    conn = connect_db()
    cur = conn.cursor()
    try:
        uid = session['uid']
        cur.execute('SELECT username FROM `user` WHERE id=\'%s\'' % uid)
        row = cur.fetchone()
        print(len(row))
        admin_name = row[0]
        print(admin_name)
        #channame = '#' + channame
        cur.execute('INSERT INTO `channels` VALUES(NULL,?, ?, ?, ?, NULL, NULL);', (channame, admin_name, admin_name, topic))
        cur.execute('SELECT channels FROM `user` where username= ?', (admin_name,))
        row =cur.fetchone()
        print("4")
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
                #return "success", 200
                return render_channel_table(uid, get_channels(session['uid']))
        else:
            conn.commit()
            conn.close()
            return "forbidden1", 403
    except sqlite3.IntegrityError:
        #TO-DO: case when the channel is already in db. SHouldn't throw an exception.
        conn.commit()
        conn.close()
        return "forbidden2", 403

@app.route('/change_topic/<channel_name>/<new_topic>')
def change_topics(channel_name, new_topic):
    print("in change tocpics")
    print(channel_name)
    new_topic = utils.escape(new_topic)
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
        conn.commit()
        conn.close()
        return "forbidden", 403

@app.route('/')
def index():
    if 'uid' in session:
        #return render_home_page(session['uid'])
        try:
            print("in uid in session index")
            print(session['uid'])
            return render_channel_table(session['uid'], get_channels(session['uid']))
        except Exception, e:
            return redirect('/login')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_login_page()
    elif request.method == 'POST':
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
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('UPDATE `user` SET status=? WHERE id=?', (0, session['uid'])) 
        cur.execute('SELECT username, status FROM `user` WHERE id = ?', (session['uid'],))
        row = cur.fetchone()
        print(row)
        session.pop('uid')
    return redirect('/login')

# Static files
@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory('css', path)


# 'encrypt_file' and 'decrypt_file' function referrence: 
# https://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto
def encrypt_file(key, in_filename, chunksize = BUFFER_SIZE):
    out_filename = in_filename + '.crypt'
    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)
    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)
            
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)
                outfile.write(encryptor.encrypt(chunk))
                    
    return out_filename
                
def decrypt_file(key, username, in_filename, chunksize=BUFFER_SIZE):
    files = in_filename[:len(in_filename) - len(".crypt")].split("/")
    single_filename = files[len(files)-1]
    out_filename = username + "/" + single_filename
    dirs = out_filename.split("/")
    dir_num = 0
    if out_filename.endswith("/"):
        dir_num = len(dirs)
    else:
        dir_num = len(dirs) - 1
    cwd = os.getcwd()
    count = 0
    while (count < dir_num):
        if not os.path.exists(dirs[count]):
            os.makedirs(dirs[count])
        os.chdir(dirs[count])
        count += 1
    os.chdir(cwd)
    
    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)
        return out_filename

if len(sys.argv) > 1 and sys.argv[1] == "init":
    init()
    exit(0)

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))

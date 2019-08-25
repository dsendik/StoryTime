from flask import Flask, render_template, request, flash, session, redirect, \
    url_for
from flask_wtf import FlaskForm
import requests
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
import sqlite3
from models import Message, User
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from models import User
from database import Base, db_session, engine
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin, logout_user, login_required, \
    current_user, login_user, user_logged_in
from flask_socketio import SocketIO, send
from sqlalchemy.orm import sessionmaker
from database import *
import os
import json
import re
# import flask_whooshalchemy as wa

app = Flask(__name__)
app.config['SECRET KEY'] = 'mysecret'
# app.config['WHOOSH_BASE']='whoosh'
socketio = SocketIO(app)
db_session = db_session()
db = SQLAlchemy(app)
conn = sqlite3.connect('/Users/Dan/PycharmProjects/TwitterChat/chatDB.db', check_same_thread=False)
cur = conn.cursor()
Base.metadata.create_all(engine)
login = LoginManager()
login.init_app(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = '/Users/Dan/PycharmProjects/TwitterChat/chatDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# SQLALCHEMY_TRACK_MODIFICATIONS = False



@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']

    if search.data['search'] == '':
        qry = db_session.query(Album)
        results = qry.all()

    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        return render_template('results.html', results=results)



@login.user_loader
def load_user(username):
    return User.get_id(username)
cur_user = ""


# to do: i need to make a for loop for each story on the main page i need to
# increment each loop with the story id. i need to send those to html using the
# arguments in the return render template. since they increment by 1, i can just use a basic jinja counter loop[index.zero] or whatever

# i also need to get the prompt to display on the top of each individual story page
# i also need to implement a photo gallery and a way for artists to upload their photos onto the indiv story pages
@app.route('/')
def index():
    storyID = ""
    #stories = conn.execute("Select storyName, storyContent from Stories").fetchall()
    history = conn.execute("Select username, message_content from Messages").fetchall()
    all_story_IDs = conn.execute("SELECT storyID FROM Stories").fetchall()
    all_story_imgs = conn.execute("SELECT image FROM Stories").fetchall()
    all_story_prompts = conn.execute("SELECT storyPrompt FROM Stories").fetchall()
    list_IDs = []
    story_img = []
    list_prompts = []
    #search_text = (request.form.get('search'))
    #print(search_text)
    search_text = (request.form.get('search_text'))
    print(search_text)
    for each in all_story_IDs:
        list_IDs.append(each[0])

    for each in all_story_imgs:
        story_img.append(each[0])
    for each in all_story_prompts:
        list_prompts.append(each[0])

    messages = ['message1','message2','message3']
    if not session.get('logged_in'):
        flash("incorrect username or password")
        print("wrong password")
        return render_template('login.html')
    else:
        #print("logged in as: " + request.form.get('username'))
        user = request.form.get('username')
        if not user:
            user = "Anonymous"
        newMessage = request.form.get('newMessage')
        #print(newMessage)
        return render_template('index.html', user=user, messages=messages, history=history, storyID=storyID, list_IDs=list_IDs, story_img=story_img, list_prompts=list_prompts)



@app.route('/indiv_story/<storyID>', methods=['GET', 'POST'])
def indiv_story(storyID):
    #storyID = conn.execute("Select storyID FROM Stories WHERE storyPrompt LIKE ?", (user,)).fetchall()
    #print(storyID)
    user = request.form.get('usernames')
    storyID = storyID
    cur_prompt = conn.execute("SELECT storyPrompt from Stories WHERE storyID LIKE ?",
                              (storyID,)).fetchone()[0]

    history = conn.execute("Select username, message_content from Messages").fetchall()
    messages = []
    print(storyID)
    print(user)
    cur_story = conn.execute(
        "Select username, message_content from Messages WHERE storyID LIKE ?",
        (storyID,)).fetchall()
    print(cur_story)
    @socketio.on('message')
    def handleMessage(msg):
        #####  the line below is what I need to figure out to get the data. right now it is being sent thru ajax post form, just have to find
        #####  out how to get it into python
        # msg = request.form.get('newMessage')
        # msg = request.json.get('value')
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url = "http://0.0.0.0:4000"

        #print(msg)
        messages.append(msg)
        test_msg = Message(message_content=msg)
        conn.execute("INSERT INTO Messages (username, message_content, storyID) VALUES (?,?,?)", (user, msg,storyID,))
        conn.commit()
        #print("next is all stories in current story: ")
        # for each in cur_story:
        #     print(each)
        send(msg, broadcast=True)
    return render_template('indiv_story.html', storyID=storyID, cur_story=cur_story, cur_prompt=cur_prompt)


@app.route('/indiv_history/<indiv>', methods=['GET', 'POST'])
def indiv_history(indiv):
    user = indiv
    print(user)
    # history = conn.execute(
    indiv_history = conn.execute("Select username, message_content from Messages WHERE username LIKE ?",(user,)).fetchall()
    conn.commit()
    for each in indiv_history:
        print(each)
    messages = ['message1','message2','message3']
    if not session.get('logged_in'):
        flash("incorrect username or password")
        #print("wrong password")
        return render_template('login.html')
    else:
        @socketio.on('message')
        def handleMessage(msg):
            conn.commit()
            send(msg, broadcast=True)
        return render_template('indiv_history.html', user=user, messages=messages, indiv_history=indiv_history)


# @app.route('/login', methods=['GET', 'POST'])
# def do_admin_login():
#     POST_USERNAME = str(request.form['username'])
#     POST_PASSWORD = str(request.form['password'])
#     Session = sessionmaker(bind=engine)
#     s = Session()
#     query = s.query(User).filter(User.username.in_([POST_USERNAME]),
#                                  User.password.in_([POST_PASSWORD]))
#     result = query.first()
#     #print(result)
#     if result:
#         session['logged_in'] = True
#         cur_user = result
#         return index()
#     else:
#         flash('wrong username or password')
#         return do_admin_login()

@app.route('/login', methods=['POST'])
def do_admin_login():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]),
                                 User.password.in_([POST_PASSWORD]))
    result = query.first()
    if result:
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return index()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return index()

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=4000)



if __name__ == '__main__':
    socketio.run(app)
    app.run(debug=True)

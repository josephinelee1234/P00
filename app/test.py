# Team Hot Cocoa: Hebe Huang, Josephine Lee, Annabel Zhang, aHan Zhang
# SoftDev
# P00: Cafe of Stories
# 2021-10-27

from flask import Flask             #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from flask import session           #facilitate flask sessions
import sqlite3   #enable control of an sqlite database
import csv       #facilitate CSV I/O
import random                       #facilitate random choice
import string                       #get characters used for random string

#the conventional way:
#from flask import Flask, render_template, request

db = sqlite3.connect("chocolate.db", check_same_thread=False) #open if file exists, otherwise create
c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events

def randomString():
    chars = string.ascii_letters + string.digits + string.punctuation
    key = ''.join(random.choice(chars) for i in range(15))
    return key

def getValue(value, table): #gets all of a certain value from db table
    list = []
    query = 'SELECT ' + value + ' FROM ' + table
    c.execute(query)
    rows = c.fetchall() #fetches results of query
    for row in rows:
        list.append(row[0])
    return list

def checkLogin(user,passwd):  #checks inputted username and password to see if the user can log in for login.html
    c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)") #creates table if one does not exist
    db.commit()                   #saves changes

    userList = getValue('username','users')    #gets username from users table
    passList = getValue('password','users')    #gets passwords from users table
    if user in userList:                   #checks if inputted user is in database
        index = userList.index(user)
        if passwd == passList[index]:
            return True
    return False

def createUser(user,passwd): #creating a new user for login.html; helper method for signup()
    c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)") #creates table if one does not exist
    query = 'INSERT INTO users VALUES(?,?)'
    c.execute(query,[user,passwd])

    #query = "CREATE TABLE IF NOT EXISTS " + user + "(title TEXT)"
    #c.execute(query)
    db.commit()                   #saves changes

c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")
db.commit()

app = Flask(__name__)    #create Flask object
app.secret_key = randomString()   #set flask session secret key

@app.route("/", methods=['GET', 'POST'])
def disp_signup_page():
    if 'currentuser' in session: #checks if user has session
        return render_template('home.html',user = session['currentuser'])
        #This should return home page

    return render_template( 'login.html' )

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if 'currentuser' in session: #checks if user has session
            return render_template('home.html',user = session['currentuser'])

    if request.method == 'POST': #conditional for 'POST' method or 'GET' method
        user = request.form['username']
        pas = request.form['password']

        if user in getValue('username','users'):    #checks if user input is in database
            return render_template('login.html', status = 'Username already in use.')
        else:
            if user != "":
                createUser(user,pas)    #adds user to database
                return render_template('login.html', status = 'Account successfully created. You may now login.')
            else:
                return render_template('login.html', status = 'No spaces allowed.')
    else:
        user = request.args['username']
        pas = request.args['password']

        if user in getValue('username','user'):     #checks if user input is in database
            return render_template('login.html', status = 'Username already in use.')
        else:
            createUser(user,pas)    #adds user to database
            return render_template('login.html', status = 'Account successfully created. You may now login.')

@app.route("/auth", methods=['GET', 'POST'])
def authenticate():
    if 'currentuser' in session: #checks if user has session
            return render_template('home.html', user = session['currentuser'])

    if request.method == 'POST': #conditional for 'POST' method or 'GET' method
        user = request.form['username']
        pas = request.form['password']

        if checkLogin(user,pas):
            session['currentuser'] = user
            return render_template('home.html', user=user)
        else:
            return render_template('login.html', status = 'Invalid username or password')
    else:
        user = request.args['username']
        pas = request.args['password']

        if checkLogin(user,pas):
            session['currentuser'] = user
            return render_template('home.html', user=user)
        else:
            return render_template('login.html', status = 'Invalid username or password')

@app.route("/logout")
def logout(): #logs user out through logout button
    if 'currentuser' in session:
        session.pop('currentuser')
    return render_template('login.html')


@app.route("/createstory", methods=['GET', 'POST'])
def createNewStory():
    c.execute("CREATE TABLE IF NOT EXISTS stories(title TEXT, content TEXT, latest TEXT, lastuser TEXT)") #creates table if one does not exist
    db.commit()     #saves changes

    if 'currentuser' in session:
        return render_template('createstory.html', user = session['currentuser'])

    return render_template('login.html', status = 'Please log in to create a new story.')

@app.route("/uploadNewStory", methods=['GET', 'POST'])
def uploadNewStory():
    c.execute("CREATE TABLE IF NOT EXISTS stories(title TEXT, content TEXT, latest TEXT, lastuser TEXT)") #creates table if one does not exist
    db.commit()     #saves changes

    if 'currentuser' in session:                #checks if user is in session
        title = request.form['title']
        content = request.form['content']

        query = 'INSERT INTO ' + session['currentuser'] + ' VALUES(?)'
        c.execute(query,[title])


        query = 'INSERT INTO stories VALUES(?,?,?,?)'
        c.execute(query,[title,content,content,session['currentuser']])
        db.commit()
        return render_template('home.html',user = session['currentuser'],status='Story successfully created')

    else:
        return render_template('login.html', status = 'Please log in to create a new story.')

@app.route("/addToStory", methods=['GET','POST'])
def addToStory():
    query = 'SELECT content FROM stories WHERE title = ' + title
    c.execute(query)
    current = ''
    rows = c.fetchall
    for row in rows:
        current = current + row[0]          #gets the FULL story from database


if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()

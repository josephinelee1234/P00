# Team Whales: Hebe Huang, Josephine Lee, Han Zhang
# SoftDev
# K15: Sessions Greetings
# 2021-10-18

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

db = sqlite3.connect("chocolate", check_same_thread=False) #open if file exists, otherwise create
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
    query = 'INSERT INTO users VALUES (\"' + user + '\",\"' + passwd + '\")'
    c.execute(query)

    query = "CREATE TABLE IF NOT EXISTS " + user + "(title TEXT)"
    c.execute(query)
    db.commit()                   #saves changes

def createNewStory(title,content,user):
    c.execute("CREATE TABLE IF NOT EXISTS stories(title TEXT, content TEXT, latest TEXT, lastuser TEXT)") #creates table if one does not exist
    query = 'INSERT INTO ' + user + ' VALUES (\"' + title + '\')'
    c.execute(query)

    query = 'INSERT INTO stories VALUES (\"' + title + '\",\"' + content + '\",\"' + content + '\",\"' + user + '\")'
    c.execute(query)

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
        
        if user in getValue('username','users'):
            return render_template('login.html', status = 'Username already in use.')
        else:
            createUser(user,pas)    #adds user to database
            return render_template('login.html', status = 'Account successfully created. You may now login.')
    else:
        user = request.args['username']
        pas = request.args['password']
        
        if user in getValue('username','user'):
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
            return render_template('home.html', user=user)
        else:
            return render_template('login.html', status = 'Invalid username or password')
    else:
        user = request.args['username']
        pas = request.args['password']
        
        if checkLogin(user,pas):
            return render_template('home.html', user=user)
        else:
            return render_template('login.html', status = 'Invalid username or password')
    
@app.route("/logout")
def logout(): #logs user out through logout button
    if 'currentuser' in session:
        session.pop('currentuser')
    return render_template('login.html')

    
if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True 
    app.run()


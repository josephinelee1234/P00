# Team Hot Cocoa: Hebe Huang, Josephine Lee, Annabel Zhang, Han Zhang
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

# creates necessary tables
c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS stories(title TEXT, content TEXT, latest TEXT, lastuser TEXT);")
db.commit()


def randomString():
    ''' Generates a random string of 15 random characters'''
    chars = string.ascii_letters + string.digits + string.punctuation
    key = ''.join(random.choice(chars) for i in range(15))
    return key


def getValue(value, table):
    ''' Gets all of a certain value from db table '''
    list = []
    query = 'SELECT ' + value + ' FROM ' + table
    c.execute(query)
    rows = c.fetchall() #fetches results of query
    for row in rows:
        list.append(row[0])
    return list


def checkLogin(user,passwd):
    ''' Checks inputted username and password to see if the user can log in for login.html '''
    userList = getValue('username','users')    #gets username from users table
    passList = getValue('password','users')    #gets passwords from users table
    if user in userList:                   #checks if inputted user is in database
        index = userList.index(user)
        if passwd == passList[index]:
            return True
    return False


def createUser(user,passwd):
    ''' Creates a new user for login.html; helper method for signup() '''
    query = 'INSERT INTO users VALUES(?,?)'
    c.execute(query,[user,passwd])

    query = "CREATE TABLE IF NOT EXISTS " + user + "(title TEXT);"
    c.execute(query)
    db.commit()                   #saves changes


def get_user_stories(user):
    ''' Returns titles of all stories the user contributed to'''
    titles = getValue("title", user)
    return titles


app = Flask(__name__)    #create Flask object
app.secret_key = randomString()   #set flask session secret key


@app.route("/", methods=['GET', 'POST'])
def disp_signup_page():
    ''' Displays home page if logged in; otherwise displays login page '''
    if 'currentuser' in session: #checks if user has session
        return render_template('home.html', user = session['currentuser'], user_stories = get_user_stories(session['currentuser']))
        #This should return home page

    return render_template( 'login.html' )


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    ''' Adds new user account to database '''
    if 'currentuser' in session: #checks if user has session
            return render_template('home.html',user = session['currentuser'], user_stories = get_user_stories(session['currentuser']))

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
    ''' Checks user login '''
    if 'currentuser' in session: #checks if user has session
            return render_template('home.html', user = session['currentuser'])

    if request.method == 'POST': #conditional for 'POST' method or 'GET' method
        user = request.form['username']
        pas = request.form['password']

        if checkLogin(user,pas):
            session['currentuser'] = user
            return render_template('home.html', user=user, user_stories = get_user_stories(user))
        else:
            return render_template('login.html', status = 'Invalid username or password')
    else:
        user = request.args['username']
        pas = request.args['password']

        if checkLogin(user,pas):
            session['currentuser'] = user
            return render_template('home.html', user=user, user_stories = get_user_stories(user))
        else:
            return render_template('login.html', status = 'Invalid username or password')


@app.route("/logout")
def logout():
    ''' Logs user out through logout button '''
    if 'currentuser' in session:
        session.pop('currentuser')
    return render_template('login.html')


@app.route("/createstory", methods=['GET', 'POST'])
def createNewStory():
    ''' From home.html
    Sends user to createstory.html '''
    if 'currentuser' in session:
        return render_template('createstory.html', user = session['currentuser'])

    return render_template('login.html', status = 'Please log in to create a new story.')


@app.route("/uploadNewStory", methods=['GET', 'POST'])
def uploadNewStory():
    ''' Adds new story from createstory.html to database;
    Goes back to home.html '''
    if 'currentuser' in session:                #checks if user is in session
        title = request.form['title']
        content = request.form['content']

        if title == '':
            return render_template('createstory.html', status="Please enter a story.", story=content)

        if title in getValue('title','stories'): # checks if story title has already been used
            return render_template('createstory.html', status="Duplicate story title- Please enter a different title.", story=content)

        else:
            query = 'INSERT INTO ' + session['currentuser'] + ' VALUES(?)'
            c.execute(query,[title])

            query = 'INSERT INTO stories VALUES(?,?,?,?);'
            c.execute(query,[title,content,content,session['currentuser']])
            c.execute('SELECT * FROM stories;')
            db.commit()
            return render_template('home.html',user = session['currentuser'], status='Story successfully created', user_stories = get_user_stories(session['currentuser']))

    else:
        return render_template('login.html', status = 'Please log in to create a new story.')


@app.route("/addToStory", methods=['GET','POST'])
def updateStory():
    ''' From home.html
    Sends user to updatestory.html '''
    if 'currentuser' in session:
        query = 'SELECT title FROM stories'
        c.execute(query)
        rows = c.fetchall()
        return render_template('updatestory.html', user = session['currentuser'],stories=rows)

    return render_template('login.html', status = 'Please log in to update a story.')


@app.route("/addToTitle", methods=['GET', 'POST'])
def addToTitle():
    ''' From updatestory.html:
    Takes in title of a story and determines whether or not user can add to the story;
    Goes to addcontent.html '''
    if 'title' in session:
        session.pop('title')

    if 'currentuser' in session:
        title = request.form['title']
        titleList = getValue('title','stories')
        if title in titleList:
            if title in get_user_stories(session['currentuser']):
                return render_template('home.html',user = session['currentuser'], status = 'You cannot add to stories you have already contributed to.', user_stories = get_user_stories(session['currentuser']))
            else:
                query = 'SELECT latest FROM stories WHERE title = \'' + title + '\''
                c.execute(query)
                rows = c.fetchall()
                content = rows[0]
                session['title'] = title
                return render_template('addcontent.html',content = content, title = title)
        else:
            return render_template('home.html', status = 'Story does not exist.', user_stories = getValue("title", session['currentuser']))
    else:
        return render_template('login.html', status = 'Please log in to update a story.')


@app.route("/uploadUpdatedStory", methods=['GET', 'POST'])
def uploadUpdatedStory():
    ''' From addcontent.html:
    Updates existing story in database with content from addcontent.html;
    Goes back to home.html '''
    if 'currentuser' in session:                #checks if user is in session
        content = request.form['content']
        title = session['title']

        query = 'SELECT latest FROM stories WHERE title = \'' + title + '\''
        c.execute(query)
        latest = c.fetchall()[0][0]

        query = 'SELECT content FROM stories WHERE title = \'' + title + '\''
        c.execute(query)
        current = c.fetchall()
        updatedContent = current[0][0] + " " + content

        query1 = "UPDATE stories SET content = \'" + updatedContent + "\' WHERE title = \'" + title + '\''
        c.execute(query1)
        db.commit()


        query2 = "UPDATE stories SET latest = \'" + content + "\' WHERE title = \'" + title + '\''
        c.execute(query2)
        db.commit()

        #add to the list of stories that the user has worked on
        query2 = 'INSERT INTO ' + session['currentuser'] + ' VALUES(?)'
        c.execute(query2, [title])
        db.commit()
        return render_template('home.html',user = session['currentuser'], status='Story successfully updated', user_stories = get_user_stories(session['currentuser']))

    return render_template('login.html', status = 'Please log in to create a new story.')


@app.route("/viewStory", methods=['GET','POST'])
def viewStory():
    ''' From home.html:
    Returns latest story content
    Goes to story.html '''
    userTitles = get_user_stories(session['currentuser'])
    title = request.form['title']

    if title in userTitles:     #checks if user has contributed to requested story.
        query = 'SELECT content FROM stories WHERE title = \'' + title + '\''
        c.execute(query)
        rows = c.fetchall()[0][0]

        return render_template('story.html',title = title, content = rows)
    else:
        return render_template('home.html',user = session['currentuser'], status='You may only view stories you have contributed to.', user_stories=get_user_stories(session['currentuser']))



if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()

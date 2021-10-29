# Team Whales: Hebe Huang, Josephine Lee, Han Zhang
# SoftDev
# K15: Sessions Greetings
# 2021-10-18

from flask import Flask             #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from flask import session           #facilitate flask sessions
import random                       #facilitate random choice
import string                       #get characters used for random string

#the conventional way:
#from flask import Flask, render_template, request

def randomString():
    chars = string.ascii_letters + string.digits + string.punctuation
    key = ''.join(random.choice(chars) for i in range(15))
    return key

app = Flask(__name__)    #create Flask object
app.secret_key = randomString()   #set flask session secret key

@app.route("/", methods=['GET', 'POST'])
def disp_loginpage():
    if 'currentuser' in session: #checks if user has session
        if session['currentuser'] == 'user': #hardcode to check if user is correct
            return render_template('response.html', method = session['currentmethod'], user = session['currentuser'])
        else: #returns error page is invalid username
            return render_template('error.html', type = 'username')

    print("\n\n\n")
    print("***DIAG: this Flask obj ***")
    print(app)
    print("***DIAG: request obj ***")
    print(request)
    print("***DIAG: request.args ***")
    print(request.args)
    #print("***DIAG: request.args['username']  ***")
    #print(request.args['username'])
    print("***DIAG: request.headers ***")
    print(request.headers)
    return render_template( 'login.html' )


@app.route("/auth", methods=['GET', 'POST'])
def authenticate():
    if 'currentuser' in session: #checks if user has session
        if session['currentuser'] == 'user': #hardcode to check if user is correct
            return render_template('response.html', method = session['currentmethod'], user = session['currentuser'])
        else: #returns error page is invalid username
            return render_template('error.html', type = 'username')
    
    print("\n\n\n")
    print("***DIAG: this Flask obj ***")
    print(app)
    print("***DIAG: request obj ***")
    print(request)
    print("***DIAG: request.args ***")
    print(request.args)
    #print("***DIAG: request.args['username']  ***")
    #print(request.args['username'])
    print("***DIAG: request.headers ***")
    print(request.headers)

    username = 'user'
    password = 'password' 
    
    if request.method == 'POST': #conditional for 'POST' method or 'GET' method
        user = request.form['username']
        pas = request.form['password']
        if user == 'user':
            if pas == 'password':
                session['currentuser'] = user
                session['currentmethod'] = request.method
                return render_template('response.html',method = request.method, user = user)  #correct login
            else:
                return render_template('error.html', type = 'password') #returns password error
        else: 
            return render_template('error.html', type = 'username') #returns username error
    else:
        user = request.args['username']
        pas = request.args['password']
        if request.args['username'] == 'user':
            if request.args['password'] == 'password':
                session['currentuser'] = user
                session['currentmethod'] = request.method
                return render_template('response.html',method = request.method, user = user)  #correct login
            else:
                return render_template('error.html', type = 'password') #returns password error
        else: 
            return render_template('error.html', type='username') #returns username error
    
    
@app.route("/logout")
def logout():
    if 'currentuser' in session:
        session.pop('currentuser')
        session.pop('currentmethod')
    return render_template('login.html')

    
if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True 
    app.run()

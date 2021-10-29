#Hot Cocoa - Hebe Huang, Josephine Lee, Annabel Zhang, Han Zhang
#SoftDev
#P00 -- Cafe of Stories | Design Doc
#2021-10-27

from flask import Flask
app = Flask(__name__) 

@app.route("/")       
def hello_world():
    print("the __name__ of this module is... ")
    print(__name__)
    return "No hablo queso!"
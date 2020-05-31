from flask import current_app as app
from flask import render_template
from models import User_Info

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/index', methods=['GET'])
def show_index():
    return render_template('index.html')

@app.route('/signup', methods=['GET'])
def show_signup():
    return render_template('signup.html')
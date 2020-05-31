from flask import current_app as app
from models import User_Info

@app.route('/')
def hello_world():
    return 'Hello, World!'
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:final@/Casino?unix_socket=/cloudsql/cnlab20-group12:asia-east1:mysql-cnlab20-group12'
db = SQLAlchemy(app)

from models import User_Info

db.create_all()
db.session.commit()

@app.route('/')
def hello_world():
    return 'Hello, World!'

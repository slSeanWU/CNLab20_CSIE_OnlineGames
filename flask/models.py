from main import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User_Info(db.Model):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hashed = db.Column(db.String(255), nullable=False)
    coins = db.Column(db.Integer)
    registration_time = db.Column(db.DateTime, default=datetime.now)
    last_active_time = db.Column(db.DateTime)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hashed = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hashed, password)



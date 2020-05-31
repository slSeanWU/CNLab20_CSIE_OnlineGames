from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin

db = SQLAlchemy()
login_manager = LoginManager()

class UserInfo(UserMixin, db.Model):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hashed = db.Column(db.String(255), nullable=False)
    coins = db.Column(db.Integer, default=100)
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

    @login_manager.user_loader
    def load_user(userid):
        return UserInfo.query.get(int(userid))

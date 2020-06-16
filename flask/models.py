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

    slot_games = db.relationship('SlotGameRecord', backref='user_info', lazy=True)
    blackjack_games = db.relationship('BlackJackGameRecord', backref='user_info', lazy=True)
    topup_records = db.relationship('TopUpRecord', backref='user_info', lazy=True)

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

class CoinVoucher(db.Model):
    '''
    For top-ups
    '''
    __tablename__ = 'coin_voucher_new'
    id = db.Column(db.Integer, primary_key=True)
    serial_num = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    issued_time = db.Column(db.DateTime, default=datetime.now)
    expiration_time = db.Column(db.DateTime)
    used = db.Column(db.Boolean, default=False, nullable=False)

class TopUpRecord(db.Model):
    '''
    For top-up records
    '''
    __tablename__ = 'topup_record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    used_serial_num = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    coins_after = db.Column(db.Integer, nullable=False)
    used_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

class SlotGameRecord(db.Model):
    '''
    For slot game records
    '''
    __tablename__ = 'slot_game_record_single_new'
    play_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    bet_amount = db.Column(db.Integer, nullable=False)
    earnings = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)

class BlackJackGameRecord(db.Model):
    __tablename__ = 'blackjack_game_record_new_1'
    play_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    bet_amount = db.Column(db.Integer, nullable=False)
    earnings = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)

class TexasGameRecord(db.Model):
    __tablename__ = 'texas_game_record'
    play_id = db.Column(db.Integer, primary_key=True)
    player_num = db.Column(db.Integer, nullable=False)
    user_id1 = db.Column(db.Integer, nullable=True)
    user_id2 = db.Column(db.Integer, nullable=True)
    user_id3 = db.Column(db.Integer, nullable=True)
    user_id4 = db.Column(db.Integer, nullable=True)
    user_id5 = db.Column(db.Integer, nullable=True)
    user_id6 = db.Column(db.Integer, nullable=True)
    user_id7 = db.Column(db.Integer, nullable=True)
    user_id8 = db.Column(db.Integer, nullable=True)
    user_id9 = db.Column(db.Integer, nullable=True)
    bet_amount = db.Column(db.Integer, nullable=False)
    earnings = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
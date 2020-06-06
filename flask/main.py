from flask import Flask
from models import db, login_manager

def create_app():
    app = Flask(__name__)
    app.secret_key='secret key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:final@35.236.142.37/Casino'

    db.init_app(app)
    with app.app_context():
        import routes, games
        db.create_all()
        db.session.commit()

    login_manager.init_app(app)
    login_manager.login_view = 'show_index'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run('127.0.0.1', 5000, debug=True)

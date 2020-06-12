from flask import Flask
from flask_socketio import SocketIO
from models import db, login_manager

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.secret_key='secret key'
    app.config['TEMPLATE_AUTO_RELOAD'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:final@35.236.142.37/Casino'

    db.init_app(app)
    with app.app_context():
        import routes, slot, blackjack, poker
        db.create_all()
        db.session.commit()

    login_manager.init_app(app)
    login_manager.login_view = 'show_index'
    
    socketio.init_app(app)

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)

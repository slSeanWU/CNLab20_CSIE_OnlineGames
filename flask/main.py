from flask import Flask
from flask_socketio import SocketIO
from models import db, login_manager

app = Flask(__name__)
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)

def create_app():
    app.secret_key='secret key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:final@35.236.142.37/Casino'

    db.init_app(app)
    with app.app_context():
        import routes, slot, blackjack, poker
        db.create_all()
        db.session.commit()

    login_manager.init_app(app)
    login_manager.login_view = 'show_index'
    
    #socketio.init_app(app, async_mode=None)

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

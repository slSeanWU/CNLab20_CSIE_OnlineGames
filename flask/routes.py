from flask import current_app as app
from flask import render_template, request, flash, redirect, url_for
from models import UserInfo, CoinVoucher
from main import db
from flask_login import login_user, logout_user, login_required, current_user

import sys
from datetime import datetime

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/index', methods=['GET'])
def show_index():
    if current_user.is_authenticated:
        return redirect(url_for('main_menu'))
    return render_template('index.html')

@app.route('/index', methods=['POST'])
def login():
    email_rec = request.form.get('email')
    passwd_rec = request.form.get('passwd')

    user = UserInfo.query.filter_by(email=email_rec).first()
    if user:
        if user.verify_password(passwd_rec):
            login_user(user, remember=True)
            return redirect(url_for('main_menu'))
        else:
            flash('Login FAILED. Wrong Email or Password')
    else:
        flash('Login FAILED. Wrong Email or Password')

    return redirect(url_for('show_index'))

@app.route('/member_center', methods=['GET'])
@login_required
def member_center():
    user = UserInfo.query.filter_by(username=current_user.username).first()
    return render_template('member_center.html', username=user.username, coins=user.coins)

@app.route('/member_center', methods=['POST'])
@login_required
def member_update():
    # TODO
    # handle change username/passwd & top-up authentication
    pass
  
@app.route('/main_menu', methods=['GET'])
@login_required
def main_menu():
    # update last active time
    user = UserInfo.query.filter_by(username=current_user.username).first()
    user.last_active_time = datetime.now()
    db.session.commit()
    return render_template('main_menu.html', username=user.username, coins=user.coins)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('Logged out.')
    return redirect(url_for('show_index'))

@app.route('/peekdb', methods=['GET'])
@login_required
def show_db_content():
  users_table = UserInfo.query.order_by(UserInfo.id).all()
  msg = '<tr> <th>{}</th> <th>{}</th> <th>{}</th> <th>{}</th> <th>{}</th> </tr>'.format('[ID]', '[username]', '[email]', '[joined at]', '[last active]')

  for u in users_table:
    msg += '<tr> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> </tr>'.format(u.id, u.username, u.email, u.registration_time, u.last_active_time)

  return '<h1> All Users </h1> <table> {} </table>'.format(msg)

@app.route('/signup', methods=['GET'])
def show_signup():
  return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def create_user():
  username = request.form.get('username')
  email = request.form.get('email')
  passwd = request.form.get('passwd')
  passwd_confirm = request.form.get('passwd-confirm')

  # user/email already exists
  if db.session.query(UserInfo.id).filter_by(username=username).scalar() is not None or \
      db.session.query(UserInfo.id).filter_by(email=email).scalar() is not None:
    flash('Signup FAILED. The username or email has been registered before!')
    return redirect(url_for('show_signup'))
  # wrong password confirmation
  if passwd_confirm != passwd:
    flash('Signup FAILED. Passwords don\'t match!')
    return redirect(url_for('show_signup'))

  new_user = UserInfo(
    username=username,
    email=email
  )
  new_user.password = passwd
  db.session.add(new_user)
  db.session.commit()

  flash('Signup successful!')
  return redirect(url_for('show_index'))

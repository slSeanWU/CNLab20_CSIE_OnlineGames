from flask import current_app as app
from flask import render_template, request, flash, redirect, url_for
from models import UserInfo
from main import db

import sys

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/index', methods=['GET'])
def show_index():
  return render_template('index.html')

@app.route('/peekdb', methods=['GET'])
def show_db_content():
  users_table = UserInfo.query.order_by(UserInfo.id).all()
  msg = '<tr> <th>{}</th> <th>{}</th> <th>{}</th> <th>{}</th> </tr>'.format('[ID]', '[username]', '[email]', '[joined at]')

  for u in users_table:
    msg += '<tr> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> </tr>'.format(u.id, u.username, u.email, u.registration_time)

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
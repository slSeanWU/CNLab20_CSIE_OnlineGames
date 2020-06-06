from flask import current_app as app
from flask import render_template, request, flash, redirect, url_for
from models import UserInfo, CoinVoucher
from main import db
from flask_login import login_user, logout_user, login_required, current_user

import sys
from datetime import datetime
from uuid import uuid1

@app.route('/')
def hello_world():
    return redirect(url_for('show_index'))

@app.route('/index', methods=['GET'])
def show_index():
    if current_user.is_authenticated:
        return redirect(url_for('main_menu'))
    # return render_template('index.html')
    return render_template('login.html')

@app.route('/index', methods=['POST'])
def login():
    email_rec = request.form.get('email')
    passwd_rec = request.form.get('passwd')

    user = UserInfo.query.filter_by(email=email_rec).first()
    if user:
        if user.verify_password(passwd_rec):
            # TODO
            # client can check remember me or not
            login_user(user, remember=True)
            return redirect(url_for('main_menu'))
        else:
            flash('Login FAILED! Wrong Email or Password')
    else:
        flash('Login FAILED! Wrong Email or Password')

    return redirect(url_for('show_index'))

@app.route('/member_center', methods=['GET'])
@login_required
def member_center():
    user = UserInfo.query.filter_by(username=current_user.username).first()
    return render_template('member_center.html', username=user.username, coins=user.coins)


@app.route('/change_username', methods=['POST'])
@login_required
def change_username():
    new_username = request.form.get('new-username')
    if db.session.query(UserInfo.id).filter_by(username=new_username).scalar() is not None:
        flash('Username changed FAILED! The username has been registered before!')
        return redirect(url_for('member_center'))
    user = current_user
    user.username = new_username
    db.session.commit()
    flash('Username successfully changed.')
    return redirect(url_for('main_menu'))


@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    old_password = request.form.get('old-passwd')
    new_password = request.form.get('new-passwd')
    new_password_confirm = request.form.get('new-passwd-confirm')
    user = current_user
    if not user.verify_password(old_password):
        flash('Wrong old password or new passwords')
    elif (not new_password) or (new_password != new_password_confirm):
        flash('Wrong old password or new passwords')
    else:
        user.password = new_password
        db.session.commit()
        flash('Password successfully changed. Please login with new password.')
        return redirect(url_for('logout'))
    return redirect(url_for('member_center'))

@app.route('/top_up', methods=['POST'])
@login_required
def top_up_authentication():
    # handle top-up authentication
    serial_num = request.form.get('topup-serial-num').strip()

    query_res = CoinVoucher.query.filter_by(serial_num=serial_num)
    if query_res.scalar() is not None and query_res.first().used is False:
      voucher = query_res.first()
      if voucher.expiration_time is not None and voucher.expiration_time < datetime.now():
        flash('Top-up FAILED! Invalid serial number.')
      else:
        voucher.used = True
        voucher.expiration_time = datetime.now()
        user = UserInfo.query.filter_by(username=current_user.username).first()
        user.coins += voucher.value
        db.session.commit()
        flash('Top-up successful! You have {} more coins now.'.format(voucher.value))
    else:
      flash('Top-up FAILED! Invalid serial number.')

    return redirect(url_for('member_center'))

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

  return '<h1>All Users</h1> <table> {} </table>'.format(msg)

@app.route('/gen_voucher', methods=['POST'])
@login_required
def generate_vouchers():
  voucher_value = int(request.form.get('new-voucher-value'))
  voucher_cnt = int(request.form.get('new-voucher-count'))
  for i in range(voucher_cnt):
    new_voucher = CoinVoucher(
      serial_num=str(uuid1()),
      value=voucher_value
    )
    db.session.add(new_voucher)
    db.session.commit()

  return redirect(url_for('manage_vouchers'))

@app.route('/manage_voucher', methods=['GET'])
@login_required
def manage_vouchers():
  head = '<h1>Coin Voucher Management Center</h1>'

  generate = '''
    <div id="generate">
    <h2>Generate Vouchers</h2> 
      <form action="/gen_voucher" method="post" id="gen-voucher">
        <label>Voucher value</label>
        <input type="number" required autocomplete="off" name="new-voucher-value"/>
        <br> <label># New vouchers</label>
        <input type="number" required autocomplete="off" name="new-voucher-count"/>
        <br> <button type="submit">Generate</button>
      </form>
    </div>
  '''

  vouchers_table = CoinVoucher.query.order_by(CoinVoucher.id).all()
  list_voucher = '''
    <div id="list">
    <h2>All Vouchers</h2> 
    <table id="list-table">
      <tr> <th>[ID]</th> <th>[serial num]</th> <th>[value]</th> <th>[issued at]</th> <th>[was used]</th> </tr>
  '''
  for v in vouchers_table:
    list_voucher += '<tr> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> </tr>'.format(v.id, v.serial_num, v.value, v.issued_time, v.used)
  list_voucher += '''
    </table>
    </div>
  '''

  return head + generate + list_voucher

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

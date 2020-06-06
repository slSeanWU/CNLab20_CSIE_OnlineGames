from flask import current_app as app
from flask import render_template, request, flash, redirect, url_for
from models import UserInfo
from main import db
from flask_login import login_user, logout_user, login_required, current_user

from datetime import datetime

'''
-- games.py
For pages that run games.
'''

@app.route('/slot_rules', methods=['GET'])
@login_required
def slot_rules():
  '''
  Displays the game's rules (accessible from main menu).
  '''
  user = UserInfo.query.filter_by(username=current_user.username).first()
  return render_template('slot_rules.html', username=user.username, coins=user.coins)

@app.route('/slot_play', methods=['GET'])
@login_required
def slot_play():
  '''
  Displays the game panel & stats of current gameplay (e.g., bet, earnings ...).
  '''
  user = UserInfo.query.filter_by(username=current_user.username).first()
  return render_template('slot_play.html', username=user.username, coins=user.coins)
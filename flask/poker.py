from flask import current_app as app
from flask import render_template, request, flash, redirect, url_for
from models import UserInfo, CoinVoucher, SlotGameRecord, TopUpRecord
from main import db
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/texas_rules', methods=['GET'])
@login_required
def texas_rules():
  '''
  Displays the game's rules (accessible from main menu).
  '''
  user = current_user
  return render_template('Lobby.html', username=user.username, coins=user.coins)

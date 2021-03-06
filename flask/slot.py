from flask import current_app as app
from flask import render_template, request, flash, redirect, url_for, json
from models import UserInfo, SlotGameRecord
from main import db
from flask_login import login_user, logout_user, login_required, current_user

from datetime import datetime
from random import randrange, random, choice
import numpy as np

'''
-- slot.py
For pages that run the slot machine game.
'''

## helpers
icons = [x for x in range(8)]
icon_probs = [1/30, 1/15, 1/15, 1/7.5, 1/7.5, 1/7.5, 1/5, 7/30]
prizes = [777, 100, 50, 25, 10, 15, 8, 4, 2, 0]

def get_slot_prize(line, slot):
  '''
  Calculates the prize.
  '''
  slot = np.array(slot)
  pr_idx = 9
  unique, counts = np.unique(slot[line], return_counts=True)

  for i, c in zip(unique, counts):
    if c == 3 and i != 7:
      pr_idx = i
    elif c == 2:
      if i in [1, 2]:
        pr_idx = 7
      elif i > 2 and i < 7:
        pr_idx = 8

  return prizes[ pr_idx ]

def get_slot_spin():
  '''
  Generates the 3 * 3 slot panel after spinning.
  '''
  return np.random.choice(
    icons, size=(3, 3), p=icon_probs
  ).tolist()

def cheat_user(slot, line, is_pline, winlines):
  '''
  Hee hee...
  '''
  if not is_pline:
    for c in range(3):
      rand = random()
      if rand < 1/8:
        slot[line][c] = 0
      elif rand < 1/3:
        slot[line][c] = choice([1, 2])
  elif line not in winlines:
    if 0 not in slot[line] and random() < 1/8:
      slot[line][c] = 0
    elif 1 not in slot[line] and random() < 1/4:
      slot[line][c] = choice([1, 2])

  return slot

## routes
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
  if request.args.get('json_str') is None:
    stats = {
      'rounds_played': 0,
      'total_bet': 0,
      'total_earnings': 0,
      'last_earnings': 0,
      'slot': get_slot_spin(),
      'winning_lines': [],
      'winning_amounts': [0, 0, 0],
      'play_line': 1
    }
  else:
    stats = json.loads(request.args.get('json_str'))
  app.logger.info(stats)

  return render_template('slot_play.html',
    username=user.username, coins=user.coins,
    rounds_played=stats['rounds_played'],
    total_bet=stats['total_bet'],
    total_earnings=stats['total_earnings'],
    last_earnings=stats['last_earnings'],
    slot=stats['slot'],
    winning_lines=stats['winning_lines'],
    winning_amounts=stats['winning_amounts'],
    play_line=stats['play_line']
  )

@app.route('/slot_spin', methods=['POST'])
@login_required
def slot_spin():
  user = UserInfo.query.filter_by(username=current_user.username).first()
  num_plines = int(request.form.get('num-plines'))
  single_bet = int(request.form.get('single-bet'))
  if user.coins < num_plines * single_bet:
    json_obj = {
      'rounds_played': 0,
      'total_bet': 0,
      'total_earnings': 0,
      'last_earnings': 0,
      'slot': get_slot_spin(),
      'winning_lines': [],
      'winning_amounts': [0,0,0],
      'play_line': 1
    }
    flash('No enough coins. Time to TOP-UP!!')

    return redirect(url_for('slot_play', json_str=json.dumps(json_obj)))

  app.logger.info(request.form)
  rounds_played = int(request.form.get('rounds-played')) + 1
  total_bet = int(request.form.get('total-bet')) + num_plines * single_bet

  slot = get_slot_spin()
  winning_lines = []
  winning_amounts = [0, 0, 0]

  if num_plines >= 1:
    last_earnings = single_bet * get_slot_prize(1, slot)
    winning_lines.append(1)
    winning_amounts[1] = last_earnings
  if num_plines >= 2:
    last_earnings += single_bet * get_slot_prize(0, slot)
    winning_lines.append(0)
    winning_amounts[0] = last_earnings - winning_amounts[1]
  if num_plines >= 3:
    last_earnings += single_bet * get_slot_prize(2, slot)
    winning_lines.append(2)
    winning_amounts[2] = last_earnings - winning_amounts[0] - winning_amounts[1]

  # place more "high-paying" icons in if they don't affect the results XD
  for l in range(3):
    if l == 0:
      slot = cheat_user(slot, 0, num_plines >= 2, winning_lines)
    elif l == 1:
      slot = cheat_user(slot, 1, num_plines >= 1, winning_lines)
    else:
      slot = cheat_user(slot, 2, num_plines >= 3, winning_lines)

  total_earnings = int(request.form.get('total-earnings')) + last_earnings
  json_obj = {
    'rounds_played': rounds_played,
    'total_bet': total_bet,
    'total_earnings': total_earnings,
    'last_earnings': last_earnings,
    'slot': slot,
    'winning_lines': winning_lines,
    'winning_amounts': winning_amounts,
    'play_line': num_plines
  }
  app.logger.info(json_obj)

  game_record = SlotGameRecord(
    user_id=user.id,
    bet_amount=num_plines * single_bet,
    earnings=last_earnings
  )
  user.coins += (last_earnings - num_plines * single_bet)
  db.session.add(game_record)
  db.session.commit()

  return redirect(url_for('slot_play', json_str=json.dumps(json_obj)))
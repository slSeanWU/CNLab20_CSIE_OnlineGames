from flask import current_app as app
from flask import render_template, request, flash, redirect, url_for, json
from models import UserInfo, BlackJackGameRecord
from __main__ import db, socketio
from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, disconnect
import random

cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
cards_player = {}
cards_dealer = {}
bet = {}

def blackjack_sum(cards_list):
    soft_sum = 0
    num_of_A = 0
    for i in cards_list:
        if i == 'A':
            soft_sum += 11
            num_of_A += 1
        elif i == 'J' or i == 'Q' or i == 'K':
            soft_sum += 10
        else:
            soft_sum += int(i)
    
    while soft_sum > 21 and num_of_A > 0:
        num_of_A -= 1
        soft_sum -= 10
    return soft_sum

def record(bet_local, earning):
    user = current_user
    game_record = BlackJackGameRecord(
        user_id=user.id,
        bet_amount=bet_local,
        earnings=earning
    )
    user.coins += earning
    db.session.add(game_record)
    db.session.commit()

@app.route('/blackjack_rules', methods=['GET'])
@login_required
def blackjack_rules():
  '''
  Displays the game's rules (accessible from main menu).
  '''
  user = current_user
  return render_template('blackjack_rules.html', username=user.username, coins=user.coins)

@app.route('/blackjack_play', methods=['GET'])
@login_required
def blackjack_play():
    user = current_user
    #return render_template('blackjack_play.html', username=user.username, coins=user.coins)
    return render_template('blackjack_play.html', async_mode=socketio.async_mode, username=user.username, coins=user.coins)

@socketio.on('connect_event', namespace='/blackjack')
def test_message(message):
    emit('server_response', {'data': message['data']})

@socketio.on('client_event', namespace='/blackjack')
def test_client_message(message):
    emit('server_response', {'data': message['data']+' Received.'})

@socketio.on('disconnect_request', namespace='/blackjack')
def test_disconnect_request():    
    def can_disconnect():
        disconnect()
    emit('server_response', {'data': 'Disconnected!'}, callback=can_disconnect)

@socketio.on('connect', namespace='/blackjack')
def test_connect():
    emit('server_response', {'data': 'Server Connected!'})

@socketio.on('disconnect', namespace='/blackjack')
def test_disconnect():
    print('Client disconnected', request.sid)

@socketio.on('check_bet', namespace='/blackjack')
def check_bet(message):
    global bet
    user = current_user
    try_bet = int(message['bet_coin'])
    if user.coins >= try_bet:
        bet[user.username] = try_bet
        emit('bet_able')
    else:
        emit('bet_refuse')

@socketio.on('start_game', namespace='/blackjack')
def start_game():
    global cards_player
    global cards_dealer
    user = current_user
    cards_player[user.username] = []
    cards_dealer[user.username] = []
    cards_player[user.username] = random.choices(cards, k=2)[:]
    cards_dealer[user.username] = random.choices(cards, k=2)[:]
    cards_dealer_show = cards_dealer[user.username].copy()
    cards_dealer_show[0] = 'X'
    emit('start', {'player': cards_player[user.username], 'dealer': cards_dealer_show})

@socketio.on('check_start_status', namespace='/blackjack')
def check_start_status():
    user = current_user
    player_total = blackjack_sum(cards_player[user.username])
    dealer_total = blackjack_sum(cards_dealer[user.username])
    if player_total == 21 and dealer_total == 21:
        record(bet[user.username], 0)
        emit('server_response', {'data': 'Draw!'})
        emit('draw', {'cards': cards_dealer[user.username]})
        emit('finish_game', {'res': 'Draw'})
    elif blackjack_sum(cards_player[user.username]) == 21:
        record(bet[user.username], round(bet[user.username]*1.5))
        emit('server_response', {'data': 'You Win! BlackJack!'})
        emit('blackjack', {'cards': cards_dealer[user.username]})
        emit('finish_game', {'res': 'Win ' + str(round(bet[user.username]*1.5)) + ' Coins'})
    elif blackjack_sum(cards_dealer[user.username]) == 21:
        record(bet[user.username], -1*bet[user.username])   
        emit('server_response', {'data': 'Dealer Win!'})
        emit('dealer_win', {'cards': cards_dealer[user.username]})         
        emit('finish_game', {'res': 'Lose ' + str(bet[user.username]) + ' Coins'})
    else:
        emit('continue_game')

@socketio.on('player_take_one', namespace='/blackjack')
def player_take_one():
    user = current_user
    card = random.choice(cards)
    cards_player[user.username].append(card)
    emit('player_picked', {'cards': cards_player[user.username]})
    if blackjack_sum(cards_player[user.username]) > 21:
        emit('player_bust')
    if blackjack_sum(cards_player[user.username]) == 21:
        emit('player_21')

@socketio.on('player_stop', namespace='/blackjack')
def player_stop():
    global cards_dealer
    user = current_user
    while blackjack_sum(cards_dealer[user.username]) < 17:
        cards_dealer[user.username].append(random.choice(cards))
    emit('dealer_picked', {'cards': cards_dealer[user.username]})

@socketio.on('check_result', namespace='/blackjack')
def check_result():
    user = current_user
    player_total = blackjack_sum(cards_player[user.username])
    dealer_total = blackjack_sum(cards_dealer[user.username])
    if player_total > 21:
        record(bet[user.username], -1*bet[user.username])
        emit('server_response', {'data': 'Dealer Win!'})
        emit('dealer_win', {'cards': cards_dealer[user.username]})
        emit('finish_game', {'res': 'Lose ' + str(bet[user.username]) + ' Coins'})
    elif dealer_total > 21:
        record(bet[user.username], bet[user.username])
        emit('server_response', {'data': 'You Win!'})
        emit('player_win', {'cards': cards_dealer[user.username]})
        emit('finish_game', {'res': 'Win ' + str(bet[user.username]) + ' Coins'})
    else:
        if dealer_total > player_total:
            record(bet[user.username], -1*bet[user.username])
            emit('server_response', {'data': 'Dealer Win!'})
            emit('dealer_win', {'cards': cards_dealer[user.username]})         
            emit('finish_game', {'res': 'Lose ' + str(bet[user.username]) + ' Coins'})
        elif player_total > dealer_total:
            record(bet[user.username], bet[user.username])
            emit('server_response', {'data': 'You Win!'})
            emit('player_win', {'cards': cards_dealer[user.username]})
            emit('finish_game', {'res': 'Win ' + str(bet[user.username]) + ' Coins'})
        else:
            record(bet[user.username], 0)
            emit('server_response', {'data': 'Draw!'})
            emit('draw', {'cards': cards_dealer[user.username]})
            emit('finish_game', {'res': 'Draw'})

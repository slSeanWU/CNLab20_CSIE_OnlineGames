from flask import current_app as app
from flask import render_template, request, flash, redirect, url_for, json
from models import UserInfo
from main import db, socketio
from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, disconnect
import random

cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
cards_player = []
cards_dealer = []
bet = 0

def blackjack_sum(cards_list):
    soft_sum = 0
    hard_sum = 0
    for i in cards_list:
        if i == 'A':
            soft_sum += 11
            hard_sum += 1
        elif i == 'J' or i == 'Q' or i == 'K':
            soft_sum += 10
            hard_sum += 10
        else:
            soft_sum += int(i)
            hard_sum += int(i)
    
    if soft_sum > 21:
        return hard_sum
    return soft_sum

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

@socketio.on('start_game', namespace='/blackjack')
def start_game(message):
    global bet
    global cards_player
    global cards_dealer
    bet = message['bet_coin']
    cards_player.clear()
    cards_dealer.clear()
    cards_player = random.choices(cards, k=2)[:]
    cards_dealer = random.choices(cards, k=2)[:]
    cards_dealer_show = cards_dealer.copy()
    cards_dealer_show[0] = 'X'
    emit('start', {'player': cards_player, 'dealer': cards_dealer_show})


@socketio.on('player_take_one', namespace='/blackjack')
def player_take_one():
    card = random.choice(cards)
    cards_player.append(card)
    emit('player_picked', {'cards': cards_player})
    if blackjack_sum(cards_player) > 21:
        emit('player_bust')

@socketio.on('player_stop', namespace='/blackjack')
def player_stop():
    global cards_dealer
    while blackjack_sum(cards_dealer) < 17:
        cards_dealer.append(random.choice(cards))
    emit('dealer_picked', {'cards': cards_dealer, 'total': blackjack_sum(cards_dealer)})

    user = current_user

    player_total = blackjack_sum(cards_player)
    dealer_total = blackjack_sum(cards_dealer)
    if player_total > 21:
        user.coins -= int(bet)
        emit('server_response', {'data': 'Dealer Win!'})
        emit('result', {'data': 'Dealer Win!', 'res': 'Lose ' + bet + ' Coins'})
    elif dealer_total > 21:
        user.coins += int(bet)
        emit('server_response', {'data': 'You Win!'})
        emit('result', {'data': 'You Win!', 'res': 'Win ' + bet + ' Coins'})
    else:
        if dealer_total > player_total:
            user.coins -= int(bet)            
            emit('server_response', {'data': 'Dealer Win!'})
            emit('result', {'data': 'Dealer Win!', 'res': 'Lose ' + bet + ' Coins'})
        elif player_total > dealer_total:
            user.coins += int(bet)            
            emit('server_response', {'data': 'You Win!'})
            emit('result', {'data': 'You Win!', 'res': 'Win ' + bet + ' Coins'})
        else:
            emit('server_response', {'data': 'Draw!'})
            emit('result', {'data': 'Draw!'})

    db.session.commit()
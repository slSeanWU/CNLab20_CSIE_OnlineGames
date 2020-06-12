from flask import current_app as app
from flask import render_template, request, flash, redirect, url_for, json
from models import UserInfo
from main import db, socketio
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

@socketio.on('start_game', namespace='/blackjack')
def start_game(message):
    global bet
    global cards_player
    global cards_dealer
    user = current_user
    bet[user.username] = message['bet_coin']
    cards_player[user.username] = []
    cards_dealer[user.username] = []
    cards_player[user.username] = random.choices(cards, k=2)[:]
    cards_dealer[user.username] = random.choices(cards, k=2)[:]
    cards_dealer_show = cards_dealer[user.username].copy()
    cards_dealer_show[0] = 'X'
    if blackjack_sum(cards_player[user.username]) == 21 and blackjack_sum(cards_dealer[user.username]) == 21:
        emit('start', {'player': cards_player[user.username], 'dealer': cards_dealer[user.username]})
        emit('server_response', {'data': 'Draw!'})
        emit('draw')
        emit('finish_game', {'res': 'Draw'})
    elif blackjack_sum(cards_player[user.username]) == 21:
        emit('start', {'player': cards_player[user.username], 'dealer': cards_dealer[user.username]})
        user.coins += round(int(bet[user.username])*1.5)
        emit('server_response', {'data': 'You Win! BlackJack!'})
        emit('blackjack')
        emit('finish_game', {'res': 'Win ' + str(int(bet[user.username])*1.5) + ' Coins'})
    elif blackjack_sum(cards_dealer[user.username]) == 21:
        emit('start', {'player': cards_player[user.username], 'dealer': cards_dealer[user.username]})
        user.coins -= int(bet[user.username])   
        emit('server_response', {'data': 'Dealer Win!'})
        emit('dealer_win')         
        emit('finish_game', {'res': 'Lose ' + bet[user.username] + ' Coins'})
    else:
        emit('start', {'player': cards_player[user.username], 'dealer': cards_dealer_show})
    
    db.session.commit()

@socketio.on('player_take_one', namespace='/blackjack')
def player_take_one():
    user = current_user
    card = random.choice(cards)
    cards_player[user.username].append(card)
    emit('player_picked', {'cards': cards_player[user.username]})
    if blackjack_sum(cards_player[user.username]) > 21:
        emit('player_bust')

@socketio.on('player_stop', namespace='/blackjack')
def player_stop():
    global cards_dealer
    user = current_user

    while blackjack_sum(cards_dealer[user.username]) < 17:
        cards_dealer[user.username].append(random.choice(cards))
    emit('dealer_picked', {'cards': cards_dealer[user.username], 'total': blackjack_sum(cards_dealer[user.username])})

    player_total = blackjack_sum(cards_player[user.username])
    dealer_total = blackjack_sum(cards_dealer[user.username])
    if player_total > 21:
        user.coins -= int(bet[user.username])
        emit('server_response', {'data': 'Dealer Win!'})
        emit('dealer_win')
        emit('finish_game', {'res': 'Lose ' + bet[user.username] + ' Coins'})
    elif dealer_total > 21:
        user.coins += int(bet[user.username])
        emit('server_response', {'data': 'You Win!'})
        emit('player_win')
        emit('finish_game', {'res': 'Win ' + bet[user.username] + ' Coins'})
    else:
        if dealer_total > player_total:
            user.coins -= int(bet[user.username])   
            emit('server_response', {'data': 'Dealer Win!'})
            emit('dealer_win')         
            emit('finish_game', {'res': 'Lose ' + bet[user.username] + ' Coins'})
        elif player_total > dealer_total:
            user.coins += int(bet[user.username])     
            emit('server_response', {'data': 'You Win!'})
            emit('player_win')
            emit('finish_game', {'res': 'Win ' + bet[user.username] + ' Coins'})
        else:
            emit('server_response', {'data': 'Draw!'})
            emit('draw')
            emit('finish_game', {'res': 'Draw'})

    db.session.commit()
# !/usr/bin/python 
# coding:utf-8 

from websocket_server import WebsocketServer
import sys
import random
import string
import numpy as np
from collections import Counter

SUITS = ['黑桃', '愛心', '方塊', '梅花']

table_list = []
clientID2name = {}
name2client = {}
name2table = {}
BB, SB = 100, 50

DB = {'surrey': {'money': 1001}, 'surrey2': {'money': 1002}, '123': {'money': 1003}}

def num_to_card(card_num):    return SUITS[card_num//13]+str(card_num%13)

# Called for every client connecting (after handshake)
def new_client(client, server):    pass

# Called for every client disconnecting
def client_left(client, server):
    if client['id'] in clientID2name.keys():
        del name2client[clientID2name[client['id']]]
        del clientID2name[client['id']]

# Called when a client sends a message
def message_received(client, server, message):
    print("Client(%d) said: %s" % (client['id'], message))

    m = message.split()
    if m[0] == '#NAME':
        clientID2name[client['id']] = m[1]
        name2client[m[1]] = client
        print(name2client)
        update_game_status(m, table_list[name2table[clientID2name[client['id']]]], server)
    elif m[0] == '#ENTER':    join_table(m, server)
    elif m[0] == '#CHAT':
        m.insert(1, clientID2name[client['id']]+":")
        server.send_message_to_all(" ".join(m))
    else:    update_game_status(m, table_list[name2table[clientID2name[client['id']]]], server)

def gen_card_list():
    # return [0, 1, 2, 3, 4, 5] + [6,7,8,9,10,11,12] + np.arange(13,52).tolist()
    return np.arange(52).tolist()

def give_card(card_list):
    card1 = card_list.pop(0)
    card2 = card_list.pop(0)
    return card_list, [card1, card2]

def turn_card(card_list):
    board = []
    for i in range(5):    board.append(card_list.pop(0))
    return board

def is_last_player(game_status):
    for player in game_status['players']:
        if player['in_game']:
            if player['action_yet'] and player['pool'] == game_status['now_bid']:    pass
            else:    return False
    return True

def compare(a, b):
    for key in a.keys():
        if a[key]:
            if isinstance(a[key], list):
                if b[key]:
                    for i,j in zip(a[key],b[key]):
                        if i > j or (i == 0 and j != 0):    return 1
                        elif i == j:    pass
                        else:    return -1
                    return -1
                else:    return 1
            else:
                if not b[key] or a[key] > b[key] or (a[key] == 0 and b[key] != 0):    return 1
                elif b[key] and a[key] == b[key]:    return 0
                else:    return -1
        elif b[key]:    return -1

def who_win(game_status):
    biggest_hands = None
    for player in game_status['players']:
        hands = {
            'Straight_Flush': [],
            'Four': False,
            'Full_House': False,
            'Flush': False,
            'Straight': [],
            'Three': False,
            'Two_Pair': [],
            'One_Pair': [],
            'High': []
        }
        if player['in_game']:
            hand_card = game_status['board'] + player['card']

            cards_num = Counter(np.sort(np.array(hand_card) % 13))
            cards_suit = Counter(np.sort(np.array(hand_card) // 13))

            if len(cards_num) >= 5:
                # 檢查順子
                c = sorted(cards_num) # list all unique element
                if 0 in c:    c += [13]
                l = 0
                for i in range(1,len(c)):
                    l = (l+1) if c[i] == c[i-1] + 1 else 0
                    if l >= 4:    hands['Straight'] += [c[i] % 13]
                if hands['Straight']:
                    hands['Straight'] = hands['Straight'][::-1]

                # 檢查同花
                if max(cards_suit.values()) >= 5:
                    u = list(cards_suit.keys())[np.argmax(list(cards_suit.values()))] # 
                    for i in range(0 + 13*u, 13*(u+1)):
                        if i in hand_card:
                            hands['Flush'] = i
                            if i % 13 == 0:    break
                
                # 檢查同花順
                if hands['Straight'] and hands['Flush']:
                    u = list(cards_suit.keys())[np.argmax(list(cards_suit.values()))] # 
                    a = False
                    l = 0
                    c = []
                    for i in range(0+13*u, 13*(u+1)):
                        if i in hand_card:
                            c.append(i%13)
                    
                    if 0 in c:    c += [13]
                    l = 0
                    for i in range(1,len(c)):
                        l = (l+1) if c[i] == c[i-1] + 1 else 0
                        if l >= 4:    hands['Straight_Flush'] += [c[i] % 13]
                    if hands['Straight_Flush']: 
                        hands['Straight_Flush'] = hands['Straight_Flush'][::-1]

                keys = list(cards_num.keys())
                values = list(cards_num.values())
                # 檢查三條
                if 3 in values:    hands['Three'] = keys[values.index(3)]

                # 檢查對子
                if 2 in values:
                    if len(cards_num) == 5:
                        if keys[values.index(2)] == 0:
                            hands['Two_Pair'].append(0)
                            hands['Two_Pair'].append(keys[::-1][values[::-1].index(2)])
                        else:
                            hands['Two_Pair'].append(keys[values[::-1].index(2)])
                            hands['Two_Pair'].append(keys[values.index(2)])
                        hands['Two_Pair'].append(keys[::-1][values[::-1].index(1)])
                    else:
                        hands['One_Pair'].append(keys[values.index(2)])
                        del keys[values.index(2)]
                        hands['One_Pair'] += keys[::-1]

                if 0 in keys:    hands['High'] = [keys[0]] + keys[1:][::-1]
                else:    hands['High'] = keys[::-1]

            else:
                keys = list(cards_num.keys())
                values = list(cards_num.values())
                # 檢查鐵支
                if 4 in values:    hands['Four'] = keys[values.index(4)]

                # 檢查葫蘆
                if 3 in values:    hands['Full_House'] = keys[values.index(3)]

                # 檢查兩對
                if 2 in values:
                    if keys[values.index(2)] == 0:
                        hands['Two_Pair'].append(0)
                        hands['Two_Pair'].append(keys[values[::-1].index(2)])
                    else:
                        hands['Two_Pair'].append(keys[values[::-1].index(2)])
                        hands['Two_Pair'].append(keys[values.index(2)])
                    hands['Two_Pair'].append(keys[values.index(1)])
            
            if biggest_hands:
                if compare(hands, biggest_hands[0]) == 1:    biggest_hands = (hands, [player['username']])
                elif compare(hands, biggest_hands[0]) == 0:    biggest_hands[1].append(player['username'])
            else:
                biggest_hands = (hands, [player['username']])

    return biggest_hands[1]

def join_table(m, server):
    for game_status in table_list:
        if game_status['turn'] == -1 and game_status['player_num'] == int(m[2]) and len(game_status['players']) != int(m[2]):
            name2table[m[1]] = table_list.index(game_status)
            update_game_status(m, game_status, server)
            return 0
    game_status = {
        'turn': -1,
        'now_bid': 0,
        'BB': 1,    # BigBlind
        'SB': 0,    # SmallBlind
        'player_num': int(m[2]),
        'now_playing': -1,
        'players': [],
        'board': []
    }
    name2table[m[1]] = len(table_list)
    table_list.append(game_status)
    update_game_status(m, game_status, server)

def init_game(game_status, server):
    card_list = gen_card_list()
    random.shuffle(card_list)
    for player in game_status['players']: # 發牌
        card_list, player['card'] = give_card(card_list)
        player['in_game'] = True
        print('initializing game...')
        print(player)

    game_status['turn'] = 0
    game_status['now_bid'] = BB
    game_status['BB'] = (game_status['BB'] + 1) % game_status['player_num']
    game_status['SB'] = (game_status['SB'] + 1) % game_status['player_num']
    game_status['now_playing'] = game_status['SB']#(game_status['SB'] - 1) % game_status['player_num']
    game_status['board'] = turn_card(card_list)

    for player in game_status['players']:
        player['in_game'] = True
        player['action_yet'] = False
        cur_client = name2client[player['username']]
        hand_card_message = "#HAND %s %s" % (SUITS[player['card'][0]//13] + str(player['card'][0]%13 + 1), SUITS[player['card'][1]//13] + str(player['card'][1]%13 + 1))
        chip_message = "#CHIP %d" % DB[player['username']]['money']
        print('server send to {}: {}'.format(cur_client, hand_card_message))
        server.send_message(cur_client, hand_card_message)
        server.send_message(cur_client, chip_message)
        print('success')


    # 大盲注，小盲注
    server.send_message_to_all("#BID %d" % BB)
    server.send_message(name2client[game_status['players'][game_status['BB']]['username']], "#BLIND %d" % BB)
    server.send_message(name2client[game_status['players'][game_status['SB']]['username']], "#BLIND %d" % SB)
    DB[game_status['players'][game_status['BB']]['username']]['money'] -= BB
    game_status['players'][game_status['BB']]['pool'] += BB
    DB[game_status['players'][game_status['SB']]['username']]['money'] -= SB
    game_status['players'][game_status['SB']]['pool'] += SB

    server.send_message_to_all("#IO Game Start!")
    server.send_message(name2client[game_status['players'][game_status['now_playing']]['username']], "#TURN")

def update_game_status(m, game_status, server):
    action = m[0]

    if game_status['turn'] == -1:   # 遊戲還沒開始
        if action == '#ENTER':
            for player in game_status['players']:    server.send_message(name2client[player['username']], "#IO %s entered the room" % m[1])
            game_status['players'].append({'username': m[1], 'card': None, 'in_game': False, 'pool': 0, 'action_yet': False})
        # 人數到齊
        if m[1] in name2client and len(game_status['players']) == game_status['player_num']:
            init_game(game_status, server)
            return None
        else:    return None

    # 仍在遊戲中所有人皆行動過該輪才有可能結束
    if action:    game_status['players'][game_status['now_playing']]['action_yet'] = True

    if action == '#CALL':
        DB[game_status['players'][game_status['now_playing']]['username']]['money'] -= game_status['now_bid'] - game_status['players'][game_status['now_playing']]['pool']
        game_status['players'][game_status['now_playing']]['pool'] = game_status['now_bid']
        server.send_message_to_all("#IO %s called" % game_status['players'][game_status['now_playing']]['username'])
        server.send_message(name2client[game_status['players'][game_status['now_playing']]['username']], "#CHIP %d" % DB[game_status['players'][game_status['now_playing']]['username']]['money'])

    elif action == '#RAISE':
        game_status['now_bid'] += int(m[1])
        DB[game_status['players'][game_status['now_playing']]['username']]['money'] -= game_status['now_bid'] - game_status['players'][game_status['now_playing']]['pool']
        game_status['players'][game_status['now_playing']]['pool'] = game_status['now_bid']
        server.send_message_to_all("#IO %s raised $%s" % (game_status['players'][game_status['now_playing']]['username'], m[1]))
        server.send_message(name2client[game_status['players'][game_status['now_playing']]['username']], "#CHIP %d" % DB[game_status['players'][game_status['now_playing']]['username']]['money'])

    elif action == '#FOLD':
        game_status['players'][game_status['now_playing']]['in_game'] = False
        server.send_message_to_all("#IO %s folded" % game_status['players'][game_status['now_playing']]['username'])

    elif action == '#CHECK':
        server.send_message_to_all("#IO %s checked" % game_status['players'][game_status['now_playing']]['username'])
        pass

    elif action == '#ALLIN':
        if DB[game_status['players'][game_status['now_playing']]['username']]['money'] < game_status['now_bid']:
            return None
        else:
            game_status['now_bid'] += DB[game_status['players'][game_status['now_playing']]['username']]['money']
            DB[game_status['players'][game_status['now_playing']]['username']]['money'] = 0
            game_status['players'][game_status['now_playing']]['pool'] = game_status['now_bid']
            server.send_message_to_all("#IO %s All-In !!" % game_status['players'][game_status['now_playing']]['username'])
            server.send_message(name2client[game_status['players'][game_status['now_playing']]['username']], "#CHIP %d" % DB[game_status['players'][game_status['now_playing']]['username']]['money'])

    # 通知所有人現在下注金額
    server.send_message_to_all("#BID %d" % game_status['now_bid'])
    
    # 若為該輪最後一位玩家，turn ++，開牌
    if is_last_player(game_status):
        if game_status['turn'] != 3:
            B = ''
            for c in game_status['board'][:3+game_status['turn']]:    B += ' ' + SUITS[c//13] + str(c%13 + 1)
            server.send_message_to_all("#BOARD%s" % B)
        game_status['turn'] += 1
        for player in game_status['players']:    player['action_yet'] = False

    # 找下一位玩家
    for i in range(game_status['player_num']):
        count = (game_status['now_playing']+i+1) % game_status['player_num']
        if game_status['players'][count]['in_game']:
            if count == game_status['now_playing']:    game_status['turn'] = 4
            else:
                game_status['now_playing'] = count
                break

    # 該輪牌局全部結束，結算，開啟新局
    if game_status['turn'] == 4:
        winners = who_win(game_status)
        server.send_message_to_all("#IO %s won!" % " and ".join(winners))
        pool = 0
        for player in game_status['players']:
            pool += player['pool']
            player['pool'] = 0
        for name in winners:
            DB[name]['money'] += pool // len(winners)
            server.send_message(name2client[name], "#CHIP %d" % DB[name]['money'])
        init_game(game_status, server)

    # 告知下個玩家：輪你
    server.send_message(name2client[game_status['players'][game_status['now_playing']]['username']], "#TURN")

PORT=9001
server = WebsocketServer(PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()

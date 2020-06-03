from websocket_server import WebsocketServer
import sys
import random
import string

# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])
    for client in server.clients:
        print(client)
    server.send_message_to_all("Hey all, a new client has joined us")


# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message, game_status):
    if len(message) > 200:
        message = message[:200]+'..'
    print("Client(%d) said: %s" % (client['id'], message))
    update_game_status(game_status, message)
    server.send_message_to_all("Client(%d) said: %s" % (client['id'], message))
    

def gen_card_list():
    card_list = []
    for i in ['黑桃', '愛心', '方塊', '梅花']:
        for j in range(13):
            card_list.append(i + str(j+1))
    return card_list

def give_card(card_list):
    card1 = card_list.pop(0)
    card2 = card_list.pop(0)
    return card_list, (card1, card2)

def turn_card(card_list):
    turned_card = []
    for i in range(5):
        turned_card.append(card_list.pop(0))
    return turned_card

def swap_card(t):
    return (t[1], t[0])


card_list = gen_card_list()
random.shuffle(card_list)
print(card_list)

# players = []
# for player in players:
#     player['username'] = ''.join(random.choice(string.ascii_lowercase) for x in range(4))
#     card_list, player['card'] = give_card(card_list)

# print(players)
# print(card_list)

# for player in players:
#     player['card'] = swap_card(player['card'])

# for player in players:
#     print(player)

game_status = {
    'turn': -1,
    'now_bid': 0,
    'money_pool': 0,
    'BB': 0,    # BigBlind
    'SB': 4,    # SmallBlind
    'player_num': 0,
    'players': [],
    'turned_card': []
}

def update_game_status(game_status, client_messege):

    split = client_messege.split()
    action, name = split[0], split[1]

    if game_status['turn'] == -1:   # 遊戲還沒開始
        # 應該會有一個"進入房間的動作"跟"id"
        game_status['players'].append({'username': name, 'card': None, 'in_game': False})

        if len(game_status['players']) == game_status['player_num']: # 人數到齊
            for player in game_status['players']: # 發牌
                card_list, player['card'] = give_card(card_list)  
                player['in_game'] = True
            game_status['turn'] = 0
            game_status['turned_card'] = turn_card(card_list)


    if action == 'call':
        # database
    elif action == 'raise':
        money = split[2] # database
        game_status['now_bid'] 
        game_status['money_pool'] += money

    elif action == 'fold':

    elif action == 'check':

    elif action == 'allin':
        money = split[2] # database
        game_status['now_bid']
        game_status['money_pool'] += money

    if is_last_player(): #TODO: is_last_player
        game_status['turn'] += 1 

    # 這輪手牌全部結束
    if game_status['turn'] == 4:
        # 給贏的人錢   # database
        BB = game_status['BB']
        SB = game_status['SB']
        player_num = game_status['player_num']
        game_status = {
            'turn': 0,
            'now_bid': 0,
            'money_pool': 0,
            'BB': (BB+1)%player_num,    # BigBlind
            'SB': (SB+1)%player_num,    # SmallBlind
            'player_num': (SB+1)%player_num
        }

    # 告知下個玩家：輪你
    server.send_message_to

PORT=9001
server = WebsocketServer(PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()

from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a very secret key 123'
socket_io = SocketIO(app)

connected_servers_group = set()

campaign_balances = {}

campaign_rearrange_holder = {}
campaign_rearrange_counters = {}


@socket_io.on('connect')
def connect():
    global connected_servers_group

    connected_servers_group.add(request.sid);


@socket_io.on('out_of_money')
def out_of_money(campaign_name):
    emit('rearrange', campaign_name, callback=rearrange, broadcast=True)


def rearrange(campaign_server_data):
    global connected_servers_group
    global campaign_balances
    global campaign_rearrange_holder
    global campaign_rearrange_counters

    campaign_name = campaign_server_data['campaign_name']
    campaign_balance = campaign_server_data['balance']

    if campaign_name in campaign_rearrange_holder:
        campaign_rearrange_holder[campaign_name] += campaign_balance
        campaign_rearrange_counters[campaign_name] += 1
    else:
        campaign_rearrange_holder[campaign_name] = campaign_balance
        campaign_rearrange_counters[campaign_name] = 1

    if campaign_name in campaign_rearrange_counters:
        if campaign_rearrange_counters[campaign_name] == len(connected_servers_group):
            campaign_balances[campaign_name] = campaign_rearrange_holder[campaign_name]

            rearranged_money = int(campaign_balances[campaign_name]) / len(connected_servers_group)
            print(rearranged_money)
            emit('retake_money', {'campaign_name': campaign_name, 'balance': rearranged_money}, broadcast=True)


@socket_io.on('disconnect')
def disconnect():
    global connected_servers_group

    connected_servers_group.remove(request.sid)


if __name__ == '__main__':
    socket_io.run(app)

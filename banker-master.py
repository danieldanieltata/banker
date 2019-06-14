from flask import Flask, request
from flask_socketio import SocketIO, emit
import json

# Flask with socket.io implementation
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a very secret key 123'
socket_io = SocketIO(app)

# Connect server set container
connected_servers_group = set()

# Load mock data from file and put it in var
with open('mocks/banker_data.json', 'r') as f:
    MOCK_DATA = json.load(f)

campaign_balances = {**MOCK_DATA}

# This is a dummy containers for the money rearrange process
campaign_rearrange_holder = {}
campaign_rearrange_counters = {}


# If a new server connect, he's getting into the list
@socket_io.on('connect')
def connect():
    global connected_servers_group

    connected_servers_group.add(request.sid)
    emit('rearrange', '*', broadcast=True)


# The servers tells to the master that he's out of money in some campaign
@socket_io.on('out_of_money')
def out_of_money(campaign_name):
    emit('rearrange', campaign_name, broadcast=True)


# Here im doing the rearrange process
@socket_io.on('rearrange')
def rearrange(campaign_server_data):
    global connected_servers_group
    global campaign_balances
    global campaign_rearrange_holder
    global campaign_rearrange_counters

    # If their is only one server and he has no data we sending the mock data
    if len(connected_servers_group) == 1 and campaign_server_data['campaigns'] == {}:
        for k, v in campaign_balances.items():
            socket_io.emit('retake_money', {'campaign_name': k, 'balance': v})
        return

    if 'campaigns' not in campaign_server_data:
        return

    # Iterating every campaign of every server in order to rearrange
    for k, v in campaign_server_data['campaigns'].items():
        campaign_name = k
        campaign_balance = v

        # campaign_rearrange_holder   - dummy dict that hold the campaign's balance
        # campaign_rearrange_counters - contains counters of every single campaign to check
        #                                                      if all the server returned their balance
        if k in campaign_rearrange_holder:
            campaign_rearrange_holder[campaign_name] += campaign_balance
            campaign_rearrange_counters[campaign_name] += 1
        else:
            campaign_rearrange_holder[campaign_name] = campaign_balance
            campaign_rearrange_counters[campaign_name] = 1

        # If all the server's return their balances, the splitting of the money begins
        if campaign_rearrange_counters[campaign_name] == len(connected_servers_group):
            campaign_balances[campaign_name] = campaign_rearrange_holder[campaign_name]

            rearranged_money = int(campaign_balances[campaign_name]) / len(connected_servers_group)

            del campaign_rearrange_holder[campaign_name]
            del campaign_rearrange_counters[campaign_name]

            socket_io.emit('retake_money', {'campaign_name': campaign_name, 'balance': rearranged_money},
                           broadcast=True)


@socket_io.on('feedback_is_for_other_server')
def feedback_is_for_other_server(ad_data):
    emit('feedback_is_for_other_server', ad_data, broadcast=True)


# disconnect a server
@socket_io.on('disconnect')
def disconnect():
    global connected_servers_group

    connected_servers_group.remove(request.sid)


if __name__ == '__main__':
    socket_io.run(app)

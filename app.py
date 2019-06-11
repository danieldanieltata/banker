from flask import Flask, request
import json
import requests
import sys

app = Flask(__name__)

with open('mocks/banker_data.json', 'r') as f:
    MOCK_DATA = json.load(f)

campaigns_balance = {}


@app.route('/')
def index():
    return json.dumps(MOCK_DATA)


@app.route('/sync')
def sync():
    global campaigns_balance

    if 'new_data' not in request.args:
        return json.dumps({'synced': False})

    new_data = request.args['new_data']
    campaigns_balance = {**campaigns_balance, **new_data}
    print(campaigns_balance)
    return json.dumps({'synced': True})


# @app.route('/get_money')
# def get_money():

# Master Routes
servers_counter = 0
servers_group = {}


@app.route('/sign_up_to_group/<port_number>')
def sign_up_to_group(port_number):
    global servers_counter
    global servers_group

    for k, v in servers_group.items():
        if v == port_number:
            return 'Port already exists'

    servers_counter += 1
    servers_group[servers_counter] = port_number
    print(servers_group)
    return json.dumps(servers_group)


@app.route('/split_money')
def split_money():
    global servers_counter

    if not 'money_to_split' in request.args or not 'campaign_name' in request.args:
        return 'Not valid query'

    if servers_counter == 0:
        return 'No slaves'

    money_to_split = request.args['money_to_split']
    campaign_name = request.args['campaign_name']

    splitted_money = int(money_to_split) / servers_counter

    for k, v in servers_group.items():
        requests.post('127.0.0.1:' + v, data={'campaign_name': campaign_name, 'balance': splitted_money})

    return json.dumps({'campaign_name': campaign_name, 'splitted_money': splitted_money})


if __name__ == '__main__':

    if len(sys.argv) > 1:
        port = sys.argv[1]

        requests.get('http://127.0.0.1:5000/sign_up_to_group/' + port)
        app.run(port=port)

    else:
        app.run()


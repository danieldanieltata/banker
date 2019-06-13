from flask import Flask, request
import socketio
import sys
import json

app = Flask(__name__)

# Balance, and logger for ads
campaigns_balance = {}
ads_logger = {}

# Socket.io client init
sio = socketio.Client()
sio.connect('http://localhost:5000')

# Master asks for campaign balance or all of them
@sio.on('rearrange')
def rearrange(campaign_name):
    global campaigns_balance

    if campaign_name == '*':
        sio.emit('rearrange', {'campaign_name': '*', 'campaigns': campaigns_balance})
        return

    sio.emit('rearrange',
             {'campaign_name': campaign_name, 'campaigns': {campaign_name: campaigns_balance[campaign_name]}})

# Master return balance after arranging
@sio.on('retake_money')
def retake_money(campaign_data):
    global campaigns_balance

    if '*' in campaign_data['campaign_name']:
        campaigns_balance = {**campaigns_balance, **campaign_data['campaigns']}
    else:
        campaigns_balance[campaign_data['campaign_name']] = campaign_data['balance']

    print(campaigns_balance)


# Some server got feedback that wasn't he's so he informs the master to check with others
@sio.on('feedback_is_for_other_server')
def feedback_is_for_other_server(ad_data):
    global campaigns_balance
    global ads_logger

    campaign_name = ad_data.campaign_name
    price = ad_data.price
    ad_id = ad_data.ad_id
    got_it = ad_data.got_it

    if campaign_name in ads_logger and ad_id in ads_logger[campaign_name]:
        if not got_it:
            campaigns_balance[campaign_name] += price
            del ads_logger[campaign_name][ad_id]


# Banker api
@app.route('/')
def index():
    return json.dumps(campaigns_balance)


# Handles the get money request
@app.route('/get_money')
def get_money():
    global campaigns_balance
    global ads_logger

    if 'campaign_name' not in request.args or 'price' not in request.args or 'ad_id' not in request.args:
        return 'wrong parameters'

    campaign_name = request.args['campaign_name']
    price = request.args['price']
    ad_id = request.args['ad_id']

    # Checking if have money or not, if not sending message to master
    if campaign_name in campaigns_balance:
        if campaigns_balance[campaign_name] == 0:
            sio.emit('out_of_money', campaign_name)
            return json.dumps({'can_buy': False, 'campaign_name': campaign_name, 'price': price, 'ad_id': ad_id})

        can_buy_ad = float(campaigns_balance[campaign_name]) - float(price)
        if can_buy_ad >= 0:
            campaigns_balance[campaign_name] = can_buy_ad
            if campaign_name not in ads_logger:
                ads_logger[campaign_name] = {}
                ads_logger[campaign_name][ad_id] = price
            else:
                ads_logger[campaign_name][ad_id] = price

            return json.dumps({'can_buy': True, 'campaign_name': campaign_name, 'price': price, 'ad_id': ad_id})
        else:
            return json.dumps({'can_buy': False, 'campaign_name': campaign_name, 'price': price, 'ad_id': ad_id})


# Getting a feedback to know if not got the ad
@app.route('/feedback')
def feedback():
    global campaigns_balance
    global ads_logger

    if 'campaign_name' not in request.args or 'price' not in request.args or 'ad_id' not in request.args or \
            'got_it' not in request.args:
        return 'wrong parameters'

    args = request.args

    campaign_name = args['campaign_name']
    price = args['price']
    ad_id = args['ad_id']
    got_it = args['got_it']

    # Checks if have this ad if not informs the master
    if campaign_name in ads_logger and ad_id in ads_logger[campaign_name]:
        if not got_it:
            campaigns_balance[campaign_name] += price
            del ads_logger[campaign_name][ad_id]

            return json.dumps(campaigns_balance)
        else:
            sio.emit('feedback_is_for_other_server', {'campaign_name': campaign_name, 'price': price,
                                                      'ad_id': ad_id, 'got_it': got_it})


if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = sys.argv[1]

        app.run(port=port)
    else:
        app.run(port=4201)

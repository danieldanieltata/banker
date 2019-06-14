import requests
import random
import sys

mock_server = 'http://127.0.0.1:'
port = '4201'

ads_data = {}


def get_money_check():
    global ads_data
    min_price = 1
    max_price = 100

    ad_id_counter = 0

    ads_data['campaign_1'] = {}
    while True:
        random_price = random.randint(min_price, max_price)
        ad_id_counter += 1

        ads_data['campaign_1'][ad_id_counter] = random_price
        request = requests.get(mock_server + '/get_money', params={'campaign_name': 'campaign_1',
                                                                   'price': random_price, 'ad_id': ad_id_counter})

        print(request.json())
        if not dict(request.json())['can_buy']:
            return request.json()


def send_feedback():
    global ads_data

    for campaign_name in ads_data:
        for k, v in ads_data[campaign_name].items():
            random_got_ad = random.choice([True, False])

            request = requests.get(mock_server + '/feedback', params={'campaign_name': campaign_name, 'price': v,
                                                                      'ad_id': k, 'got_it': random_got_ad})

            print(request.text)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = sys.argv[1]
    mock_server += port

    print('Running mock get money function in loop until gets false')
    get_all_money_until_refuse = get_money_check()

    if not get_all_money_until_refuse['can_buy']:
        print("Running mock feedback function in loops of all ads id's")
        send_feedback()

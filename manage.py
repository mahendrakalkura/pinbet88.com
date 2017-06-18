from datetime import date, datetime
from pprint import pprint
from sys import argv
from time import time

from requests import request


def main(options):
    if options[1] == '--matches':
        execute_matches()
        return


def execute_matches():
    matches = get_matches()
    pprint(matches)


def get_matches():
    matches = []
    url = 'https://ropinwev.pinbet88.com/sports-service/sv/odds/events'
    method = 'GET'
    _ = time()
    d = date.today().isoformat()
    params = {
        '_': _,
        'btg': '1',
        'c': 'IN',
        'd': d,
        'ev': '',
        'g': 'QQ==',
        'l': '3',
        'lg': '',
        'locale': 'en_US',
        'me': '0',
        'mk': '1',
        'more': 'false',
        'o': '1',
        'ot': '1',
        'pa': '0',
        'sp': '29',
        'tm': '0',
        'v': '0',
    }
    response = request(url=url, method=method, params=params)
    print(response.text)
    json = response.json()
    tournaments = json['l'][0][2] + json['n'][0][2]
    for tournament in tournaments:
        items = tournament[2]
        for item in items:
            id = item[0]
            home = item[1]
            away = item[2]
            date_ = item[3]
            date_ = date_ / 1000
            date_ = int(date_)
            date_ = datetime.utcfromtimestamp(date_)
            match = {
                'id': id,
                'teams': {
                    'home': home,
                    'away': away,
                },
                'date': date_,
            }
            matches.append(match)
    return matches


if __name__ == '__main__':
    main(argv)

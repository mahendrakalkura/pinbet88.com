from datetime import date, datetime
from os import getenv
from pprint import pprint
from sys import argv
from time import time

from requests import Session
from requests.cookies import RequestsCookieJar


def main(options):
    if options[1] == '--matches':
        execute_matches()
        return


def execute_matches():
    session = Session()
    response = home(session)
    response = sign_in(session)
    matches = get_matches(session)
    pprint(matches)


def home(session):
    url = 'https://www.pinbet88.com/en/'
    method = 'GET'
    response = session.request(url=url, method=method)
    return response


def sign_in(session):
    url = 'https://www.pinbet88.com/member-service/v1/login?locale=en_US'
    method = 'POST'
    data = {
        'loginId': getenv('USERNAME'),
        'password': getenv('PASSWORD'),
    }
    response = session.request(url=url, method=method, data=data)
    return response


def get_matches(session):
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
    headers = {
        'host': 'ropinwev.pinbet88.com',
        'referer': 'https://ropinwev.pinbet88.com/en/sports',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/5.0 (KHTML, like Gecko) Chrome/5.0 Safari/5.0',
        'x-requested-with': 'XMLHttpRequest',
    }
    response = session.request(url=url, method=method, params=params)
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

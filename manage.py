from contextlib import closing
from datetime import date, datetime
from pprint import pprint
from os.path import devnull
from sys import argv
from time import time
from traceback import print_exc

from requests import request
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT = 30
URLS_HOME = 'https://www.pinbet88.com/en/sports/soccer'
URLS_MATCHES = 'https://www.pinbet88.com/sports-service/sv/odds/events'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/5.0 (KHTML, like Gecko) Chrome/5.0 Safari/5.0'

RemoteConnection._timeout = TIMEOUT


def main(options):
    if options[1] == '--matches':
        execute_matches()
        return


def execute_matches():
    matches = get_matches()
    pprint(matches)


def get_matches():
    matches = []
    firefox_profile = get_firefox_profile()
    browser = webdriver.Firefox(firefox_profile=firefox_profile, log_path=devnull)
    with closing(browser) as browser:
        contents, cookies = get_contents_and_cookies(browser)
    if not contents:
        return matches
    json = None
    try:
        d = date.today().isoformat()
        v = time()
        method = 'GET'
        url = URLS_MATCHES
        headers = {
            'referer': 'https://www.pinbet88.com/en/sports/soccer',
            'user-agent': USER_AGENT,
            'x-requested-with': 'XMLHttpRequest',
        }
        params = {
            '_': v,
            'btg': '1',
            'c': 'IN',
            'd': d,
            'ev': '',
            'g': 'QQ==',
            'l': '3',
            'lg': '',
            'locale': 'en_US',
            'mk': '2',
            'more': 'false',
            'o': '1',
            'ot': '1',
            'pa': '0',
            'sp': '29',
            'tm': '0',
            'v': v,
        }
        response = request(method, url, cookies=cookies, headers=headers, params=params, timeout=TIMEOUT)
        if response:
            json = response.json()
    except Exception:
        print_exc()
    if not json:
        return matches
    tournaments = []
    if json['l']:
        tournaments += json['l'][0][2]
    if json['n']:
        tournaments += json['n'][0][2]
    for tournament in tournaments:
        items = tournament[2]
        for item in items:
            id = item[0]
            home = item[1]
            away = item[2]
            date_ = item[4]
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


def get_firefox_profile():
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.add_extension('adblock_plus.xpi')
    firefox_profile.set_preference('general.useragent.override', USER_AGENT)
    firefox_profile.set_preference('network.proxy.type', 0)
    firefox_profile.set_preference('xpinstall.signatures.required', False)
    return firefox_profile


def conditions_home(browser):
    if 'id="sports"' in browser.page_source:
        return True
    return False


def get_contents_and_cookies(browser):
    contents = None
    try:
        browser.get(URLS_HOME)
        wait = WebDriverWait(browser, TIMEOUT)
        wait.until(conditions_home)
        contents = browser.execute_script('return document.getElementsByTagName("html")[0].innerHTML')
    except Exception:
        print_exc()
    cookies = browser.get_cookies()
    cookies = {cookie['name']: cookie['value'] for cookie in cookies}
    return contents, cookies


def conditions_matches(browser):
    print(browser.page_source[-100:])
    if browser.page_source.startswith('{'):
        print('conditions_matches - True')
        return True
    print('conditions_matches - False')
    return False


if __name__ == '__main__':
    main(argv)

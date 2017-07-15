from datetime import date, datetime
from json import loads
from os.path import devnull
from pprint import pprint
from sys import argv
from time import time
from traceback import print_exc

from requests import request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

URLS_HOME = 'https://www.pinbet88.com/en/sports/soccer'
URLS_MATCHES = 'https://www.pinbet88.com/sports-service/sv/odds/events'
URLS_MATCH = 'http://live.pinbet88.com/live-center-service/s/match/restore/{id:s}'
USERNAME = 'CA701YT003'
PASSWORD = 'abcd1234'
TIMEOUT = 30
USER_AGENT = 'Mozilla/6.0 (X11; Linux x86_64) AppleWebKit/6.0 (KHTML, like Gecko) Chrome/6.0 Safari/6.0'

RemoteConnection._timeout = TIMEOUT


def main(options):
    if options[1] == '--matches':
        execute_matches()
        return
    if options[1] == '--match':
        execute_match(options[2])
        return


def execute_matches():
    firefox_profile = get_firefox_profile()
    browser = get_browser(firefox_profile)
    matches = get_matches(browser)
    browser.quit()
    pprint(matches)


def get_matches(browser):
    matches = []
    contents, cookies = get_matches_contents_and_cookies(browser)
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
            id = item[20]
            if not id:
                continue
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


def get_matches_contents_and_cookies(browser):
    contents = None
    try:
        browser.get(URLS_HOME)
        wait = WebDriverWait(browser, TIMEOUT)
        wait.until(get_matches_condition)
        contents = browser.execute_script('return document.getElementsByTagName("html")[0].innerHTML')
    except Exception:
        print_exc()
    cookies = browser.get_cookies()
    cookies = {cookie['name']: cookie['value'] for cookie in cookies}
    return contents, cookies


def get_matches_condition(browser):
    condition = expected_conditions.presence_of_element_located((By.ID, 'sports'))
    status = condition(browser)
    if not status:
        return False
    return True


def execute_match(id):
    firefox_profile = get_firefox_profile()
    browser = get_browser(firefox_profile)
    match = get_match(browser, id)
    browser.quit()
    pprint(match)


def get_match(browser, id):
    match = []
    contents, cookies = get_match_contents_and_cookies(browser)
    if not contents:
        return match
    json = None
    try:
        method = 'GET'
        url = URLS_MATCH
        url = url.format(id=id)
        headers = {
            'referer': 'https://www.pinbet88.com/en/sports/soccer',
            'user-agent': USER_AGENT,
            'x-requested-with': 'XMLHttpRequest',
        }
        response = request(method, url, cookies=cookies, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        json = response.json()
        json['data'] = loads(json['data'])
    except Exception:
        print_exc()
    if not json:
        return match
    match = json
    return match


def get_match_contents_and_cookies(browser):
    contents = None
    try:
        browser.get(URLS_HOME)
        wait = WebDriverWait(browser, TIMEOUT)
        wait.until(get_match_condition_1)
        username = browser.find_element_by_name('loginId')
        username.send_keys(USERNAME)
        password = browser.find_element_by_name('password')
        password.send_keys(PASSWORD)
        button = browser.find_element_by_id('login')
        button.click()
        wait = WebDriverWait(browser, TIMEOUT)
        wait.until(get_match_condition_2)
        contents = browser.execute_script('return document.getElementsByTagName("html")[0].innerHTML')
    except Exception:
        print_exc()
    cookies = browser.get_cookies()
    cookies = {cookie['name']: cookie['value'] for cookie in cookies}
    return contents, cookies


def get_match_condition_1(browser):
    body = browser.find_element_by_tag_name('body')
    className = body.get_attribute('class')
    className = className.strip()
    if className != 'en_US noauth':
        return False
    condition = expected_conditions.visibility_of_element_located((By.NAME, 'loginId'))
    status = condition(browser)
    if not status:
        return False
    condition = expected_conditions.visibility_of_element_located((By.NAME, 'password'))
    status = condition(browser)
    if not status:
        return False
    return True


def get_match_condition_2(browser):
    body = browser.find_element_by_tag_name('body')
    className = body.get_attribute('class')
    className = className.strip()
    if className != 'en_US PLAYER auth':
        return False
    login_id = browser.find_element_by_id('login-id')
    text = login_id.text
    if text != USERNAME:
        return False
    return True


def get_browser(firefox_profile):
    browser = webdriver.Firefox(firefox_profile=firefox_profile, log_path=devnull)
    return browser


def get_firefox_profile():
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.add_extension('adblock_plus.xpi')
    firefox_profile.set_preference('general.useragent.override', USER_AGENT)
    firefox_profile.set_preference('network.proxy.type', 0)
    firefox_profile.set_preference('xpinstall.signatures.required', False)
    return firefox_profile


if __name__ == '__main__':
    main(argv)

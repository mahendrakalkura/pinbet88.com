from __future__ import print_function
from csv import writer
from datetime import date, datetime
from json import loads
from os.path import devnull
from sys import argv, stdout
from time import time

from requests import request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

URLS_HOME = 'https://www.pinbet88.com/en/sports/soccer'
URLS_MATCHES = 'https://www.pinbet88.com/sports-service/sv/odds/events'
URLS_MATCH = 'http://live.pinbet88.com/live-center-service/s/match/restore/{id:d}'
USERNAME = 'CA701YT003'
PASSWORD = 'abcd1234'
TIMEOUT = 60
USER_AGENT = 'Mozilla/6.0 (X11; Linux x86_64) AppleWebKit/6.0 (KHTML, like Gecko) Chrome/6.0 Safari/6.0'

RemoteConnection._timeout = TIMEOUT


def main(options):
    if options[1] == '--matches':
        execute_matches()
        return
    if options[1] == '--match':
        execute_match(options[2])
        return
    if options[1] == '--report':
        execute_report()
        return


def execute_matches():
    contents, cookies = get_contents_and_cookies()
    if not contents:
        return
    while True:
        print('', end='')
        success = 0
        failure = 0
        while True:
            matches = get_matches(cookies)
            matches = len(matches)
            if matches:
                success = success + 1
            else:
                failure = failure + 1
            message = '\r{success:03d}/{failure:03d}'.format(success=success, failure=failure)
            print(message, end='')


def get_matches(cookies):
    matches = []
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
        pass
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


def execute_match(id):
    contents, cookies = get_contents_and_cookies()
    if not contents:
        return
    while True:
        print('', end='')
        success = 0
        failure = 0
        while True:
            match = get_match(id, cookies)
            keys = match.keys()
            keys = len(keys)
            if keys == 3:
                success = success + 1
            else:
                failure = failure + 1
            message = '\r{success:03d}/{failure:03d}'.format(success=success, failure=failure)
            print(message, end='')


def get_match(id, cookies):
    match = {}
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
        data = json['data']
        data = loads(data)
        match = data
    except Exception:
        pass
    return match


def get_contents_and_cookies():
    contents = None
    cookies = {}
    try:
        firefox_profile = get_firefox_profile()
        browser = get_browser(firefox_profile)
        browser.get(URLS_HOME)
        wait = WebDriverWait(browser, TIMEOUT)
        wait.until(condition_1)
        username = browser.find_element_by_name('loginId')
        username.send_keys(USERNAME)
        password = browser.find_element_by_name('password')
        password.send_keys(PASSWORD)
        button = browser.find_element_by_id('login')
        button.click()
        wait = WebDriverWait(browser, TIMEOUT)
        wait.until(condition_2)
        contents = browser.execute_script('return document.getElementsByTagName("html")[0].innerHTML')
        cookies = browser.get_cookies()
        cookies = {cookie['name']: cookie['value'] for cookie in cookies}
        browser.quit()
    except Exception:
        pass
    return contents, cookies


def condition_1(browser):
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


def condition_2(browser):
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
    firefox_profile.set_preference('general.useragent.override', USER_AGENT)
    firefox_profile.set_preference('network.proxy.type', 0)
    firefox_profile.set_preference('xpinstall.signatures.required', False)
    return firefox_profile


def execute_report():
    contents, cookies = get_contents_and_cookies()
    if not contents:
        return
    events = []
    matches = get_matches(cookies)
    for match in matches:
        match = get_match(match['id'], cookies)
        if 'event_list' not in match:
            continue
        event_list = match['event_list']
        if 'event' not in event_list:
            continue
        event = event_list['event']
        for e in event:
            events.append(e)
    headers = [
        'clockRunning',
        'currentPlaytime',
        'date',
        'event_code',
        'event_code_id',
        'event_number',
        'game_id',
        'minute',
        'player_in_num',
        'player_num',
        'player_out_num',
        'related_event_codes',
        'related_events',
        'score_away',
        'score_home',
        'seconds',
        'statistics',
        'team_id',
        'tickerstate',
        'tickerstate_id',
        'zone',
    ]
    rows = []
    rows.append(headers)
    for event in events:
        row = []
        for header in headers:
            r = ''
            if header in event:
                r = event[header]
            row.append(r)
        rows.append(row)
    writer(stdout).writerows(rows)


if __name__ == '__main__':
    main(argv)

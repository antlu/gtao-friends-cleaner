from time import sleep
import datetime
import webbrowser

import browser_cookie3
import requests

from constants import (
    RGSC_HOME_URL,
    PROFILE_FULL_INFO_URL,
    REQUEST_TIMEOUT,
    TOKEN_REFRESH_URL,
    SLEEP_TIME,
    FRIEND_REMOVE_URL,
    AUTH_TOKEN_PATH,
)


class TokenNotFoundError(Exception):
    pass


def get_auth_token_from_browser():
    webbrowser.open_new_tab(RGSC_HOME_URL)
    input("Press Enter when you are logged in to Social Club.")
    cookie_jar = browser_cookie3.load('socialclub.rockstargames.com')
    for cookie in cookie_jar:
        if cookie.name == 'BearerToken':
            return cookie.value
    raise TokenNotFoundError


def get_full_info(name, session):
    params = {'nickname': name}
    response = session.get(
        PROFILE_FULL_INFO_URL, params=params, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def get_full_info_with_delay(data, session):
    sleep(SLEEP_TIME)
    if isinstance(data, list):
        return map(lambda name: get_full_info_with_delay(name, session), data)
    return get_full_info(data, session)


def is_inactive_player(profile, days_of_inactivity):
    games = profile.get('gamesOwned', False)
    if not games:
        return True
    gta_info = list(filter(lambda game: game['name'] == 'GTAV', games))
    last_seen = gta_info[0]['lastSeen']  # YYYY-MM-DDT00:00:00.00 or empty
    if not last_seen:
        return True
    last_date_online = datetime.datetime.strptime(last_seen[0:10], '%Y-%m-%d').date()
    current_date = datetime.date.today()
    return (current_date - last_date_online).days >= days_of_inactivity


def refresh_auth_token(old_token):
    response = requests.post(
        TOKEN_REFRESH_URL,
        headers={'x-requested-with': 'XMLHttpRequest'},
        cookies={'BearerToken': old_token},
        data={'accessToken': old_token}
    )
    response.raise_for_status()
    return response.cookies['BearerToken']


def remove_friend(id, session):
    params = {'rockstarId': id}
    response = session.post(FRIEND_REMOVE_URL, params=params)
    response.raise_for_status()
    return response.json()  # {"status": true}


def remove_friend_with_delay(id, session):
    sleep(SLEEP_TIME)  # Avoid HTTP 429 Too Many Requests
    return remove_friend(id, session)


def ask_yes_or_no(question, default='y'):
    valid_answers = {
        'y': True,
        'n': False
    }
    prompt_values = {
        'y': '[Y/n]',
        'n': '[y/N]'
    }
    while True:
        answer = input(f"{question} {prompt_values[default]} ").lower()
        if answer == '':
            answer = default
        if answer in valid_answers:
            return valid_answers[answer]
        else:
            print("Invalid answer.")


def save_token_to_file(token):
    with open(AUTH_TOKEN_PATH, 'w', encoding='utf-8') as token_file:
        token_file.write(token)


def approximate_time_for(array):
    return round(len(array) * SLEEP_TIME / 60)


def announce_task(msg, array):
    print(
        f"{msg}. Wait.\n"
        f"(approximate time: {approximate_time_for(array)} min)"
    )


def get_valid_number(prompt=''):
    n = input(f"{prompt}: ") if prompt else input()
    while True:
        try:
            num = int(n)
        except ValueError:
            n = input("Not a number. Repeat: ")
        else:
            return num

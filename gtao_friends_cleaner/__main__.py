import os
import re
import sys

import requests

from constants import (
    PROFILE_BASIC_INFO_URL,
    REQUEST_TIMEOUT,
    CONFIG_DIR_PATH,
    AUTH_TOKEN_PATH,
)
import functions


# Create config directory
if not os.path.exists(CONFIG_DIR_PATH):
    os.mkdir(CONFIG_DIR_PATH)

# Get an auth token from file or browser
if os.path.exists(AUTH_TOKEN_PATH):
    with open(AUTH_TOKEN_PATH, encoding='utf-8') as token_file:
        auth_token = token_file.read()
else:
    auth_token = functions.get_auth_token_from_browser()

# Start the task in a session
with requests.Session() as session:
    session.headers = {
        'authorization': f'Bearer {auth_token}',
        'x-requested-with': 'XMLHttpRequest',
    }

    # Get brief account details to know the user's name
    while True:
        response = session.get(PROFILE_BASIC_INFO_URL, timeout=REQUEST_TIMEOUT)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                auth_token = functions.get_auth_token_from_browser()
                functions.save_token_to_file(auth_token)
                session.headers.update({'authorization': f'Bearer {auth_token}'})
            else:
                raise e
        else:
            acc_basic_info = response.json()['accounts'][0]['rockstarAccount']
            break

    # Get friends names
    acc_full_info = functions.get_full_info(acc_basic_info['name'], session)
    raw_brief_friends_info = acc_full_info['accounts'][0]['friends']  # has no 'lastSeen'
    friends_names = map(lambda friend: friend['name'], raw_brief_friends_info)
    friends_to_process = friends_names

    # Read friends and crews names to ignore
    ignore_list_path = os.path.join(CONFIG_DIR_PATH, 'ignore_list.txt')
    if os.path.exists(ignore_list_path):
        with open(ignore_list_path, encoding='utf-8') as ignore_list:
            # Delete empty lines and newlines
            ignored_names = filter(lambda line: line != '\n', ignore_list.readlines())
        ignored_names = list(map(lambda line: line.rstrip('\n'), ignored_names))

        # Make separate lists of names depending on sections in file
        friends_start_index = (
            ignored_names.index('[friends]') + 1 if '[friends]' in ignored_names else -1
        )
        crews_start_index = (
            ignored_names.index('[crews]') + 1 if '[crews]' in ignored_names else -1
        )
        if friends_start_index != -1 and crews_start_index != -1:
            if friends_start_index < crews_start_index:
                ignored_friends_names = ignored_names[friends_start_index:crews_start_index-1]
                ignored_crews_names = ignored_names[crews_start_index:]
            else:
                ignored_friends_names = ignored_names[friends_start_index:]
                ignored_crews_names = ignored_names[crews_start_index:friends_start_index-1]
        elif friends_start_index == -1 and crews_start_index != -1:
            ignored_crews_names = ignored_names[crews_start_index:]
        elif friends_start_index != -1 and crews_start_index == -1:
            ignored_friends_names = ignored_names[friends_start_index:]
        else:
            ignored_friends_names = ignored_names

    # Ignore whitelisted friends
    if ignored_friends_names:
        friends_to_process = filter(lambda name: name not in ignored_friends_names, friends_names)

    # Get friends full info
    friends_to_process = list(friends_to_process)
    functions.announce_task("Gathering friends info", friends_to_process)
    start_index = 0
    raw_full_friends_info = []
    while True:
        for name in friends_to_process[start_index:]:
            try:
                raw_full_friends_info.append(functions.get_full_info_with_delay(
                    name, session
                ))
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    auth_token = functions.refresh_auth_token(auth_token)
                    functions.save_token_to_file(auth_token)
                    session.headers.update({'authorization': f'Bearer {auth_token}'})
                    continue_from_name = re.search(r'[\w.-]+$', e.response.url).group()
                    start_index = friends_to_process.index(continue_from_name)
                    break
                else:
                    raise e
        else:
            break
    # Move crews to profile
    for friend in raw_full_friends_info:
        friend['accounts'][0]['rockstarAccount']['crews'] = {
            crew['crewName'] for crew in friend['accounts'][0].get('crews', set())
        }
    # Normalize the list to discard unnecessary data
    friends_list = map(
        lambda friend: friend['accounts'][0]['rockstarAccount'], raw_full_friends_info
    )

    # Ignore whitelisted crews
    # Could not be done earlier because there is no crews info at that time
    if ignored_crews_names:
        friends_to_process = list(filter(
            lambda friend: friend['crews'].isdisjoint(set(ignored_crews_names)), friends_list
        ))

    # Select friends who have been offline for a long time
    while True:
        n = functions.get_valid_number(
            "Enter the number of days to remove friends "
            "who have been offline for this time or longer"
        )
        friends_to_remove = list(filter(
            lambda friend: functions.is_inactive_player(friend, n), friends_to_process
        ))
        print(f"{len(friends_to_remove)} friend(s) will be removed.")
        if not functions.ask_yes_or_no("Change the value?", 'n'):
            break

    # Continue?
    if not functions.ask_yes_or_no("Continue?"):
        sys.exit()

    # Remove friends
    functions.announce_task("Removing friends", friends_to_remove)
    start_index = 0
    while True:
        for friend, iter_num in zip(friends_to_remove[start_index:], range(len(friends_to_remove))):
            try:
                functions.remove_friend_with_delay(friend['rockstarId'], session)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    auth_token = functions.refresh_auth_token(auth_token)
                    functions.save_token_to_file(auth_token)
                    session.headers.update({'authorization': f'Bearer {auth_token}'})
                    start_index = iter_num
                    break
                else:
                    raise e
        else:
            break

    input("Done.")

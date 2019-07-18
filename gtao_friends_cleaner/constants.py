from os import path


RGSC_HOME_URL = 'https://socialclub.rockstargames.com'
RGSC_API_URL = 'https://scapi.rockstargames.com'
PROFILE_BASIC_INFO_URL = f'{RGSC_API_URL}/profile/getbasicprofile'
PROFILE_FULL_INFO_URL = f'{RGSC_API_URL}/profile/getprofile'
FRIEND_REMOVE_URL = f'{RGSC_API_URL}/friends/remove'
TOKEN_REFRESH_URL = f'{RGSC_HOME_URL}/connect/refreshaccess'
REQUEST_TIMEOUT = 10
SLEEP_TIME = 5  # Avoid HTTP 429 Too Many Requests
CONFIG_DIR_PATH = path.join(path.expanduser('~'), '.gtao_friends_cleaner')
AUTH_TOKEN_PATH = path.join(CONFIG_DIR_PATH, 'access_token.txt')

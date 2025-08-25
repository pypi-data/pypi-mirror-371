from typing import Dict

from biolib._internal.http_client import HttpClient
from biolib.biolib_logging import logger


def exchange_username_password_for_tokens(username: str, password: str, base_url: str) -> Dict[str, str]:
    try:
        response = HttpClient.request(
            method='POST',
            url=f'{base_url}/api/user/token/',
            data={'username': username, 'password': password},
        )
    except Exception as exception:
        logger.error('Sign in with username/password failed')
        raise exception

    try:
        response_dict = response.json()
    except Exception as error:
        logger.error('Could not decode response from server as JSON')
        raise Exception(response.text) from error

    if 'access' not in response_dict or 'refresh' not in response_dict:
        raise Exception('Invalid response: missing access or refresh token')

    return {'access': response_dict['access'], 'refresh': response_dict['refresh']}

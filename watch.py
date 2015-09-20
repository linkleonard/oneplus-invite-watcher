"""
Reports the current position of a specific oneplus invite, as well as
how long the queue is.

"""
import json
import requests
import argparse
from urllib.parse import urlparse, parse_qs


PROGRAM_DESCRIPTION = (
    'Reports information about a OnePlus invite. '
    'The returned values are in the order: rank, total')
INVALID_INVITE_CODE_ERRMSG = 'invite_url does not contain an invite code, or code is invalid'  # noqa


class InvalidInviteCode(Exception):
    pass


def get_invite_data_url(code):
    """
    Returns the invite data lookup URL for the invite with the specified code.
    """
    # This value was obtained by reverse engineering the OnePlus invite
    # page. If you look at the network resources tab on Chrome, you'll
    # see that there is a request going to index.php that returns a
    # javascript function call to success_jsonpCallback. We remove all
    # the unnecessary querystring variables so that we retrieve the raw
    # json.
    return 'https://invites.oneplus.net/index.php?r=share/view&kid=' + code


def retrieve_invite_data(invite_code):
    """
    Retrieves the invite data and returns it as json.
    """
    http_response = requests.get(get_invite_data_url(invite_code))
    response = json.loads(http_response.content.decode('utf-8'))
    return response['data']


def get_data_for_invite(invite_url):
    """
    Retrieves the invite data from the invite URL and returns the data
    as a dictionary.
    """
    query_string = urlparse(invite_url)[4]
    # The query string's 'kid' key contains the invite code.
    try:
        # Its possible that we get multiple values for 'kid'. We'll just
        # take the sane option of using the first value.
        invite_code = parse_qs(query_string)['kid'][0]
    except (KeyError, IndexError):
        raise InvalidInviteCode

    return retrieve_invite_data(invite_code)


def main():
    parser = argparse.ArgumentParser(
        description=PROGRAM_DESCRIPTION)
    parser.add_argument(
        'invite_url', type=str,
        help=(
            'The URL to use to lookup the invite. It looks like: '
            'https://oneplus.net/invites?kid=[invite_code]')
        )
    args = parser.parse_args()
    try:
        data = get_data_for_invite(args.invite_url)
    except InvalidInviteCode:
        parser.error(INVALID_INVITE_CODE_ERRMSG)  # noqa

    print(data['rank'], data['total'])


if __name__ == '__main__':
    main()

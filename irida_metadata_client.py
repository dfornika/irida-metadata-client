#!/usr/bin/env python

import argparse
import json

from rauth import OAuth2Service
from urllib.parse import urlsplit

def decode_access_token(s):
    """
    Used to decode the access token.
    :param s: The input bytes.
    :return: A dictionary.
    """
    return json.loads(s.decode('utf-8'))


def join_path(base_path, path):
    if (base_path is None or base_path == ''):
        return path
    # If passed full URL like http://localhost/path, don't add on base_path
    elif (urlsplit(path).scheme != ''):
        return path
    else:
        if (path[0] == '/'):
            return base_path + path
        else:
            return base_path + '/' + path


def get(session, base_path, path):
        """
        A GET request to a particular path in IRIDA.
        :param path: The path to GET, minus the IRIDA url (e.g., '/projects').
        :return:  The result of rauth.OAuth2Service.get()
        """
        path = join_path(base_path, path)

        response = session.get(path, timeout=10)

        if (response.ok):
            return response.json()['resource']
        else:
            response.raise_for_status()


def main(args):

    base_url = args.base_url.rstrip('/')

    auth_params = {
        "data": {
            "grant_type": "password",
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "username": args.username,
            "password": args.password
        }
    }
    
    access_token_url = base_url + '/oauth/token'
    oauth_service = OAuth2Service(
        client_id=args.client_id,
        client_secret=args.client_secret,
        name="irida",
        access_token_url=access_token_url,
        base_url=base_url
    )
    token = oauth_service.get_access_token(decoder=decode_access_token, **auth_params)

    session = oauth_service.get_session(token)

    project = get(session, base_url, '/projects/' + args.project_id)
    project_samples = get(session, base_url, '/projects/' + args.project_id + '/samples')['resources']
    print(json.dumps(project_samples, indent=2))
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser("irida_metadata_client.py")
    parser.add_argument('--base-url', help="")
    parser.add_argument('--client-id', help="")
    parser.add_argument('--client-secret', help="")
    parser.add_argument('--username', help="")
    parser.add_argument('--password', help="")
    parser.add_argument('--project-id', help="")
    args = parser.parse_args()
    main(args)

# -*- coding: utf-8 -*-
"""
    flask.ext.social.providers.twitter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains the Flask-Social twitter code

    :copyright: (c) 2012 by Matt Wright.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import
from twython import Twython, TwythonError


config = {
    'id': 'twitter',
    'name': 'Twitter',
    'install': 'pip install twython',
    'base_url': 'http://api.twitter.com/1.1/',
    'request_token_url': 'https://api.twitter.com/oauth/request_token',
    'access_token_url': 'https://api.twitter.com/oauth/access_token',
    'authorize_url': 'https://api.twitter.com/oauth/authenticate',
    'consumer_key': 'EVjDQnCBVFnMYcSQoMr2xg',
    'consumer_secret': '62VFxTHg55XqU2A5AFfnEuFQdNWFAoPFSCpUirFyO0'
}


def get_api(connection, **kwargs):
    return Twython(kwargs.get('consumer_key'), kwargs.get('consumer_secret'),
                   connection.access_token, connection.secret)


def get_provider_user_id(response, **kwargs):
    return response['user_id'] if response else None


def get_connection_values(response=None, **kwargs):
    if not response:
        return None

    api = Twython(kwargs.get('consumer_key'), kwargs.get('consumer_secret'),
                  response['oauth_token'], response['oauth_token_secret'])

    user = api.verify_credentials()

    return dict(
        provider_id=config['id'],
        provider_user_id=str(user["id"]),
        access_token=response['oauth_token'],
        secret=response['oauth_token_secret'],
        display_name='@%s' % user["screen_name"],
        profile_url="http://twitter.com/%s" % user["screen_name"],
        image_url=user["profile_image_url_https"]
    )

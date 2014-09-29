from __future__ import absolute_import
from tumblpy import Tumblpy


config = {
    "id": "tumblr",
     "name": "tumblr",
     "module": "oauth_providers.tumblr",
     'install': 'pip install http://github.com/pythonforfacebook/facebook-sdk/tarball/master',
     "base_url": "http://api.tumblr.com/v2/",
     "request_token_url": "http://www.tumblr.com/oauth/request_token",
     "access_token_url": 'http://www.tumblr.com/oauth/access_token',
     "authorize_url": 'http://www.tumblr.com/oauth/authorize',
     "consumer_secret": 'Bk85Gx5P5Snr09qMwAJLRf38cGTWGItBAecHkDAPbLnNBKSb2W',
     "consumer_key": 'bNyZqBlueYpRV3fNTsYXwIhC6Y8m5bJsPM5n8qzcNqS0NRqDGI'

}

def get_api(connection, **kwargs):
    return Tumblpy(app_key=config["consumer_key"], app_secret=config["consumer_secret"],
        oauth_token=connection.access_token,oauth_token_secret=str(connection.secret))

def get_provider_user_id(response, **kwargs):
    return response['user_id'] if response else None


def get_connection_values(response, **kwargs):
    if not response:
        return None

    t = Tumblpy(app_key=config["consumer_key"], app_secret=config["consumer_secret"],
        oauth_token=response['oauth_token'],oauth_token_secret=response['oauth_token_secret'])

    blog_url = t.post('user/info')
    return dict(
        provider_id=config['id'],
        provider_user_id=str(blog_url["user"]["name"]),
        access_token=response['oauth_token'],
        secret=response['oauth_token_secret'],
        #display_name='%s %s' %(profile.first_name, profile.last_name) ,
        profile_url="N/A",
        image_url= ""
    )




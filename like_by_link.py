import http
from base64 import b64encode

from termcolor import colored

from constants import Constants
from request import Request
import requests
import json
import urllib.parse
import time
import datetime
import random

try:
    from Database.db import Account, LikeData, db, AccountStatus
except ImportError:
    from .Database.db import Account, LikeData, db, AccountStatus
try:
    from Database.user import User
except ImportError:
    from .Database.user import User
try:
    from Database.update import *
except ImportError:
    from .Database.update import *
try:
    from geography import Geo
except ImportError:
    from .geography import Geo
try:
    from session import Session
except ImportError:
    from .session import Session


class LikeByLink:

    def __init__(self, username=None, link=None, proxy=None):
        self.request = Request()
        self.session = Session(username=username, proxy=proxy)
        self.ig = User(username=username)
        self.account = self.ig.account
        self.device = self.ig.device

        self.media_id = None
        self.link = link
        self.geo = Geo(proxy=proxy)

    def save_like_data(self):
        new_like_data = LikeData(account_username=self.account.get('username'),
                                 media_id=self.media_id,
                                 created_at=datetime.datetime.now().timestamp()
                                 )
        db.session.add(new_like_data)
        db.session.commit()

    def save_account_status(self, status=None):
        new_status = AccountStatus(account_username=self.account.get('username'),
                                   status=status,
                                   created_at=datetime.datetime.now().timestamp())
        db.session.add(new_status)
        db.session.commit()

    def check_if_media_is_liked(self):
        liked_media = LikeData.query.filter_by(account_username=self.account.get('username')).all()
        for lm in liked_media:
            lm = lm.__dict__
            if self.media_id == lm.get('media_id'):
                return True
        return False

    def oembed(self):
        self.session.set_headers(auth=True)

        try:
            response = self.request.send_request(
                endpoint=Constants.API_URL1 + 'oembed/?url={}'.format(urllib.parse.quote_plus(self.link)),
                session=self.session
            )
            return response
        except Exception as e:
            print(e)
            return False

    def media_info(self):
        self.session.set_headers(auth=True)

        return self.request.send_request(endpoint=Constants.API_URL1 + 'media/{}/info/'.format(self.media_id),
                                         session=self.session
                                         )

    def media_like(self):
        self.session.set_headers(is_post=True, auth=True)
        data = {
            "inventory_source": "media_or_ad",
            "media_id": self.media_id,
            # "carousel_index": "0",
            "_csrftoken": self.account.get('csrftoken'),
            "radio_type": "wifi-none",
            "_uid": self.account.get('user_id'),
            "_uuid": self.device.get('uuid'),
            "is_carousel_bumped_post": "false",
            "container_module": "feed_short_url",
            "feed_position": "0"
        }
        double_tap = random.randint(0, 1)
        return self.request.send_request(
            endpoint=Constants.API_URL1 + 'media/{}/like/'.format(self.media_id),
            post=data,
            extra_sig="d={}".format(double_tap),
            session=self.session
        )

    def like_by_link(self):
        if not self.oembed():
            print(colored('THIS ACCOUNT IS PROBABLY BLOCKED OR BAD LINK', 'red', attrs=['bold']))
            try:
                message = self.request.last_json.get('message')
            except KeyError:
                message = 'unresponsive'
            self.save_account_status(status=message)
        else:
            self.media_id = self.request.last_json['media_id']
            if not self.media_info():
                try:
                    message = self.request.last_json.get('message')
                except KeyError:
                    message = 'unresponsive'
                self.save_account_status(status=message)

            if self.check_if_media_is_liked():
                print(colored('THIS MEDIA IS ALREADY LIKED BY THIS ACCOUNT', 'yellow', attrs=['bold']))
            else:
                try:
                    if self.media_like():
                        print(colored('LIKE ATTEMPT IS SUCCESSFUL', 'green', attrs=['bold']))
                    else:
                        raise Exception
                except Exception as e:
                    print(colored('LIKE ATTEMPT IS FAILED', 'red', attrs=['bold']))
                else:
                    self.save_like_data()
                    self.save_account_status(status='ok')
                    update_cookie(self.account.get('username'), self.request.cookie)


if __name__ == "__main__":
    users = [
        'kimbrellnedobitova',
        # 'vrienabitkova1999',
        # 'salvadorhoyt',
        # 'shajaralihanina98'
        # 'nafasathodakovskaya1999',
        # 'raznosschikovahazina',
        # 'nadejdapetuha1992'
    ]

    links = [
        'https://www.instagram.com/p/B9ooaVunGhn/?igshid=upy40c2cmctk',
        'https://www.instagram.com/p/B-Djvd1KNjG/?igshid=107c3sl02tn1u',
        # 'https://www.instagram.com/p/BoD9G_ZFVF2/?igshid=1clg1f2itf1w7',
        # 'https://www.instagram.com/p/B8mpVZ1g4oe/?igshid=114o3zb0wnlue'
        # 'https://www.instagram.com/p/B9cYMlgn0dt/?igshid=1qtbfmnvawsy3',
        # 'https://www.instagram.com/p/B6ys4NxCoG-/?igshid=4wb7ponuc0nh',
        # 'https://www.instagram.com/p/B1DdK-2BF3G/?igshid=hhgtbqeox8y'
    ]

    proxies = [
        {'http': 'http://51.15.13.145:3111', 'https': 'https://51.15.13.145:3111'},
        {'http': 'http://51.15.13.145:3112', 'https': 'https://51.15.13.145:3112'},
        {'http': 'http://51.15.13.145:3113', 'https': 'https://51.15.13.145:3113'},
        {'http': 'http://51.15.13.145:3114', 'https': 'https://51.15.13.145:3114'},
        {'http': 'http://51.15.13.145:3115', 'https': 'https://51.15.13.145:3115'},
        {'http': 'http://51.15.13.145:3116', 'https': 'https://51.15.13.145:3116'},
        {'http': 'http://51.15.13.145:3117', 'https': 'https://51.15.13.145:3117'},
        {'http': 'http://51.15.13.145:3118', 'https': 'https://51.15.13.145:3118'},
        {'http': 'http://51.15.13.145:3119', 'https': 'https://51.15.13.145:3119'},
        {'http': 'http://51.15.13.145:3120', 'https': 'https://51.15.13.145:3120'},
        {'http': 'http://51.15.13.145:3121', 'https': 'https://51.15.13.145:3121'},
        {'http': 'http://51.15.13.145:3122', 'https': 'https://51.15.13.145:3122'},
        {'http': 'http://51.15.13.145:3123', 'https': 'https://51.15.13.145:3123'}
    ]

    while True:
        username = users.pop()
        link = links.pop()
        print(username)
        print(link)


        def task():
            print(colored('Task has started', 'yellow'))
            proxy = proxies.pop()
            proxies.insert(0, proxy)
            try:
                print(username)
                fbl = LikeByLink(username=username, link=link, proxy=proxy)
            except Exception as e:
                print(colored('SOMETHING WENT WRONG', 'red'))
                time.sleep(15)
                task()
            else:
                if fbl.geo.country != 'US':
                    print('COUNTRY IS NOT US')
                    task()
                else:
                    fbl.like_by_link()
                    time.sleep(15)


        task()

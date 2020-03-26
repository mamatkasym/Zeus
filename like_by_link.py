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


class LikeByLink:

    # TODO compare these two version variables
    # 117.0.0.28.123 has X-Bloks-Version-Id = 0a3ae4c88248863609c67e278f34af44673cff300bc76add965a9fb036bd3ca3
    # 123.0.0.21.114 has X-Bloks-Version-Id": "7ab39aa203b17c94cc6787d6cd9052d221683361875eee1e1bfe30b8e9debd74
    # 117.0.0.28.123 has X-IG-WWW-Claim = hmac.AR1GHOOu2MKXw8ZJrOzMeEskLzHlUuy9BIBSoQuqPiA53aDv
    # 123.0.0.21.114 has X-Bloks-Version-Id": 0

    def __init__(self, username=None, link=None, proxy=None):
        self.request = Request()
        self.session = requests.session()
        try:
            self.ig = User(username=username)
        except Exception as e:
            print(e)
        self.account = self.ig.account
        self.device = self.ig.device
        try:
            cookies = requests.utils.cookiejar_from_dict(self.get_cookie())
        except:
            print('error is here')
        try:
            self.session.cookies = cookies
        except:
            print('cookie error')
        self.session.proxies = proxy
        self.media_id = None
        self.link = link
        self.bearer = self.set_authorization_bearer()
        try:
            self.geo = Geo(proxy=proxy)
        except:
            print('geo error')
        self.country = self.geo.country



    def get_mid(self):
        try:
            return self.session.cookies.get_dict()['mid']
        except KeyError:
            return None

    def get_sessionid(self):
        try:
            return self.session.cookies.get_dict()['sessionid']
        except KeyError:
            return None

    def get_ds_user_id(self):
        try:
            return self.session.cookies.get_dict()['ds_user_id']
        except KeyError:
            return None

    def set_authorization_bearer(self):
        bearer = dict()
        bearer['ds_user_id'] = self.get_ds_user_id()
        bearer['sessionid'] = self.get_sessionid()
        bearer = json.dumps(bearer, separators=(',', ':'))
        return b64encode(bearer.encode()).decode()

    def get_cookie(self):
        try:
            return json.loads(self.account.get('cookie'))
        except:
            str_cookie = self.account.get('cookie')
            cookies = str_cookie.split("; ")
            dict_cookie = dict()
            for c in cookies:
                k, v = c.split("=")
                dict_cookie[k] = v

            return dict_cookie

    def set_headers(self,
                    x_device=False,
                    prefetch_request=False,
                    is_post=False,
                    ):
        self.session.headers =  {}

        if x_device:
            self.session.headers['X-DEVICE-ID'] = self.device.get('uuid')
        self.session.headers['X-IG-App-Locale'] = 'en_US'
        self.session.headers['X-IG-Device-Locale'] = 'en_US'
        self.session.headers['X-IG-Mapped-Locale'] = 'en_US'
        self.session.headers['X-Pigeon-Session-Id'] = self.device.get('x_pigeon')
        self.session.headers['X-Pigeon-Rawclienttime'] = str(round(time.time(), 3))
        self.session.headers['X-IG-Connection-Speed'] = '-1kbps'
        self.session.headers['X-IG-Bandwidth-Speed-KBPS'] = str(round(random.uniform(2000,5000), 3))
        self.session.headers['X-IG-Bandwidth-TotalBytes-B'] = str(random.randint(500000, 900000))
        self.session.headers['X-IG-Bandwidth-TotalTime-MS'] = str(random.randint(200, 500))
        self.session.headers['X-IG-App-Startup-Country'] = 'US'
        if prefetch_request:
            self.session.headers['X-IG-Prefetch-Request'] = 'foreground'
        self.session.headers['X-Bloks-Version-Id'] = Constants.X_BLOKS_VERSION_ID
        self.session.headers['X-IG-WWW-Claim'] = Constants.X_IG_WWW_CLAIM
        self.session.headers['X-Bloks-Is-Layout-RTL'] = 'false'
        self.session.headers['X-Bloks-Enable-RenderCore'] = 'false'
        self.session.headers['X-IG-Device-ID'] = self.device.get('uuid')
        self.session.headers['X-IG-Android-ID'] = self.device.get('android_device_id')
        self.session.headers['X-IG-Connection-Type'] = 'WIFI'
        self.session.headers['X-IG-Capabilities'] = Constants.X_IG_CAPABILITIES
        self.session.headers['X-IG-App-ID'] = Constants.X_IG_APP_ID
        self.session.headers['User-Agent'] = self.device.get('user_agent')
        self.session.headers['Accept-Language'] = 'en-US'
        self.session.headers['Authorization'] = 'Bearer IGT:2:' + self.bearer
        self.session.headers['X-MID'] = self.get_mid()
        if is_post:
            self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.session.headers['Accept-Encoding'] = 'gzip, deflate'
        self.session.headers['Host'] = 'i.instagram.com'
        self.session.headers['X-FB-HTTP-Engine'] = 'Liger'
        self.session.headers['Connection'] = 'close'

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
        self.set_headers()

        try:
            response = self.request.send_request(
                        endpoint=Constants.API_URL1 + 'oembed/?url={}'.format(urllib.parse.quote_plus(self.link)),
                        account=self.account,
                        device=self.device,
                        session=self.session
                    )
            return response
        except:
            return False



    def media_info(self):
        self.set_headers()
        def get_response():
            response = self.request.send_request(endpoint=Constants.API_URL1 + 'media/{}/info/'.format(self.media_id),
                                                 account=self.account,
                                                 device=self.device,
                                                  session=self.session
                                                 )
            if response:
                return
            get_response()
        get_response()

    def media_like(self):
        self.set_headers(is_post=True)
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
        return     self.request.send_request(
                                            endpoint=Constants.API_URL1 + 'media/{}/like/'.format(self.media_id),
                                            post=data,
                                            extra_sig="d={}".format(double_tap),
                                            account=self.account,
                                            device=self.device,
                                            session=self.session
                                        )
    #
    # def like_flow(self):
    #     self.oembed()
    #     self.media_info()
    #     self.media_like()
    def like_by_link(self):
        if not self.oembed():
            print(colored('THIS ACCOUNT IS PROBABLY BLOCKED OR BAD LINK', 'red', attrs=['bold']))
            try:
                message = self.request.last_json.get('message')
            except:
                message = 'unresposive'
            self.save_account_status(status=message)
        else:
            self.media_id = self.request.last_json['media_id']
            self.media_info()

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


if __name__=="__main__":
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
            if fbl.country != 'US':
                print('COUNTRY IS NOT US')
                task()
            else:
                fbl.like_by_link()
                time.sleep(15)
        task()


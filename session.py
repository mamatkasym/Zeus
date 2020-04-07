import json
from base64 import b64encode

import requests
import random
import time

from signature import Signature

try:
    from Database.user import User
except ImportError:
    from .Database.user import User
try:
    from constants import Constants
except ImportError:
    from .constants import Constants


class Session(requests.Session):
    def __init__(self, username=None, proxy=None):
        super().__init__()
        self.user = User(username=username)
        self.account = self.user.account
        self.device = self.user.device
        self.proxies = proxy
        self.cookies = requests.utils.cookiejar_from_dict(self.get_account_cookie())

    def get_csrftoken(self):
        try:
            return self.cookies.get_dict()['csrftoken']
        except KeyError:
            return self.account.get('csrftoken')

    def get_mid(self):
        try:
            return self.cookies.get_dict()['mid']
        except KeyError:
            return None

    def get_sessionid(self):
        try:
            return self.cookies.get_dict()['sessionid']
        except KeyError:
            return None

    def get_ds_user_id(self):
        try:
            return self.cookies.get_dict()['ds_user_id']
        except KeyError:
            return None

    def get_authorization_bearer(self):
        bearer = dict()
        bearer['ds_user_id'] = self.get_ds_user_id()
        bearer['sessionid'] = self.get_sessionid()
        bearer = json.dumps(bearer)
        bearer = bearer.replace(' ', '')
        return b64encode(bearer.encode()).decode()

    def get_account_cookie(self):
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

    def get_cookie_string(self):
        cookie_dict = self.cookies.get_dict()
        found = ['%s=%s' % (name, value) for (name, value) in cookie_dict.items()]
        cookie_string = '; '.join(found)
        return cookie_string.strip()

    def print_headers(self):
        for k, v in self.headers.items():
            print(k + ": " + str(v))

    def set_headers(self,
                    prefix=False,
                    x_device=False,
                    prefetch_request=False,
                    is_post=False,
                    cookie=True,
                    auth=False,
                    mid=False,
                    gzip=False,
                    retry_context=False,
                    host='i.instagram.com'
                    ):
        self.headers = {}
        if prefix:
            self.headers['X-Ads-Opt-Out'] = '0'
            self.headers['X-Attribution-ID'] = Signature.generate_UUID(True) # self.device.get('attribution_id')
            self.headers['X-Google-AD-ID'] = self.device.get('advertising_id')
            self.headers['X-DEVICE-ID'] = self.device.get('uuid')
            self.headers['X-FB'] = '1'
            self.headers['X-CM-Bandwidth-KBPS'] = str(round(random.uniform(2000, 5000), 3))  # TODO
            self.headers['X-CM-Latency'] = str(round(random.uniform(8, 20), 3))  # TODO
        if x_device and not prefix:
            self.headers['X-DEVICE-ID'] = self.device.get('uuid')
        self.headers['X-IG-App-Locale'] = 'en_US'
        self.headers['X-IG-Device-Locale'] = 'en_US'
        self.headers['X-IG-Mapped-Locale'] = 'en_US'
        self.headers['X-Pigeon-Session-Id'] = self.device.get('x_pigeon')
        self.headers['X-Pigeon-Rawclienttime'] = str(round(time.time(), 3))
        self.headers['X-IG-Connection-Speed'] = '-1kbps'
        self.headers['X-IG-Bandwidth-Speed-KBPS'] = str(round(random.uniform(2000, 5000), 3))
        self.headers['X-IG-Bandwidth-TotalBytes-B'] = str(random.randint(500000, 900000))
        self.headers['X-IG-Bandwidth-TotalTime-MS'] = str(random.randint(200, 500))
        if prefetch_request:
            self.headers['X-IG-Prefetch-Request'] = 'foreground'
        self.headers['X-IG-App-Startup-Country'] = 'US'
        self.headers['X-Bloks-Version-Id'] = Constants.X_BLOKS_VERSION_ID
        self.headers['X-IG-WWW-Claim'] = Constants.X_IG_WWW_CLAIM
        self.headers['X-Bloks-Is-Layout-RTL'] = 'false'
        self.headers['X-Bloks-Enable-RenderCore'] = 'false'
        self.headers['X-IG-Device-ID'] = self.device.get('uuid')
        self.headers['X-IG-Android-ID'] = self.device.get('android_device_id')
        if retry_context:
            self.headers['retry_context'] = json.dumps(
                {"num_reupload": 0, "num_step_auto_retry": 0, "num_step_manual_retry": 0}, separators=(',', ':'))
        self.headers['X-IG-Connection-Type'] = 'WIFI'
        self.headers['X-IG-Capabilities'] = Constants.X_IG_CAPABILITIES
        self.headers['X-IG-App-ID'] = Constants.X_IG_APP_ID
        self.headers['User-Agent'] = self.device.get('user_agent')
        self.headers['Accept-Language'] = 'en-US'
        if cookie:
            self.headers['Cookie'] = self.get_cookie_string()
        if auth:
            self.headers['Authorization'] = 'Bearer IGT:2:'  + self.get_authorization_bearer()
            self.headers['X-MID'] = self.get_mid()
        if is_post:
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        if gzip:
            self.headers['Content-Encoding'] = 'gzip'
        self.headers['Accept-Encoding'] = 'gzip, deflate'

        self.headers['Host'] = host
        self.headers['X-FB-HTTP-Engine'] = 'Liger'
        self.headers['Connection'] = 'close'

if __name__ == '__main__':
    s = Session(username='consuelo_baker_688')



import json
import random
import secrets
import string
import time
import urllib.parse
import pytz
import requests

from base64 import b64encode
from datetime import datetime
from math import floor
from random import randrange
from Cryptodome.Random import get_random_bytes
from requests.adapters import HTTPAdapter
from termcolor import colored
from urllib3 import Retry

from Database.device import DeviceInfo
from Database.update import *
from constants import Constants
from request import Request
from signature import Signature


class Create:

    def __init__(self, line=None, proxy=None, user_agent=None):
        # Account information
        self.username = None
        self.email = line.split(';')[0]
        self.password = line.split(';')[1]
        self.user_id = None
        # self.fullname = names.get_full_name()
        self.fullname = self.get_full_name(line)
        self.suggested_usernames = self.set_username(line)

        self.day = str(random.randint(1, 28))
        self.month = str(random.randint(1, 12))
        self.year = str(random.randint(1970, 2004))

        # Device information
        self.device = DeviceInfo().get_device_info()
        self.user_agent = user_agent

        # Session
        self.session = self.requests_retry_session()
        self.proxy = proxy
        self.session.proxies.update(self.proxy)
        self.request = Request()

        # Other informations
        self.bearer = ''
        self.timezone = None
        self.country = None
        self.timezone_offset = self.get_timezone_offset()
        self.cookie = ''

    # ======= Functions to retrieve info from session cookie ===================================

    def get_csrftoken(self):
        try:
            return self.session.cookies.get_dict()['csrftoken']
        except:
            return None

    def get_mid(self):
        try:
            return self.session.cookies.get_dict()['mid']
        except:
            return None

    def get_rur(self):
        try:
            return self.session.cookies.get_dict()['rur']
        except:
            return None

    def get_cookie_string(self):
        return str(self.session.cookies.get_dict())

    def get_sessionid(self):
        try:
            return self.session.cookies.get_dict()['sessionid']
        except:
            return None

    def get_ds_user_id(self):
        try:
            return self.session.cookies.get_dict()['ds_user_id']
        except:
            return None

    def get_urlgen(self):
        try:
            return self.session.cookies.get_dict()['urlgen']
        except:
            return None

    def get_igfl(self):
        return self.session.cookies.get_dict()['igfl']

    def get_is_starred_enabled(self):
        return self.session.cookies.get_dict()['is_starred_enabled']

    def make_cookie(self):
        cookie = ''
        if self.get_urlgen() is not None:
            if cookie == '':
                cookie += 'urlgen=' + self.get_urlgen()
            else:
                cookie += '; urlgen=' + self.get_urlgen()

        if self.get_igfl() is not None:
            if cookie == '':
                cookie += 'igfl=' + self.get_igfl()
            else:
                cookie += '; igfl=' + self.get_igfl()

        if self.get_urlgen() is not None:
            if cookie == '':
                cookie += 'urlgen=' + self.get_urlgen()
            else:
                cookie += '; urlgen=' + self.get_urlgen()

    def set_cookie(self):
        pass

    def update_account_cookie(self):
        update_cookie(self.username, self.request.cookie)

    # ============= Utility functions =================================

    def set_headers(self,
                    x_device=False,
                    prefetch_request=False,
                    is_post=False,
                    post_create=True,
                    host='i.instagram.com'
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
        # These values seem to be constant when creating account
        self.session.headers['X-IG-Bandwidth-Speed-KBPS'] = '-1.000' # str(round(random.uniform(2000,5000), 3))
        self.session.headers['X-IG-Bandwidth-TotalBytes-B'] = '0' # str(random.randint(500000, 900000))
        self.session.headers['X-IG-Bandwidth-TotalTime-MS'] = '0'# str(random.randint(200, 500))
        if prefetch_request:
            self.session.headers['X-IG-Prefetch-Request'] = 'foreground'
        self.session.headers['X-Bloks-Version-Id'] = Constants.X_BLOKS_VERSION_ID
        if post_create:
            self.session.headers['Authorization'] = 'Bearer IGT:2' + self.bearer
            self.session.headers['X-MID'] = self.get_mid()
        self.session.headers['X-Bloks-Is-Layout-RTL'] = 'false'
        self.session.headers['X-IG-Device-ID'] = self.device.get('uuid')
        self.session.headers['X-IG-Android-ID'] = self.device.get('android_device_id')
        self.session.headers['X-IG-Connection-Type'] = 'WIFI'
        self.session.headers['X-IG-Capabilities'] = Constants.X_IG_CAPABILITIES
        self.session.headers['X-IG-App-ID'] = Constants.X_IG_APP_ID
        self.session.headers['User-Agent'] = self.user_agent
        self.session.headers['Accept-Language'] = 'en-US'
        if is_post:
            self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.session.headers['Accept-Encoding'] = 'gzip, deflate'
        self.session.headers['Host'] = host
        self.session.headers['X-FB-HTTP-Engine'] = 'Liger'
        self.session.headers['Connection'] = 'close'

    def requests_retry_session(self,
                               retries=3,
                               backoff_factor=0.3,
                               status_forcelist=(500, 502, 504),
                               ):
        session = requests.session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def account_information(self):
        print(colored('Account creation start time :', 'blue', attrs=['bold']), end=' ')
        print(colored(time.ctime().upper(), 'magenta', attrs=['bold']))
        print('PROXY :' + ' ' * (30 - len('PROXY :')) + colored(self.proxy, 'magenta'))
        print('COUNTRY :' + ' ' * (30 - len('COUNTRY :')) + colored(self.country, 'magenta'))
        print('IP ADDRESS :' + ' ' * (30 - len('IP ADDRESS :')) + colored(self.ip_adress, 'magenta'))
        print("FULLNAME :" + ' ' * (30 - len("FULLNAME :")) + colored(self.fullname, 'magenta'))
        print('USER_AGENT :' + ' ' * (30 - len('USER_AGENT :')) + colored(self.user_agent, 'magenta'))

        print()

        if self.country != 'US':
            raise print(colored('Create only US accounts', 'red', attrs=['bold']))

    def set_username(self, line):
        # suggested_usernames = []
        # username = self.fullname.replace(' ','_')
        # username = username.lower()
        # suggested_usernames.append(username)
        # return suggested_usernames

        suggested_usernames = []

        firstname = line.split(';')[2].lower()
        lastname = line.split(';')[3].lower()
        suggested_usernames.append(firstname + '_' + lastname)
        suggested_usernames.append(lastname + '_' + firstname)
        suggested_usernames.append(lastname + '.' + firstname)
        suggested_usernames.append(firstname + '.' + lastname)
        suggested_usernames.append(lastname + firstname)
        suggested_usernames.append(firstname + lastname)
        return suggested_usernames

    def is_legal_username(self, username):
        if username[-1] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
            return False
        return True

    def add_usernames(self):
        try:
            suggested_usernames = self.request.last_json['suggestions_with_metadata']['suggestions']
            for su in suggested_usernames:
                name = su['username']
                # if self.is_legal_username(name):
                self.suggested_usernames.append(name)
        except:
            pass

    def get_full_name(self, line):
        # name_surname = line.split('@')[0]
        # nm = re.findall('[A-Z][^A-Z]*', name_surname)
        # name = nm[0]
        # surname = nm[1]
        # while surname[-1] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
        #     surname = surname[:-1]
        # fullname = name + " " + surname
        # return fullname
        firstname = line.split(';')[2]
        lastname = line.split(';')[3]
        fullname = firstname + ' ' + lastname
        return fullname

    def get_timezone_offset(self):
        url = 'http://ipinfo.io/json'
        session = requests.session()
        session.proxies = self.proxy
        response = session.get(url)
        data = json.loads(response.text)
        self.ip_adress = data['ip']
        self.timezone = data['timezone']
        self.country = data['country']
        tz = pytz.timezone(self.timezone)
        d = datetime.now(tz)  # or some other local date
        utc_offset = d.utcoffset().total_seconds()

        return str(int(utc_offset))

    # def get_confirmation_code(self, EMAIL, PASSWORD):
    #     mail = imaplib.IMAP4_SSL("imap.gmail.com")
    #     mail.login(EMAIL, PASSWORD)
    #     mail.select('inbox')
    #
    #     response, data = mail.search(None, 'ALL')
    #     if data == []:
    #         time.sleep(30)
    #         return self.get_confirmation_code(EMAIL,PASSWORD)
    #
    #     mail_ids = data[0]
    #
    #     id_list = mail_ids.split()
    #     last_email_id = int(id_list[-1])
    #     (status, data) = mail.fetch(str(last_email_id), '(RFC822)')
    #     msg = email.message_from_string(data[0][1].decode())
    #
    #     if not msg['from'].startswith('"Instagram"'):
    #         print('Sleeping')
    #         time.sleep(30)
    #         return self.get_confirmation_code(EMAIL,PASSWORD)
    #
    #
    #
    #     print(msg['Subject'])
    #     code = msg['Subject'][:6]
    #     # if code == self.old_code:
    #     #     print('Sleeping')
    #     #     time.sleep(30)
    #     #     return self.get_confirmation_code(EMAIL,PASSWORD)
    #
    #     return code

    def generate_password(self):
        """Generate a random string of fixed length """
        alphabet = string.ascii_letters + string.digits
        while True:
            password = ''.join(secrets.choice(alphabet) for i in range(10))
            if (any(c.islower() for c in password)
                    and any(c.isupper() for c in password)
                    and sum(c.isdigit() for c in password) >= 3):
                break
        return password

    def get_nonce(self):
        gmail = self.email.encode()
        tm = str(floor(time.time())).encode()
        rnd = get_random_bytes(24)

        msg = gmail + b'|' + tm + b'|' + rnd

        return b64encode(msg).decode()

    def set_authorization_bearer(self):
        bearer = dict()
        bearer['ds_user_id'] = self.get_ds_user_id()
        bearer['sessionid'] = self.get_sessionid()
        bearer = json.dumps(bearer, separators=(',', ':'))
        self.bearer = b64encode(bearer.encode()).decode()

    def save_successful_create(self):

        account_rows = db.session.query(Account).count()
        new_account = Account(
            id=account_rows + 1,
            username=self.username,
            fullname=self.fullname,
            email=self.email,
            password=self.password,
            last_login=datetime.now().timestamp(),
            is_logged_in=True,
            cookie=json.dumps(self.request.last_response.cookies.get_dict()),
            user_id=self.user_id,
            timezone=self.timezone,
            csrftoken=self.get_csrftoken(),
            rur=self.get_rur(),
            sessionid=self.get_sessionid(),
            ds_user_id=self.get_ds_user_id(),
            is_from_appium=False,
        )

        db.session.add(new_account)
        db.session.commit()
        time.sleep(2)
        # device_rows = db.session.query(Device).count()
        new_device = Device(
            # id=device_rows+1,
            account_username=self.username,
            user_agent=self.user_agent,
            uuid=self.device.get('uuid'),
            android_device_id=self.device.get('android_device_id'),
            waterfall_id=self.device.get('waterfall_id'),
            advertising_id=self.device.get('advertising_id'),
            jazoest=self.device.get('jazoest'),
            phone_id=self.device.get('phone_id'),
            x_pigeon=self.device.get('x_pigeon'),
            attribution_id=self.device.get('attribution_id'),
        )
        db.session.add(new_device)
        db.session.commit()

    # ===============   PRE CREATE REQUESTS   ==============================================

    def read_msisdn_header(self):
        data = dict()
        data["mobile_subno_usage"] = 'default'
        data['device_id'] = self.device.get('uuid')
            
        self.set_headers(x_device=True,
                         is_post=True,
                         )

        return self.request.send_request(endpoint=Constants.API_URL2 + "accounts/read_msisdn_header/",
                                         post=data,
                                         device=self.device,
                                         session=self.session
                                         )

    def msisdn_header_bootstrap(self):
        data = dict()
        data["mobile_subno_usage"] = 'ig_select_app'
        data['device_id'] = self.device.get('uuid')
        
        self.set_headers(is_post=True)

        return self.request.send_request(endpoint=Constants.API_URL2 + "accounts/msisdn_header_bootstrap/",
                                         post=data,
                                         device=self.device,
                                         session=self.session
                                         )

    def log_attribution(self):
        body = dict()
        body['adid'] = self.device.get('advertising_id')
        
        self.set_headers()

        return self.request.send_request(endpoint=Constants.API_URL2 + "attribution/log_attribution/",
                                         post=body,
                                         device=self.device,
                                         session=self.session
                                         )

    def accounts_contact_point_prefill(self, token_required=False, post_create=False):

        data = dict()
        if token_required:
            data['_csrftoken'] = self.get_csrftoken()
        if post_create:
            data['_uid'] = self.user_id
            data['device_id'] = self.device.get('uuid')
            data['_uuid'] = self.device.get('uuid')
        else:
            data['phone_id'] = self.device.get('phone_id')
        data['usage'] = 'auto_confirmation' if post_create else 'prefill'

        self.set_headers(is_post=True)

        return self.request.send_request(endpoint=Constants.API_URL2 + 'accounts/contact_point_prefill/',
                                         post=data,
                                         device=self.device,
                                         session=self.session
                                         )

    def accounts_get_prefill_candidates(self, token_required=False):

        data = dict()
        data['android_device_id'] = self.device.android_device_id
        data['usages'] = "[\"account_recovery_omnibox\"]"
        data['device_id'] = self.device.get('uuid')
        if token_required:
            data['_csrftoken'] = self.get_csrftoken()

        self.set_headers(is_post=True)

        return self.request.send_request(endpoint=Constants.API_URL2 + "accounts/get_prefill_candidates/",
                                         post=data,
                                         device=self.device,
                                         session=self.session
                                         )

    def zr_token(self, post_create=False):
        data = dict()
        data['device_id'] = self.device.android_device_id
        data['token_hash'] = ''
        data['custom_device_id'] = self.device.get('uuid')
        data['fetch_reason'] = 'token_expired'

        self.set_headers()
        self.request.send_request(endpoint=Constants.API_URL2 + 'zr/token/result/',
                                  params=data,
                                  session=self.session
                                  )

    def qe_sync(self, pre_login=True, token_required=False):

        data = dict()
        if token_required:
            data['_csrftoken'] = self.get_csrftoken()
        data['id'] = self.device.get('uuid')
        data['server_config_retrieval'] = '1'
        data['experiments'] = Constants.EXPERIMENTS

        self.set_headers()

        return self.request.send_request(endpoint=API_URL + "qe/sync/",
                                         post=data,
                                         device=self.device,
                                         session=self.session
                                         )

    def launcher_sync(self, token_required=False, api_url=None):

        data = dict()
        if token_required:
            data['_csrftoken'] = self.get_csrftoken()
            host = 'i.instagram.com'
        else:
            host = 'b.i.instagram.com'
        data['id'] = self.device.get('uuid')
        data['server_config_retrieval'] = '1'

        self.set_headers(host=host,
                         is_post=True,
                         post_create=False,
                         )

        return self.request.send_request(endpoint=api_url + "launcher/sync/",
                                         post=data,
                                         device=self.device,
                                         session=self.session,
                                         )

    def check_email(self):
        body = dict()
        body['android_device_id'] = self.device.android_device_id
        body['login_nonce_map'] = str({})
        body['_csrftoken'] = self.get_csrftoken()
        body['login_nonces'] = str([])
        body['email'] = self.email
        body['qe_id'] = self.device.get('uuid')
        body['waterfall_id'] = self.device.get('waterfall_id')

        self.set_headers()

        return self.request.send_request(endpoint=Constants.API_URL1 + 'users/check_email/',
                                         post=body,
                                         device=self.device,
                                         session=self.session
                                         )

    # def send_verify_email(self):
    #     body = dict()
    #     body['phone_id'] = self.device.get('phone_id')
    #     body['_csrftoken'] = self.get_csrftoken()
    #     body['device_id'] = self.device.get('device_id')
    #     body['email'] = self.account.get('email')
    #     body['waterfall_id'] = self.device.get('waterfall_id')
    #
    #     return self.request.send_request(endpoint='accounts/send_verify_email/',
    #                                      post=body,
    #                                      account=self.account,
    #                                      device=self.device,
    #                                      session=self.session
    #                                      )

    # def check_confirmaton_code(self):
    #     body = dict()
    #     body['_csrftoken'] = self.get_csrftoken()
    #     body['code'] = self.confirmation_code
    #     body['device_id'] = self.device.android_device_id
    #     body['email'] = self.email
    #     body['waterfall_id'] = self.device.get('waterfall_id')
    #
    #     return self.request.send_request(endpoint=Constants.API_URL1 + 'accounts/check_confirmation_code/',
    #                                      post=body,
    #                                      device=self.device,
    #                                      session=self.session
    #                                      )

    def fetch_headers(self):
        param = dict()
        param['guid'] = self.device.get('uuid').replace('-', '')
        param['challenge_type'] = 'signup'

        self.set_headers()

        return self.request.send_request(endpoint=Constants.API_URL1 + 'si/fetch_headers/',
                                         params=param,
                                         session=self.session
                                         )
    #
    # def get_signup_config(self):
    #     url = dict()
    #     url['guid'] = self.device.get('uuid')
    #     url = urllib.parse.urlencode(url)
    #     return self.request.send_request(endpoint='consent/get_signup_config/?',
    #
    #                                      device=self.device,
    #                                      session=self.session
    #                                      )

    def username_suggestions(self, name):

        body = dict()
        body['phone_id'] = self.device.get('phone_id')
        body['_csrftoken'] = self.get_csrftoken()
        body['guid'] = self.device.get('uuid')
        body['name'] = name
        body['device_id'] = self.device.android_device_id
        body['email'] = self.email
        body['waterfall_id'] = self.device.get('waterfall_id')

        self.set_headers()

        return self.request.send_request(endpoint=Constants.API_URL1 + 'accounts/username_suggestions/',
                                         post=body,
                                         device=self.device,
                                         session=self.session
                                         )

    def check_username(self, username):
        body = dict()
        body['_csrftoken'] = self.get_csrftoken()
        body['username'] = username
        body['_uuid'] = self.device.get('uuid')

        self.set_headers()

        return self.request.send_request(endpoint=Constants.API_URL1 + 'users/check_username/',
                                         post=body,
                                         device=self.device,
                                         session=self.session
                                         )

    def check_age_eligibility(self):
        body = dict()
        body['_csrftoken'] = self.get_csrftoken()
        body['day'] = self.day
        body['year'] = self.year
        body['month'] = self.month

        self.set_headers()

        return self.request.send_request(endpoint=Constants.API_URL1 + 'consent/check_age_eligibility/',
                                         post=body,
                                         with_signature=False,
                                         device=self.device,
                                         session=self.session
                                         )

    def consent_new_user_flow_begins(self, ):

        data = dict()
        data['_csrftoken'] = self.get_csrftoken()
        data['device_id'] = self.device.get('uuid')

        self.set_headers()

        self.request.send_request(endpoint=Constants.API_URL1 + 'consent/new_user_flow_begins/',
                                  post=data,
                                  with_signature=True,
                                  device=self.device,
                                  session=self.session)

    def create(self):
        body = dict()
        body['is_secondary_account_creation'] = 'false'
        body['jazoest'] = self.device.get('jazoest')
        body['tos_version'] = 'row'
        body['suggestedUsername'] = ''
        # body['allow_contacts_sync'] = 'true'
        # body['enc_password'] = Signature.get_enc_password(self.password, self.public_key, self.public_key_id)
        body[
            'sn_result'] = 'eyJhbGciOiJSUzI1NiIsIng1YyI6WyJNSUlGa3pDQ0JIdWdBd0lCQWdJUkFOY1NramRzNW42K0NBQUFBQUFwYTBjd0RRWUpLb1pJaHZjTkFRRUxCUUF3UWpFTE1Ba0dBMVVFQmhNQ1ZWTXhIakFjQmdOVkJBb1RGVWR2YjJkc1pTQlVjblZ6ZENCVFpYSjJhV05sY3pFVE1CRUdBMVVFQXhNS1IxUlRJRU5CSURGUE1UQWVGdzB5TURBeE1UTXhNVFF4TkRsYUZ3MHlNVEF4TVRFeE1UUXhORGxhTUd3eEN6QUpCZ05WQkFZVEFsVlRNUk13RVFZRFZRUUlFd3BEWVd4cFptOXlibWxoTVJZd0ZBWURWUVFIRXcxTmIzVnVkR0ZwYmlCV2FXVjNNUk13RVFZRFZRUUtFd3BIYjI5bmJHVWdURXhETVJzd0dRWURWUVFERXhKaGRIUmxjM1F1WVc1a2NtOXBaQzVqYjIwd2dnRWlNQTBHQ1NxR1NJYjNEUUVCQVFVQUE0SUJEd0F3Z2dFS0FvSUJBUUNXRXJCUVRHWkdOMWlaYk45ZWhSZ2lmV0J4cWkyUGRneHcwM1A3VHlKWmZNeGpwNUw3ajFHTmVQSzVIemRyVW9JZDF5Q0l5Qk15eHFnYXpxZ3RwWDVXcHNYVzRWZk1oSmJOMVkwOXF6cXA2SkQrMlBaZG9UVTFrRlJBTVdmTC9VdVp0azdwbVJYZ0dtNWpLRHJaOU54ZTA0dk1ZUXI4OE5xd1cva2ZaMWdUT05JVVQwV3NMVC80NTIyQlJXeGZ3eGMzUUUxK1RLV2tMQ3J2ZWs2V2xJcXlhQzUyVzdNRFI4TXBGZWJ5bVNLVHZ3Zk1Sd3lLUUxUMDNVTDR2dDQ4eUVjOHNwN3dUQUhNL1dEZzhRb3RhcmY4T0JIa25vWjkyWGl2aWFWNnRRcWhST0hDZmdtbkNYaXhmVzB3RVhDdnFpTFRiUXRVYkxzUy84SVJ0ZFhrcFFCOUFnTUJBQUdqZ2dKWU1JSUNWREFPQmdOVkhROEJBZjhFQkFNQ0JhQXdFd1lEVlIwbEJBd3dDZ1lJS3dZQkJRVUhBd0V3REFZRFZSMFRBUUgvQkFJd0FEQWRCZ05WSFE0RUZnUVU2REhCd3NBdmI1M2cvQzA3cHJUdnZ3TlFRTFl3SHdZRFZSMGpCQmd3Rm9BVW1OSDRiaERyejV2c1lKOFlrQnVnNjMwSi9Tc3daQVlJS3dZQkJRVUhBUUVFV0RCV01DY0dDQ3NHQVFVRkJ6QUJoaHRvZEhSd09pOHZiMk56Y0M1d2Eya3VaMjl2Wnk5bmRITXhiekV3S3dZSUt3WUJCUVVITUFLR0gyaDBkSEE2THk5d2Eya3VaMjl2Wnk5bmMzSXlMMGRVVXpGUE1TNWpjblF3SFFZRFZSMFJCQll3RklJU1lYUjBaWE4wTG1GdVpISnZhV1F1WTI5dE1DRUdBMVVkSUFRYU1CZ3dDQVlHWjRFTUFRSUNNQXdHQ2lzR0FRUUIxbmtDQlFNd0x3WURWUjBmQkNnd0pqQWtvQ0tnSUlZZWFIUjBjRG92TDJOeWJDNXdhMmt1WjI5dlp5OUhWRk14VHpFdVkzSnNNSUlCQkFZS0t3WUJCQUhXZVFJRUFnU0I5UVNCOGdEd0FIY0E5bHlVTDlGM01DSVVWQmdJTUpSV2p1Tk5FeGt6djk4TUx5QUx6RTd4Wk9NQUFBRnZudXkwWndBQUJBTUFTREJHQWlFQTdlLzBZUnUzd0FGbVdIMjdNMnZiVmNaL21ycCs0cmZZYy81SVBKMjlGNmdDSVFDbktDQ0FhY1ZOZVlaOENDZllkR3BCMkdzSHh1TU9Ia2EvTzQxaldlRit6Z0IxQUVTVVpTNnc3czZ2eEVBSDJLaitLTURhNW9LKzJNc3h0VC9UTTVhMXRvR29BQUFCYjU3c3RKTUFBQVFEQUVZd1JBSWdFWGJpb1BiSnA5cUMwRGoyNThERkdTUk1BVStaQjFFaVZFYmJiLzRVdk5FQ0lCaEhrQnQxOHZSbjl6RHZ5cmZ4eXVkY0hUT1NsM2dUYVlBLzd5VC9CaUg0TUEwR0NTcUdTSWIzRFFFQkN3VUFBNElCQVFESUFjUUJsbWQ4TUVnTGRycnJNYkJUQ3ZwTVhzdDUrd3gyRGxmYWpKTkpVUDRqWUZqWVVROUIzWDRFMnpmNDluWDNBeXVaRnhBcU9SbmJqLzVqa1k3YThxTUowajE5ekZPQitxZXJ4ZWMwbmhtOGdZbExiUW02c0tZN1AwZXhmcjdIdUszTWtQMXBlYzE0d0ZFVWFHcUR3VWJHZ2wvb2l6MzhGWENFK0NXOEUxUUFFVWZ2YlFQVFliS3hZait0Q05sc3MwYlRTb0wyWjJkL2ozQnBMM01GdzB5eFNLL1VUcXlrTHIyQS9NZGhKUW14aStHK01LUlNzUXI2MkFuWmF1OXE2WUZvaSs5QUVIK0E0OFh0SXlzaEx5Q1RVM0h0K2FLb2hHbnhBNXVsMVhSbXFwOEh2Y0F0MzlQOTVGWkdGSmUwdXZseWpPd0F6WHVNdTdNK1BXUmMiLCJNSUlFU2pDQ0F6S2dBd0lCQWdJTkFlTzBtcUdOaXFtQkpXbFF1REFOQmdrcWhraUc5dzBCQVFzRkFEQk1NU0F3SGdZRFZRUUxFeGRIYkc5aVlXeFRhV2R1SUZKdmIzUWdRMEVnTFNCU01qRVRNQkVHQTFVRUNoTUtSMnh2WW1Gc1UybG5iakVUTUJFR0ExVUVBeE1LUjJ4dlltRnNVMmxuYmpBZUZ3MHhOekEyTVRVd01EQXdOREphRncweU1URXlNVFV3TURBd05ESmFNRUl4Q3pBSkJnTlZCQVlUQWxWVE1SNHdIQVlEVlFRS0V4VkhiMjluYkdVZ1ZISjFjM1FnVTJWeWRtbGpaWE14RXpBUkJnTlZCQU1UQ2tkVVV5QkRRU0F4VHpFd2dnRWlNQTBHQ1NxR1NJYjNEUUVCQVFVQUE0SUJEd0F3Z2dFS0FvSUJBUURRR005RjFJdk4wNXprUU85K3ROMXBJUnZKenp5T1RIVzVEekVaaEQyZVBDbnZVQTBRazI4RmdJQ2ZLcUM5RWtzQzRUMmZXQllrL2pDZkMzUjNWWk1kUy9kTjRaS0NFUFpSckF6RHNpS1VEelJybUJCSjV3dWRnem5kSU1ZY0xlL1JHR0ZsNXlPRElLZ2pFdi9TSkgvVUwrZEVhbHROMTFCbXNLK2VRbU1GKytBY3hHTmhyNTlxTS85aWw3MUkyZE44RkdmY2Rkd3VhZWo0YlhocDBMY1FCYmp4TWNJN0pQMGFNM1Q0SStEc2F4bUtGc2JqemFUTkM5dXpwRmxnT0lnN3JSMjV4b3luVXh2OHZObWtxN3pkUEdIWGt4V1k3b0c5aitKa1J5QkFCazdYckpmb3VjQlpFcUZKSlNQazdYQTBMS1cwWTN6NW96MkQwYzF0Skt3SEFnTUJBQUdqZ2dFek1JSUJMekFPQmdOVkhROEJBZjhFQkFNQ0FZWXdIUVlEVlIwbEJCWXdGQVlJS3dZQkJRVUhBd0VHQ0NzR0FRVUZCd01DTUJJR0ExVWRFd0VCL3dRSU1BWUJBZjhDQVFBd0hRWURWUjBPQkJZRUZKalIrRzRRNjgrYjdHQ2ZHSkFib090OUNmMHJNQjhHQTFVZEl3UVlNQmFBRkp2aUIxZG5IQjdBYWdiZVdiU2FMZC9jR1lZdU1EVUdDQ3NHQVFVRkJ3RUJCQ2t3SnpBbEJnZ3JCZ0VGQlFjd0FZWVphSFIwY0RvdkwyOWpjM0F1Y0d0cExtZHZiMmN2WjNOeU1qQXlCZ05WSFI4RUt6QXBNQ2VnSmFBamhpRm9kSFJ3T2k4dlkzSnNMbkJyYVM1bmIyOW5MMmR6Y2pJdlozTnlNaTVqY213d1B3WURWUjBnQkRnd05qQTBCZ1puZ1F3QkFnSXdLakFvQmdnckJnRUZCUWNDQVJZY2FIUjBjSE02THk5d2Eya3VaMjl2Wnk5eVpYQnZjMmwwYjNKNUx6QU5CZ2txaGtpRzl3MEJBUXNGQUFPQ0FRRUFHb0ErTm5uNzh5NnBSamQ5WGxRV05hN0hUZ2laL3IzUk5Ha21VbVlIUFFxNlNjdGk5UEVhanZ3UlQyaVdUSFFyMDJmZXNxT3FCWTJFVFV3Z1pRK2xsdG9ORnZoc085dHZCQ09JYXpwc3dXQzlhSjl4anU0dFdEUUg4TlZVNllaWi9YdGVEU0dVOVl6SnFQalk4cTNNRHhyem1xZXBCQ2Y1bzhtdy93SjRhMkc2eHpVcjZGYjZUOE1jRE8yMlBMUkw2dTNNNFR6czNBMk0xajZieWtKWWk4d1dJUmRBdktMV1p1L2F4QlZielltcW13a201ekxTRFc1bklBSmJFTENRQ1p3TUg1NnQyRHZxb2Z4czZCQmNDRklaVVNweHU2eDZ0ZDBWN1N2SkNDb3NpclNtSWF0ai85ZFNTVkRRaWJldDhxLzdVSzR2NFpVTjgwYXRuWnoxeWc9PSJdfQ.eyJhcGtDZXJ0aWZpY2F0ZURpZ2VzdFNoYTI1NiI6W10sImVycm9yIjoiaW50ZXJuYWxfZXJyb3IifQ.LU2sgoKrKe-F7eyqElv9_yI68hc2cEyRW0AUtu_yDnJF2IVs71Alc9QgQQMKbAmirqhzKmERaE1fMw11mj0scHiEnvPLmJ3quclnoqFbM_Mx4NpgvzOQdP-tt8e5k6-xvFHqH_AP1ox36c52N26mOuI-RLAd539X3limIVyy-wwCFFo3M3T1B6IAZi_Ew15k1fqHvOVrjIEHvajseXgV7kWhqw69kGjehkFMde-4D0yUs9Ci3zDgSUr1tls7Rbv3yOFPZPHeJqhekePpIkbRJFjA7ZFksTvZ4ggNXcWn_piDM3Xy_rJ7PuG86xQnAzTsJSAhB1twHslgjNXbrfAfOw'  # TODO
        body['phone_id'] = self.device.get('phone_id')
        body['_csrftoken'] = self.get_csrftoken()
        body['username'] = self.username
        body['first_name'] = self.fullname
        body['day'] = self.day
        body['adid'] = self.device.get('advertising_id')
        body['guid'] = self.device.get('uuid')
        body['year'] = self.year
        body['device_id'] = self.device.android_device_id
        body['_uuid'] = self.device.get('uuid')
        body['email'] = self.email
        body['month'] = self.month
        body['sn_nonce'] = self.get_nonce()
        body['force_sign_up_code'] = ''
        body['waterfall_id'] = self.device.get('waterfall_id')
        body['qs_stamp'] = ''
        body['password'] = self.password
        body['one_tap_opt_in'] = 'true'

        self.set_headers()

        return self.request.send_request(endpoint=Constants.API_URL1 + 'accounts/create/',
                                         post=body,
                                         device=self.device,
                                         session=self.session,
                                         timeout=30
                                         )

    def dynamic_onboarding_get_steps(self, post_create=False, progress_state=None, tos_accepted=None):

        data = dict()
        data['is_secondary_account_creation'] = 'false'
        data['fb_connected'] = 'false'
        if progress_state == 'finish':
            data['seen_steps'] = Constants.SEEN_STEPS
        else:
            data['seen_steps'] = '[]'
        data['progress_state'] = progress_state
        data['phone_id'] = self.device.get('phone_id')
        data['fb_installed'] = 'false'
        data['locale'] = 'en_US'
        data['timezone_offset'] = self.timezone_offset
        if progress_state != 'finish':
            data['_csrftoken'] = self.get_csrftoken()
        data['network_type'] = 'WIFI-UNKNOWN'
        if post_create:
            data['_uid'] = self.user_id
        data['guid'] = self.device.get('uuid')
        if post_create:
            data['_uuid'] = self.device.get('uuid')
        data['is_ci'] = 'false'
        data['android_id'] = self.device.android_device_id
        data['waterfall_id'] = self.device.get('waterfall_id')
        data['reg_flow_taken'] = 'email'
        data['tos_accepted'] = tos_accepted

        self.set_headers()

        self.request.send_request(endpoint=API_URL + 'dynamic_onboarding/get_steps/',
                                  post=data,
                                  session=self.session,
                                  )

    # ===============   POST CREATE REQUESTS =====================================
    def post_launcher_sync(self, host=None):

        data = dict()
        data['_csrftoken'] = self.get_csrftoken()  # 'TecVE5Z4uvu2vy87rmn2hl7c5dcZsI6k'
        data['id'] = self.user_id
        data['_uid'] = self.user_id
        data['uuid'] = self.device.get('uuid')
        data['server_config_retrieval'] = '1'

        self.set_headers()

        API_URL = Constants.API_URL2

        return self.request.send_request(endpoint=API_URL + "launcher/sync/",
                                         post=data,
                                         session=self.session,
                                         )

    def post_qe_sync(self):

        data = dict()
        data['_csrftoken'] = self.get_csrftoken()
        data['id'] = self.user_id
        data['_uid'] = self.user_id
        data['_uuid'] = self.device.get('uuid')
        data['server_config_retrieval'] = '1'
        data['experiments'] = Constants.EXPERIMENTS2

        self.set_headers()

        API_URL = Constants.API_URL2

        return self.request.send_request(endpoint=API_URL + "qe/sync/",
                                         post=data,
                                         session=self.session
                                         )

    def new_account_nux_seen(self):

        data = dict()
        data['is_fb4a_installed'] = 'false'  # TODO
        data['phone_id'] = self.device.get('phone_id')
        data['_csrftoken'] = self.get_csrftoken()
        data['_uid'] = self.user_id
        data['guid'] = self.device.get('uuid')
        data['device_id'] = self.device.android_device_id
        data['_uuid'] = self.device.get('uuid')
        data['waterfall_id'] = self.device.get('waterfall_id')

        self.set_headers()

        API_URL = Constants.API_URL2

        return self.request.send_request(endpoint=API_URL + "nux/new_account_nux_seen/",
                                         post=data,
                                         session=self.session
                                         )

    def get_account_family(self):

        self.set_headers()
        API_URL = Constants.API_URL1

        return self.request.send_request(endpoint=API_URL + "multiple_accounts/get_account_family/",
                                         session=self.session
                                         )

    def banyan_banyan(self):

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'banyan/banyan/?views=%5B%22story_share_sheet%22%2C%22threads_people_picker%22'
                               '%2C%22group_stories_share_sheet%22%2C%22reshare_share_sheet%22%5D',
            device=self.device,
            session=self.session
        )

    def broswe_feed(self):

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'igtv/browse_feed/?prefetch=1',
            device=self.device,
            session=self.session
        )

    def reels_tray(self, reason=''):
        data = dict()
        data['supported_capabilities_new'] = Constants.NEW_SUPPORTED_CAPABILITIES117
        data['reason'] = reason
        data['_csrftoken'] = self.get_csrftoken()
        data['_uuid'] = self.device.get('uuid')

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'feed/reels_tray/',
            post=data,
            with_signature=False,
            session=self.session
        )

    def feed_timeline(self, reason='cold_start_fetch'):
        data = {}
        data['feed_view_info'] = '[]'
        data['phone_id'] = self.device.get('phone_id')
        data['reason'] = reason
        data['battery_level'] = randrange(20, 100)
        data['timezone_offset'] = self.timezone_offset
        data['_csrftoken'] = self.get_csrftoken()
        data['device_id'] = self.device.get('uuid')
        data['is_pull_to_refresh'] = '0'
        data['_uuid'] = self.device.get('uuid')
        data['is_charging'] = '0'
        data['will_sound_on'] = '0'
        data['session_id'] = self.device.get('x_pigeon')
        data['bloks_versioning_id'] = '0a3ae4c88248863609c67e278f34af44673cff300bc76add965a9fb036bd3ca3'

        self.session.headers = {}
        self.session.headers['Accept'] = None
        self.session.headers['X-Ads-Opt-Out'] = '0'
        self.session.headers['X-Attribution-ID'] = self.device.get('attribution_id')
        self.session.headers['X-Google-AD-ID'] = self.device.get('advertising_id')
        self.session.headers['X-DEVICE-ID'] = self.device.get('uuid')
        self.session.headers['X-FB'] = '1'
        self.session.headers['X-CM-Bandwidth-KBPS'] = '-1.000'
        self.session.headers['X-CM-Latency'] = '81.450'  # TODO
        self.session.headers['X-IG-App-Locale'] = 'en_US'
        self.session.headers['X-IG-Device-Locale'] = 'en_US'
        self.session.headers['X-Pigeon-Session-Id'] = self.device.get('x_pigeon')
        self.session.headers['X-Pigeon-Rawclienttime'] = str(round(time.time(), 3))
        self.session.headers['X-IG-Connection-Speed'] = '-1kbps'
        self.session.headers['X-IG-Bandwidth-Speed-KBPS'] = '-1.000'
        self.session.headers['X-IG-Bandwidth-TotalBytes-B'] = '0'
        self.session.headers['X-IG-Bandwidth-TotalTime-MS'] = '0'
        self.session.headers['X-Bloks-Version-Id'] = '0a3ae4c88248863609c67e278f34af44673cff300bc76add965a9fb036bd3ca3'
        self.session.headers['Authorization'] = 'Bearer IGT:2:' + self.bearer
        self.session.headers['X-MID'] = self.get_mid()  # 'XlEeXQABAAH9SxysyqjKyBwclt0s'
        self.session.headers['X-Bloks-Is-Layout-RTL'] = 'false'
        self.session.headers['X-IG-Device-ID'] = self.device.get('uuid')
        self.session.headers['X-IG-Android-ID'] = self.device.android_device_id
        self.session.headers['X-IG-Connection-Type'] = 'WIFI'
        self.session.headers['X-IG-Capabilities'] = '3brTvwE='
        self.session.headers['X-IG-App-ID'] = '567067343352427'
        self.session.headers[
            'User-Agent'] = self.user_agent  # Instagram 117.0.0.28.123 Android (28/9; 440dpi; 1080x2135; Xiaomi; Mi 9 Lite; pyxis; qcom; en_US; 180322800)
        self.session.headers['Accept-Language'] = 'en-US'
        # self.session.headers['Cookie'] = 'mid={}; sessionid={}; csrftoken={}; rur={}; ds_user_id={}'.format(self.get_mid(), self.get_sessionid(), self.get_csrftoken(), self.get_rur(), self.get_ds_user_id())
        self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.session.headers['Content-Encoding'] = 'gzip'
        self.session.headers['Accept-Encoding'] = 'gzip, deflate'
        self.session.headers['Host'] = 'i.instagram.com'
        self.session.headers['X-FB-HTTP-Engine'] = 'Liger'
        self.session.headers['Connection'] = 'close'

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'feed/timeline/',
            post=data,
            with_signature=False,
            device=self.device,
            session=self.session
        )

    def media_blocked(self):
        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'media/blocked/',
            device=self.device,
            session=self.session
        )

    def loom_fetch_config(self):
        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'loom/fetch_config/',
            device=self.device,
            session=self.session
        )

    def news_inbox(self):
        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'news/inbox/',
            device=self.device,
            session=self.session
        )

    def linked_accounts(self):
        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'linked_accounts/get_linkage_status/',
            device=self.device,
            session=self.session
        )

    def is_eligible_for_monetization_products(self):
        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'eligibility/is_eligible_for_monetization_products/?product_types=branded_content',
            device=self.device,
            session=self.session
        )

    def scores_bootstrap_users(self):
        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'scores/bootstrap/users/?surfaces=%5B%22autocomplete_user_list%22%2C%22coefficient_besties_list_ranking%22%2C%22coefficient_rank_recipient_user_suggestion%22%2C%22coefficient_ios_section_test_bootstrap_ranking%22%2C%22coefficient_direct_recipients_ranking_variant_2%22%5D',
            device=self.device,
            session=self.session
        )

    def get_cooldowns(self):
        data = {}
        data = json.dumps(data)
        data = Signature.generate_signature_data(data)
        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'qp/get_cooldowns/?' + data,
            device=self.device,
            session=self.session
        )

    def write_supported_capabilities(self):

        data = dict()
        data['supported_capabilities_new'] = Constants.NEW_SUPPORTED_CAPABILITIES117
        data['_csrftoken'] = self.get_csrftoken()
        data['_uid'] = self.user_id
        data['_uuid'] = self.device.get('uuid')

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'creatives/write_supported_capabilities/',
            post=data,
            device=self.device,
            session=self.session
        )

    def log_resurrect_attribution(self):

        body = dict()
        body['_csrftoken'] = self.get_csrftoken()
        body['_uid'] = self.user_id
        body['adid'] = self.device.get('advertising_id')
        body['_uuid'] = self.device.get('uuid')

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'attribution/log_resurrect_attribution/',
            post=body,
            device=self.device,
            session=self.session
        )

    def store_client_push_permissions(self):

        body = dict()
        body['enabled'] = 'true'
        body['_csrftoken'] = self.get_csrftoken()
        body['device_id'] = self.device.get('uuid')
        body['_uuid'] = self.device.get('uuid')

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'notifications/store_client_push_permissions/',
            post=body,
            with_signature=False,
            device=self.device,
            session=self.session
        )

    def arlink_download_info(self):

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'users/arlink_download_info/?version_override=2.2.1',
            device=self.device,
            session=self.session
        )

    def userinfo(self, userid):

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'users/{userid}/info/'.format(userid=userid),
            device=self.device,
            session=self.session
        )

    def get_presence(self):

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'direct_v2/get_presence/',
            device=self.device,
            session=self.session
        )

    def process_contact_point_signals(self):

        body = dict()
        body["phone_id"] = self.device.get('phone_id')
        body["_csrftoken"] = self.get_csrftoken()
        body["_uid"] = self.user_id
        body["device_id"] = self.device.get('uuid')
        body["_uuid"] = self.device.get('uuid')
        body["google_tokens"] = "[]"

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'accounts/process_contact_point_signals/',
            post=body,
            device=self.device,
            session=self.session
        )

    def get_viewable_statuses(self):

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'status/get_viewable_statuses/',
            device=self.device,
            session=self.session
        )

    def qp_batch_fetch(self):

        body = dict()
        body[
            'surfaces_to_triggers'] = '{"4715":["instagram_feed_header"],"5858":["instagram_feed_tool_tip"],"5734":["instagram_feed_prompt"]}'
        body[
            'surfaces_to_queries'] = '{"4715":"Query QuickPromotionSurfaceQuery: Viewer {viewer() {eligible_promotions.trigger_context_v2(<trigger_context_v2>).ig_parameters(<ig_parameters>).trigger_name(<trigger_name>).surface_nux_id(<surface>).external_gating_permitted_qps(<external_gating_permitted_qps>).supports_client_filters(true).include_holdouts(true) {edges {client_ttl_seconds,log_eligibility_waterfall,is_holdout,priority,time_range {start,end},node {id,promotion_id,logging_data,max_impressions,triggers,contextual_filters {clause_type,filters {filter_type,unknown_action,value {name,required,bool_value,int_value,string_value},extra_datas {name,required,bool_value,int_value,string_value}},clauses {clause_type,filters {filter_type,unknown_action,value {name,required,bool_value,int_value,string_value},extra_datas {name,required,bool_value,int_value,string_value}},clauses {clause_type,filters {filter_type,unknown_action,value {name,required,bool_value,int_value,string_value},extra_datas {name,required,bool_value,int_value,string_value}},clauses {clause_type,filters {filter_type,unknown_action,value {name,required,bool_value,int_value,string_value},extra_datas {name,required,bool_value,int_value,string_value}}}}}},is_uncancelable,template {name,parameters {name,required,bool_value,string_value,color_value,}},creatives {title {text},content {text},footer {text},social_context {text},social_context_images,primary_action{title {text},url,limit,dismiss_promotion},secondary_action{title {text},url,limit,dismiss_promotion},dismiss_action{title {text},url,limit,dismiss_promotion},image.scale(<scale>) {uri,width,height}}}}}}}","5858":"Query QuickPromotionSurfaceQuery: Viewer {viewer() {eligible_promotions.trigger_context_v2(<trigger_context_v2>).ig_parameters(<ig_parameters>).trigger_name(<trigger_name>).surface_nux_id(<surface>).external_gating_permitted_qps(<external_gating_permitted_qps>).supports_client_filters(true).include_holdouts(true) {edges {client_ttl_seconds,log_eligibility_waterfall,is_holdout,priority,time_range {start,end},node {id,promotion_id,logging_data,max_impressions,triggers,contextual_filters {clause_type,filters {filter_type,unknown_action,value {name,required,bool_value,int_value,string_value},extra_datas {name,required,bool_value,int_value,string_value}},clauses {clause_type,filters {filter_type,unknown_action,value {name,required,bool_value,int_value,string_value},extra_datas {name,required,bool_value,int_value,string_value}},clauses {clause_type,filters {filter_type,unknown_action,value {name,required,bool_value,int_value,string_value},extra_datas {name,required,bool_value,int_value,string_value}},clauses {clause_type,filters {filter_type,unknown_action,value {name,required,bool_value,int_value,string_value},extra_datas {name,required,bool_value,int_value,string_value}}}}}},is_uncancelable,template {name,parameters {name,required,bool_value,string_value,color_value,}},creatives {title {text},content {text},footer {text},social_context {text},social_context_images,primary_action{title {text},url,limit,dismiss_promotion},secondary_action{title {text},url,limit,dismiss_promotion},dismiss_action{title {text},url,limit,dismiss_promotion},image.scale(<scale>) {uri,width,height}}}}}}}","5734":"Query QuickPromotionSurfaceQuery: Viewer {viewer() {eligible_promotions.trigger_context_v2(<trigger_context_v2>).ig_parameters(<ig_parameters>).trigger_name(<trigger_name>).surface_nux_id(<surface>).external_gating_permitted_qps(<external_gating_permitted_qps>).supports_client_filters(true).include_holdouts(true) {edges {client_ttl_seconds,log_eligibility_waterfall,is_holdout,priority,time_range {start,end},node {id,promotion_id,logging_data,max_impressions,triggers,contextual_filters {clause_type,filters {filter_type,unknown_action,value {name,required,bool_value,int_value,string_value},extra_datas {name,required,bool_value,int_value,string_value}},clauses {clause_type,filters {filter_type,unknown_action,value {name,required,bool_value,int_value,string_value},extra_datas {name,required,bool_value,int_value,string_value}},clauses {clause_type,filters {filter_type,unknown_action,value {name,required,bool_value,int_value,string_value},extra_datas {name,required,bool_value,int_value,string_value}},clauses {clause_type,filters {filter_type,unknown_action,value {name,required,bool_value,int_value,string_value},extra_datas {name,required,bool_value,int_value,string_value}}}}}},is_uncancelable,template {name,parameters {name,required,bool_value,string_value,color_value,}},creatives {title {text},content {text},footer {text},social_context {text},social_context_images,primary_action{title {text},url,limit,dismiss_promotion},secondary_action{title {text},url,limit,dismiss_promotion},dismiss_action{title {text},url,limit,dismiss_promotion},image.scale(<scale>) {uri,width,height}}}}}}}"}'
        body["vc_policy"] = "default"
        body["_csrftoken"] = self.get_csrftoken()
        body["_uid"] = self.user_id
        body["_uuid"] = self.device.get('uuid')
        body["scale"] = Constants.BATCH_SCALE
        body["version"] = Constants.BATCH_VERSION

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'qp/batch_fetch/',
            post=body,
            device=self.device,
            session=self.session
        )

    def push_register(self, host):
        body = dict()
        body['device_type'] = 'android_mqtt'
        body['is_main_push_channel'] = 'true'
        body['device_sub_type'] = 2
        body['device_token'] = '{}'  # TODO
        body['_csrftoken'] = self.get_csrftoken()
        body['guid'] = self.device.get('uuid')
        body['_uuid'] = self.device.get('uuid')
        body['users'] = self.user_id
        body['family_device_id'] = self.device.get('phone_id')

        self.set_headers()

        API_URL = Constants.API_URL1

        return self.request.send_request(
            endpoint=API_URL + 'push/register/',
            post=body,
            with_signature=False,
            device=self.device,
            session=self.session
        )

    def direct_v2_inbox(self):
        self.set_headers()

        API_URL = Constants.API_URL1
        return self.request.send_request(
            endpoint=API_URL + 'direct_v2/inbox/?visual_message_return_type=unseen&persistentBadging=true&limit=0',
            session=self.session
        )

    def discover(self):
        self.set_headers()


        API_URL = Constants.API_URL1

        url = {
            'is_prefetch': 'true',
            'omit_cover_media': 'true',
            'use_sectional_payload': 'true',
            'timezone_offset': self.timezone_offset,
            'session_id': self.device.get('x_pigeon'),
            'include_fixed_destinations': 'true'
        }
        url = urllib.parse.urlencode(url)
        return self.request.send_request(endpoint=API_URL + 'discover/topical_explore/?' + url,
                                         session=self.session
                                         )

    def post_create_flow(self):
        self.post_launcher_sync(host='b.i.instagram')
        self.device['x_pigeon'] = Signature.generate_UUID(True)

        self.dynamic_onboarding_get_steps(post_create=True, progress_state='start', tos_accepted='true')
        self.post_qe_sync()
        self.new_account_nux_seen()
        self.zr_token(post_create=True)
        self.accounts_contact_point_prefill(token_required=True, post_create=True)

        self.dynamic_onboarding_get_steps(progress_state='finish', tos_accepted='true')
        self.banyan_banyan()
        self.broswe_feed()
        self.reels_tray(reason='cold_start')
        self.feed_timeline()

        self.post_launcher_sync(host='i.instagram')
        self.media_blocked()
        self.get_account_family()
        self.loom_fetch_config()
        self.news_inbox()
        self.linked_accounts()
        self.get_cooldowns()
        self.write_supported_capabilities()
        self.log_resurrect_attribution()
        self.arlink_download_info()
        self.store_client_push_permissions()
        self.userinfo(userid=self.user_id)
        self.get_presence()
        self.process_contact_point_signals()
        self.get_viewable_statuses()
        self.direct_v2_inbox()
        self.qp_batch_fetch()
        self.discover()
        print('Account created successfully !')

    # =============================================================================
    def create_account(self):

        # self.account_information()
        # self.zr_token()
        # self.read_msisdn_header()
        #
        # self.msisdn_header_bootstrap()
        # self.log_attribution()
        # self.msisdn_header_bootstrap()
        self.launcher_sync(api_url=Constants.API_URL2)
        # self.accounts_contact_point_prefill() is not tested
        # self.qe_sync()  # NOTE:: if this function is called once, then the csrf token is not added to the body, but the device id is added as a header parameter
        #
        # self.accounts_get_prefill_candidates()
        #
        # time.sleep(randrange(30, 60))
        # #
        # #
        # self.check_email()
        # self.fetch_headers()
        # #
        #
        # self.username_suggestions('')
        # # self.add_usernames()
        # try:
        #     self.username = self.request.last_json['suggestions_with_metadata']['suggestions'][0]['username']
        # except:
        #     print("Could not get username")
        #     pass
        # self.fetch_headers()
        # time.sleep(2)
        # self.fetch_headers()
        # cnt = 1
        # while cnt < len(self.fullname) - 1:
        #     name = self.fullname[:cnt]
        #     self.username_suggestions(name)
        #     # self.add_usernames()
        #     cnt += random.randint(1, 2)
        #     time.sleep(random.uniform(0, 1))
        #
        # #
        # time.sleep(randrange(15, 25))
        # self.username_suggestions(self.fullname)
        # # self.add_usernames()
        # if self.username == None:
        #     try:
        #         self.username = self.request.last_json['suggestions_with_metadata']['suggestions'][0]['username']
        #     except:
        #         print("Could not get username")
        #         pass
        #
        # self.fetch_headers()
        # self.check_age_eligibility()
        # self.consent_new_user_flow_begins()
        # self.dynamic_onboarding_get_steps(progress_state='prefetch', tos_accepted='false')
        # # self.consent_new_user_flow_begins()
        #
        # # for su in self.suggested_usernames:
        # #     time.sleep(random.randint(10,20))
        # #     self.check_username(su)
        # #     if self.request.last_json['available']:
        # #         self.username = su
        # #         break
        #
        # print('USERNAME :        ' + colored(self.username, 'magenta', attrs=['bold']))
        #
        # time.sleep(randrange(2, 5))
        # try:
        #     self.create()
        #     if self.request.last_response.status_code == 200:
        #         if self.request.last_json['account_created']:
        #             # self.device.get_device_info()
        #             # print(self.username)
        #             # print(self.password)
        #             # print('Account_created_successfully !')
        #             # Session id changes after successful create
        #             self.user_id = str(self.request.last_json['created_user']['pk'])
        #             self.set_authorization_bearer()
        #             self.save_successful_create()
        #             self.post_create_flow()
        #             self.update_account_cookie()
        #         else:
        #             try:
        #                 print(colored('MESSAGE : ' + self.request.last_json['message'], 'red', attrs=['bold']))
        #             except:
        #                 print(colored('Account is not created !', 'red', attrs=['bold']))
        #
        #
        #     else:
        #         print(colored('MESSAGE : ' + self.request.last_json['message'], 'red', attrs=['bold']))
        # except:
        #     print(colored('SORRY, SOMETHING WENT WRONG', 'red', attrs=['bold']))

if __name__ == "__main__":
    proxy = {'http': 'http://192.168.0.100:1111', 'https': 'https://192.168.0.100:1111'}
    a = Create(line='sheilawilson.jj@yandex.com;UqCUEdiL7P4h9;Sheila;Wilson',proxy=proxy,user_agent='Instagram 133.0.0.32.120 Android (29/10; 444dpi; 1080x2280; Google; Pixel 4; flame; qcom; en_US; 204019456)')
    a.create_account()
# # #










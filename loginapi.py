# coding=utf8
from datetime import datetime
import json
import urllib.parse, urllib
import pytz
import requests
import random
import time

from termcolor import colored

try:
    from constants import Constants
except ImportError:
    from .constants import Constants
try:
    from request import Request
except ImportError:
    from .request import Request
try:
    from Database.update import *
except ImportError:
    from .Database.update import *
try:
    from signature import Signature
except ImportError:
    from .signature import Signature
try:
    from Database.user import User
except ImportError:
    from .Database.user import User
try:
    from Database.update import *
except ImportError:
    from .Database.update import *
try:
    from session import Session
except ImportError:
    from .session import Session
try:
    from geography import Geo
except ImportError:
    from .geography import Geo


class Login:

    def __init__(self, username=None, session=None, proxy=None):
        self.user = User(username=username)
        self.account = self.user.account
        self.device = self.user.device
        self.request = Request()
        self.public_key_id = None
        self.public_key = None
        self.target_response = None
        self.session = session if session else Session(username=username, proxy=proxy)
        self.geo = Geo(proxy=proxy)

    # =========================================================================
    def save_login_state(self):
        # SAVE SUCCESSFUL LOGIN IN DATABASE
        update_last_login(self.account.get('id'), time.time())
        update_is_logged_in(self.account.get('id'), True)

        print("Login update is saved successfully !")

    # ============ PRE LOGIN FLOW ============================================

    def zr_token(self):
        data = dict()
        data['device_id'] = self.device.get('android_device_id')
        data['token_hash'] = '[]'
        data['custom_device_id'] = self.device.get('phone_id')
        data['fetch_reason'] = 'token_expired'

        self.request.send_request(endpoint=Constants.API_URL2 + 'zr/token/result/?',
                                  params=data,
                                  session=self.session
                                  )

    def msisdn_header_bootstrap(self):
        data = dict()
        data["mobile_subno_usage"] = 'ig_select_app'
        data['device_id'] = self.device.get('uuid')

        return self.request.send_request(endpoint="accounts/msisdn_header_bootstrap/",
                                         post=data,
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def read_msisdn_header(self):
        data = dict()
        data["mobile_subno_usage"] = 'default'
        data['device_id'] = self.device.get('uuid')

        return self.request.send_request(endpoint="accounts/read_msisdn_header/",
                                         post=data,
                                         session=self.session
                                         )

    def log_attribution(self):
        body = dict()
        body['adid'] = self.device.get('advertising_id')

        return self.request.send_request(endpoint="attribution/log_attribution/",
                                         post=body,
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def qe_sync(self, pre_login=True, experiments=None, id_is_uuid=False):

        data = dict()
        data["_csrftoken"] = self.session.get_csrftoken()
        if pre_login:
            data['id'] = self.device.get('uuid')
        else:
            if id_is_uuid:
                data['id'] = self.device.get('uuid')
            else:
                data['id'] = self.account.get('user_id')
            data["_uid"] = self.account.get('user_id')
            data["_uuid"] = self.device.get('uuid')
        data['server_config_retrieval'] = '1'
        data['experiments'] = experiments

        self.session.set_headers(x_device=True, is_post=True, auth=True)

        return self.request.send_request(endpoint=Constants.API_URL1 + "qe/sync/",
                                         post=data,
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def accounts_contact_point_prefill(self):

        data = dict()
        data['phone_id'] = self.device.get('phone_id')
        data['_csrftoken'] = self.session.get_csrftoken()
        data['usage'] = 'prefill'

        return self.request.send_request(endpoint='accounts/contact_point_prefill/',
                                         post=data,
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def launcher_sync(self, pre_login=True, login_configs=False, id_is_uuid=False):

        data = dict()
        data['_csrftoken'] = self.session.get_csrftoken()
        if id_is_uuid:
            data['id'] = self.device.get('uuid')
        else:
            data['id'] = self.account.get('user_id')
        # data['server_config_retrieval'] = Constants.LAUNCHER_LOGIN_CONFIGS if login_configs else Constants.LAUNCHER_CONFIGS

        if not pre_login:
            data["_uid"] = self.account.get('user_id')
            data["_uuid"] = self.device.get('phone_id')
        data['server_config_retrieval'] = '1'

        self.session.set_headers(is_post=True, auth=True)

        return self.request.send_request(endpoint=Constants.API_URL1 + "launcher/sync/",
                                         post=data,
                                         session=self.session
                                         )

    def accounts_get_prefill_candidates(self, usage='prefill'):

        data = dict()
        data['android_device_id'] = self.device.get('android_device_id')
        data['phone_id'] = self.device.get('phone_id')
        data['usages'] = usage
        data['_csrftoken'] = self.session.get_csrftoken()
        data['device_id'] = self.device.get('android_device_id')

        return self.request.send_request(endpoint="accounts/get_prefill_candidates/",
                                         post=data,
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def pre_login_flow(self):
        if self.account is not None:
            self.zr_token()
            self.msisdn_header_bootstrap()
            self.read_msisdn_header()
            self.qe_sync()
            try:
                self.public_key = self.request.last_response.headers.get("ig-set-password-encryption-pub-key")
            except KeyError:
                pass
            try:
                self.public_key_id = self.request.last_response.headers.get("ig-set-password-encryption-key-id")
            except KeyError:
                pass

            self.msisdn_header_bootstrap()
            self.log_attribution()
            self.accounts_contact_point_prefill()
            self.launcher_sync()
            self.accounts_get_prefill_candidates()
        else:
            print("Enter account & device information")

    # ============= Login Flow ============

    def feed_timeline(self):

        body = dict()
        body["feed_view_info"] = '[]'  # TODO
        body["phone_id"] = self.device.get('phone_id')
        body["reason"] = "cold_start_fetch"
        body["battery_level"] = random.randint(40, 100)
        # body['last_unseen_ad_id'] = '' # TODO
        body["timezone_offset"] = '2600' # self.geo.timezone_offset
        body["_csrftoken"] = self.session.get_csrftoken()
        body["device_id"] = self.device.get('android_device_id')
        body["request_id"] = Signature.generate_UUID(True),
        body["is_pull_to_refresh"] = '0'
        body["_uuid"] = self.device.get('uuid')
        body["is_charging"] = '0'
        body["will_sound_on"] = '0'
        body["session_id"] = Signature.generate_UUID(True)
        body["bloks_versioning_id"] = Constants.X_BLOKS_VERSION_ID

        self.session.set_headers(is_post=True, prefix=True, gzip=True)

        return self.request.send_request(endpoint=Constants.API_URL1 + 'feed/timeline/',
                                         post=body,
                                         with_signature=False,
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def feed_reels_tray(self):
        body = dict()
        body['supported_capabilities_new'] = Constants.SUPPORTED_CAPABILITIES_NEW
        body['reason'] = 'cold_start'
        body['_csrftoken'] = self.session.get_csrftoken()
        body['_uuid'] = self.device.get('uuid')
        #        body['preloaded_reel_ids'] = '505375811,8920462506,27947232682,1829143577,667490035', # THIS IS MISSING IN MGP25'S API
        #        body['preloaded_reel_timestamp'] = '1580140337,1580138827,1580132182,1579670788,1579567381' # THIS IS MISSING IN MGP25'S API

        self.session.set_headers(is_post=True, auth=True)
        return self.request.send_request(endpoint=Constants.API_URL1 + 'feed/reels_tray/',
                                         post=body,
                                         with_signature=False,
                                         session=self.session,
                                         must_respond=True
                                         )

    def media_blocked(self):
        self.session.set_headers(auth=True)
        return self.request.send_request(endpoint=Constants.API_URL1 + 'media/blocked/',
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def news_inbox(self):
        self.session.set_headers(prefetch_request=True, auth=True)
        # param = {
        #     'mark_as_seen': 'false'
        # } # TODO
        return self.request.send_request(endpoint=Constants.API_URL1 + 'news/inbox/',
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def discover(self):
        self.session.set_headers(prefetch_request=True, auth=True)

        param = {
            'is_prefetch': 'true',
            'omit_cover_media': 'true',
            'use_sectional_payload': 'true',
            'timezone_offset': self.geo.timezone_offset,
            'session_id': self.session.get_sessionid(),
            'include_fixed_destinations': 'true'
        }
        return self.request.send_request(endpoint=Constants.API_URL1 + 'discover/topical_explore/',
                                         params=param,
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def business_eligibility(self):

        self.session.set_headers(auth=True)
        param = {
            'product_types': 'branded_content'
        }
        return self.request.send_request(
            endpoint=Constants.API_URL1 + 'business/eligibility/get_monetization_products_eligibility_data/',
            params=param,
            account=self.account,
            device=self.device,
            session=self.session)

    def multiple_accounts(self):
        self.session.set_headers(auth=True)
        return self.request.send_request(endpoint=Constants.API_URL1 + 'multiple_accounts/get_account_family/',
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def users_info(self, userid=None):
        self.session.set_headers(auth=True)
        return self.request.send_request(endpoint=Constants.API_URL1 + 'users/{userid}/info/'.format(userid=userid),
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def linked_accounts(self):
        self.session.set_headers(auth=True)
        return self.request.send_request(endpoint=Constants.API_URL1 + 'linked_accounts/get_linkage_status/',
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def banyan_banyan(self):
        param = dict()
        param[
            'views'] = '["story_share_sheet","threads_people_picker","group_stories_share_sheet","reshare_share_sheet"]'

        self.session.set_headers(auth=True)
        return self.request.send_request(
            endpoint=Constants.API_URL1 + 'banyan/banyan/',
            params=param,
            account=self.account,
            device=self.device,
            session=self.session
        )

    def log_resurrect_attribution(self):
        body = dict()
        body['_csrftoken'] = self.session.get_csrftoken()
        body['_uid'] = self.account.get('user_id')
        body['adid'] = self.device.get('advertising_id')
        body['_uuid'] = self.device.get('uuid')

        self.session.set_headers(auth=True)
        return self.request.send_request(endpoint=Constants.API_URL1 + 'attribution/log_resurrect_attribution/', post=body,
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def direct_v2_inbox(self):
        self.session.set_headers(auth=True, prefetch_request=True)
        param = {
            'visual_message_return_type': 'unseen',
            'persistentBadging': 'true',
            'limit': '0'
        }
        return self.request.send_request(endpoint=Constants.API_URL1 + 'direct_v2/inbox/',
                                         params=param,
                                         session=self.session
                                         )

    def push_register(self):
        body = dict()
        body["_csrftoken"] = self.account.get('_csrftoken')
        body["_uuid"] = self.device.get('uuid')
        body["device_sub_type"] = "2"
        body[
            "device_token"] = "{\"k\":\"eyJwbiI6ImNvbS5pbnN0YWdyYW0uYW5kcm9pZCIsImRpIjoiNjU3MmY4YWMtNDE4NC00NjY2LThmZTUtZGIxY2U4MWIzNDNmIiwiYWkiOjU2NzMxMDIwMzQxNTA1MiwiY2siOiI0MTYwMDIzODEzNjE0ODkifQ==\",\"v\":0,\"t\":\"fbns-b64\"}"
        body["device_type"] = "android_mqtt"
        body["family_device_id"] = "8fc05a56-ad3b-4327-a3b9-a93ac00a3b30"
        body["guid"] = self.device.get('uuid')
        body["is_main_push_channel"] = "true"
        body["users"] = "26438472173"

        return self.request.send_request(endpoint='push/register/', post=body, with_signature=False,
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def status(self):
        self.session.set_headers(auth=True)
        return self.request.send_request(endpoint=Constants.API_URL1 + 'status/get_viewable_statuses/',
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def get_presence(self):
        self.session.set_headers(auth=True)
        return self.request.send_request(endpoint=Constants.API_URL1 + 'direct_v2/get_presence/',
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def notifications_badge(self):
        body = dict()
        body['phone_id'] = self.device.get('phone_id')
        body['_csrftoken'] = self.session.get_csrftoken()
        body['user_ids'] = self.account.get('user_id')
        body['device_id'] = self.device.get('uuid')
        body['_uuid'] = self.device.get('uuid')

        self.session.set_headers(auth=True, is_post=True)
        return self.request.send_request(endpoint=Constants.API_URL1 + 'notifications/badge/',
                                         post=body,
                                         with_signature=False,
                                         session=self.session
                                         )

    def write_supported_capabilities(self):
        data = dict()
        data['supported_capabilities_new'] = Constants.SUPPORTED_CAPABILITIES_NEW
        data['_uuid'] = self.device.get('uuid')
        data['_uid'] = self.account.get('user_id')
        data['_csrftoken'] = self.session.get_csrftoken()

        self.session.set_headers()
        return self.request.send_request(endpoint=Constants.API_URL1 + 'creatives/write_supported_capabilities/', post=data,
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         )

    def loom_fetch(self):
        self.session.set_headers(auth=True)
        self.request.send_request(endpoint=Constants.API_URL1 + 'loom/fetch_config/',
                                  account=self.account,
                                  device=self.device,
                                  session=self.session
                                  )

    def scores_bootstrap(self):
        self.session.set_headers()

        param = dict()
        param['surfaces'] = Constants.SURFACES
        self.request.send_request(endpoint=Constants.API_URL1 + 'scores/bootstrap/users/',
                                  params=param,
                                  account=self.account,
                                  device=self.device,
                                  session=self.session
                                  )

    def qp_batch_fetch(self, surfaces_to_triggers, surfaces_to_queries):
        body = dict()
        body["surfaces_to_triggers"] = surfaces_to_triggers
        body["surfaces_to_queries"] = surfaces_to_queries
        body["vc_policy"] = "default"
        body["_csrftoken"] = self.session.get_csrftoken()
        body["_uid"] = self.account.get('user_id')
        body["_uuid"] = self.device.get('uuid')
        body["scale"] = Constants.BATCH_SCALE
        body["version"] = Constants.BATCH_VERSION

        self.session.set_headers(is_post=True)
        self.request.send_request(endpoint=Constants.API_URL1 + 'qp/batch_fetch/',
                                  post=body,
                                  session=self.session
                                  )

    def qp_get_cooldowns(self):
        data = {}
        data = json.dumps(data)
        data = Signature.generate_signature_data(data)
        self.request.send_request(endpoint=Constants.API_URL1 + 'qp/get_cooldowns/?' + data,
                                  account=self.account,
                                  device=self.device,
                                  session=self.session
                                  )

    def process_contact_point_signals(self):
        body = dict()
        body["phone_id"] = self.device.get('phone_id')
        body["_csrftoken"] = self.session.get_csrftoken()
        body["_uid"] = self.account.get('user_id')
        body["device_id"] = self.device.get('android_device_id')
        body["_uuid"] = self.device.get('uuid')
        body["google_tokens"] = "[]"
        self.session.set_headers(auth=True, is_post=True)
        self.request.send_request(endpoint=Constants.API_URL1 + 'accounts/process_contact_point_signals/',
                                  post=body,
                                  session=self.session
                                  )

    def arlink_download_info(self):
        self.session.set_headers(auth=True)
        self.request.send_request(endpoint=Constants.API_URL1 + 'users/arlink_download_info/?version_override=2.2.1',
                                  session=self.session
                                  )

    def facebook_ota(self):
        param = dict()
        param['fields'] = Constants.FACEBOOK_OTA_FIELDS
        param['custom_user_id'] = self.account.get('user_id')
        param['signed_param'] = Signature.generate_signature(')') + '.'
        param['ig_sig_key_version'] = Constants.SIG_KEY_VERSION
        param['version_code'] = Constants.VERSION_CODE
        param['version_name'] = Constants.APP_VERSION
        param['custom_app_id'] = Constants.FACEBOOK_ORCA_APPLICATION_ID
        param['custom_device_id'] = self.device.get('uuid')

        self.request.send_request(endpoint=Constants.API_URL1 + 'facebook_ota/?',
                                  params=param,
                                  session=self.session
                                  )

    def feed_reels_media(self):
        body = dict()
        body["supported_capabilities_new"] = Constants.NEW_SUPPORTED_CAPABILITIES
        body["source"] = "feed_timeline"
        body["_csrftoken"] = self.session.get_csrftoken()
        body["_uid"] = self.account.get('user_id')
        body["_uuid"] = self.device.get("uuid")
        body["user_ids"] = list({self.account.get('user_id')})

        self.request.send_request(endpoint=Constants.API_URL1 + 'feed/reels_media/', post=body,
                                  account=self.account,
                                  device=self.device,
                                  session=self.session
                                  )

    def store_client_push_permissions(self):

        body = dict()
        body["enabled"] = 'true'
        body["_csrftoken"] = self.session.get_csrftoken()
        body["device_id"] = self.device.get('device_id')
        body["_uuid"] = self.device.get("uuid")

        self.request.send_request(endpoint=Constants.API_URL1 + 'notifications/store_client_push_permissions/', post=body,
                                  with_signature=False,
                                  account=self.account,
                                  device=self.device,
                                  session=self.session
                                  )

    def igtv_browse_feed(self):
        self.session.set_headers(prefetch_request=True, auth=True)

        self.request.send_request(endpoint=Constants.API_URL1 + 'igtv/browse_feed/?prefetch=1',
                                  account=self.account,
                                  device=self.device,
                                  session=self.session
                                  )

    def branded_content(self):
        self.session.set_headers(auth=True)
        self.request.send_request(
            endpoint=Constants.API_URL1 + 'business/branded_content/should_require_professional_account/',
            session=self.session
            )

    # =======================================================================================
    def open_app(self):
        # Open the instagram application and go to main page
        # This function is called in photo upload function in 'photo' module
        print("Refresh the application session [Close and reopen your instagram app]")
        x_pigeon = Signature.generate_UUID(True)
        try:
            self.device.update({'x_pigeon': x_pigeon})
        except Exception as e:
            print(e)
        # If this endpoint response is not ok, then account may be blocked
        # so get the message and update account status
        if not self.feed_reels_tray():
            message = 'message'
            try:
                message = self.request.last_json['message']
            except Exception as e:
                print(e)
            update_account_status(self.account.get('username'), message)
            print(colored('THIS ACCOUNT IS PROBABLY BLOCKED', 'red'))
            return False

        self.feed_timeline()
        self.igtv_browse_feed()
        self.launcher_sync(pre_login=False, id_is_uuid=True)
        self.qe_sync(pre_login=False, experiments=Constants.EXPERIMENTS, id_is_uuid=True)
        self.launcher_sync(pre_login=False)
        self.qe_sync(pre_login=False, experiments=Constants.EXPERIMENTS2)
        self.media_blocked()
        self.qp_batch_fetch(Constants.SURFACES_TO_TRIGGERS1, Constants.SURFACES_TO_QUERIES1)
        self.banyan_banyan()
        self.branded_content()
        self.news_inbox()
        self.arlink_download_info()
        # self.process_contact_point_signals() # TODO 429 response
        self.business_eligibility()
        self.multiple_accounts()
        self.scores_bootstrap()
        self.banyan_banyan()
        self.status()
        self.users_info(userid=self.account.get('user_id'))
        self.get_presence()
        self.discover()
        self.direct_v2_inbox()
        self.loom_fetch()
        self.notifications_badge()

        # Save your application session information
        self.save_login_state()
        # Update the x_pigeon of the application so that
        # the same x_pigeon can be used in other classes
        update_x_pigeon(self.account.get('username'), x_pigeon)

        return True


    def login_flow(self, just_logged_in, app_refresh_interval=3):

        # If user is just logged in then make sure that all login API flow is performed successfully
        if just_logged_in:
            self.multiple_accounts()
            self.launcher_sync(pre_login=True)
            self.qe_sync(pre_login=False)
            self.feed_timeline()
            self.igtv_browse_feed()
            self.feed_reels_tray()
            self.launcher_sync(pre_login=True, login_configs=True)
            self.feed_reels_media()
            self.news_inbox()
            #        self.business_eligibility()
            self.log_attribution()
            self.loom_fetch()
            self.scores_bootstrap()
            self.users_info(self.account.get('user_id'))
            self.linked_accounts()
            self.write_supported_capabilities()
            self.media_blocked()
            self.store_client_push_permissions()
            self.qp_get_cooldowns()
            self.discover()
            self.qp_batch_fetch(Constants.SURFACES_TO_TRIGGERS1, Constants.SURFACES_TO_QUERIES1)
            #           self.process_contact_point_signals()
            self.arlink_download_info()
            self.banyan_banyan()
            self.get_presence()
            self.direct_v2_inbox()
            self.notifications_badge()
            self.facebook_ota()

            self.save_login_state()
            print("You logged in successfully !")

        else:
            print("YOU ALREADY LOGGED IN")
            # GET USER'S LAST LOGIN TIME
            last_login_time = self.account.get('last_login')

            # CHECK USER'S SESSION IS EXPIRED
            is_session_expired = (last_login_time is None) or (
                    time.time() - last_login_time) > app_refresh_interval
            if is_session_expired:

                # update app's session id when user closes and re opens the app
                print("Refresh the application session [Close and reopen your instagram app]")
                x_pigeon = Signature.generate_UUID(True)
                try:
                    self.device.update({'x_pigeon': x_pigeon})
                except Exception as e:
                    print(e)
                # If this endpoint response is not ok, then account may be blocked
                # so get the message and update account status
                if not self.feed_reels_tray():
                    message = 'message'
                    try:
                        message = self.request.last_json['message']
                    except Exception as e:
                        print(e)
                    update_account_status(self.account.get('username'), message)
                    print(colored('THIS ACCOUNT IS PROBABLY BLOCKED', 'red'))
                    return False

                self.feed_timeline()
                self.igtv_browse_feed()
                self.launcher_sync(pre_login=False, id_is_uuid=True)
                self.qe_sync(pre_login=False, experiments=Constants.EXPERIMENTS, id_is_uuid=True)
                self.launcher_sync(pre_login=False)
                self.qe_sync(pre_login=False, experiments=Constants.EXPERIMENTS2)
                self.media_blocked()
                self.qp_batch_fetch(Constants.SURFACES_TO_TRIGGERS1, Constants.SURFACES_TO_QUERIES1)
                self.banyan_banyan()
                self.branded_content()
                self.news_inbox()
                self.business_eligibility()
                self.multiple_accounts()
                self.scores_bootstrap()
                self.banyan_banyan()
                self.status()
                self.users_info(userid=self.account.get('user_id'))
                self.get_presence()
                self.discover()
                self.direct_v2_inbox()
                self.loom_fetch()
                self.notifications_badge()

                # Save your application session information
                self.save_login_state()
                # Update the x_pigeon of the application so that
                # the same x_pigeon can be used in other classes
                update_x_pigeon(self.account.get('username'), x_pigeon)

                return True

            else:
                print("Your app is open")
                return True

    # ====================== Login ==============================================================
    #    'force_login' is used to re login when the 'login session' is expired [ which is expected approximately in 1 year ]
    #    'app_refresh_interval' is used to refresh app session, which is equal to 3600 seconds = 1 hours ( in our case,
    #    it can be changed to any interval )
    def login(self, force_login=False, app_refresh_interval=3600):

        if self.account is None:
            raise Exception("User does not exist ! Invalid username !")

        # if the user is logged in already then use the login cookie to authenticate
        if self.account.get('is_logged_in'):
            cookies = requests.utils.cookiejar_from_dict(json.loads(self.account.get('cookie')))
            self.session.cookies = cookies

        # check if the user is already logged in or is the login session expired
        if not self.account.get('is_logged_in') or force_login:
            self.pre_login_flow()

            data = dict()
            data['jazoest'] = self.account.get('jazoest')
            data['country_codes'] = [{"country_code": "1", "source": ["default"]}]
            data['enc_password'] = Signature.get_enc_password(self.account['password'], self.public_key_id,
                                                              self.public_key)
            data['_csrftoken'] = self.session.get_csrftoken()
            data['username'] = self.account.get('username')
            data['adid'] = self.device.get('uuid')
            data['guid'] = self.device.get('uuid')
            data['device_id'] = self.device.get('android_device_id')
            data['google_tokens'] = '[]'
            data['password'] = self.account.get('password')
            data['login_attempt_count'] = '0'

            if self.request.send_request(endpoint="accounts/login/",
                                         post=data,
                                         account=self.account,
                                         device=self.device,
                                         session=self.session
                                         ):
                user_id = self.request.last_json['logged_in_user']['pk']
                update_user_id(self.account.get('id'), user_id)  # SET USER ID IN DATABASE
                update_token(self.account.get('id'), self.request.last_response.cookies.get_dict().get('csrftoken'))
                update_cookie(self.account.get('id'), json.dumps(self.request.last_response.cookies.get_dict()))

                self.login_flow(just_logged_in=True)
                return True
        else:
            return self.login_flow(False)


if __name__ == "__main__":
    try:
        l = Login('ainura.bolotbek', proxy={'http': 'http://192.168.0.102:1111', 'https': 'https://192.168.0.102:1111'})
        l.open_app()

    except Exception as e:
        print(e)

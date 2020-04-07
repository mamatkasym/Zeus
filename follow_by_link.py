import random

from termcolor import colored

from Database.user import User
from constants import Constants
from request import Request

try:
    from Database.update import *
except ImportError:
    from .Database.update import *
try:
    from signature import Signature
except ImportError:
    from .signature import Signature
try:
    from geography import Geo
except ImportError:
    from .geography import Geo
try:
    from session import Session
except ImportError:
    from .session import Session    


class Follow:

    def __init__(self, username=None, link=None, proxy=None):
        self.user = User(username=username)
        self.account = self.user.account
        self.device = self.user.device
        self.session = Session(username=username, proxy=proxy)
        self.request = Request()
        self.client_username = link.split('?')[0].split('/')[3]
        self.client_id = None
        self.x_pigeon = Signature.generate_UUID(True)
        self.geo = Geo(proxy=proxy)

    def users_info(self):

        self.session.set_headers(auth=True)
        self.request.send_request(
            endpoint=Constants.API_URL1 + 'users/{client_username}/usernameinfo/?from_module=deep_link_util'.format(
                client_username=self.client_username),
            account=self.account,
            device=self.device,
            session=self.session
        )

    def feed_reels_media(self):
        self.session.set_headers(auth=True, is_post=True)

        body = dict()
        body["supported_capabilities_new"] = Constants.NEW_SUPPORTED_CAPABILITIES
        body["source"] = "profile"
        body["_csrftoken"] = self.account.get('csrftoken')
        body["_uid"] = self.account.get('user_id')
        body["_uuid"] = self.device.get("uuid")
        body["user_ids"] = list('highlight:17958815605168824')  # TODO

        self.request.send_request(endpoint=Constants.API_URL1 + 'feed/reels_media/',
                                  post=body,
                                  session=self.session
                                  )

    def get_invite_suggestions(self):
        body = dict()
        body['count_only'] = '1'
        body['_csrftoken'] = self.account.get('csrftoken')
        body['_uuid'] = self.device.get('uuid')

        self.session.set_headers(is_post=True, auth=True)

        return self.request.send_request(endpoint=Constants.API_URL1 + "fb/get_invite_suggestions/",
                                         post=body,
                                         with_signature=False,
                                         session=self.session
                                         )

    def qp_batch_fetch(self):
        body = dict()
        body["surfaces_to_triggers"] = Constants.SURFACES_TO_TRIGGERS_OTHER_PROFILE_PAGE
        body["surfaces_to_queries"] = Constants.SURFACES_TO_QUERIES_OTHER_PROFILE_PAGE
        body["vc_policy"] = "default"
        body["_csrftoken"] = self.account.get('csrftoken')
        body["_uid"] = self.account.get('user_id')
        body["_uuid"] = self.device.get('uuid')
        body["scale"] = Constants.BATCH_SCALE
        body["version"] = Constants.BATCH_VERSION

        self.session.set_headers(is_post=True, auth=True)

        self.request.send_request(endpoint=Constants.API_URL1 + 'qp/batch_fetch/',
                                  post=body,
                                  session=self.session
                                  )

    def feed_user(self, max_id=None):
        param = dict()
        param['exclude_comment'] = 'true'
        if not max_id:
            param['max_id'] = max_id
        param['only_fetch_first_carousel_media'] = 'false'
        self.session.set_headers(auth=True)
        self.request.send_request(endpoint=Constants.API_URL1 + 'feed/user/{}/'.format(self.client_id),
                                  params=param,
                                  session=self.session
                                  )

    def highlights(self):
        param = dict()
        param['supported_capabilities_new'] = Constants.NEW_SUPPORTED_CAPABILITIES117
        param['phone_id'] = self.device.get('phone_id')
        param['battery_level'] = random.randint(30, 100)
        param['is_charging'] = '0'
        param['will_sound_on'] = '0'

        self.session.set_headers(prefix=True, auth=True)
        self.request.send_request(endpoint=Constants.API_URL1 + 'highlights/{client_id}/highlights_tray/?'.format(
            client_id=self.client_id),
                                  params=param,
                                  session=self.session
                                  )

    def feed_user_story(self):
        param = dict()
        param['supported_capabilities_new'] = Constants.NEW_SUPPORTED_CAPABILITIES117
        self.session.set_headers(auth=True)
        self.request.send_request(
            endpoint=Constants.API_URL1 + 'feed/user/{client_id}/story/'.format(client_id=self.client_id),
            params=param,
            session=self.session
        )

    def create_friendship(self):
        body = dict()
        body['_csrftoken'] = self.account.get('csrftoken')
        body['user_id'] = self.client_id
        body['radio_type'] = 'wifi-none'
        body['_uid'] = self.account.get('user_id')
        body['device_id'] = self.device.get('android_device_id')
        body['_uuid'] = self.device.get('uuid')

        self.session.set_headers(is_post=True, auth=True)
        self.request.send_request(
            endpoint=Constants.API_URL1 + 'friendships/create/{client_id}/'.format(client_id=self.client_id),
            post=body,
            session=self.session)

    def discover_chaining(self):
        param = dict()
        param['target_id'] = self.client_id
        self.session.set_headers(auth=True)
        self.request.send_request(endpoint=Constants.API_URL1 + 'discover/chaining/',
                                  params=param,
                                  session=self.session)

    def friendships_show(self):
        self.session.set_headers(auth=True)
        self.request.send_request(Constants.API_URL1 + 'friendships/show/{}/'.format(self.client_id),
                                  session=self.session)

    def follow_by_link(self):
        self.get_invite_suggestions()  # TODO
        self.qp_batch_fetch()  # Done
        self.users_info()  # Done
        self.client_id = self.request.last_json['user']['pk']
        self.friendships_show()  # Done
        self.feed_user()  # Done
        try:
            max_id = self.request.last_json['items'][0]['id']
        except Exception as e:
            print(e)
        else:
            self.feed_user(max_id=max_id)
        self.highlights()  # Done
        self.feed_user_story()  # Done
        # self.feed_reels_media() # TODO
        self.create_friendship()  # Done
        self.discover_chaining()  # Done
        print(colored(self.client_username + ' is now followed by ' + self.account.get('username'), 'yellow',
                      attrs=['bold']))

        # Update account cookie
        update_cookie(self.account.get('username'), self.request.cookie)


if __name__ == "__main__":
    link = "https://instagram.com/akzhol_makhmudov?igshid=1widv7x46l29k"
    f = Follow('ainura.bolotbek',
               link=link) #, proxy = {'http': 'http://192.168.0.102:1111', 'https': 'https://192.168.0.102:1111'})
    # f.feed_user_story()

    f.follow_by_link()

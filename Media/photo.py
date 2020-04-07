# coding=utf8
import imghdr
import random
import struct
import time
import os
import PIL

import requests
import json

# PERFORM BOTH RELATIVE AND ABSOLUTE IMPORTS ( YOU CAN CAN CHANGE IF YOU HAVE BETTER SOLUTION )
from termcolor import colored

try:
    from constants import Constants
except ImportError:
    from ..constants import Constants
try:
    from geography import Geo
except ImportError:
    from ..geography import Geo
try:
    from loginapi import Login
except ImportError:
    from ..loginapi import Login
try:
    from request import Request
except ImportError:
    from ..request import Request
try:
    from signature import Signature
except ImportError:
    from ..signature import Signature
try:
    from Database.user import User
except ImportError:
    from ..Database.user import User
try:
    from Database.update import *
except ImportError:
    from ..Database.update import *
try:
    from session import Session
except ImportError:
    from ..session import Session


class Photo:
    def __init__(self, username=None, proxy=None):

        self.user = User(username=username)
        self.account = self.user.account
        self.device = self.user.device
        self.request = Request()
        self.session = Session(username=username, proxy=proxy)

        self.login = Login(username=username, session=self.session , proxy=proxy)
        self.geo = Geo(proxy=proxy)

        self.username = username
        self.upload_id = None

    def reload_user(self, username=None):
        self.user = User(username)
        self.account = self.user.account
        self.device = self.user.device

    # ========== UTILITY FUNCTIONS ==========================

    def get_device_details(self):
        device_details = self.device.get('user_agent')
        device_details = device_details.split('; ')
        device = {
            'manufacturer': device_details[3],
            'model': device_details[4],
            'android_version': int(device_details[0].split('/')[0][-2:]),
            'android_release': device_details[0].split('/')[1]
        }
        return device

    def get_path_to_photo(self):
        try:
            path_to_photo_list = os.listdir(os.getcwd() + '/Data/Photos/')

            def get_path_to_photo():
                path_to_photo = path_to_photo_list.pop()
                if (not path_to_photo.endswith('jpg')) and (not path_to_photo.endswith('jpeg')):
                    return get_path_to_photo()
                return path_to_photo

            path_to_photo = os.getcwd() + '/Data/Photos/' + get_path_to_photo()
        except Exception as e:
            raise Exception
        print(path_to_photo)
        return path_to_photo

    def check_supportibilty(self, path_to_photo):
        try:
            self.get_image_size(path_to_photo)
            return path_to_photo
        except Exception:
            os.remove(path_to_photo)
            print(colored('PLEASE CHOOSE ANOTHER PHOTO', 'red'))
            new_path_to_photo = self.get_path_to_photo()
            return self.check_supportibilty(new_path_to_photo)

    # ================= PRE UPLOAD REQUESTS ============================================
    def get_profile_page(self):
        # OPEN THE APP OR LOGIN AGAIN IN ORDER TO CHANGE PROFILE PHOTO
        # before getting prfile page
        # ( We use 'loginapi' module to do this )
        self.login.login(False)

        time.sleep(random.randint(4, 10))  # TODO

        self.reload_user(self.username)

        # Go to profile page
        # self.ig_query() # TODO
        self.feed_user_story(1)
        self.feed_user_story(2)
        self.profile_su_badge()
        self.users_info(self.account.get('user_id'))
        self.qp_batch_fetch()
        self.highlights()
        self.profile_archive_badge()
        self.get_invite_suggestions()

    def ig_query(self): # TODO
        data = dict()
        data['doc_id'] = '2615360401861024' # TODO
        data['locale'] = 'en_US'
        data['vc_policy'] = 'default'
        data['signed_body'] = Signature.generate_signature('')
        data['ig_sig_key_version'] = '4'
        data['strip_nulls'] = 'true'
        data['strip_defaults'] = 'true'
        data['query_params'] = ''

        print(data['signed_body'])

        self.session.headers = dict()
        self.session.headers['X-IG-Connection-Type'] = 'WIFI'
        self.session.headers['X-IG-Capabilities'] = '3brTvwE='
        self.session.headers['X-IG-App-ID'] = '567067343352427'
        self.session.headers['User-Agent'] = self.device.get('user_agent')
        self.session.headers['Accept-Language'] = 'en-US'
        self.session.headers['Cookie'] = self.session.get_cookie_string()
        self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.session.headers['Accept-Encoding'] = 'gzip, deflate'
        self.session.headers['Host'] = 'i.instagram.com'
        self.session.headers['X-FB-HTTP-Engine'] = 'Liger'
        self.session.headers['Connection'] = 'close'

        self.request.send_request(
            endpoint=Constants.API_URL1 + 'wwwgraphql/ig/query/',
            post=data,
            with_signature=False,
            session=self.session)

    def feed_user_story(self, version):
        param = dict()
        if version == 1:
            param['supported_capabilities_new'] = Constants.NEW_SUPPORTED_CAPABILITIES117 # TODO
        else:
            param['exclude_comment'] = 'true'
            param['only_fetch_first_carousel_media'] = 'false'

        self.session.set_headers()
        self.request.send_request(
            endpoint=Constants.API_URL1 + 'feed/user/{}/story/'.format(self.account.get('user_id')),
            params=param,
            session=self.session)

    def profile_su_badge(self):
        self.session.set_headers()
        data = dict()
        data['_csrftoken'] = self.session.get_csrftoken()
        data['_uuid'] = self.device.get('uuid')

        self.request.send_request(endpoint=Constants.API_URL1 + 'discover/profile_su_badge/',
                                  post=data,
                                  with_signature=False,
                                  session=self.session)

    def users_info(self, userid=None):
        self.session.set_headers()
        return self.request.send_request(
            endpoint=Constants.API_URL1 + 'users/{}/info/?from_module=self_profile'.format(userid),
            session=self.session
        )

    def qp_batch_fetch(self):
        body = dict()
        body["surfaces_to_triggers"] = Constants.SURFACES_TO_TRIGGERS_SELF_PROFILE
        body["surfaces_to_queries"] = Constants.SURFACES_TO_QUERIES_SELF_PROFILE
        body["vc_policy"] = "default"
        body["_csrftoken"] = self.session.get_csrftoken()
        body["_uid"] = self.account.get('user_id')
        body["_uuid"] = self.device.get('uuid')
        body["scale"] = Constants.BATCH_SCALE
        body["version"] = Constants.BATCH_VERSION

        self.session.set_headers(is_post=True, auth=True)

        self.request.send_request(endpoint=Constants.API_URL1 + 'qp/batch_fetch/',
                                  post=body,
                                  session=self.session
                                  )

    def highlights(self):
        body = dict()
        body['supported_capabilities_new'] = Constants.NEW_SUPPORTED_CAPABILITIES117
        body['phone_id'] = self.device.get('phone_id')
        body['battery_level'] = random.randint(30, 100)
        body['is_charging'] = '0'
        body['will_sound_on'] = '0'

        self.session.set_headers(prefix=True)
        self.request.send_request(
            endpoint=Constants.API_URL1 + 'highlights/{}/highlights_tray/'.format(self.account.get('user_id')),
            params=body,
            session=self.session
        )

    def profile_archive_badge(self):
        body = dict()
        body['timezone_offset'] = self.geo.timezone_offset
        body['_csrftoken'] = self.session.get_csrftoken()
        body['_uuid'] = self.device.get('uuid')

        self.session.set_headers()
        self.request.send_request(endpoint=Constants.API_URL1 + 'archive/reel/profile_archive_badge/',
                                  post=body,
                                  with_signature=False,
                                  session=self.session
                                  )

    def get_invite_suggestions(self):
        body = dict()
        body['count_only'] = '1'
        body['_csrftoken'] = self.session.get_csrftoken()
        body['_uuid'] = self.device.get('uuid')

        self.session.set_headers(is_post=True)

        return self.request.send_request(endpoint=Constants.API_URL1 + "fb/get_invite_suggestions/",
                                         post=body,
                                         with_signature=False,
                                         session=self.session
                                         )

    def location_search(self):
        param = dict()
        param['latitude'] = self.geo.latitude
        param['rankToken'] = Signature.generate_UUID(True)  # TODO
        param['longitude'] = self.geo.longitude
        self.session.set_headers(auth=True)
        return self.request.send_request(endpoint=Constants.API_URL1 + "location_search/",
                                         params=param,
                                         session=self.session
                                         )

    def get_upload_photo(self, upload_id, some_number, waterfall_id):

        rupload_params = {
            "upload_id": upload_id,
            # "retry_context": '{"num_step_auto_retry":0,"num_reupload":0,"num_step_manual_retry":0}',
            "media_type": "1",
            # "xsharing_user_ids": "[]",
            "image_compression": json.dumps(
                {"lib_name": "moz", "lib_version": "3.1.m", "quality": "81"}, separators=(',', ':')
            ),
        }
        upload_name = "{upload_id}_0_{rand}".format(
            upload_id=upload_id, rand=some_number
        )

        self.session.headers = dict()
        self.session.headers['X_FB_PHOTO_WATERFALL_ID'] = waterfall_id
        self.session.headers['X-Instagram-Rupload-Params'] = json.dumps(rupload_params, separators=(',', ':'))
        self.session.headers['X-IG-Connection-Type'] = 'WIFI'
        self.session.headers['X-IG-Capabilities'] = '3brTvwE='
        self.session.headers['X-IG-App-ID'] = '567067343352427'
        self.session.headers['User-Agent'] = self.device.get('user_agent')
        self.session.headers['Cookie'] = self.session.get_cookie_string()
        self.session.headers['Authorization'] = 'Bearer IGT:2:' + self.session.get_authorization_bearer()
        self.session.headers['X-MID'] = self.session.get_mid()
        self.session.headers['Accept-Language'] = 'en-US'
        self.session.headers['Accept-Encoding'] = 'gzip, deflate'
        self.session.headers['Host'] = 'i.instagram.com'
        self.session.headers['X-FB-HTTP-Engine'] = 'Liger'
        self.session.headers['Connection'] = 'close'

        return self.request.send_request(endpoint='https://i.instagram.com/rupload_igphoto/' + upload_name,
                                         session=self.session
                                         )

    def upload_photo(self, path_to_photo, upload_id, some_number, waterfall_id, force_resize=False, post=False):

        if not path_to_photo:
            raise print('Provide path to photo file')

        path_to_photo =  self.check_supportibilty(path_to_photo)

        if not self.compatible_aspect_ratio(self.get_image_size(path_to_photo)):
            print("Photo does not have a compatible photo aspect ratio.")
            if force_resize:
                path_to_photo = self.resize_image(path_to_photo)
            else:
                return False
        upload_name = "{upload_id}_0_{rand}".format(
            upload_id=upload_id, rand=some_number
        )
        photo_data = open(path_to_photo, "rb").read()
        photo_len = str(len(photo_data))

        if post:
            rupload_params = {
                "upload_id": upload_id,
                "media_type": "1",
                "retry_context": '{"num_step_auto_retry":0,"num_reupload":0,"num_step_manual_retry":0}',
                "original_photo_pdq_hash": "1d81dac9c27f37267d9a629ca901be43dee4d3aa619a6f3498c39ccb2e344334:100",
                "image_compression": json.dumps(
                    {"lib_name": "moz", "lib_version": "3.1.m", "quality": "80", "ssim": 0.9903625845909119},
                    separators=(',', ':')
                ),
                "xsharing_user_ids": "[]",
            }
        else:
            rupload_params = {
                "upload_id": upload_id,
                "media_type": "1",
                "image_compression": json.dumps(
                    {"lib_name": "moz", "lib_version": "3.1.m", "quality": "81"}, separators=(',', ':')
                ),
            }

        self.session.headers = {}
        self.session.headers['X_FB_PHOTO_WATERFALL_ID'] = waterfall_id
        self.session.headers['X-Entity-Length'] = photo_len
        self.session.headers['X-Entity-Name'] = upload_name
        self.session.headers['X-Instagram-Rupload-Params'] = json.dumps(rupload_params, separators=(',', ':'))
        self.session.headers['X-Entity-Type'] = 'image/jpeg'
        self.session.headers['Offset'] = '0'
        self.session.headers['X-IG-Connection-Type'] = 'WIFI'
        self.session.headers['X-IG-Capabilities'] = '3brTvwE='
        self.session.headers['X-IG-App-ID'] = '567067343352427'
        self.session.headers['User-Agent'] = self.device.get('user_agent')
        self.session.headers['Accept-Language'] = 'en-US'
        self.session.headers['Cookie'] = self.session.get_cookie_string()
        self.session.headers['Authorization'] = 'Bearer IGT:2:' + self.session.get_authorization_bearer()
        self.session.headers['X-MID'] = self.session.get_mid()
        self.session.headers['Content-Type'] = 'application/octet-stream'
        self.session.headers['Accept-Encoding'] = 'gzip, deflate'
        self.session.headers['Host'] = 'i.instagram.com'
        self.session.headers['X-FB-HTTP-Engine'] = 'Liger'
        self.session.headers['Connection'] = 'close'

        return self.request.send_request(endpoint='https://i.instagram.com/rupload_igphoto/' + upload_name,
                                         post=photo_data,
                                         with_signature=False,
                                         session=self.session,
                                         timeout=30,
                                         )

    # ============== UPLOAD PROFILE PHOTO =============

    def set_profile_photo(self, path_to_photo):

        # OPEN THE APP OR LOGIN AGAIN IN ORDER TO CHANGE PROFILE PHOTO ( We use 'loginapi' module to do this )
        self.login.login(False)

        time.sleep(random.randint(4, 10))  # TODO

        self.reload_user(self.username)

        self.feed_user_story(1)
        self.feed_user_story(2)
        self.profile_su_badge()
        self.users_info(self.account.get('user_id'))
        self.qp_batch_fetch()
        self.highlights()
        self.profile_archive_badge()
        self.get_invite_suggestions()

        time.sleep(random.randint(5, 15))
        self.location_search() # TODO

        upload_id = str(int(time.time() * 1000))
        some_number = str(random.randint(-2 ** 10, 2 ** 10))
        waterfall_id = Signature.generate_UUID(True)

        time.sleep(random.randint(10, 15))
        try:
            if not self.get_upload_photo(upload_id, some_number, waterfall_id):
                raise Exception
        except Exception as e:
            print(e)
            print('MISSING OR INCOMPATIBLE PHOTO')

        try:
            if not self.upload_photo(path_to_photo, upload_id, some_number, waterfall_id, force_resize=True):
                raise Exception
        except Exception as e:
            print(e)
            print('MISSING OR INCOMPATIBLE PHOTO')
            raise

        data = dict()
        data['_csrftoken'] = self.session.get_csrftoken()
        data['_uuid'] = self.device.get('uuid')
        data['use_fbuploader'] = 'true'
        data['upload_id'] = upload_id  # TODO

        self.session.set_headers(is_post=True)

        is_photo_uploaded = self.request.send_request(endpoint=Constants.API_URL1 + 'accounts/change_profile_picture/',
                                                      post=data,
                                                      with_signature=False,
                                                      session=self.session)

        if is_photo_uploaded:
            print(colored('*** YOUR PROFILE PICTURE IS CHANGED ***', 'green', attrs=['bold']))
        else:
            print(colored('*** CHANGING PROFILE PICTURE ATTEMPT IS FAILED ***', 'red', attrs=['bold']))

        try:
            update_cookie(self.account.get('username'), self.request.cookie)
        except:
            pass

    # =========   UPLOAD POST PHOTO   ==================================================================================

    def upload_post_photo(self, path_to_photo):
        # Open the app and get timeline page before post.
        # If timeline does not respond, update the account status
        if not self.login.open_app():
            return

        time.sleep(random.randint(3, 10))

        self.reload_user(self.username) # TODO

        time.sleep(random.randint(10, 20))
        self.location_search()
        self.qp_batch_fetch()

        time.sleep(random.randint(5, 10))
        upload_id = str(int(time.time() * 1000))
        some_number = str(random.randint(-2 ** 10, 2 ** 10))
        waterfall_id = Signature.generate_UUID(True)

        def upload():
            response = self.upload_photo(path_to_photo, upload_id, some_number, waterfall_id, force_resize=True,
                                                post=True)
            if not response:
                return upload()
            return True

        upload()

        self.session.set_headers(retry_context=True ,is_post=True, auth=True)
        width, height = self.get_image_size(path_to_photo)

        data = dict()
        data['timezone_offset'] = self.geo.timezone_offset
        data['_csrftoken'] = self.session.get_csrftoken()
        data['media_folder'] = 'Download'
        data['source_type'] = '4'
        data['_uid'] = self.account.get('user_id')
        data['device_id'] = self.device.get('android_device_id')
        data['_uuid'] = self.device.get('uuid')
        data['creation_logger_session_id'] = Signature.generate_UUID(True)
        # data['location'] = json.dumps({}, separators=(",",":")) # TODO
        # data['suggested_venue_position'] = '-1' # TODO
        data['caption'] = ''
        data['upload_id'] = upload_id
        data['device'] = self.get_device_details()
        data['edits'] = {
            "crop_original_size": [width * 1.0, height * 1.0],
            "crop_center": [0.0, -0.0], # TODO
            "crop_zoom": 1.0,
        }
        data['extra'] = {"source_width": width, "source_height": height}
        # data['is_suggested_venue'] = 'False' # TODO

        try:
            is_photo_posted = self.request.send_request(endpoint=Constants.API_URL1 + 'media/configure/',
                                                        post=data,
                                                        session=self.session
                                                        )

            if is_photo_posted:
                print(colored('*** PHOTO POSTED SUCCESSFULLY ***', 'green', attrs=['bold']))
            else:
                print(colored('*** POSTING PHOTO ATTEMPT IS FAILED ***', 'red', attrs=['bold']))
        except:
            print(colored('SOMETHING WENT WRONG WHEN UPLOADING PROFILE PHOTO', 'red', attrs=['bold']))
        update_cookie(self.account.get('username'), self.request.cookie)

    def set_biography(self, text=''):
        self.get_profile_page()
        data = dict()
        data['_csrftoken'] = self.session.get_csrftoken()
        data['_uid'] = self.account.get('user_id')
        data['device_id'] = self.device.get('android_device_id')
        data['_uuid'] = self.device.get('uuid')
        data['raw_text'] = text

        self.session.set_headers(is_post=True)
        return self.request.send_request(endpoint=Constants.API_URL1 + "accounts/set_biography/",
                                         post=data,
                                         session=self.session
                                         )

    # =============== PHOTO DETAILS ======================================

    def get_image_size(self, fname):
        with open(fname, "rb") as fhandle:
            head = fhandle.read(24)
            if len(head) != 24:
                raise RuntimeError("Invalid Header")

            if imghdr.what(fname) == "png":
                check = struct.unpack(">i", head[4:8])[0]
                if check != 0x0D0A1A0A:
                    raise RuntimeError("PNG: Invalid check")
                width, height = struct.unpack(">ii", head[16:24])
            elif imghdr.what(fname) == "gif":
                width, height = struct.unpack("<HH", head[6:10])
            elif imghdr.what(fname) == "jpeg":
                fhandle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xC0 <= ftype <= 0xCF:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xFF:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack(">H", fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack(">HH", fhandle.read(4))
            else:
                raise RuntimeError("Unsupported format")
            return width, height

    def compatible_aspect_ratio(self, size):
        min_ratio, max_ratio = 4.0 / 5.0, 90.0 / 47.0
        width, height = size
        ratio = width * 1.0 / height * 1.0
        print("FOUND: w:{w} h:{h} r:{r}".format(w=width, h=height, r=ratio))
        return min_ratio <= ratio <= max_ratio

    def resize_image(self, fname):
        from math import ceil

        try:
            from PIL import Image, ExifTags
        except ImportError as e:
            print("ERROR: {err}".format(err=e))
            print(
                "Required module `PIL` not installed\n"
                "Install with `pip install Pillow` and retry"
            )
            return False
        print("Analizing `{fname}`".format(fname=fname))
        h_lim = {"w": 90.0, "h": 47.0}
        v_lim = {"w": 4.0, "h": 5.0}
        try:
            img = Image.open(fname)
        except Exception:
            raise

        print(type(img))
        (w, h) = img.size
        deg = 0
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == "Orientation":
                    break
            exif = dict(img.getexif().items())
            o = exif[orientation]
            print(o)
            if o == 3:
                deg = 180
            if o == 6:
                deg = 270
            if o == 8:
                deg = 90
            if deg != 0:
                print("Rotating by {d} degrees".format(d=deg))
                img = img.rotate(deg, expand=True)
                (w, h) = img.size
        except (AttributeError, KeyError, IndexError) as e:
            print("No exif info found (ERR: {err})".format(err=e))
            pass
        img = img.convert("RGBA")
        ratio = w * 1.0 / h * 1.0
        print("FOUND w:{w}, h:{h}, ratio={r}".format(w=w, h=h, r=ratio))
        if w > h:
            print("Horizontal image")
            if ratio > (h_lim["w"] / h_lim["h"]):
                print("Cropping image")
                cut = int(ceil((w - h * h_lim["w"] / h_lim["h"]) / 2))
                left = cut
                right = w - cut
                top = 0
                bottom = h
                img = img.crop((left, top, right, bottom))
                (w, h) = img.size
            if w > 1080:
                print("Resizing image")
                nw = 1080
                nh = int(ceil(1080.0 * h / w))
                img = img.resize((nw, nh), Image.ANTIALIAS)
        elif w < h:
            print("Vertical image")
            if ratio < (v_lim["w"] / v_lim["h"]):
                print("Cropping image")
                cut = int(ceil((h - w * v_lim["h"] / v_lim["w"]) / 2))
                left = 0
                right = w
                top = cut
                bottom = h - cut
                img = img.crop((left, top, right, bottom))
                (w, h) = img.size
            if h > 1080:
                print("Resizing image")
                nw = int(ceil(1080.0 * w / h))
                nh = 1080
                img = img.resize((nw, nh), Image.ANTIALIAS)
        else:
            print("Square image")
            if w > 1080:
                print("Resizing image")
                img = img.resize((1080, 1080), Image.ANTIALIAS)
        (w, h) = img.size
        new_fname = "{fname}.jpg".format(fname=fname)
        print("Saving new image w:{w} h:{h} to `{f}`".format(w=w, h=h, f=new_fname))
        new = Image.new("RGB", img.size, (255, 255, 255))
        new.paste(img, (0, 0, w, h), img)
        new.save(new_fname, quality=95)
        return new_fname

#
if __name__ == "__main__":
    # username = sys.argv[1]
    # try:
    #     path_to_photo_list = os.listdir(os.getcwd() + '/Instagram/CAERUS/Media/Photos/')
    #     def get_path_to_photo():
    #         path_to_photo = path_to_photo_list.pop()
    #         if not path_to_photo.endswith('jpg'):
    #             return  get_path_to_photo()
    #         return path_to_photo
    #     path_to_photo = os.getcwd() + '/Instagram/CAERUS/Media/Photos/' + get_path_to_photo()
    # except Exception as e:
    #     raise Exception
    # print(path_to_photo)
    # try:
    #     with open( os.path.abspath('proxies.txt') , 'r' ) as fout:
    #         lines = fout.read().splitlines(True)
    #         print(lines)
    #         proxy = lines.pop(0)
    #         lines.insert(-1, proxy)
    #     with open(os.path.abspath('proxies.txt') , 'w' ) as fin:
    #         fin.writelines(lines)
    # except Exception as e:
    #     print(e)
    #     print(colored('CANNOT RETRIEVE PROXY', 'red'))
    #
    # print(proxy)
    # proxy = literal_eval(proxy)

    # proxy = {'http': 'http://192.168.0.100:2222', 'https': 'https://192.168.0.100:2222'}
    # proxy = None
    proxy = {'http': 'http://51.15.13.145:3118', 'https': 'https://51.15.13.145:3118'}

    username = 'alinathompson1615'
    path_to_photo = '/Users/azat/Desktop/Instagram/Zeus/Media/Photos/resized_299350_f219f20a.jpg'
    pd = open(path_to_photo, "rb").read()
    print(pd)
    try:
        a = Photo(username=username, proxy=proxy)
        print(a.geo.country)
        print(a.geo.longitude)
        print(a.geo.latitude)
        # CHECK IF TIMEZONE COINCIDES OR NOT
        a.geo.check_timezone()
        if a.geo.country != 'US':
            print('Country must be US')
        else:
            try:
                a.upload_post_photo(path_to_photo=path_to_photo)
            except Exception as e:
                print(e)
                print(colored('PATH TO PHOTO MAY NOT BE AVAILABLE', 'red', attrs=['bold']))
            else:
                try:
                    os.remove(path_to_photo)
                    print(colored('PHOTO HAS BEEN REMOVED', 'green', attrs=['bold']))

                except Exception as e:
                    print(e)
                    print(colored('PHOTO CANNOT BE REMOVED', 'red', attrs=['bold']))

    except Exception as e:
        print(e)
        print(colored('CANNOT INITIALIZE "PHOTO" CLASS', 'red'))


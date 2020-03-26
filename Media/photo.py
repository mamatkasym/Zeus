# coding=utf8
import imghdr
import random
import struct
import sys
import time
import os
from pathlib import Path

import requests
import json

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


class Photo:
    def __init__(self, username=None, proxy=None):
        self.user = User(username)
        self.account = self.user.account
        self.device = self.user.device
        self.request = Request()
        self.session = requests.session()
        self.session.proxies = proxy
        try:
            self.session.cookies = requests.utils.cookiejar_from_dict(json.loads(self.account.get('cookie')))
        except Exception as e:
            print(e)

        self.login = Login(username=username, session=self.session, proxy=proxy)

        self.longitude = Geo.get_longitude(proxy)
        self.latitude = Geo.get_latitude(proxy)
        self.username = username
        self.upload_id = None

    def reload_user(self, username=None):
        self.user = User(username)
        self.account = self.user.account
        self.device = self.user.device

    def get_csrftoken(self):
        try:
            return self.session.cookies.get_dict()['csrftoken']
        except KeyError:
            return self.account.get('csrftoken')

    def set_headers(self,
                    x_device=False,
                    prefetch_request=False,
                    is_post=False,
                    retry_context=False,
                    ):

        self.session.headers = {}

        if x_device:
            self.session.headers['X-DEVICE-ID'] = self.device.get('uuid')
        self.session.headers['X-IG-App-Locale'] = 'en_US'
        self.session.headers['X-IG-Device-Locale'] = 'en_US'
        self.session.headers['X-Pigeon-Session-Id'] = self.device.get('x_pigeon')
        self.session.headers['X-Pigeon-Rawclienttime'] = str(round(time.time(), 3))
        self.session.headers['X-IG-Connection-Speed'] = '-1kbps'
        self.session.headers['X-IG-Bandwidth-Speed-KBPS'] = '-1.000'
        self.session.headers['X-IG-Bandwidth-TotalBytes-B'] = '0'
        self.session.headers['X-IG-Bandwidth-TotalTime-MS'] = '0'
        if prefetch_request:
            self.session.headers['X-IG-Prefetch-Request'] = 'foreground'
        self.session.headers['X-IG-Extended-CDN-Thumbnail-Sizes'] = '160,180,360'
        self.session.headers['X-Bloks-Version-Id'] = '0e9b6d9c0fb2a2df4862cd7f46e3f719c55e9f90c20db0e5d95791b66f43b367'
        self.session.headers['X-IG-WWW-Claim'] = 'hmac.AR3skglIBS45Xd_AkJdCKJH2Cmv6zg8qFmIf91klyi_PjoJe'
        self.session.headers['X-Bloks-Is-Layout-RTL'] = 'false'
        self.session.headers['X-IG-Device-ID'] = self.device.get('uuid')
        self.session.headers['X-IG-Android-ID'] = self.device.get('android_device_id')
        if retry_context:
            self.session.headers['retry_context'] = json.dumps({"num_reupload":0,"num_step_auto_retry":0,"num_step_manual_retry":0} , separators=(',', ':'))
        self.session.headers['X-IG-Connection-Type'] = 'WIFI'
        self.session.headers['X-IG-Capabilities'] = '3brTvwE='
        self.session.headers['X-IG-App-ID'] = '567067343352427'
        self.session.headers['User-Agent'] = self.device.get('user_agent')
        self.session.headers['Accept-Language'] = 'en-US'
        if is_post:
            self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.session.headers['Accept-Encoding'] = 'gzip, deflate'
        self.session.headers['Host'] = 'i.instagram.com'
        self.session.headers['X-FB-HTTP-Engine'] = 'Liger'
        self.session.headers['Connection'] = 'close'

    def get_device_details(self):
        device_details = self.device.get('user_agent')
        device_details = device_details.split('; ')
        device = {
            'manufacturer':device_details[3],
            'model':device_details[4],
            'android_version': int(device_details[0][-4:-2]),
            'android_release':device_details[0][-1]
        }
        return device
# =============================================================
    def feed_user_story(self):
        param = dict()
        param['supported_capabilities_new'] = Constants.NEW_SUPPORTED_CAPABILITIES117
        self.set_headers()
        self.request.send_request(
            endpoint=Constants.API_URL1 + 'feed/user/{}/story/'.format(self.account.get('user_id')),
            params=param,
            session=self.session)

    def profile_su_badge(self):
        self.set_headers()
        data = dict()
        data['_csrftoken'] = self.get_csrftoken()
        data['_uuid'] = self.device.get('uuid')

        self.request.send_request(endpoint=Constants.API_URL1 + 'discover/profile_su_badge/',
                                  post=data,
                                  with_signature=False,
                                  session=self.session)

    def users_info(self, userid=None):
        self.set_headers()
        return self.request.send_request(
            endpoint=Constants.API_URL1 + 'users/{}/info/?from_module=self_profile'.format(userid),
            session=self.session
            )

    def qp_batch_fetch(self, surfaces_to_triggers, surfaces_to_qieries):
        body = dict()
        body["surfaces_to_triggers"] = surfaces_to_triggers
        body["surfaces_to_queries"] = surfaces_to_qieries
        body["vc_policy"] = "default"
        body["_csrftoken"] = self.get_csrftoken()
        body["_uid"] = self.account.get('user_id')
        body["_uuid"] = self.device.get('uuid')
        body["scale"] = Constants.BATCH_SCALE
        body["version"] = Constants.BATCH_VERSION

        self.set_headers(is_post=True)

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

        self.session.headers = dict()
        self.session.headers['X-Ads-Opt-Out'] = '0'
        self.session.headers['X-Attribution-ID'] = self.device.get('attribution_id')
        self.session.headers['X-Google-AD-ID'] = self.device.get('advertising_id')
        self.session.headers['X-DEVICE-ID'] = self.device.get('uuid')
        self.session.headers['X-FB'] = '1'
        self.session.headers['X-CM-Bandwidth-KBPS'] = ''  # TODO
        self.session.headers['X-CM-Latency'] = ''  # TODO
        self.session.headers['X-IG-App-Locale'] = 'en_US'
        self.session.headers['X-IG-Device-Locale'] = 'en_US'
        self.session.headers['X-Pigeon-Session-Id'] = self.device.get('x_pigeon')
        self.session.headers['X-Pigeon-Rawclienttime'] = str(round(time.time(), 3))
        self.session.headers['X-IG-Connection-Speed'] = '-1kbps'
        self.session.headers['X-IG-Bandwidth-Speed-KBPS'] = '-1.000'
        self.session.headers['X-IG-Bandwidth-TotalBytes-B'] = '0'
        self.session.headers['X-IG-Bandwidth-TotalTime-MS'] = '0'
        self.session.headers['X-IG-Extended-CDN-Thumbnail-Sizes'] = '160,180,360'
        self.session.headers['X-Bloks-Version-Id'] = '0e9b6d9c0fb2a2df4862cd7f46e3f719c55e9f90c20db0e5d95791b66f43b367'
        self.session.headers['X-IG-WWW-Claim'] = 'hmac.AR3skglIBS45Xd_AkJdCKJH2Cmv6zg8qFmIf91klyi_PjoJe'
        self.session.headers['X-Bloks-Is-Layout-RTL'] = 'false'
        self.session.headers['X-IG-Device-ID'] = self.device.get('uuid')
        self.session.headers['X-IG-Android-ID'] = self.device.get('android_device_id')
        self.session.headers['X-IG-Connection-Type'] = 'WIFI'
        self.session.headers['X-IG-Capabilities'] = '3brTvwE='
        self.session.headers['X-IG-App-ID'] = '567067343352427'
        self.session.headers['User-Agent'] = self.device.get('user_agent')
        self.session.headers['Accept-Language'] = 'en-US'
        self.session.headers['Accept-Encoding'] = 'gzip, deflate'
        self.session.headers['Host'] = 'i.instagram.com'
        self.session.headers['X-FB-HTTP-Engine'] = 'Liger'
        self.session.headers['Connection'] = 'close'
        self.request.send_request(
            endpoint=Constants.API_URL1 + 'highlights/{}/highlights_tray/'.format(self.account.get('user_id')),
            params=body,
            session=self.session
            )

    def profile_archive_badge(self):
        body = dict()
        body['timezone_offset'] = self.login.timezone_offset
        body['_csrftoken'] = self.get_csrftoken()
        body['_uuid'] = self.device.get('uuid')

        self.set_headers()
        self.request.send_request(endpoint=Constants.API_URL1 + 'archive/reel/profile_archive_badge/',
                                  post=body,
                                  with_signature=False,
                                  session=self.session
                                  )

    def get_invite_suggestions(self):
        body = dict()
        body['count_only'] = '1'
        body['_csrftoken'] = self.get_csrftoken()
        body['_uuid'] = self.device.get('uuid')

        self.set_headers(is_post=True)

        return self.request.send_request(endpoint=Constants.API_URL1 + "fb/get_invite_suggestions/",
                                         post=body,
                                         with_signature=False,
                                         session=self.session
                                         )

    def location_search(self):
        param = dict()
        param['latitude'] = self.latitude
        param['rankToken'] = Signature.generate_UUID(True)  # TODO
        param['longitude'] = self.longitude
        self.set_headers()
        return self.request.send_request(endpoint=Constants.API_URL1 + "location_search/",
                                         params=param,
                                         session=self.session
                                         )

    def get_upload_igphoto(self, upload_id, some_number, waterfall_id):

        rupload_params = {
            "upload_id": upload_id,
            # "retry_context": '{"num_step_auto_retry":0,"num_reupload":0,"num_step_manual_retry":0}',
            "media_type": "1",
            # "xsharing_user_ids": "[]",
            "image_compression": json.dumps(
                {"lib_name": "moz", "lib_version": "3.1.m", "quality": "81"}
            ),
        }
        upload_name = "{upload_id}_0_{rand}".format(
            upload_id=upload_id, rand=some_number
        )

        self.session.headers = {}
        self.session.headers['X_FB_PHOTO_WATERFALL_ID'] = waterfall_id
        self.session.headers['X-Instagram-Rupload-Params'] = json.dumps(rupload_params)
        self.session.headers['X-IG-Connection-Type'] = 'WIFI'
        self.session.headers['X-IG-Capabilities'] = '3brTvwE='
        self.session.headers['X-IG-App-ID'] = '567067343352427'
        self.session.headers['User-Agent'] = self.device.get('user_agent')
        self.session.headers['Accept-Language'] = 'en-US'
        self.session.headers['Accept-Encoding'] = 'gzip, deflate'
        self.session.headers['Host'] = 'i.instagram.com'
        self.session.headers['X-FB-HTTP-Engine'] = 'Liger'
        self.session.headers['Connection'] = 'close'

        return self.request.send_request(endpoint='https://i.instagram.com/rupload_igphoto/' + upload_name,
                                         session=self.session
                                         )

    def post_upload_igphoto(self, path_to_photo, upload_id, some_number, waterfall_id, force_resize=False, post=False):

        if not path_to_photo:
            raise print('Provide path to photo file')
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
                    {"lib_name":"moz","lib_version":"3.1.m","quality":"80","ssim":0.9903625845909119}, separators=(',', ':')
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

    def upload_profile_photo(self, path_to_photo):

        # OPEN THE APP OR LOGIN AGAIN IN ORDER TO CHANGE PROFILE PHOTO ( We use 'loginapi' module to do this )
        self.login.login(False)

        time.sleep(random.randint(4,10))  # TODO

        self.reload_user(self.username)

        self.feed_user_story()
        self.profile_su_badge()
        self.users_info(self.account.get('user_id'))
        self.qp_batch_fetch(Constants.SURFACES_TO_TRIGGERS, Constants.SURFACES_TO_QUERIES)
        self.highlights()
        self.profile_archive_badge()
        self.get_invite_suggestions()

        time.sleep(random.randint(5,15))
        self.location_search()

        upload_id = str(int(time.time() * 1000))
        some_number = str(random.randint(-2 ** 10, 2 ** 10))
        waterfall_id = Signature.generate_UUID(True)


        time.sleep(random.randint(10,15))
        try:
            self.get_upload_igphoto(upload_id, some_number, waterfall_id)
            raise Exception('MISSING OR INCOMPATIBLE PHOTO')
        except:
            print('PHOTO ERROR')

        try:
            self.post_upload_igphoto(path_to_photo, upload_id, some_number, waterfall_id, force_resize=True)
            raise Exception('MISSING OR INCOMPATIBLE PHOTO')
        except:
            print('PHOTO ERROR')

        data = dict()
        data['_csrftoken'] = self.get_csrftoken()
        data['_uuid'] = self.device.get('uuid')
        data['use_fbuploader'] = 'true'
        data['upload_id'] = upload_id  # TODO

        self.set_headers(is_post=True)

        is_photo_uploaded = self.request.send_request(endpoint=Constants.API_URL1 + 'accounts/change_profile_picture/',
                                                      post=data,
                                                      with_signature=False,
                                                      session=self.session)

        if is_photo_uploaded:
            print(colored('*** YOUR PROFILE PICTURE IS CHANGED ***', 'green', attrs=['bold']))
        else:
            print(colored('*** CHANGING PROFILE PICTURE ATTEMPT IS FAILED ***', 'red', attrs=['bold']))

        try:
            update_cookie(self.account.get('username'), self.request.cookie )
        except:
            pass

    def upload_post_photo(self, path_to_photo):
        self.login.login(False)

        time.sleep(random.randint(3,10))

        self.reload_user(self.username)

        time.sleep(random.randint(10,20))
        self.location_search()
        self.qp_batch_fetch(Constants.SURFACES_TO_TRIGGERS117, Constants.SURFACES_TO_QUERIES1)

        time.sleep(random.randint(5,10))
        upload_id = str(int(time.time() * 1000))
        some_number = str(random.randint(-2 ** 10, 2 ** 10))
        waterfall_id = Signature.generate_UUID(True)

        def upload():
            response = self.post_upload_igphoto(path_to_photo, upload_id, some_number, waterfall_id, force_resize=True, post=True)
            if not response:
                return upload()
            return True

        upload()


        self.set_headers(retry_context=True)
        width, height = self.get_image_size(path_to_photo)

        data = dict()
        data['timezone_offset'] = self.login.timezone_offset
        data['_csrftoken'] = self.get_csrftoken()
        data['media_folder'] = 'Download'
        data['source_type'] = '4'
        data['_uid'] = self.account.get('user_id')
        data['device_id'] = self.device.get('android_device_id')
        data['_uuid'] = self.device.get('uuid')
        data['creation_logger_session_id'] = Signature.generate_UUID(True)
        data['caption'] = ''
        data['upload_id'] = upload_id
        data['device'] = self.get_device_details()
        data['edits'] = {
            "crop_original_size": [width * 1.0, height * 1.0],
            "crop_center": [0.0, 0.0],
            "crop_zoom": 1.0,
        }
        data['extra'] = {"source_width": width, "source_height": height}

        is_photo_posted =  self.request.send_request(endpoint=Constants.API_URL1 + 'media/configure/',
                                         post=data,
                                         session=self.session
                                         )
        if is_photo_posted:
            print(colored('*** PHOTO POSTED SUCCESSFULLY ***', 'green', attrs=['bold']))
        else:
            print(colored('*** POSTING PHOTO ATTEMPT IS FAILED ***', 'red', attrs=['bold']))


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
        new_fname = "{fname}.CONVERTED.jpg".format(fname=fname)
        print("Saving new image w:{w} h:{h} to `{f}`".format(w=w, h=h, f=new_fname))
        new = Image.new("RGB", img.size, (255, 255, 255))
        new.paste(img, (0, 0, w, h), img)
        new.save(new_fname, quality=95)
        return new_fname


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
    # os.remove(path_to_photo)
    # try:
    #     with open( os.getcwd() + '/Instagram/CAERUS/Database/proxies.txt' , 'r' ) as fout:
    #         lines = fout.read().splitlines(True)
    #         print(lines)
    #         proxy = lines.pop(0)
    #         lines.insert(-1, proxy)
    #     with open(os.getcwd() + '/Instagram/CAERUS/Database/proxies.txt' , 'w' ) as fin:
    #         fin.writelines(lines)
    # except Exception as e:
    #     print(e)
    #     print(colored('CANNOT RETRIEVE PROXY', 'red'))
    #
    # try:
    #     a = Photo(username=username, proxy=proxy)
    # except Exception as e:
    #     print(colored('CANNOT INITIALIZE "PHOTO" CLASS', 'red'))
    # else:
    #     try:
    #         a.upload_post_photo(path_to_photo=path_to_photo)
    #         os.remove(path_to_photo)
    #     except Exception as e:
    #         print(colored('WRONG PATH TO PHOTO', 'red', attrs=['bold']))
    p = Photo('vedo_xooor', proxy={'http': 'http://192.168.0.100:1111','https': 'https://192.168.0.100:1111'})
    p.upload_post_photo(os.getcwd() + '/Photos/download.jpeg')
    # time.sleep(random.randint(5, 10))
    # upload_id = str(int(time.time() * 1000))
    # some_number = str(random.randint(-2 ** 10, 2 ** 10))
    # waterfall_id = Signature.generate_UUID(True)
    # p.post_upload_igphoto(os.getcwd() + '/Photos/download.jpeg', upload_id, some_number, waterfall_id, force_resize=True, post=True)















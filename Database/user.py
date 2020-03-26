from datetime import datetime
import logging
import sys
try:
    from Database.db import Account, Device, db
except:
    from ..Database.db import Account, Device, db



class User:


    def __init__(self, username=None, account_id=None):

        if not username and not account_id:
            logging.info("ERROR: Please provide username or account id")
            sys.exit()
        if username:
            self.account = Account.query.filter_by(username=username).first()
        elif account_id:
            self.account = Account.query.filter_by(id=account_id).first()

        if not self.account:
            raise Exception("ERROR: Could not find account with username '{0}'".format(str(username)))

        if not self.account.device:
            raise Exception("ERROR: Could not find device with username '{0}'".format(str(username)))

        else:
            self.device = self.account.device[0].__dict__
            self.account = self.account.__dict__


# if __name__ == "__main__":
#     account_rows = db.session.query(Account).count()
#     new_account = Account(
#         id=account_rows + 1,
#         username='username',
#         fullname='fullname',
#         email='email',
#         password='password',
#         last_login=datetime.now().timestamp(),
#         is_logged_in=True,
#         cookie='cookie',  # json.dumps(self.request.last_response.cookies.get_dict()),
#         user_id='user_id',
#         timezone='timezone',
#         csrftoken='token',
#         rur='rur',
#         sessionid='get_sessionid',
#         ds_user_id='ds_user_id',
#         is_from_appium=False,
#     )
#
#     db.session.add(new_account)
#     db.session.commit()
#
#     device_rows = db.session.query(Device).count()
#     new_device = Device(
#         id=device_rows + 1,
#         account_username='username',
#         user_agent='user_agent',
#         uuid='uuid',
#         android_device_id='device.android_device_id',
#         waterfall_id='device.waterfall_id',
#         advertising_id='device.advertising_id',
#         jazoest='device.jazoest',
#         phone_id='device.phone_id',
#         x_pigeon='self.device.x_pigeon',
#         attribution_id='self.device.attribution_id',
#     )
#     db.session.add(new_device)
#     db.session.commit()

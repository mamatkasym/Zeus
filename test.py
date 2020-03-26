import json
import requests
import time
import urllib.parse
from base64 import b64decode
import datetime
from Database.db import Account, db, Device
from Database.user import User
from Database.device import DeviceInfo
# from urllib.parse import parse_qs
# from constants import Constants
# s = input()
# s = parse_qs(s)
#
# for key in s:
#     print(key.upper() + ' = ' +  "'''" +  s[key][0] + "'''")


# s = input()
# s = urllib.parse.parse_qs(s)
# s = s['signed_body'][0]
# s = s[65:]
# s = json.loads(s)
# for key in s:
#     print(key + " : " + str(s[key]))

user_agents = [
'Instagram 117.0.0.28.123 Android (28/9; 403dpi; 1080x2340; Xiaomi/xiaomi; Mi 9 Lite; pyxis; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/8; 577dpi; 1440x2560; samsung; SM-G930F; herolte; exynos8890; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 401dpi; 1080x2280; samsung; SM-N970U; davinci; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 403dpi; 1080x2340; Xiaomi/xiaomi; Mi 9; cepheus; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 529dpi; 1440x2960; samsung; SM-G955F; cruiser; exynos8895; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 269dpi; 720x1520; Xiaomi/xiaomi; Redmi 7; onclite; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 403dpi; 1080x2280; Xiaomi/xiaomi; Mi 8 Lite; platina; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 529dpi; 1440x2960; samsung; SM-G955FD; cruiser; exynos8895; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 537dpi; 1440x3040; Google; Pixel 4XL; coral; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/8; 534dpi; 1440x2560; samsung; SM-G935F; hero2lte; exynos8890; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 438dpi; 1080x2280; samsung; SM-G970U;  beyond0; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 409dpi; 1080x2340; Xiaomi/xiaomi; Redmi Note 7; lavender; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 432dpi; 1080x2340; Xiaomi/xiaomi; Mi 9 SE; grus; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 498dpi; 1440x3040; samsung; SM-N975F; davinci; exynos9825; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 550dpi; 1440x3040; samsung; SM-G973F;  beyond1; exynos9820; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 521dpi; 1440x2960; samsung; SM-N950U1; great; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/10; 529dpi; 1440x2960; samsung; SM-G960DS; star; exynos9810; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 388dpi; 2088x2250; Xiaomi/xiaomi; Mi Mix Alpha; papyrus; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 395dpi; 1080x2400; Xiaomi/xiaomi; Black Shark 3; tucana; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 550dpi; 1440x3040; samsung; SM-G973U;  beyond1; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 402dpi; 1080x2160; Google; Pixel 3a XL; bonito; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 560dpi; 1440x2723; samsung; SM-G973F;  beyond1; exynos9820; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 516dpi; 1440x2960; samsung; SM-N960F; crown; exynos9810; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/8; 577dpi; 1440x2560; samsung; SM-G930FD; herolte; exynos8890; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 401dpi; 1080x2280; samsung; SM-N970DS; davinci; exynos9825; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 521dpi; 1440x2960; samsung; SM-N950FD; great; exynos8895; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 529dpi; 1440x2960; samsung; SM-G955U; cruiser; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 403dpi; 1080x2340; samsung; SM-A505U; a50dd; exynos9610; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 401dpi; 1080x2280; samsung; SM-N970F; davinci; exynos9825; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/10; 570dpi; 1440x2960; samsung; SM-G960F; star; exynos9810; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 438dpi; 1080x2280; samsung; SM-G970DS;  beyond0; exynos9820; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/10; 570dpi; 1440x2960; samsung; SM-G960DS; star; exynos9810; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 398dpi; 1080x2340; Xiaomi/xiaomi; Mi Note 10 Pro; tucana; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 498dpi; 1440x3040; samsung; SM-N975DS; davinci; exynos9825; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 438dpi; 1080x2280; samsung; SM-G970F;  beyond0; exynos9820; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 498dpi; 1440x3040; samsung; SM-N975U1; davinci; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 401dpi; 1080x2280; samsung; SM-N970U1; davinci; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 522dpi; 1440x3040; samsung; SM-G975DS; beyond2; exynos9820; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/10; 570dpi; 1440x2960; samsung; SM-G960U; star; exynos9810; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 443dpi; 1080x2160; Google; Pixel 3; blueline; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 403dpi; 1080x2340; Xiaomi/xiaomi; Redmi K20 Pro; raphael; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 403dpi; 1080x2280; Xiaomi/xiaomi; Redmi Note 6 Pro; tulip; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 570dpi; 1440x2960; samsung; SM-G950F; cruiser; exynos8895; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 403dpi; 1080x2340; Xiaomi/xiaomi; Redmi K20; davinci; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 521dpi; 1440x2960; samsung; SM-N950F; great; exynos8895; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 295dpi; 720x1440; Xiaomi/xiaomi; Redmi 7A; pine; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 550dpi; 1440x3040; samsung; SM-G973DS;  beyond1; exynos9820; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 521dpi; 1440x2960; samsung; SM-N950U; great; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 570dpi; 1440x2960; samsung; SM-G950FD; cruiser; exynos8895; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 522dpi; 1440x3040; samsung; SM-G975F; beyond2; exynos9820; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 516dpi; 1440x2960; samsung; SM-N960DS; crown; exynos9810; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 523dpi; 1440x2960; Google; Pixel 3 XL; crosshatch; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 405dpi; 1080x2400; samsung; SM-A515F; davinci; exynos9611; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 441dpi; 1080x2220; Google; Pixel 3; sargo; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 498dpi; 1440x3040; samsung; SM-N975U; davinci; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/10; 529dpi; 1440x2960; samsung; SM-G960U; star; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/10; 529dpi; 1440x2960; samsung; SM-G960F; star; exynos9810; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 444dpi; 1080x2280; Google; Pixel 4; flame; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 522dpi; 1440x3040; samsung; SM-G975U; beyond2; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 516dpi; 1440x2960; samsung; SM-N960U; crown; exynos9810; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (29/10; 409dpi; 1080x2340; Xiaomi/xiaomi; Redmi Note 7 Pro; violet; qcom; en_US; 180322800)',
'Instagram 117.0.0.28.123 Android (28/9; 570dpi; 1440x2960; samsung; SM-G950U; cruiser; exynos8895; en_US; 180322800)',
]

def get_user_agent_130():
    user_agent = user_agents.pop()
    user_agents.insert(0, user_agent)
    user_agent = user_agent.replace('117.0.0.28.123', '130.0.0.31.121')
    user_agent = user_agent.replace('180322800', '200396023')
    return user_agent

def get_user_agent_117():
    user_agent = user_agents.pop()
    user_agents.insert(0, user_agent)
    return user_agent


def message(username):
    try:
        user = User(username=username)
        device = user.device
        return 'ok'
    except Exception as e:
        return e
accounts = Account.query.filter_by(username='vedo_xooor')
print(type(accounts))


accounts = Account.query.all()
users = []
for account in accounts:
    user = account.__dict__
    username = user.get('username')
    msg = message(username)
    print(msg)
    if msg != 'ok':
        users.append(user)

print(len(users))
for account in users:
#     time.sleep(2)
    if account.get('is_from_appium'):
        user_agent  = get_user_agent_130()
    else:
        user_agent = get_user_agent_117()

    print(type(account))


for account in users:
    if account.get('is_from_appium'):
        user_agent  = get_user_agent_130()
    else:
        user_agent = get_user_agent_117()

    device = DeviceInfo().get_device_info()
    username = account.get('username')
    print(username)
    new_device = Device(
        account_username=username,
        user_agent=user_agent,
        uuid=device.get('uuid'),
        android_device_id=device.get('android_device_id'),
        waterfall_id=device.get('waterfall_id'),
        advertising_id=device.get('advertising_id'),
        jazoest=device.get('jazoest'),
        phone_id=device.get('phone_id'),
        x_pigeon=device.get('x_pigeon'),
        attribution_id=device.get('attribution_id'),
    )
    db.session.add(new_device)
    print('DONE')
    time.sleep(1)
db.session.commit()





import json
import random
import time
from datetime import datetime, timedelta
import logging
import requests
from Database.db import Account, Device, db, AccountStatus, LikeData
# from urllib.parse import parse_qs
# import json
#
# s = input()
#
# s = parse_qs(s)
# s = s['signed_body'][0][65:]
# s = json.loads(s)
#
# for key in s:
#     print(key + " : " + str(s[key]))
#
import logging
import threading, time, signal, os

from datetime import timedelta, datetime

from termcolor import colored

try:
    from create import Create
except:
    from .create import Create
try:
    from like_by_link import LikeByLink
except ImportError:
    from .like_by_link import LikeByLink

WAIT_TIME_SECONDS = 60


class ProgramKilled(Exception):
    pass


usernames = []
try:
    accounts = Account.query.filter(Account.last_login <= (datetime.now() - timedelta(days=0)).timestamp())
except Exception as e:
    print(e)
    raise Exception

for account in accounts:
    statuses = AccountStatus.query.filter_by(account_username=account.username).first()
    if statuses != None:
        continue
    if account.is_from_appium:
        json.loads(account.cookie)
        usernames.append(account.username)


print(len(usernames))
proxies = [
# {'http': 'http://51.15.13.145:3111', 'https': 'https://51.15.13.145:3111'},
# {'http': 'http://51.15.13.145:3112', 'https': 'https://51.15.13.145:3112'},
# {'http': 'http://51.15.13.145:3113', 'https': 'https://51.15.13.145:3113'},
# {'http': 'http://51.15.13.145:3114', 'https': 'https://51.15.13.145:3114'},
#     {'http': 'http://51.15.13.145:3115', 'https': 'https://51.15.13.145:3115'},
# {'http': 'http://51.15.13.145:3116', 'https': 'https://51.15.13.145:3116'},
# {'http': 'http://51.15.13.145:3117', 'https': 'https://51.15.13.145:3117'},
    {'http': 'http://51.15.13.145:3118', 'https': 'https://51.15.13.145:3118'},
    {'http': 'http://51.15.13.145:3119', 'https': 'https://51.15.13.145:3119'},
    {'http': 'http://51.15.13.145:3120', 'https': 'https://51.15.13.145:3120'},
    {'http': 'http://51.15.13.145:3121', 'https': 'https://51.15.13.145:3121'},
    {'http': 'http://51.15.13.145:3122', 'https': 'https://51.15.13.145:3122'},
    {'http': 'http://51.15.13.145:3123', 'https': 'https://51.15.13.145:3123'},
]

links = [
    'https://www.instagram.com/p/B9iifwDpwp4/?igshid=1hsomnd7g60r',
    'https://www.instagram.com/p/B9pm__OBcnV/?igshid=nmig8913qq99',
    'https://www.instagram.com/p/B-CWhZaKpvm/?igshid=q7sn4ajl0knv',
    'https://www.instagram.com/p/B9u4q_ypYPh/?igshid=1q7puo4vx5gd3',
    'https://www.instagram.com/p/B0PKQ0Il0Eo/?igshid=1om5b6k96q7ld',
    'https://www.instagram.com/p/B9-GGjLF3To/?igshid=1iieh3jm1g5cm',
    'https://www.instagram.com/p/B-BRX75H6Y5/?igshid=bjtm1axavkrr',
    'https://www.instagram.com/p/B9TDojBAQKa/?igshid=17xg918sl3lkk',
    'https://www.instagram.com/p/B-AdIavggGU/?igshid=s11ldwrplg9s',
    'https://www.instagram.com/p/B7xOgFjnuiO/?igshid=1t2adg3ly8qp5',
    'https://www.instagram.com/p/B9xG7jHJHYH/?igshid=9uyhkochygvx',
    'https://www.instagram.com/p/B-FJkFjlQJe/?igshid=vgxv4h14slni',
    'https://www.instagram.com/p/B-FJkFjlQJe/?igshid=g38mrv9hnkop',
    'https://www.instagram.com/p/B-C71yhHBOv/?igshid=12ddzcdrhvhb7',
    'https://www.instagram.com/p/B-GferRHGN2/?igshid=fn7scjf5szct',
    'https://www.instagram.com/p/B-GferRHGN2/?igshid=fn7scjf5szct',
    'https://www.instagram.com/p/B9ri2X9oUpr/?igshid=1n0umhar05gv8',
    'https://www.instagram.com/p/B7zM-R2oT0u/?igshid=18undg57papyp',
    'https://www.instagram.com/p/B-FS5mTnaRq/?igshid=rj33rl1wpi9y',
    'https://www.instagram.com/p/B9RycToFeh4/?igshid=92aqtsmcr40e',
    'https://www.instagram.com/p/B9vZND-JjIJ/?igshid=rflorfi1ux70',
    'https://www.instagram.com/p/B-DYXC_nRTN/?igshid=wc36d47kt03k',
    'https://www.instagram.com/p/B5ooTsVlr4-/?igshid=1vbeb0qqqmiir',
    'https://www.instagram.com/p/B9SjUhHBH3m/?igshid=1ngp4cel7dggh',
    'https://www.instagram.com/p/B9_4fMGAD4S/?igshid=1lcqq8fejn690',
    'https://www.instagram.com/p/B9-RIhMH42a/?igshid=wtbv7r7c1vri',
    'https://www.instagram.com/p/B-CUoiHHkxi/?igshid=ga0wez9eo1qm',
    'https://www.instagram.com/p/B9wbJ2YHXx_/?igshid=ckdn2pw1hfra',
    'https://www.instagram.com/p/B9tvo02gMmz/?igshid=1qstd2cpur23d',
    'https://www.instagram.com/p/B9XYf0inSSY/?igshid=1pkg86d8zjuzo',
    'https://www.instagram.com/p/B-AJJQ9KNEh/?igshid=15idnafja57vx',
    'https://www.instagram.com/p/B9AlsCEnJI3/?igshid=1grfrtldbc891',
    'https://www.instagram.com/p/B9tdlDqq11P/?igshid=1p6o6m0p861n7',
    'https://www.instagram.com/p/B9fQv73BF6t/?igshid=18dbg6obo9wgl',
    'https://www.instagram.com/p/B78ROvyjwsx/?igshid=mhgkuryfheef',
    'https://www.instagram.com/p/B99wLq8IRQm/?igshid=1h9uttcvmamo9',
    'https://www.instagram.com/p/B96jiEzBhBh/?igshid=a89v3cqrmutn',
    'https://www.instagram.com/p/B95NNkmDZSO/?igshid=5xkbum6u7vti',
    'https://www.instagram.com/p/B8XDpOFA1Xn/?igshid=8f2v5ekobzx2',
    'https://www.instagram.com/p/B9Nv2Tgls0y/?igshid=16wix18dhc8r0',
    'https://www.instagram.com/p/B9NrduAp1wo/?igshid=15oy88w9aens8',
    'https://www.instagram.com/p/B9cKVFIgbHB/?igshid=le0zp7i5maya',
    'https://www.instagram.com/p/B8ERQDuHPcJ/?igshid=1918gsceltrql',

]
logging.basicConfig(filename='logfile.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('Instagram')


def like():
    def task(username, link):
        proxy = proxies.pop(0)
        proxies.append(proxy)
        try:
            lbl = LikeByLink(username=username, link=link, proxy=proxy)
            print(colored(lbl.country.upper(), 'yellow' ))
            if lbl.country != 'US':
                print(colored('WARNING : COUNTRY MUST BE US !', 'RED'))
                raise Exception
        except json.decoder.JSONDecodeError as e:
            print(e)
            return
        except Exception as e:
            logger.exception(e)
            print(e)
            # print(colored('Plaese, try another proxy server','red',attrs=['bold','blink']))
            task(username, link)
        else:
            try:
                lbl.like_by_link()
            except Exception as e:
                logger.exception(e)
                print(e)
                # print(colored('Something went wrong in accountapi.py module', 'red', attrs=['bold', 'blink']))

    # Log the time when create task has started

    # Get email and password from line
    link = links.pop(0)
    links.append(link)

    # Get first proxy and append it back

    username = usernames.pop(0)
    usernames.append(username)
    task(username, link)


def signal_handler(signum, frame):
    raise ProgramKilled


class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        self.stopped.set()
        self.join()

    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=like)
    job.start()


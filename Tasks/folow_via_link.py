import logging
import os
import random
import signal
import threading
from ast import literal_eval
from datetime import timedelta
from pathlib import Path
from termcolor import colored

try:
    from follow_by_link import Follow
except ImportError:
    from ..follow_by_link import Follow
try:
    from Database.db import AccountStatus, Account, db
except ImportError:
    from ..Database.db import AccountStatus, Account, db

WAIT_TIME_SECONDS = 1
USERNAMES = []

logging.basicConfig(filename='logfile.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('Instagram')


class ProgramKilled(Exception):
    pass


# Retrieves proxy server from proxies.txt file. Takes first and appends it to the tail
def get_proxy():
    try:
        with open(os.path.abspath('proxies.txt'), 'r') as fout:
            lines = fout.read().splitlines(True)
            proxy = lines.pop(0)
            lines.insert(-1, proxy)
        with open(os.path.abspath('proxies.txt'), 'w') as fin:
            fin.writelines(lines)
    except Exception as e:
        print(e)
        print(colored('CANNOT RETRIEVE PROXY', 'red'))

    print(proxy)
    proxy = literal_eval(proxy)
    return proxy


def get_random_accounts(count):
    # Get accounts that are created by instagram version 130
    accounts = Account.query.filter_by(is_from_appium=True).all()
    usernames = []
    while len(usernames) < count:
        account = accounts.pop(random.randrange(len(accounts)))
        account_status = AccountStatus.query.filter_by(account_username=account.username).first()
        if account_status.status == 'ok':
            usernames.append(account.username)
    return usernames


# This function performs follow task
def follow_via_link(link):
    def task(username, link):
        proxy = get_proxy()
        try:
            F = Follow(username=username, proxy=proxy, link=link)
            print('fuuck')
            print(F.geo.country)
            print(F.geo.longitude)
            print(F.geo.latitude)
            # CHECK IF TIMEZONE COINCIDES OR NOT
            F.geo.check_timezone()
            if F.geo.country != 'US':
                print(colored('WARNING : Country must be US', 'red'))
                raise Exception

        except Exception as e:
            # print(e)
            print(colored('WARNING : Choose another proxy and try again', 'red'))
            task(username, link)
        else:
            try:
                F.follow_by_link()
            except Exception as e:
                print(e)

    username = USERNAMES.pop()
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
    print('Please provide the link of account page the client account to be followed :')
    link = input()
    print('Please provide the number of accounts to follow this account')
    count = int(input())
    USERNAMES = get_random_accounts(count)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=follow_via_link(link))
    job.start()

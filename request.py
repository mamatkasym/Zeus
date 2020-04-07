import gzip
import json
import logging

from requests.exceptions import ConnectionError, ProxyError, ConnectTimeout
from termcolor import colored
from urllib.parse import urlencode
try:
    from signature import Signature
except ImportError:
    from .signature import Signature

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Request:
    last_response = None
    last_json = None
    cookie = ''

    def get_cookie_string(self, session):
        try:
            return json.dumps(session.cookies.get_dict())
        except Exception as e:
            print(e)
            return ''

    def send_request(self, endpoint=None, post=None, headers=None, with_signature=True, extra_sig=None, timeout=None,
                     account=None, device=None, session=None, params=None, must_respond=False):
        print(colored(endpoint, 'blue', attrs=['bold']))

        logging.basicConfig(filename='logfile.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
        logger = logging.getLogger('Instagram')
        logger.info(session.headers)
        self.cookie = self.get_cookie_string(session)

        try:
            if post is not None:
                if with_signature:
                    post = json.dumps(post, separators=(',', ':'))
                    post = Signature.generate_signature_data(post)
                    if extra_sig is not None and extra_sig != []:
                        post += "&".join(extra_sig)
                try:
                    session.headers['Content-Length'] = str(len(urlencode(post)))
                except:
                    session.headers['Content-Length'] = str(len(post))

                if 'Content-Encoding' in session.headers.keys():
                    post = json.dumps(post, separators=(',', ':'))
                    post = gzip.compress(post.encode())
                response = session.post(endpoint, data=post, params=params, timeout=30 if timeout is None else timeout, verify=False)

            else:
                response = session.get(endpoint, params=params, timeout=30 if timeout is None else timeout, verify=False)

        except ProxyError as e:
            logger.exception(e)
            print(colored('PROXY ERROR', 'red', attrs=['bold']))
            if must_respond:
                raise
        except TimeoutError as e:
            logger.exception(e)
            print(colored('REQUEST TIMED OUT', 'red', attrs=['bold']))
            if must_respond:
                raise
        except ConnectTimeout as e:
            logger.exception(e)
            print(colored('CONNECT TIMEOUT ERROR', 'red', attrs=['bold']))
            if must_respond:
                raise
        except ConnectionError as e:
            logger.exception(e)
            print(colored('CONNECTION', 'red', attrs=['bold']))
            if must_respond:
                raise
        except Exception as e:
            print(e)
            print(colored('SOME REQUESTS ERROR HAS OCCURRED !', 'red', attrs=['bold']))
            logger.exception(e)
            if must_respond:
                raise

        else:
            # Print headers to check
            # for k, v in session.headers.items():
            #     print(k + ": " + str(v))
            self.last_response = response
            try:
                print(colored('RESPONSE : ' + str(response.content.decode()), 'magenta', attrs=['bold']))
            except Exception as e:
                print(e)
                print('Find it')


            try:
                self.last_json = json.loads(response.text)
            except json.decoder.JSONDecodeError:
                print(colored('RESPONSE UNAVAILABLE', 'red', attrs=['bold']))

            if response.status_code == 200:
                print(colored('STATUS_CODE : '+ str(response.status_code), 'green', attrs=['bold']))
                return True

            elif response.status_code == 400:
                print(colored('STATUS_CODE : '+ str(response.status_code), 'red', attrs=['bold']))
                # self.last_response = response
                # self.last_json = json.loads(response.text)
                return False
            # elif response.status_code == 429:
            #     # if we come to this error, add 5 minutes of sleep everytime we hit the 429 error (aka soft bann) keep increasing untill we are unbanned
            #     if timeout is None:
            #         timeout = 0
            #     timeout += 1
            #     logger.warning(
            #         "That means 'too many requests'. I'll go to sleep "
            #         "for {} seconds.".format(timeout * 15)
            #     )
            #     time.sleep(timeout * 15)
            #     return self.send_request(endpoint, post, headers, with_signature, extra_sig, timeout)
            else:
                # raise Exception("Cannot receive successful response !")
                print(colored('STATUS_CODE : ' + str(response.status_code), 'red', attrs=['bold']))
                print("Cannot receive successful response !")


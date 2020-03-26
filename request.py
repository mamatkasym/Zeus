import gzip
import json
import logging
import urllib.parse

from termcolor import colored

try:
    from signature import Signature
except ImportError:
    from .signature import Signature


class Request:
    last_response = None
    last_json = None
    cookie = ''

    def get_cookie_string(self, session):
        try:
            return json.dumps(session.cookies.get_dict())
        except:
            return ''

    def send_request(self, endpoint=None, post=None, headers=None, with_signature=True, extra_sig=None, timeout=None,
                     account=None, device=None, session=None, params=None):
        print(colored(endpoint, 'blue', attrs=['bold']))

        logger = logging.getLogger('REQUEST')

        self.cookie = self.get_cookie_string(session)

        try:
            if post is not None:
                try:
                    post = json.dumps(post, separators=(',', ':'))  # VERY VERY VERY IMPORTANT
                except Exception as e:  # TODO
                    print(e)
                if with_signature:
                    post = Signature.generate_signature_data(post)
                    if extra_sig is not None and extra_sig != []:
                        post += "&".join(extra_sig)
                else:
                    try:
                        post = urllib.parse.urlencode(json.loads(post))
                    except Exception as e:  # TODO
                        print(e)
                #  If request is post, then include length of posted data
                session.headers['Content-Length'] = str(len(post))

                if 'Content-Encoding' in session.headers.keys():
                    post = gzip.compress(post.encode())
                try:
                    response = session.post(endpoint, data=post, params=params, timeout=10 if timeout is None else timeout, verify=False)
                except TimeoutError:
                    print(colored('REQUEST TIMED OUT', 'red', attrs=['bold']))





            else:
                try:
                    response = session.get(endpoint, params=params, timeout=10 if timeout is None else timeout, verify=False)
                except TimeoutError:
                    print(colored('REQUEST TIMED OUT', 'red', attrs=['bold']))
                # else:
                    # print(colored('COULD NOT GET RESPONSE', 'red', attrs=['bold']))
        except Exception as e:
            print('SORRY !')
            logger.warning(str(e))
            return False
        if post is not None:
            logger.debug(
                "POST to endpoint: {} returned response: {}".format(endpoint, response)
            )
        else:
            logger.debug(
                "GET to endpoint: {} returned response: {}".format(endpoint, response)
            )


#        print(session.headers)
        self.last_response = response
        print(colored('RESPONSE : ' + str(response.content.decode()), 'magenta', attrs=['bold']))

        try:
            self.last_json = json.loads(response.text)
        except:
            pass
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


import json
import requests
from urllib.parse import parse_qs

# s = input()
# print('[1] with signed body')
# print('[2] without signed body')
# n = int(input())
# if n == 1:
#     s = parse_qs(s)
#     s = s['signed_body'][0][65:]
#     s = json.loads(s)
#
#     for k, v in s.items():
#         print(k + ": " + str(v))
# else:
#     s = parse_qs(s)
#     for k, v in s.items():
#         print(k.upper() + ": " + str(v))
s = requests.session()

re = s.get('http://ipinfo.io/json', proxies={'http': 'http://51.15.13.145:3122','https': 'https://51.15.13.145:3122'})
print(re.elapsed.total_seconds())

from datetime import datetime

import pytz
import requests, json
from ip2geotools.databases.noncommercial import DbIpCity
from timezonefinder import TimezoneFinder

COUNTRY_LIST = ['US', 'United States', 'BE', 'Belgium', 'BG', 'Bulgaria', 'BA', 'Bosnia and Herzegovina', 'JE', 'Jersey', 'BY', 'Belarus', 'RU', 'Russia', 'RS', 'Serbia', 'RO', 'Romania', 'GR', 'Greece', 'GG', 'Guernsey', 'GB', 'United Kingdom', 'GI', 'Gibraltar', 'HR', 'Croatia', 'HU', 'Hungary', 'PT', 'Portugal', 'PL', 'Poland', 'EE', 'Estonia', 'IT', 'Italy', 'ES', 'Spain', 'ME', 'Montenegro', 'MD', 'Moldova', 'MC', 'Monaco', 'MK', 'Macedonia', 'MT', 'Malta', 'IM', 'Isle of Man', 'FR', 'France', 'FI', 'Finland', 'NL', 'Netherlands', 'NO', 'Norway', 'CH', 'Switzerland', 'CZ', 'Czech Republic', 'SK', 'Slovakia', 'SI', 'Slovenia', 'SM', 'San Marino', 'SE', 'Sweden', 'DK', 'Denmark', 'DE', 'Germany', 'TR', 'Turkey', 'LI', 'Liechtenstein', 'LV', 'Latvia', 'LT', 'Lithuania', 'LU', 'Luxembourg', 'VA', 'Vatican', 'AD', 'Andorra', 'AL', 'Albania', 'AT', 'Austria', 'AX', 'Aland Islands', 'IE', 'Ireland', 'UA', 'Ukraine']


class Geo:

    def __init__(self, proxy=None):
        self.proxy = proxy
        self.location = self.get_location()
        self.ip_address = self.get_ip_address()
        self.country = self.get_country()
        self.timezone= self.get_timezone()
        self.timezone_offset = self.get_timezone_offset()

        self.longitude = self.get_longitude()
        self.latitude = self.get_latitude()

    def get_location(self):
        try:
            response = requests.get('http://ipinfo.io/json', proxies=self.proxy, timeout=60) # TODO This service may have mistakes

        except Exception as e:
            print(e)
            try:
                response = requests.get('https://ipgeolocation.com', proxies=self.proxy, timeout=60) # TODO This service may have mistakes
            except Exception as e:
                print(e)
                try:
                    response = requests.get('https://mobile-action-ip2country.herokuapp.com/',
                                            proxies=self.proxy, timeout=60)
                except Exception as e:
                    raise e
        print(response.text)
        return response.json()

    def get_longitude(self):
        response = DbIpCity.get(self.ip_address, api_key='free')

        return response.longitude

    def get_latitude(self):
        response = DbIpCity.get(self.ip_address, api_key='free')

        return response.latitude

    def check_timezone(self):
        tf = TimezoneFinder()
        latitude, longitude = self.latitude, self.longitude
        timezone = tf.timezone_at(lng=longitude, lat=latitude)
        print(timezone)
        print(self.timezone)

        if self.timezone != timezone:
            raise Exception('Timezone does not coincide')
        else:
            print('ok')

    def get_timezone_offset(self):
        tz = pytz.timezone(self.timezone)
        d = datetime.now(tz)  # or some other local date
        utc_offset = d.utcoffset().total_seconds()

        return str(int(utc_offset))

    def is_country_valid(self):
        if not self.country in COUNTRY_LIST:
            raise Exception('Country is not valid')

    def get_ip_address(self):
        try:
            return self.location['ip']
        except Exception as e:
            print(e)
            return self.location['IpAddress']

    def get_country(self):
        try:
            return self.location['country']
        except Exception as e:
            print(e)
            return self.location['countryCode']

    def get_timezone(self):
        try:
            return self.location['timezone']
        except Exception as e:
            print(e)
            return ''


if __name__ == "__main__":
    geo = Geo({'http': 'http://51.15.13.145:3117','https': 'https://51.15.13.145:3117'})
    print(geo.longitude)
    print(geo.latitude)
    geo.check_timezone()
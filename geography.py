import requests, json
from ip2geotools.databases.noncommercial import DbIpCity


class Geo:
    def __init__(self, proxy=None):
        self.ip_address = self.get_ip_address(proxy)
        self.longitude = self.get_longitude()
        self.latitude = self.get_latitude()
        self.country = self.get_country()

    def get_ip_address(self, proxy):
        url = 'http://ipinfo.io/json'
        session = requests.session()
        session.proxies = proxy
        response = session.get(url)
        data = json.loads(response.text)
        ip_address = data['ip']
        return ip_address

    def get_longitude(self):
        response = DbIpCity.get(self.ip_address, api_key='free')

        return response.longitude

    def get_latitude(self):
        response = DbIpCity.get(self.ip_address, api_key='free')

        return response.latitude

    def get_country(self):
        response = DbIpCity.get(self.ip_address, api_key='free')

        return response.country


if __name__ == "__main__":
    print(Geo.get_longitude({'http': 'http://192.168.0.100:2222', 'https': 'https://192.168.0.100:2222'}))
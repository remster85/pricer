import requests
from app.iss_data import ISSData
from app.ip_data import IPData
from app.types import Fetchable

class ISSHandler(Fetchable):
    def fetch(self) -> ISSData:
        res = requests.get("http://api.open-notify.org/iss-now.json")
        return ISSData(res.json())

class IPHandler(Fetchable):
    def fetch(self) -> IPData:
        res = requests.get("https://api.ipify.org?format=json")
        return IPData(res.json())
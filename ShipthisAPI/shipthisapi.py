from typing import Dict
import requests
class ShipthisAPI:
    base_api_endpoint = 'https://api.shipthis.co/api/v3/'

    def __init__(self, base_url: str, organisation: str, x_api_key:str, user_type='employee') -> None:
        self.x_api_key = x_api_key
        self.organisation_id = organisation
        self.base_url = base_url
        self.user_type = user_type
    
    def _make_request(self, method: str, path: str, query_params: str=None, request_data=None) ->  None:
        headers = {
            "x-api-key": self.x_api_key,
            "organisation_id": self.organisation_id,
            "user_type": self.user_type
        }
        resp = requests.request(method, self.base_api_endpoint + path, data=request_data or {}, headers=headers)
        if resp.status_code == 200:
            return resp.json

    def info(self) ->  Dict:
        info_resp = self._make_request('GET', 'auth/info')
        return info_resp

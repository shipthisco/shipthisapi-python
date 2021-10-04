from typing import Dict, List
import requests
class ShipthisAPI:
    base_api_endpoint = 'https://api.shipthis.co/api/v3/'

    def __init__(self, organisation: str, x_api_key:str, user_type='employee', region_id: str=None, location_id: str=None) -> None:
        self.x_api_key = x_api_key
        self.organisation_id = organisation
        self.user_type = user_type
        self.region_id = region_id
        self.location_id = location_id

    
    def set_region_location(self, region_id, location_id):
        self.region_id = region_id
        self.location_id = location_id
    
    def _make_request(self, method: str, path: str, query_params: str=None, request_data=None) ->  None:
        headers = {
            "x-api-key": self.x_api_key,
            "organisation": self.organisation_id,
            "user_type": self.user_type,
            "location": 'new_york'
        }
        resp = requests.request(method, self.base_api_endpoint + path, data=request_data or {}, headers=headers)
        if resp.status_code == 200:
            raw_response = resp.json()
            if raw_response.get("success"):
                return raw_response.get("data")

    def info(self) ->  Dict:
        info_resp = self._make_request('GET', 'auth/info')
        return info_resp
    
    

    def get_one_item(self, collection_name: str, params=None) ->  Dict:
        resp = self._make_request('GET', 'incollection/' + collection_name)
        if resp.get("items"):
            # return first elem
            return resp.get("items")[0]

    def get_list(self, collection_name: str, params=None) -> List[Dict]:
        resp = self._make_request('GET', 'incollection/' + collection_name)
        if resp.get("items"):
            return resp.get("items", [])
        


    def create_item(self, collection_name: str, data=None) ->  Dict:
        resp = self._make_request('POST', 'incollection/' + collection_name, request_data={"reqbody": data})
        if resp.get("data"):
            return resp.get("data")

    def update_item(self, collection_name: str, object_id: str, updated_data=None) ->  Dict:
        resp = self._make_request('PUT', 'incollection/' + collection_name + '/' + object_id, request_data={"reqbody": updated_data})
        if resp.get("data"):
            return resp.get("data")

    def delete_item(self, collection_name: str, object_id: str) -> Dict:
        resp = self._make_request('DELETE', 'incollection/' + collection_name + '/' + object_id)
        return resp
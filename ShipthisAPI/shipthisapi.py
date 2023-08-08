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
        fetched_response = requests.request(method, self.base_api_endpoint + path, data=request_data or {}, headers=headers, params=query_params)
        result = fetched_response.json()
        
        if fetched_response.status_code == 200:
            if result.get("success"):
                return result.get("data")
            else:
                error_message = result.get("errors") or "API call failed. Please check your internet connection or try again later"
                return error_message[0].get('message') if error_message[0].get('message') else "Please provide the necessary requirements or try again later"
        else:
            return "Internal Server error, please try again later"

    def info(self) ->  Dict:
        info_resp = self._make_request('GET', 'auth/info')
        return info_resp
    
    

    def get_one_item(self, collection_name: str, params=None) ->  Dict:
        resp = self._make_request('GET', 'incollection/' + collection_name)
        if  isinstance(resp, dict):
            if resp.get("items"):
                # return first elem
                return resp.get("items")[0]
        else:
            return resp

    def get_list(self, collection_name: str, params=None) -> List[Dict] or str:
        get_list_response = self._make_request('GET', 'incollection/' + collection_name, params)
        if isinstance(get_list_response, str):
            return get_list_response
        else:
            if get_list_response.get("items", False):
                return get_list_response.get("items", [])
            else:
                return get_list_response


    def create_item(self, collection_name: str, data=None) ->  Dict:
        resp = self._make_request('POST', 'incollection/' + collection_name, request_data={"reqbody": data})
        if  isinstance(resp, dict):
            if resp.get("data"):
                return resp.get("data")
        else:
            return resp

    def update_item(self, collection_name: str, object_id: str, updated_data=None) ->  Dict:
        resp = self._make_request('PUT', 'incollection/' + collection_name + '/' + object_id, request_data={"reqbody": updated_data})
        if  isinstance(resp, dict):
            if resp.get("data"):
                return resp.get("data")
        else:
            return resp

    def delete_item(self, collection_name: str, object_id: str) -> Dict:
        resp = self._make_request('DELETE', 'incollection/' + collection_name + '/' + object_id)
        # if  isinstance(resp, str):
        #     return resp
        # else:
        return resp
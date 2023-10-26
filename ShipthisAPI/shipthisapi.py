import requests
from typing import List, Dict, Union, Any
import json 
from .getCollection import get_Collection, update_delete, get_search_list_collection, get_full_search_list_collection


class ShipthisAPI:
    BASE_API_ENDPOINT = 'https://api.shipthis.co/api/v3/'

    def __init__(self, organisation: str, x_api_key:str, user_type='employee', region_id: str=None, location_id: str=None) -> None:
        self.x_api_key = x_api_key
        self.organisation_id = organisation
        self.user_type = user_type
        self.region_id = region_id
        self.location_id = location_id

    def set_region_location(self, region_id, location_id):
        self.region_id = region_id
        self.location_id = location_id

    def _make_request(self, method: str, path: str, query_params: Dict=None, request_data: Dict=None) -> Union[Dict, str]:
        headers = {
            "x-api-key": self.x_api_key,
            "organisation": self.organisation_id,
            "user_type": self.user_type,
            "location": 'new_york'
        }
        try:
            fetched_response = requests.request(method, self.BASE_API_ENDPOINT + path, json=request_data, headers=headers, params=query_params)
            fetched_response.raise_for_status() 
            result = fetched_response.json()

            if fetched_response.status_code == 200 and result.get("success", True):
                if (result.get('success')):
                    return "Successfully completed the request"
                # if (result.get('data', True)):
                #     return "Please provide the proper information to get all the desired results"
                return result.get("data")
            else:
                error_message = result.get("errors") or "API call failed. Please check your internet connection or try again later"
                return error_message[0].get('message') if error_message[0].get('message') else "Please provide the necessary requirements or try again later"
        except (requests.exceptions.RequestException, ValueError, Exception) as e:
            return f"An error occurred: {e}"

    def info(self) ->  Dict:
        return self._make_request('GET', 'auth/info')

    def get_one_item(self, collection_name: get_Collection) ->  Dict:
        resp = self._make_request('GET', f'incollection/{collection_name.collection_name}')
        if isinstance(resp, dict) and resp.get("items"):
            return resp.get("items")[0]
        return resp

    def get_list(self, collection_name: get_Collection,params=None) -> Union[List[Dict], str]:
        response = self._make_request('GET', f'incollection/{collection_name}',params)
        if isinstance(response, dict) and response.get("items"):
            return response.get("items")
        return response

    def create_item(self, collection_name: get_Collection, data: Dict) ->  Dict:
        resp = self._make_request('POST', f'incollection/{collection_name.collection_name}', request_data={"reqbody": data})
        return resp if isinstance(resp, dict) and resp.get("data") else resp

    def update_item(self, item_data: update_delete, updated_data: Dict=None) ->  Dict:
        resp = self._make_request('PUT', f'incollection/{item_data.collection_name}/{str(item_data.object_id)}', request_data={"reqbody": updated_data})
        return resp if isinstance(resp, dict) and resp.get("data") else resp

    def delete_item(self, item_data: update_delete) -> Dict:
        return self._make_request('DELETE', f'incollection/{item_data.collection_name}/{str(item_data.object_id)}')

    def get_search_list_collection(self, item_data: get_search_list_collection)  -> Dict:
        path = f'incollection/{item_data.collection_name}?search_query={item_data.query_filter}'
        return self._make_request('GET', path)

    def get_full_search_list_collection(self, item_data: get_full_search_list_collection) ->Dict:
        query_path = '&'.join([f"{key}={json.dumps(value) if not isinstance(value, str) else value}" for key, value in item_data.query_params.items()])
        path = f'incollection/{item_data.collection_name}?{query_path}'
        return self._make_request('GET', path)

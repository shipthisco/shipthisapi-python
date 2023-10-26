from ShipthisAPI.shipthisapi import ShipthisAPI
from ShipthisAPI.getCollection import get_Collection, update_delete, get_search_list_collection, get_full_search_list_collection
x_api_key = '<Your API Key>'
shipthisapi = ShipthisAPI(organisation='demo', x_api_key=x_api_key, region_id='usa', location_id='new_york')

# print(shipthisapi.get_list(collection_name="airport"))
# print(shipthisapi.get_list(collection_name="sea_shipment", params={"count": 2}))  # count is the number of records you need


# # Fucntion call for getting full search list with query parameteres
# search_data = update_delete(collection_name="airport", object_id="653a610e67c2e9c2bea3d301")
# print(shipthisapi.delete_item(item_data=search_data))

# query_payload = {
#     "search_query": "S",
#     "count": 25,
#     "page": 1,
#     "multi_sort": [{"sort_by": "created_at", "sort_order": "dsc"}],
#     "output_type": "json",
#     "meta": False,
#     "queryFilterV2": [],
#     "general_filter": {"job_status": {"$nin": ["closed", "cancelled", "ops_complete"]}},
#     "only": "job_id,shipment_name,shipment_status,customer_name.company.name,customer_name._id,customer_name._cls,customer_name._id,consignee_name.company.name,consignee_name._id,shipper_name.company.name,shipper_name._id,mawb_no,hawb_no",
#     "location": "new_york",
#     "region_override": False,
# }
# search_data = get_full_search_list_collection(collection_name="airport",query_params=query_payload)
# print(shipthisapi.get_full_search_list_collection(item_data=search_data))
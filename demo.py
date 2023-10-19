from ShipthisAPI.shipthisapi import ShipthisAPI

x_api_key = 'WyJqdW5haWRAc2hpcHRoaXMuY28iLCJkZW1vIl0.ZS0mOA.k2yBEld1jx7perTOqgLjYIELUkw'
shipthisapi = ShipthisAPI(organisation='demo', x_api_key=x_api_key, region_id='usa', location_id='new_york')

# print(shipthisapi.get_list(collection_name="invoice"))
# print(shipthisapi.get_list(collection_name="sea_shipment", params={"count": 2}))  # count is the number of records you need
# print(shipthisapi.get_search_list_collection(collection_name="airport",query_filter="Salekhard"))
query_payload = {
    "search_query": "Salekhard",
    "count": 25,
    "page": 1,
    "multi_sort": [{"sort_by": "created_at", "sort_order": "dsc"}],
    "output_type": "json",
    "meta": False,
    "queryFilterV2": [],
    "general_filter": {"job_status": {"$nin": ["closed", "cancelled", "ops_complete"]}},
    "only": "job_id,shipment_name,shipment_status,customer_name.company.name,customer_name._id,customer_name._cls,customer_name._id,consignee_name.company.name,consignee_name._id,shipper_name.company.name,shipper_name._id,mawb_no,hawb_no",
    "location": "new_york",
    "region_override": False,
}

print(shipthisapi.get_full_search_list_collection(collection_name="airport",query_params=query_payload)) 
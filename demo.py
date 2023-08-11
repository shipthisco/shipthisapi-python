from ShipthisAPI.shipthisapi import ShipthisAPI

x_api_key = ''
shipthisapi = ShipthisAPI(organisation='demo', x_api_key=x_api_key, region_id='usa', location_id='new_york')

print(shipthisapi.get_list(collection_name="invoice"))
print(shipthisapi.get_list(collection_name="sea_shipment", params={"count": 2}))  # count is the number of records you need

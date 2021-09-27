from ShipthisAPI.shipthisapi import ShipthisAPI


shipthisapi = ShipthisAPI('https://demo.manage.shipthis.co', 'demo', None)

print(shipthisapi.info())
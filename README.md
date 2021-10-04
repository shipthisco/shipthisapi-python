# ShipthisAPI Python 

[![PyPI version](https://badge.fury.io/py/shipthisapi-python.svg)](https://badge.fury.io/py/shipthisapi-python)

A Python wrapper package for ShipthisAPI for making api calls using python.


Features
--------

* Demo setup with ``demo.py``
* Simple Step API calls.

Quickstart
----------


Install the latest `shipthisapi-python`
if you haven't installed it yet.


    pip install shipthisapi-python


[Generate a API Key For your Organisation](https://shipthis.crisp.help/en/article/how-to-generate-an-api-key-1qnsq1d/?bust=1633352029281)


```python
from ShipthisAPI.shipthisapi import ShipthisAPI

x_api_key = '<your_api_key>'
organisation = 'demo'
region_id='<your_region_id>'
location_id='<your_location_id>'


shipthisapi = ShipthisAPI(organisation=organisation, x_api_key=x_api_key, region_id=region_id, location_id=location_id)


# Get Organisation/User Info 

print(shipthisapi.info())


# Get Invoice Collection List

print(shipthisapi.get_list(collection_name='invoice'))


```


Documentation
-----------

For more details related to available fields and operations check our [developer portal](https://developer.shipthis.co)


 Available Operations 

-  Get Organisation / User Information
-  Create New Collection Entry
-  Update Collection
-  Get Collection Items
-  Delete an existing collection item



Support
------------------

If you have any queries related to usage of the api please raise a issue [here](https://github.com/shipthisco/shipthisapi-python) 





# shipthisapi-python v3.0.0 Release

We're excited to announce the release of **shipthisapi-python v3.0.0** - now with full async support!

## What's New

### Async-First Design
The library has been completely rewritten to support async/await, making it perfect for modern Python applications like FastAPI, aiohttp, and other async frameworks.

```python
import asyncio
from ShipthisAPI import ShipthisAPI

async def main():
    client = ShipthisAPI(
        organisation="your_org_id",
        x_api_key="your_api_key"
    )

    await client.connect()

    # Fetch shipments
    shipments = await client.get_list("sea_shipment")

    # Update a document
    await client.patch_item(
        "fcl_load",
        "68a4f906743189ad061429a7",
        update_fields={"container_no": "CONT123"}
    )

asyncio.run(main())
```

### Custom Headers Support
Server-to-server authentication is now supported via custom headers:

```python
client = ShipthisAPI(
    organisation="org_id",
    custom_headers={
        "authorization": "Bearer your_token",
        # ... other custom headers
    }
)
```

### Simplified Field Updates
`patch_item` is now the recommended way to update document fields. It provides:
- Full field validation
- Workflow triggers
- Audit logging
- Business logic execution

## Breaking Changes

1. **All methods are now async** - You must use `await` when calling API methods
2. **`requests` replaced with `httpx`** - The library now uses `httpx` for HTTP calls
3. **Removed deprecated methods**:
   - `webhook_sync` - Use `patch_item` instead
   - `webhook_update` - Use `patch_item` instead

## Installation

```bash
pip install shipthisapi-python==3.0.0
```

Or update your requirements:
```
shipthisapi-python>=3.0.0
```

## Migration Guide

See [CHANGELOG.md](./CHANGELOG.md) for a detailed migration guide from v2.x to v3.x.

## Questions or Issues?

- Open an issue on [GitHub](https://github.com/shipthisco/shipthisapi-python/issues)
- Contact support at support@shipthis.co

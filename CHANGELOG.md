# Changelog

All notable changes to this project will be documented in this file.

## [3.0.0] - 2025-02-06

### Breaking Changes
- **Async-first**: All API methods are now async and require `await`
- Replaced `requests` library with `httpx` for async HTTP support
- Removed `webhook_sync` and `webhook_update` methods (use `patch_item` instead)

### Added
- Full async/await support using `httpx`
- `custom_headers` parameter for server-to-server authentication
- `create_reference_linked_field` method
- Per-request header override support

### Changed
- `x_api_key` is now optional (can use `custom_headers` for auth)
- `patch_item` is now the recommended method for updating document fields
- Updated all method signatures to be async

### Migration Guide

**Before (v2.x):**
```python
from ShipthisAPI import ShipthisAPI

client = ShipthisAPI(organisation="org_id", x_api_key="key")
client.connect()
items = client.get_list("shipment")
client.patch_item("fcl_load", doc_id, {"status": "done"})
```

**After (v3.x):**
```python
import asyncio
from ShipthisAPI import ShipthisAPI

async def main():
    client = ShipthisAPI(organisation="org_id", x_api_key="key")
    await client.connect()
    items = await client.get_list("shipment")
    await client.patch_item("fcl_load", doc_id, {"status": "done"})

asyncio.run(main())
```

## [2.2.0] - 2025-02-06

### Added
- `custom_headers` parameter for overriding default headers
- `create_reference_linked_field` method
- Per-request header override in `_make_request`

### Changed
- `x_api_key` is now optional
- Enhanced `patch_item` documentation

## [2.1.0] - 2025-01-15

### Added
- `primary_workflow_action` method for workflow transitions
- `secondary_workflow_action` method for sub-status changes
- `bulk_edit` method for batch updates

## [2.0.0] - 2024-12-01

### Added
- Complete rewrite with better error handling
- `ShipthisAPIError`, `ShipthisAuthError`, `ShipthisRequestError` exceptions
- Comprehensive CRUD operations
- Workflow operations
- Report views
- Third-party integrations (currency, places)
- Conversation methods
- File upload support

## [1.0.0] - 2024-06-01

### Added
- Initial release
- Basic API client functionality

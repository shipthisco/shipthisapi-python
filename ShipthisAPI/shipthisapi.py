"""Shipthis API Client.

An async Python client for the Shipthis public API.

Usage:
    import asyncio
    from ShipthisAPI import ShipthisAPI

    async def main():
        # Initialize the client
        client = ShipthisAPI(
            organisation="your_org_id",
            x_api_key="your_api_key",
            region_id="your_region",
            location_id="your_location"
        )

        # Connect and validate
        await client.connect()

        # Get items from a collection
        items = await client.get_list("shipment")

        # Patch document fields
        await client.patch_item("fcl_load", doc_id, {"status": "completed"})

    asyncio.run(main())
"""

from typing import Any, Dict, List, Optional
import json
import httpx


class ShipthisAPIError(Exception):
    """Base exception for Shipthis API errors."""

    def __init__(self, message: str, status_code: int = None, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ShipthisAuthError(ShipthisAPIError):
    """Raised when authentication fails."""

    pass


class ShipthisRequestError(ShipthisAPIError):
    """Raised when a request fails."""

    pass


class ShipthisAPI:
    """Async Shipthis API client for public API access.

    Attributes:
        base_api_endpoint: The base URL for the API.
        organisation_id: Your organisation ID.
        x_api_key: Your API key.
        user_type: User type for requests (default: "employee").
        region_id: Region ID for requests.
        location_id: Location ID for requests.
        timeout: Request timeout in seconds.
        custom_headers: Custom headers to override defaults.
    """

    DEFAULT_TIMEOUT = 30
    BASE_API_ENDPOINT = "https://api.shipthis.co/api/v3/"

    def __init__(
        self,
        organisation: str,
        x_api_key: str = None,
        user_type: str = "employee",
        region_id: str = None,
        location_id: str = None,
        timeout: int = None,
        base_url: str = None,
        custom_headers: Dict[str, str] = None,
    ) -> None:
        """Initialize the Shipthis API client.

        Args:
            organisation: Your organisation ID.
            x_api_key: Your API key (optional if using custom_headers with auth).
            user_type: User type for requests (default: "employee").
            region_id: Region ID for requests.
            location_id: Location ID for requests.
            timeout: Request timeout in seconds (default: 30).
            base_url: Custom base URL (optional, for testing).
            custom_headers: Custom headers that override defaults.
        """
        if not organisation:
            raise ValueError("organisation is required")

        self.x_api_key = x_api_key
        self.organisation_id = organisation
        self.user_type = user_type
        self.region_id = region_id
        self.location_id = location_id
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.base_api_endpoint = base_url or self.BASE_API_ENDPOINT
        self.custom_headers = custom_headers or {}
        self.organisation_info = None
        self.is_connected = False

    def set_region_location(self, region_id: str, location_id: str) -> None:
        """Set the region and location for subsequent requests.

        Args:
            region_id: Region ID.
            location_id: Location ID.
        """
        self.region_id = region_id
        self.location_id = location_id

    def _get_headers(self, override_headers: Dict[str, str] = None) -> Dict[str, str]:
        """Build request headers.

        Args:
            override_headers: Headers to override for this specific request.

        Returns:
            Dictionary of headers.
        """
        headers = {
            "organisation": self.organisation_id,
            "usertype": self.user_type,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.x_api_key:
            headers["x-api-key"] = self.x_api_key
        if self.region_id:
            headers["region"] = self.region_id
        if self.location_id:
            headers["location"] = self.location_id
        # Apply custom headers from init
        headers.update(self.custom_headers)
        # Apply per-request override headers
        if override_headers:
            headers.update(override_headers)
        return headers

    async def _make_request(
        self,
        method: str,
        path: str,
        query_params: Dict[str, Any] = None,
        request_data: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """Make an async HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            path: API endpoint path.
            query_params: Query parameters.
            request_data: Request body data.
            headers: Headers to override for this request.

        Returns:
            API response data.

        Raises:
            ShipthisAuthError: If authentication fails.
            ShipthisRequestError: If the request fails.
        """
        url = self.base_api_endpoint + path
        request_headers = self._get_headers(headers)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method,
                    url,
                    headers=request_headers,
                    params=query_params,
                    json=request_data,
                )
            except httpx.TimeoutException:
                raise ShipthisRequestError(
                    message="Request timed out",
                    status_code=408,
                )
            except httpx.ConnectError as e:
                raise ShipthisRequestError(
                    message=f"Connection error: {str(e)}",
                    status_code=0,
                )
            except httpx.RequestError as e:
                raise ShipthisRequestError(
                    message=f"Request failed: {str(e)}",
                    status_code=0,
                )

        # Handle authentication errors
        if response.status_code == 401:
            raise ShipthisAuthError(
                message="Authentication failed. Check your API key.",
                status_code=401,
            )
        if response.status_code == 403:
            raise ShipthisAuthError(
                message="Access denied. Check your permissions.",
                status_code=403,
            )

        # Parse response
        try:
            result = response.json()
        except json.JSONDecodeError:
            raise ShipthisRequestError(
                message=f"Invalid JSON response: {response.text[:200]}",
                status_code=response.status_code,
            )

        # Handle success
        if response.status_code in [200, 201]:
            if result.get("success"):
                return result.get("data")
            else:
                errors = result.get("errors", [])
                if errors and isinstance(errors, list) and len(errors) > 0:
                    error_msg = errors[0].get("message", "Unknown error")
                else:
                    error_msg = result.get("message", "API call failed")
                raise ShipthisRequestError(
                    message=error_msg,
                    status_code=response.status_code,
                    details=result,
                )

        # Handle other error status codes
        raise ShipthisRequestError(
            message=f"Request failed with status {response.status_code}",
            status_code=response.status_code,
            details=result if isinstance(result, dict) else {"response": str(result)},
        )

    # ==================== Connection ====================

    async def connect(self) -> Dict[str, Any]:
        """Connect and validate the API connection.

        Fetches organisation info and validates region/location.
        If no region/location is set, uses the first available one.

        Returns:
            Dictionary with region_id and location_id.

        Raises:
            ShipthisAPIError: If connection fails.
        """
        info = await self.info()
        self.organisation_info = info.get("organisation")

        if not self.region_id or not self.location_id:
            # Use first available region/location
            regions = self.organisation_info.get("regions", [])
            if regions:
                self.region_id = regions[0].get("region_id")
                locations = regions[0].get("locations", [])
                if locations:
                    self.location_id = locations[0].get("location_id")

        self.is_connected = True
        return {
            "region_id": self.region_id,
            "location_id": self.location_id,
            "organisation": self.organisation_info,
        }

    def disconnect(self) -> None:
        """Disconnect and clear credentials."""
        self.x_api_key = None
        self.is_connected = False

    # ==================== Info ====================

    async def info(self) -> Dict[str, Any]:
        """Get organisation and user info.

        Returns:
            Dictionary with organisation and user information.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        return await self._make_request("GET", "user-auth/info")

    # ==================== Collection CRUD ====================

    async def get_one_item(
        self,
        collection_name: str,
        doc_id: str = None,
        filters: Dict[str, Any] = None,
        only_fields: str = None,
    ) -> Optional[Dict[str, Any]]:
        """Get a single item from a collection.

        Args:
            collection_name: Name of the collection.
            doc_id: Document ID (optional, if not provided returns first item).
            filters: Query filters (optional).
            only_fields: Comma-separated list of fields to return.

        Returns:
            Document data or None if not found.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        if doc_id:
            path = f"incollection/{collection_name}/{doc_id}"
            params = {}
            if only_fields:
                params["only"] = only_fields
            return await self._make_request(
                "GET", path, query_params=params if params else None
            )
        else:
            params = {}
            if filters:
                params["query_filter_v2"] = json.dumps(filters)
            if only_fields:
                params["only"] = only_fields
            resp = await self._make_request(
                "GET", f"incollection/{collection_name}", params
            )
            if isinstance(resp, dict) and resp.get("items"):
                return resp.get("items")[0]
            return None

    async def get_list(
        self,
        collection_name: str,
        filters: Dict[str, Any] = None,
        search_query: str = None,
        page: int = 1,
        count: int = 20,
        only_fields: str = None,
        sort: List[Dict[str, Any]] = None,
        output_type: str = None,
        meta: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get a list of items from a collection.

        Args:
            collection_name: Name of the collection.
            filters: Query filters (optional).
            search_query: Search query string (optional).
            page: Page number (default: 1).
            count: Items per page (default: 20).
            only_fields: Comma-separated list of fields to return (optional).
            sort: List of sort objects [{"field": "name", "order": "asc"}] (optional).
            output_type: Output type (optional).
            meta: Include metadata (default: True).

        Returns:
            List of documents.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        params = {"page": page, "count": count}
        if filters:
            params["query_filter_v2"] = json.dumps(filters)
        if search_query:
            params["search_query"] = search_query
        if only_fields:
            params["only"] = only_fields
        if sort:
            params["multi_sort"] = json.dumps(sort)
        if output_type:
            params["output_type"] = output_type
        if not meta:
            params["meta"] = "false"

        response = await self._make_request(
            "GET", f"incollection/{collection_name}", params
        )

        if isinstance(response, dict):
            return response.get("items", [])
        return []

    async def search(
        self,
        collection_name: str,
        query: str,
        page: int = 1,
        count: int = 20,
        only_fields: str = None,
    ) -> List[Dict[str, Any]]:
        """Search for items in a collection.

        Args:
            collection_name: Name of the collection.
            query: Search query string.
            page: Page number (default: 1).
            count: Items per page (default: 20).
            only_fields: Comma-separated list of fields to return (optional).

        Returns:
            List of matching documents.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        return await self.get_list(
            collection_name,
            search_query=query,
            page=page,
            count=count,
            only_fields=only_fields,
        )

    async def create_item(
        self,
        collection_name: str,
        data: Dict[str, Any],
        ignore_new_required: bool = False,
        skip_sequence_if_exists: bool = False,
        replicate_count: int = 0,
        input_filters: Optional[Dict[str, Any]] = None,
        action_op_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new item in a collection with all advanced Shipthis features.

        Args:
            collection_name: Name of the collection.
            data: Document data.
            ignore_new_required: Ignore new required fields (default: False).
            skip_sequence_if_exists: Skip sequence if exists (default: False).
            replicate_count: Number of times to replicate the item (default: 0).
            input_filters: Input filters (optional).
            action_op_data: Action operation data (optional).

        Returns:
            Created document data.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        params = {}
        if replicate_count > 0:
            params["replicate_count"] = min(replicate_count, 100)
        if input_filters:
            params["input_filters"] = json.dumps(input_filters)

        request_payload = {
            "reqbody": data,
            "ignore_new_required": ignore_new_required,
            "skip_sequence_if_exists": skip_sequence_if_exists,
        }

        if action_op_data:
            request_payload["action_op_data"] = action_op_data

        resp = await self._make_request(
            "POST",
            f"incollection/{collection_name}",
            query_params=params,
            request_data=request_payload,
        )
        if isinstance(resp, dict) and resp.get("data"):
            return resp.get("data")
        return resp

    async def update_item(
        self,
        collection_name: str,
        object_id: str,
        updated_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update an existing item (full replacement).

        Args:
            collection_name: Name of the collection.
            object_id: Document ID.
            updated_data: Updated document data.

        Returns:
            Updated document data.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        resp = await self._make_request(
            "PUT",
            f"incollection/{collection_name}/{object_id}",
            request_data={"reqbody": updated_data},
        )
        if isinstance(resp, dict) and resp.get("data"):
            return resp.get("data")
        return resp

    async def patch_item(
        self,
        collection_name: str,
        object_id: str,
        update_fields: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Patch specific fields of an item.

        This is the recommended way to update document fields. It goes through
        full field validation, workflow triggers, audit logging, and business logic.

        Args:
            collection_name: Name of the collection (e.g., "sea_shipment", "fcl_load").
            object_id: Document ID.
            update_fields: Dictionary of field_id to value mappings.

        Returns:
            Updated document data.

        Raises:
            ShipthisAPIError: If the request fails.

        Example:
            await client.patch_item(
                "fcl_load",
                "68a4f906743189ad061429a7",
                update_fields={"container_no": "CONT123", "seal_no": "SEAL456"}
            )
        """
        return await self._make_request(
            "PATCH",
            f"incollection/{collection_name}/{object_id}",
            request_data={"update_fields": update_fields},
        )

    async def delete_item(self, collection_name: str, object_id: str) -> Dict[str, Any]:
        """Delete an item.

        Args:
            collection_name: Name of the collection.
            object_id: Document ID.

        Returns:
            Deletion response.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        return await self._make_request(
            "DELETE",
            f"incollection/{collection_name}/{object_id}",
        )

    # ==================== Workflow Operations ====================

    async def get_job_status(
        self, collection_name: str, object_id: str
    ) -> Dict[str, Any]:
        """Get the job status for a document.

        Args:
            collection_name: Name of the collection.
            object_id: Document ID.

        Returns:
            Job status data.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        return await self._make_request(
            "GET",
            f"workflow/{collection_name}/job_status/{object_id}",
        )

    async def set_job_status(
        self,
        collection_name: str,
        object_id: str,
        action_index: int,
    ) -> Dict[str, Any]:
        """Set the job status for a document.

        Args:
            collection_name: Name of the collection.
            object_id: Document ID.
            action_index: The index of the action to execute.

        Returns:
            Updated status data.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        return await self._make_request(
            "POST",
            f"workflow/{collection_name}/job_status/{object_id}",
            request_data={"action_index": action_index},
        )

    async def get_workflow(self, object_id: str) -> Dict[str, Any]:
        """Get a workflow configuration.

        Args:
            object_id: Workflow ID.

        Returns:
            Workflow data.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        return await self._make_request("GET", f"incollection/workflow/{object_id}")

    # ==================== Reports ====================

    async def get_report_view(
        self,
        report_name: str,
        start_date: str,
        end_date: str,
        post_data: Dict[str, Any] = None,
        output_type: str = "json",
        skip_meta: bool = True,
    ) -> Dict[str, Any]:
        """Get a report view.

        Args:
            report_name: Name of the report.
            start_date: Start date (YYYY-MM-DD or timestamp).
            end_date: End date (YYYY-MM-DD or timestamp).
            post_data: Additional filter data (optional).
            output_type: Output format (default: "json").
            skip_meta: Skip metadata (default: True).

        Returns:
            Report data.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "output_type": output_type,
            "skip_meta": "true" if skip_meta else "false",
        }
        if self.location_id:
            params["location"] = self.location_id

        return await self._make_request(
            "POST",
            f"report-view/{report_name}",
            query_params=params,
            request_data=post_data,
        )

    # ==================== Third-party Services ====================

    async def get_exchange_rate(
        self,
        source_currency: str,
        target_currency: str = "USD",
        date: int = None,
    ) -> Dict[str, Any]:
        """Get exchange rate between currencies.

        Args:
            source_currency: Source currency code (e.g., "EUR").
            target_currency: Target currency code (default: "USD").
            date: Date timestamp in milliseconds (optional, defaults to now).

        Returns:
            Exchange rate data.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        import time

        if date is None:
            date = int(time.time() * 1000)

        return await self._make_request(
            "GET",
            f"thirdparty/currency?source={source_currency}&target={target_currency}&date={date}",
        )

    async def autocomplete(
        self,
        reference_name: str,
        data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Get autocomplete suggestions for a reference field.

        Args:
            reference_name: Name of the reference (e.g., "port", "airport").
            data: Search data with query.

        Returns:
            List of suggestions.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        params = {}
        if self.location_id:
            params["location"] = self.location_id

        return await self._make_request(
            "POST",
            f"autocomplete-reference/{reference_name}",
            query_params=params if params else None,
            request_data=data,
        )

    async def search_location(self, query: str) -> List[Dict[str, Any]]:
        """Search for locations using Google Places.

        Args:
            query: Search query string.

        Returns:
            List of location suggestions.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        return await self._make_request(
            "GET",
            f"thirdparty/search-place-autocomplete?query={query}",
        )

    async def get_place_details(
        self,
        place_id: str,
        description: str = "",
    ) -> Dict[str, Any]:
        """Get details for a Google Place.

        Args:
            place_id: Google Place ID.
            description: Place description (optional).

        Returns:
            Place details.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        return await self._make_request(
            "GET",
            f"thirdparty/select-google-place?query={place_id}&description={description}",
        )

    # ==================== Conversations ====================

    async def create_conversation(
        self,
        view_name: str,
        document_id: str,
        conversation_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a conversation/message on a document.

        Args:
            view_name: Collection/view name.
            document_id: Document ID.
            conversation_data: Conversation data (message, type, etc.).

        Returns:
            Created conversation data.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        payload = {
            "conversation": conversation_data,
            "document_id": document_id,
            "view_name": view_name,
            "message_type": conversation_data.get("type", ""),
        }
        return await self._make_request("POST", "conversation", request_data=payload)

    async def get_conversations(
        self,
        view_name: str,
        document_id: str,
        message_type: str = "all",
        page: int = 1,
        count: int = 100,
    ) -> Dict[str, Any]:
        """Get conversations for a document.

        Args:
            view_name: Collection/view name.
            document_id: Document ID.
            message_type: Filter by message type (default: "all").
            page: Page number (default: 1).
            count: Items per page (default: 100).

        Returns:
            Conversations data.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        params = {
            "view_name": view_name,
            "document_id": document_id,
            "page": str(page),
            "count": str(count),
            "message_type": message_type,
            "version": "2",
        }
        return await self._make_request("GET", "conversation", query_params=params)

    # ==================== Bulk Operations ====================

    async def bulk_edit(
        self,
        collection_name: str,
        ids: List[str],
        update_data: Dict[str, Any],
        external_update_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Bulk edit multiple items in a collection.

        Args:
            collection_name: Name of the collection.
            ids: List of document IDs to update.
            update_data: Key-value pairs of fields to update.
            external_update_data: Extra data for external updates (optional).

        Returns:
            Update response.

        Raises:
            ShipthisAPIError: If the request fails.

        Example:
            await client.bulk_edit(
                "customer",
                ids=["5fdc00487f7636c97b9fa064", "608fe19fc33215427867f34e"],
                update_data={"company.fax_no": "12323231", "address.state": "California"}
            )
        """
        payload = {
            "data": {
                "ids": ids,
                "update_data": update_data,
            }
        }
        if external_update_data:
            payload["data"]["external_update_data"] = external_update_data

        return await self._make_request(
            "POST",
            f"incollection_group_edit/{collection_name}",
            request_data=payload,
        )

    # ==================== Workflow Actions ====================

    async def primary_workflow_action(
        self,
        collection: str,
        workflow_id: str,
        object_id: str,
        action_index: int,
        intended_state_id: str,
        start_state_id: str = None,
    ) -> Dict[str, Any]:
        """Trigger a primary workflow transition (status change on a record).

        Args:
            collection: Target collection (e.g., "pickup_delivery", "sea_shipment").
            workflow_id: Workflow status key (e.g., "job_status").
            object_id: The document's ID.
            action_index: Index of action within the status.
            intended_state_id: Intended resulting state ID (e.g., "ops_complete").
            start_state_id: Current/starting state ID (optional).

        Returns:
            Workflow action response with success status and resulting state.

        Raises:
            ShipthisAPIError: If the request fails.

        Example:
            await client.primary_workflow_action(
                collection="pickup_delivery",
                workflow_id="job_status",
                object_id="68a4f906743189ad061429a7",
                action_index=0,
                intended_state_id="ops_complete",
                start_state_id="closed"
            )
        """
        payload = {
            "action_index": action_index,
            "intended_state_id": intended_state_id,
        }
        if start_state_id:
            payload["start_state_id"] = start_state_id

        return await self._make_request(
            "POST",
            f"workflow/{collection}/{workflow_id}/{object_id}",
            request_data=payload,
        )

    async def secondary_workflow_action(
        self,
        collection: str,
        workflow_id: str,
        object_id: str,
        target_state: str,
        additional_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Trigger a secondary workflow transition (sub-status change).

        Args:
            collection: Target collection (e.g., "pickup_delivery").
            workflow_id: Secondary status key (e.g., "driver_status").
            object_id: The document's ID.
            target_state: Resulting sub-state (e.g., "to_pick_up").
            additional_data: Optional additional data to send with the request.

        Returns:
            Workflow action response.

        Raises:
            ShipthisAPIError: If the request fails.

        Example:
            await client.secondary_workflow_action(
                collection="pickup_delivery",
                workflow_id="driver_status",
                object_id="67ed10859b7cf551a19f813e",
                target_state="to_pick_up"
            )
        """
        payload = additional_data or {}

        return await self._make_request(
            "POST",
            f"workflow/{collection}/{workflow_id}/{object_id}/{target_state}",
            request_data=payload,
        )

    # ==================== File Upload ====================

    async def upload_file(
        self,
        file_path: str,
        file_name: str = None,
    ) -> Dict[str, Any]:
        """Upload a file.

        Args:
            file_path: Path to the file to upload.
            file_name: Custom file name (optional).

        Returns:
            Upload response with file URL.

        Raises:
            ShipthisAPIError: If the request fails.
        """
        import os

        if file_name is None:
            file_name = os.path.basename(file_path)

        upload_url = self.base_api_endpoint.replace("/api/v3/", "").rstrip("/")
        upload_url = upload_url.replace("api.", "upload.")
        upload_url = f"{upload_url}/api/v3/file-upload"

        headers = self._get_headers()
        # Remove Content-Type for multipart
        headers.pop("Content-Type", None)

        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_name, f)}
                async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                    response = await client.post(
                        upload_url,
                        headers=headers,
                        files=files,
                    )
        except FileNotFoundError:
            raise ShipthisRequestError(
                message=f"File not found: {file_path}",
                status_code=0,
            )
        except httpx.RequestError as e:
            raise ShipthisRequestError(
                message=f"Upload failed: {str(e)}",
                status_code=0,
            )

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"url": response.text}

        raise ShipthisRequestError(
            message=f"Upload failed with status {response.status_code}",
            status_code=response.status_code,
        )

    # ==================== Reference Linked Fields ====================

    async def create_reference_linked_field(
        self,
        collection_name: str,
        doc_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a reference-linked field on a document.

        Args:
            collection_name: Collection name.
            doc_id: Document ID.
            payload: Field data to create.

        Returns:
            API response.

        Raises:
            ShipthisAPIError: If the request fails.

        Example:
            await client.create_reference_linked_field(
                "sea_shipment",
                "68a4f906743189ad061429a7",
                payload={"field_name": "containers", "data": {...}}
            )
        """
        return await self._make_request(
            "POST",
            f"incollection/create-reference-linked-field/{collection_name}/{doc_id}",
            request_data=payload,
        )

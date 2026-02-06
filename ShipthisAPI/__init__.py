# __variables__ with double-quoted values will be available in setup.py
__version__ = "2.2.0"

from .shipthisapi import (
    ShipthisAPI,
    ShipthisAPIError,
    ShipthisAuthError,
    ShipthisRequestError,
)

__all__ = [
    "ShipthisAPI",
    "ShipthisAPIError",
    "ShipthisAuthError",
    "ShipthisRequestError",
]
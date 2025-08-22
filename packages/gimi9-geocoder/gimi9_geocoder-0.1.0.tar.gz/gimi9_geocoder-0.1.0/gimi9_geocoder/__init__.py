"""
gimi9_geocoder - A Python library for geocoding Korean addresses.

This package provides an interface to interact with the geocoding API, allowing users to perform geocoding operations and integrate results with pandas for data analysis.

Modules:
- client: Main client class for API interactions.
- exceptions: Custom exceptions for error handling.
- models: Data models for requests and responses.
- pandas_utils: Utility functions for pandas integration.
- utils: General utility functions for the library.
"""

from .client import GeocoderClient
from .exceptions import GeocoderError
from .models import GeocodeRequest, GeocodeResponse
from .pandas_utils import *

# from .pandas_utils import integrate_with_pandas
from .utils import validate_address

__all__ = [
    "GeocoderClient",
    "GeocoderError",
    "GeocodeRequest",
    "GeocodeResponse",
    # "integrate_with_pandas",
    "validate_address",
]

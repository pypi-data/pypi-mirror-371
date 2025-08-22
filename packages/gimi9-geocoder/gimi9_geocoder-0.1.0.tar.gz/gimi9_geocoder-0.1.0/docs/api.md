# Korean Geocoder API Documentation

## Overview

The `gimi9_geocoder` library provides a simple interface for geocoding Korean addresses using a RESTful API. This document outlines the available methods, parameters, and return values for the library's API.

## API Endpoints

### Geocoding

#### `geocode(address: str) -> GeocodeResult`

Geocodes a single address.

- **Parameters:**
  - `address` (str): The address to be geocoded.

- **Returns:**
  - `GeocodeResult`: An object containing the geocoding result, including coordinates and additional information.

#### Example:

```python
from gimi9_geocoder.client import KoreanGeocoder

geocoder = KoreanGeocoder()
result = geocoder.geocode("서울특별시 강남구 역삼동")
print(result)
```

### Batch Geocoding

#### `batch_geocode(addresses: List[str]) -> GeocodeSummary`

Geocodes multiple addresses in a single request.

- **Parameters:**
  - `addresses` (List[str]): A list of addresses to be geocoded.

- **Returns:**
  - `GeocodeSummary`: A summary of the geocoding results, including total counts and individual results.

#### Example:

```python
addresses = [
    "서울특별시 강남구 역삼동",
    "부산광역시 해운대구 우동"
]
summary = geocoder.batch_geocode(addresses)
print(summary)
```

### Reverse Geocoding

#### `reverse_geocode(x: float, y: float) -> ReverseGeocodeResult`

Performs reverse geocoding to retrieve the address for given coordinates.

- **Parameters:**
  - `x` (float): The longitude.
  - `y` (float): The latitude.

- **Returns:**
  - `ReverseGeocodeResult`: An object containing the address and additional information.

#### Example:

```python
result = geocoder.reverse_geocode(127.0276, 37.4979)
print(result)
```

## Error Handling

The library raises custom exceptions defined in `exceptions.py` for various error scenarios, such as invalid input or API errors. Users should handle these exceptions appropriately.

### Custom Exceptions

- `APIError`: Raised when there is an error with the API request.
- `InvalidInputError`: Raised when the input provided is invalid.

## Integration with Pandas

The `pandas_utils.py` module provides utility functions to integrate geocoding results with pandas DataFrames.

### Example:

```python
import pandas as pd
from gimi9_geocoder.pandas_utils import geocode_addresses

df = pd.DataFrame({"addresses": ["서울특별시 강남구 역삼동", "부산광역시 해운대구 우동"]})
geocoded_df = geocode_addresses(df, "addresses")
print(geocoded_df)
```

## Conclusion

The `gimi9_geocoder` library simplifies the process of geocoding Korean addresses and provides seamless integration with pandas for data analysis. For further details, please refer to the source code and examples provided in the repository.
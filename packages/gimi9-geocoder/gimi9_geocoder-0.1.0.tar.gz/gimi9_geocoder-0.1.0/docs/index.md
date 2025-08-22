# Gimi9 Geocoder Documentation

## Overview

The `gimi9_geocoder` library provides a simple and efficient way to perform geocoding operations for Korean addresses. It is designed to integrate seamlessly with pandas, allowing users to analyze geocoding results alongside their data.

## Features

- **Geocoding API Integration**: Easily convert Korean addresses into geographic coordinates (latitude and longitude).
- **Pandas Integration**: Utility functions to work with pandas DataFrames, making it easier to analyze and visualize geocoding results.
- **Custom Exceptions**: Handle errors gracefully with custom exceptions for API errors and invalid inputs.

## Installation

You can install the `gimi9_geocoder` library using pip:

```bash
pip install korean-geocoder
```

## Usage

### Basic Geocoding

To perform basic geocoding operations, you can use the `KoreanGeocoder` client:

```python
from gimi9_geocoder import KoreanGeocoder

geocoder = KoreanGeocoder()
result = geocoder.geocode("서울특별시 강남구 역삼동")
print(result)
```

### Pandas Integration

For users working with pandas, the library provides utility functions to integrate geocoding results directly into DataFrames:

```python
import pandas as pd
from gimi9_geocoder import geocode_addresses

df = pd.DataFrame({"addresses": ["서울특별시 강남구 역삼동", "부산광역시 해운대구 우동"]})
df["geocoded"] = geocode_addresses(df["addresses"])
print(df)
```

## Documentation

For detailed API documentation, please refer to [API Documentation](api.md).

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.
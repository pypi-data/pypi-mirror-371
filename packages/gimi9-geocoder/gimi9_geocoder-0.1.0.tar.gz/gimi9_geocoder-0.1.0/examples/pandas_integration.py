import asyncio
import pandas as pd

from gimi9_geocoder.client import GeocoderClient

# Sample DataFrame with addresses
data = {
    "address": [
        "서울특별시 강남구 테헤란로 123",
        "부산광역시 해운대구 해운대해변로 456",
        "대구광역시 중구 동성로 789",
    ]
}

df = pd.DataFrame(data)

# Initialize the Geocoder
geocoder = GeocoderClient(token="DEMO_TOKEN")  # Replace with your actual token


# Function to geocode addresses in the DataFrame
async def geocode_addresses(df):
    results = []
    for address in df["address"]:
        result = await geocoder.geocode(address)
        results.append(result)
    return results


# Main function to execute the geocoding
async def main():
    # Geocode the addresses and add results to the DataFrame
    df["geocode_results"] = await geocode_addresses(df)

    # Display the DataFrame with geocoding results
    print(df)


# Run the main function
asyncio.run(main())

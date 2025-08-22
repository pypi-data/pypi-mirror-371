import asyncio
from gimi9_geocoder.client import GeocoderClient


async def main():
    # Initialize the geocoder client
    client = GeocoderClient(token="DEMO_TOKEN")  # Replace with your actual token

    # Example address to geocode
    address_list = [
        "서울특별시 강남구 테헤란로 123",
        "서울특별시 송파구 송파대로8길 10",
        "서울특별시 송파구 양재대로72길 20",
        "서울특별시 구로구 고척로21나길 85-6",
        "서울특별시 노원구 월계로53길 21",
    ]

    # Perform geocoding
    result = await client.geocode("\n".join(address_list))

    # Print the result
    print("Geocoding result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

from gimi9_geocoder.client import GeocoderClient


def main():
    # GeocoderClient 초기화
    geocoder = GeocoderClient(token="DEMO_TOKEN")

    # 주소를 좌표로 변환 (지오코딩)
    result = geocoder.geocode("서울특별시 강남구 테헤란로 123")
    print(f"지오코딩 결과: {result}")

    # Bulk 지오코딩
    addresses = [
        "서울특별시 강남구 테헤란로 123",
        "부산광역시 해운대구 해운대해변로 349-25",
    ]
    bulk_result = geocoder.geocode(addresses)
    print(f"배치 지오코딩 결과: {bulk_result}")

    # 좌표를 주소로 변환 (역지오코딩)
    reverse_result = geocoder.reverse_geocode(127.1146829, 37.5138498)
    print(f"역지오코딩 결과: {reverse_result}")

    # 코드로 행정구역 형상 검색
    regions = geocoder.region(type="hd", code="1114055000,4111760000", yyyymm="202506")
    print(f"행정구역 형상 검색 결과: {regions}")

    # 행정동 이력
    hd_history = geocoder.hd_history(x=127.075074, y=37.143834, yyyymm="202506")
    print(f"행정동 이력 결과: {hd_history}")

    # 토큰 통계
    token_stats = geocoder.token_stats()
    print(f"토큰 통계 결과: {token_stats}")


if __name__ == "__main__":
    main()

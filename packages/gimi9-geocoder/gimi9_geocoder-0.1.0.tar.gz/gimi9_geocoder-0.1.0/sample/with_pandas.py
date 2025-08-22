import pandas as pd

from gimi9_geocoder.client import GeocoderClient


def main():
    # GeocoderClient 초기화
    geocoder = GeocoderClient(token="DEMO_TOKEN")

    # DataFrame 생성
    data = {
        "name": [
            "장소1",
            "장소2",
            "장소3",
            "장소4",
            "장소5",
            "장소6",
            "장소7",
            "장소8",
        ],
        "address": [
            "서울특별시 중구 세종대로 110 서울특별시청",
            "부산광역시 연제구 중앙대로 1001(연산동) 부산광역시청",
            "대구광역시 중구 공평로 88 (동인동1가) 대구광역시청",
            "인천광역시 남동구 정각로29 (구월동 1138) 인천광역시청",
            "광주광역시 서구 내방로 111(치평동) 광주광역시청",
            "대전 서구 둔산로 100 대전광역시청",
            "울산광역시 남구 중앙로 201 (신정동) 울산광역시청",
            "한누리대로 2130 (보람동) 세종특별자치시청",
        ],
    }

    df = pd.DataFrame(data)

    try:
        print("DataFrame으로 지오코딩 수행...")
        geocode_result = geocoder.geocode(df, address_col="address")
        print(f"지오코딩 결과:")
        print(geocode_result)
        print()
    except Exception as e:
        print(f"지오코딩 오류: {e}")
        print()

    # 리스트로도 테스트
    try:
        print("리스트로 지오코딩 수행...")
        addresses = df["address"].tolist()
        list_result = geocoder.geocode(addresses)
        print(f"리스트 지오코딩 결과:")
        print(list_result)
        print()
    except Exception as e:
        print(f"리스트 지오코딩 오류: {e}")
        print()

    # 단일 문자열로도 테스트
    try:
        print("단일 주소로 지오코딩 수행...")
        single_result = geocoder.geocode("서울특별시 강남구 테헤란로 152")
        print(f"단일 주소 지오코딩 결과:")
        print(single_result)
        print()
    except Exception as e:
        print(f"단일 주소 지오코딩 오류: {e}")
        print()

    # 리버스 지오코딩 (단순)
    try:
        print("리버스 지오코딩 수행...")
        reverse_result = geocoder.reverse_geocode(127.1146829, 37.5138498)
        print(f"리버스 지오코딩 결과: {reverse_result}")
        print()
    except Exception as e:
        print(f"리버스 지오코딩 오류: {e}")
        print()

    # 리버스 지오코딩 (DataFrame)
    try:
        print("리버스 지오코딩 (DataFrame) 수행...")
        df_xy = pd.DataFrame(columns=["x", "y"])
        df_xy["x"] = geocode_result["geometry"].x
        df_xy["y"] = geocode_result["geometry"].y
        df_reversed = geocoder.reverse_geocode(x_col="x", y_col="y", coordinates=df_xy)
        print(f"리버스 지오코딩 (DataFrame) 결과:")
        print(df_reversed)
        print()
    except Exception as e:
        print(f"리버스 지오코딩 (DataFrame) 오류: {e}")
        print()

    # 리버스 지오코딩 (GeoDataFrame)
    try:
        print("리버스 지오코딩 (DataFrame) 수행...")
        df_reversed = geocoder.reverse_geocode(coordinates=geocode_result)
        print(f"리버스 지오코딩 (DataFrame) 결과:")
        print(df_reversed)
        print()
    except Exception as e:
        print(f"리버스 지오코딩 (DataFrame) 오류: {e}")
        print()

    # 코드로 행정구역 형상 검색
    try:
        print("행정구역 형상 검색...")
        regions = geocoder.region(
            type="hd", code="1114055000,4111760000", yyyymm="202506"
        )
        print(f"행정구역 형상 검색 결과: {regions}")
        print()
    except Exception as e:
        print(f"행정구역 형상 검색 오류: {e}")
        print()

    # 행정동 이력
    try:
        print("행정동 이력 검색...")
        hd_history = geocoder.hd_history(x=127.075074, y=37.143834, yyyymm="202506")
        print(f"행정동 이력 결과: {hd_history}")
        print()
    except Exception as e:
        print(f"행정동 이력 검색 오류: {e}")
        print()

    # 행정동 이력 (전체 이력)
    try:
        print("행정동 이력 검색...")
        hd_history = geocoder.hd_history(x=127.075074, y=37.143834)
        print(f"행정동 이력 결과: {hd_history}")
        print()
    except Exception as e:
        print(f"행정동 이력 검색 오류: {e}")
        print()

    # 토큰 통계
    try:
        print("토큰 통계 조회...")
        token_stats = geocoder.token_stats()
        print(f"토큰 통계 결과: {token_stats}")
        print()
    except Exception as e:
        print(f"토큰 통계 조회 오류: {e}")
        print()


if __name__ == "__main__":
    main()

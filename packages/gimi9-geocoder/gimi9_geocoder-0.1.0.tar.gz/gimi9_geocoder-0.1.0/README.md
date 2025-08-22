# Gimi9 Geocoder

한국 주소 지오코딩을 위한 Python 라이브러리입니다. 주소를 좌표로 변환하거나, 좌표를 주소로 변환하는 기능을 제공하며, pandas와 geopandas를 활용한 데이터 분석과 GIS 작업에 최적화되어 있습니다.

## API 토큰 발급

서비스를 이용하려면 API 토큰이 필요합니다. [geocode.gimi9.com](https://geocode.gimi9.com/)에서 API 토큰을 발급받으세요.

## 주요 기능

- **다양한 입력 형식 지원**: 단일 주소(str), 주소 리스트(List[str]), pandas DataFrame 지원
- **지오코딩**: 한국 주소를 위도/경도 좌표로 변환
- **역지오코딩**: 좌표를 도로명주소와 지번주소로 변환
- **Pandas/GeoPandas 통합**: DataFrame을 활용한 대량 주소 처리
- **행정구역 정보**: 한국 행정구역(시도/시군구/행정동) 형상 조회
- **이력 조회**: 행정구역 변화 이력 조회
- **토큰 관리**: API 토큰 사용량 통계 확인

## 설치

pip를 사용하여 라이브러리를 설치할 수 있습니다:

```bash
pip install gimi9-geocoder
```

## 시작하기

### 기본 사용법

```python
from gimi9_geocoder.client import GeocoderClient

# 클라이언트 초기화
geocoder = GeocoderClient(token="YOUR_API_TOKEN")

# 단일 주소 지오코딩
result = geocoder.geocode("서울특별시 강남구 테헤란로 123")
print(result)

# 여러 주소 일괄 지오코딩
addresses = [
    "서울특별시 강남구 테헤란로 123",
    "부산광역시 해운대구 해운대해변로 456",
    "대구광역시 중구 동성로 789"
]
result = geocoder.geocode(addresses)
print(result)
```

### DataFrame 활용

```python
import pandas as pd
from gimi9_geocoder.client import GeocoderClient

# 주소가 포함된 DataFrame 생성
data = {
    "name": ["서울시청", "부산시청", "대구시청", "인천시청"],
    "address": [
        "서울특별시 중구 세종대로 110 서울특별시청",
        "부산광역시 연제구 중앙대로 1001(연산동) 부산광역시청",
        "대구광역시 중구 공평로 88 (동인동1가) 대구광역시청",
        "인천광역시 남동구 정각로29 (구월동 1138) 인천광역시청"
    ]
}
df = pd.DataFrame(data)

# DataFrame을 사용한 지오코딩
geocoder = GeocoderClient(token="YOUR_API_TOKEN")
result = geocoder.geocode(df, address_col='address')
print(result)
# 결과는 GeoPandas DataFrame으로 반환되며, 원본 데이터와 지오코딩 결과가 합쳐집니다
```

### 역지오코딩

```python
# 단일 좌표 역지오코딩
result = geocoder.reverse_geocode(127.1146829, 37.5138498)
print(result)
# 결과: 도로명주소와 지번주소 정보가 포함된 GeoDataFrame

# DataFrame을 활용한 대량 역지오코딩
df_coords = pd.DataFrame({
    'x': [127.1146829, 129.0440854],
    'y': [37.5138498, 35.1021227]
})
result = geocoder.reverse_geocode(x_col="x", y_col="y", coordinates=df_coords)
print(result)

# GeoDataFrame을 활용한 역지오코딩
# geocode 결과를 바로 사용 가능
result = geocoder.reverse_geocode(coordinates=geocoded_gdf)
print(result)
```

### 행정구역 형상 조회

```python
# 행정동 형상 조회
regions = geocoder.region(
    type="hd",  # 행정동
    code="1114055000,4111760000",  # 행정동 코드
    yyyymm="202506"  # 기준년월
)
print(regions)

# 시군구 형상 조회
regions = geocoder.region(
    type="h23",  # 시군구
    code="11140,41117",  # 시군구 코드
    yyyymm="202506"
)

# 시도 형상 조회
regions = geocoder.region(
    type="h1",  # 시도
    code="11,41",  # 시도 코드
    yyyymm="202506"
)
```

### 행정구역 이력 조회

```python
# 특정 좌표의 행정구역 이력 조회
hd_history = geocoder.hd_history(
    x=127.075074, 
    y=37.143834, 
    yyyymm="202506"
)
print(hd_history)

# 전체 이력 조회 (yyyymm 생략)
hd_history = geocoder.hd_history(x=127.075074, y=37.143834)
print(hd_history)
```

### 토큰 사용량 확인

```python
# API 토큰 사용 통계 조회
token_stats = geocoder.token_stats()
print(token_stats)
```

## API 메서드

### geocode(locations, address_col=None)

주소를 좌표로 변환합니다.

**매개변수:**

- `locations`: 단일 주소(str), 주소 리스트(List[str]), 또는 DataFrame
- `address_col`: DataFrame 사용 시 주소가 있는 컬럼명 (DataFrame 사용 시 필수)

**반환값:** GeoPandas DataFrame (geometry 컬럼에 Point 객체)

### reverse_geocode(x_col, y_col, coordinates=None)

좌표를 주소로 변환합니다.

**매개변수:**

- `x_col`: X좌표 값 또는 DataFrame의 X좌표 컬럼명
- `y_col`: Y좌표 값 또는 DataFrame의 Y좌표 컬럼명  
- `coordinates`: 좌표가 포함된 DataFrame 또는 GeoDataFrame

**반환값:** GeoPandas DataFrame (도로명주소, 지번주소 정보 포함)

### region(type, code, yyyymm)

행정구역 형상을 조회합니다.

**매개변수:**

- `type`: 행정구역 유형 ("h1": 시도, "h23": 시군구, "hd": 행정동)
- `code`: 행정구역 코드 (쉼표로 구분하여 여러 개 가능)
- `yyyymm`: 기준년월 (예: "202506")

**반환값:** GeoPandas DataFrame (행정구역 형상 정보)

### hd_history(x, y, yyyymm=None)

특정 좌표의 행정구역 이력을 조회합니다.

**매개변수:**

- `x`: X좌표 (경도)
- `y`: Y좌표 (위도)
- `yyyymm`: 기준년월 (생략 시 전체 이력)

**반환값:** 행정구역 이력 정보 (dict)

### token_stats()

API 토큰 사용량 통계를 조회합니다.

**반환값:** 토큰 사용량 통계 (dict)

## 예제

더 자세한 사용 예제는 다음 파일들을 참고하세요:

- `sample/simple.py`: 기본 사용법
- `sample/with_pandas.py`: pandas DataFrame 활용
- `sample/notebook.ipynb`: Jupyter Notebook 예제 (시각화 포함)

## Jupyter Notebook에서 사용하기

```python
# 패키지 설치
%pip install gimi9-geocoder

import pandas as pd
import geopandas as gpd
import folium
from gimi9_geocoder.client import GeocoderClient

# 지오코딩 후 지도 시각화
geocoder = GeocoderClient(token="YOUR_API_TOKEN")
gdf = geocoder.geocode("서울특별시 강남구 테헤란로 123")

# Folium을 사용한 지도 시각화
m = folium.Map(location=[37.5665, 126.9780], zoom_start=10)
for idx, row in gdf.iterrows():
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=row['address']
    ).add_to(m)
m
```

## 의존성

이 패키지는 다음 라이브러리들을 사용합니다:

- `httpx`: HTTP 클라이언트
- `pandas`: 데이터 조작 및 분석
- `geopandas`: 공간 데이터 처리
- `shapely`: 기하학적 객체 조작

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참고하세요.

## 기여하기

기여를 환영합니다! 개선사항이나 버그 수정을 위해 Pull Request를 제출하거나 Issue를 열어주세요.

## 문의

- 작성자: gisman
- 이메일: <gisman@gmail.com>
- GitHub: <https://github.com/gisman/gimi9_geocoder>

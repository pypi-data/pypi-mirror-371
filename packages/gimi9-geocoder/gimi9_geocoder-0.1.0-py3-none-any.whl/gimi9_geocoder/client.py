import httpx
import json
from typing import Union, List, Optional, Any
from io import StringIO
from shapely.geometry import shape

import pandas as pd
import geopandas as gpd
from shapely import wkt


class GeocoderClient:
    def __init__(
        self, base_url: str = "https://geocode-api.gimi9.com", token: str = None
    ):
        self.base_url = base_url
        self.token = token

    def _geocode(self, addresses: List[str]):
        COLUMNS_REMOVE = [
            "bm",
            "hash",
            "toksString",
            "address",
            "hd_history",
            "inputaddr",
        ]

        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/geocode",
                headers={"Authorization": self.token},
                json={"q": addresses},
            )
            response.raise_for_status()
            results = response.json().get("results")
            for r in results:
                for col in COLUMNS_REMOVE:
                    r.pop(col, None)

        return results

    def geocode(
        self, locations: Union[str, List[str], Any], address_col: Optional[str] = None
    ):
        """
        주소를 지오코딩합니다.

        Args:
            address: 단일 주소 (str), 주소 리스트 (List[str]), 또는 데이터프레임 (pd.DataFrame)
            address_col: 데이터프레임 사용 시 주소가 있는 열 이름 (데이터프레임 입력 시 필수)

        Returns:
            API로부터 받은 지오코딩 결과
        """
        # Handle different input types
        addresses = []
        if isinstance(locations, str):
            addresses = locations.splitlines() if "\n" in locations else [locations]
        elif isinstance(locations, list):
            addresses = locations
            results = self._geocode(addresses)

        if addresses:
            results = self._geocode(addresses)

            if not results:
                return gpd.GeoDataFrame(
                    columns=["address", "geometry"], crs="EPSG:4326"
                )

            # 주소와 결과를 딕셔너리 리스트로 결합합니다.
            combined_results = [
                {"address": addr, **res} for addr, res in zip(addresses, results)
            ]

            if all(col in combined_results[0] for col in ["x_axis", "y_axis"]):
                geometries = [
                    shape(
                        {"type": "Point", "coordinates": (res["x_axis"], res["y_axis"])}
                    )
                    for res in combined_results
                ]
                for res in combined_results:
                    res.pop("x_axis", None)
                    res.pop("y_axis", None)
                gdf = gpd.GeoDataFrame(
                    combined_results, geometry=geometries, crs="EPSG:4326"
                )
                return gdf

            raise ValueError(
                "Missing required columns 'x_axis' and 'y_axis' in results"
            )

        if isinstance(locations, pd.DataFrame):
            if address_col is None:
                raise ValueError(
                    "address_col parameter is required when using DataFrame input"
                )
            if address_col not in locations.columns:
                raise ValueError(f"Column '{address_col}' not found in DataFrame")
            addresses = locations[address_col].tolist()
            results = self._geocode(addresses)

            if all(col in results[0] for col in ["x_axis", "y_axis"]):
                geometries = [
                    shape(
                        {"type": "Point", "coordinates": (res["x_axis"], res["y_axis"])}
                    )
                    for res in results
                ]
                for res in results:
                    res.pop("x_axis", None)
                    res.pop("y_axis", None)
                gdf = gpd.GeoDataFrame(results, geometry=geometries, crs="EPSG:4326")

            # Combine the original DataFrame with the GeoDataFrame
            combined_gdf = gpd.GeoDataFrame(
                pd.concat([locations, gdf], axis=1), crs="EPSG:4326"
            )
            return combined_gdf

    def _reverse_geocode(self, x_axis: float, y_axis: float):
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/reverse_geocode",
                params={"x": x_axis, "y": y_axis, "token": self.token},
            )
            response.raise_for_status()
            result = response.json()
            road_addr = result.get("road_addr") or {}
            jibun_addr = result.get("jibun_addr") or {}
            plat_result = {
                "ADR_MNG_NO": road_addr.get("ADR_MNG_NO"),
                "yyyymm_road": road_addr.get("yyyymm"),
                "address_road": road_addr.get("address"),
                "geom_road": road_addr.get("geom"),
                "PNU": jibun_addr.get("PNU"),
                "yyyymm_jibun": jibun_addr.get("yyyymm"),
                "address_jibun": jibun_addr.get("address"),
                "geom_jibun": jibun_addr.get("geom"),
            }
            return plat_result

    def reverse_geocode(
        self,
        x_col: Union[str, float] = None,
        y_col: Union[str, float] = None,
        coordinates: Union[pd.DataFrame, gpd.GeoDataFrame] = None,
    ):
        if coordinates is None:
            if isinstance(x_col, str):
                x_axis = float(x_col)
            else:
                x_axis = x_col

            if isinstance(y_col, str):
                y_axis = float(y_col)
            else:
                y_axis = y_col

            result = self._reverse_geocode(x_axis, y_axis)

            try:
                geom_jibun = result.get("geom_jibun")
                if geom_jibun:
                    jibun_geometry = wkt.loads(geom_jibun)
                else:
                    jibun_geometry = None
                road_geometry = wkt.loads(result.get("geom_road"))
                gdf = gpd.GeoDataFrame(
                    [result], geometry=[jibun_geometry], crs="EPSG:4326"
                )
                gdf.drop(
                    columns=["geom_jibun", "geom_road"], inplace=True, errors="ignore"
                )
                gdf["road_geometry"] = [road_geometry]
                return gdf
            except KeyError:
                return gpd.GeoDataFrame(
                    columns=["ADR_MNG_NO", "PNU", "geometry", "road_geometry"],
                    crs="EPSG:4326",
                )
        elif isinstance(coordinates, gpd.GeoDataFrame):
            results = []
            for _, row in coordinates.iterrows():
                if row.geometry and not row.geometry.is_empty:
                    x_axis = row.geometry.x
                    y_axis = row.geometry.y
                    result = self._reverse_geocode(x_axis, y_axis)
                    results.append(result)
                else:
                    results.append({})

            df_result = pd.DataFrame(results)

            combined_gdf = coordinates.copy()

            jibun_geometries = df_result["geom_jibun"].apply(
                lambda geom: wkt.loads(geom) if geom else None
            )
            combined_gdf["jibun_geometry"] = jibun_geometries

            road_geometries = df_result["geom_road"].apply(
                lambda geom: wkt.loads(geom) if geom else None
            )
            combined_gdf["road_geometry"] = road_geometries
            df_result.drop(
                columns=["geom_jibun", "geom_road"], inplace=True, errors="ignore"
            )

            combined_gdf = combined_gdf.join(df_result)

            return combined_gdf
        elif isinstance(coordinates, pd.DataFrame):
            if not all(col in coordinates.columns for col in [x_col, y_col]):
                raise ValueError(
                    f"Columns '{x_col}' and '{y_col}' must exist in the DataFrame"
                )

            results = []
            for _, row in coordinates.iterrows():
                try:
                    x_axis = row[x_col]
                    y_axis = row[y_col]
                    result = self._reverse_geocode(x_axis, y_axis)
                    results.append(result)
                except Exception as e:
                    results.append({})

            jibun_geometries = [
                wkt.loads(result["geom_jibun"]) if result.get("geom_jibun") else None
                for result in results
            ]

            gdf = gpd.GeoDataFrame(results, geometry=jibun_geometries, crs="EPSG:4326")
            gdf["road_geometry"] = gdf["geom_road"].apply(
                lambda geom: wkt.loads(geom) if geom else None
            )
            gdf.drop(columns=["geom_jibun", "geom_road"], inplace=True, errors="ignore")
            combined_gdf = gpd.GeoDataFrame(
                pd.concat([coordinates, gdf], axis=1), crs="EPSG:4326"
            )
            return combined_gdf
        else:
            raise ValueError("Unsupported coordinates type")

    def region(self, type="hd", code="1114055000,4111760000", yyyymm="202506"):
        params = {"type": type, "code": code, "yyyymm": yyyymm, "token": self.token}
        with httpx.Client() as client:
            response = client.get(f"{self.base_url}/region", params=params)
            response.raise_for_status()
            results = response.json()

            geometries = [
                wkt.loads(feature["wkt"]) for feature in results if "wkt" in feature
            ]
            for feature in results:
                feature.pop("wkt", None)
            return gpd.GeoDataFrame(results, geometry=geometries, crs="EPSG:4326")

    def hd_history(self, x, y, yyyymm=None):
        params = {"x": x, "y": y, "yyyymm": yyyymm, "token": self.token}
        with httpx.Client() as client:
            response = client.get(f"{self.base_url}/hd_history", params=params)
            response.raise_for_status()
            return response.json()

    def token_stats(self):
        params = {"token": self.token}
        with httpx.Client() as client:
            response = client.get(f"{self.base_url}/token/stats", params=params)
            response.raise_for_status()
            return response.json()

    async def upload_file(self, file_path: str, target_crs: str = "EPSG:4326"):
        with open(file_path, "rb") as file:
            files = {"file": file}
            data = {"uploaded_filename": file_path, "target_crs": target_crs}
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/upload", data=data, files=files
                )
                response.raise_for_status()
                return response.json()

    async def geocode_file(
        self, file_path: str, download_dir: str, target_crs: str = "EPSG:4326"
    ):
        data = {
            "filepath": file_path,
            "download_dir": download_dir,
            "target_crs": target_crs,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/geocode_file", json=data)
            response.raise_for_status()
            return response.json()

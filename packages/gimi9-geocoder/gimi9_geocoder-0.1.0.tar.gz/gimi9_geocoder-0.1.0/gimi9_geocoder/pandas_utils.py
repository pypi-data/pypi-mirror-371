from typing import List
import pandas as pd
from .client import GeocoderClient


def geocode_addresses(df: pd.DataFrame, address_col: str) -> pd.DataFrame:
    if address_col not in df.columns:
        raise ValueError(f"Column '{address_col}' not found in DataFrame.")

    addresses = df[address_col].tolist()
    results = GeocoderClient().geocode(addresses)

    # Assuming results is a list of dictionaries with geocoding results
    for i, result in enumerate(results):
        for key, value in result.items():
            df.at[i, key] = value

    return df


def reverse_geocode_coordinates(
    df: pd.DataFrame, x_col: str, y_col: str
) -> pd.DataFrame:
    if x_col not in df.columns or y_col not in df.columns:
        raise ValueError(f"Columns '{x_col}' or '{y_col}' not found in DataFrame.")

    coordinates = df[[x_col, y_col]].values.tolist()
    results = [GeocoderClient().reverse_geocode(x, y) for x, y in coordinates]

    # Assuming results is a list of dictionaries with reverse geocoding results
    for i, result in enumerate(results):
        for key, value in result.items():
            df.at[i, key] = value

    return df


def add_geocoding_results(df: pd.DataFrame, results: List[dict]) -> pd.DataFrame:
    for result in results:
        df = df.append(result, ignore_index=True)
    return df

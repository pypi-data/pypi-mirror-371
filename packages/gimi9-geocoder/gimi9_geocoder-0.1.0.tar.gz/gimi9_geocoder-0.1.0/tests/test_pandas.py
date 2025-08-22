import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from gimi9_geocoder.pandas_utils import geocode_addresses


def test_geocode_addresses_success():
    """Test successful geocoding of addresses in a DataFrame"""
    # Arrange
    test_df = pd.DataFrame(
        {"address": ["123 Main St", "456 Elm St"], "city": ["Seoul", "Busan"]}
    )

    # Mock results from geocoder
    mock_results = [
        {"x": 126.978, "y": 37.566, "score": 0.95},
        {"x": 129.075, "y": 35.179, "score": 0.92},
    ]

    with patch("gimi9_geocoder.pandas_utils.GeocoderClient") as MockClient:
        # Set up the mock
        mock_instance = MockClient.return_value
        mock_instance.geocode.return_value = mock_results

        # Act
        result_df = geocode_addresses(test_df, "address")

        # Assert
        mock_instance.geocode.assert_called_once_with(["123 Main St", "456 Elm St"])
        assert "x" in result_df.columns
        assert "y" in result_df.columns
        assert "score" in result_df.columns
        assert result_df.at[0, "x"] == 126.978
        assert result_df.at[1, "y"] == 35.179
        assert result_df.shape[0] == 2


def test_geocode_addresses_column_not_found():
    """Test ValueError is raised when column is not in DataFrame"""
    # Arrange
    test_df = pd.DataFrame({"location": ["123 Main St"], "city": ["Seoul"]})

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        geocode_addresses(test_df, "address")

    assert "Column 'address' not found" in str(excinfo.value)


def test_geocode_addresses_empty_dataframe():
    """Test geocoding with empty DataFrame"""
    # Arrange
    test_df = pd.DataFrame(columns=["address"])

    with patch("gimi9_geocoder.pandas_utils.GeocoderClient") as MockClient:
        # Set up the mock
        mock_instance = MockClient.return_value
        mock_instance.geocode.return_value = []

        # Act
        result_df = geocode_addresses(test_df, "address")

        # Assert
        mock_instance.geocode.assert_called_once_with([])
        assert result_df.equals(test_df)


def test_geocode_addresses_null_values():
    """Test geocoding with null values in address column"""
    # Arrange
    test_df = pd.DataFrame(
        {"address": ["123 Main St", None, pd.NA], "city": ["Seoul", "Busan", "Incheon"]}
    )

    # Mock results - assuming the geocoder handles None/NA values
    mock_results = [
        {"x": 126.978, "y": 37.566, "score": 0.95},
        {"x": None, "y": None, "score": 0},
        {"x": None, "y": None, "score": 0},
    ]

    with patch("gimi9_geocoder.pandas_utils.GeocoderClient") as MockClient:
        # Set up the mock
        mock_instance = MockClient.return_value
        mock_instance.geocode.return_value = mock_results

        # Act
        result_df = geocode_addresses(test_df, "address")

        # Assert
        mock_instance.geocode.assert_called_once()
        assert result_df.at[0, "x"] == 126.978
        assert pd.isna(result_df.at[1, "x"])
        assert pd.isna(result_df.at[2, "x"])


def test_geocode_addresses_preserve_original_data():
    """Test that original data is preserved when geocoding"""
    # Arrange
    test_df = pd.DataFrame(
        {
            "id": [1, 2],
            "address": ["123 Main St", "456 Elm St"],
            "city": ["Seoul", "Busan"],
        }
    )

    mock_results = [{"x": 126.978, "y": 37.566}, {"x": 129.075, "y": 35.179}]

    with patch("gimi9_geocoder.pandas_utils.GeocoderClient") as MockClient:
        # Set up the mock
        mock_instance = MockClient.return_value
        mock_instance.geocode.return_value = mock_results

        # Act
        result_df = geocode_addresses(test_df, "address")

        # Assert
        assert result_df["id"].tolist() == [1, 2]
        assert result_df["city"].tolist() == ["Seoul", "Busan"]
        assert result_df["address"].tolist() == ["123 Main St", "456 Elm St"]

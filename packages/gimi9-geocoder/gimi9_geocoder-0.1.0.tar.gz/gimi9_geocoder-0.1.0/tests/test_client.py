import pytest
import httpx
from gimi9_geocoder.client import GeocoderClient


@pytest.mark.asyncio
async def test_batch_geocode_success():
    """Test successful batch geocoding operation"""
    # Arrange
    mock_response = {
        "results": [
            {"address": "123 Main St", "x": 126.978, "y": 37.566, "score": 0.95},
            {"address": "456 Elm St", "x": 127.001, "y": 37.588, "score": 0.92},
        ]
    }

    async def mock_transport(request):
        assert request.url == "https://geocode-api.gimi9.com/batch_geocode"
        assert request.method == "POST"
        assert request.content == b'{"q": ["123 Main St", "456 Elm St"]}'
        return httpx.Response(200, json=mock_response, request=request)

    client = GeocoderClient()

    # Act
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(mock_transport)
    ) as http_client:
        with pytest.monkeypatch.context() as m:
            m.setattr(httpx, "AsyncClient", lambda: http_client)
            result = await client.batch_geocode(["123 Main St", "456 Elm St"])

    # Assert
    assert result == mock_response
    assert "results" in result
    assert len(result["results"]) == 2


@pytest.mark.asyncio
async def test_batch_geocode_empty_list():
    """Test batch geocoding with empty address list"""
    # Arrange
    mock_response = {"results": []}

    async def mock_transport(request):
        assert request.url == "https://geocode-api.gimi9.com/batch_geocode"
        assert request.method == "POST"
        assert request.content == b'{"q": []}'
        return httpx.Response(200, json=mock_response, request=request)

    client = GeocoderClient()

    # Act
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(mock_transport)
    ) as http_client:
        with pytest.monkeypatch.context() as m:
            m.setattr(httpx, "AsyncClient", lambda: http_client)
            result = await client.batch_geocode([])

    # Assert
    assert result == mock_response
    assert "results" in result
    assert len(result["results"]) == 0


@pytest.mark.asyncio
async def test_batch_geocode_custom_base_url():
    """Test batch geocoding with custom base URL"""
    # Arrange
    mock_response = {
        "results": [
            {"address": "123 Main St", "x": 126.978, "y": 37.566, "score": 0.95}
        ]
    }
    custom_url = "https://custom-geocode.example.com"

    async def mock_transport(request):
        assert request.url == f"{custom_url}/batch_geocode"
        return httpx.Response(200, json=mock_response, request=request)

    client = GeocoderClient(base_url=custom_url)

    # Act
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(mock_transport)
    ) as http_client:
        with pytest.monkeypatch.context() as m:
            m.setattr(httpx, "AsyncClient", lambda: http_client)
            result = await client.batch_geocode(["123 Main St"])

    # Assert
    assert result == mock_response


@pytest.mark.asyncio
async def test_batch_geocode_http_error():
    """Test batch geocoding with HTTP error response"""

    # Arrange
    async def mock_transport(request):
        return httpx.Response(
            500, json={"error": "Internal Server Error"}, request=request
        )

    client = GeocoderClient()

    # Act/Assert
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(mock_transport)
    ) as http_client:
        with pytest.monkeypatch.context() as m:
            m.setattr(httpx, "AsyncClient", lambda: http_client)
            with pytest.raises(httpx.HTTPStatusError):
                await client.batch_geocode(["123 Main St"])

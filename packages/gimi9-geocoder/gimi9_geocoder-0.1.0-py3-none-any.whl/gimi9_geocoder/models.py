from pydantic import BaseModel
from typing import List, Optional


class GeocodeRequest(BaseModel):
    addresses: List[str]
    token: str = "DEMO_TOKEN"


class GeocodeResult(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    success: bool = False
    errmsg: str = ""
    inputaddr: str = ""


class GeocodeSummary(BaseModel):
    total_count: int
    success_count: int
    fail_count: int
    results: List[GeocodeResult]


class GeocodeResponse(BaseModel):
    summary: GeocodeSummary
    results: List[GeocodeResult]

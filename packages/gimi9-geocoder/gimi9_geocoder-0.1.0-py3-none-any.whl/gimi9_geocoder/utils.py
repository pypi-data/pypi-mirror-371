def validate_address(address: str) -> bool:
    if not address or not isinstance(address, str):
        return False
    return True

def format_geocode_result(result: dict) -> dict:
    formatted_result = {
        "address": result.get("address"),
        "coordinates": {
            "x": result.get("x_axis"),
            "y": result.get("y_axis"),
        },
        "success": result.get("success", False),
        "error_message": result.get("errmsg", ""),
    }
    return formatted_result

def extract_coordinates(data: list) -> list:
    coordinates = []
    for item in data:
        if "x_axis" in item and "y_axis" in item:
            coordinates.append((item["x_axis"], item["y_axis"]))
    return coordinates
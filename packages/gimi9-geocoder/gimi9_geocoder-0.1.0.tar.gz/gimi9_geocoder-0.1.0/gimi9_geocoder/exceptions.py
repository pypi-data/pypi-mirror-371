class GeocoderError(Exception):
    """Base class for all exceptions raised by the Korean Geocoder library."""
    pass


class APIError(GeocoderError):
    """Exception raised for errors related to the API."""
    
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


class InvalidInputError(GeocoderError):
    """Exception raised for invalid input provided to the geocoding functions."""
    
    def __init__(self, message: str):
        super().__init__(message)


class GeocodingError(GeocoderError):
    """Exception raised when geocoding fails for any reason."""
    
    def __init__(self, message: str):
        super().__init__(message)
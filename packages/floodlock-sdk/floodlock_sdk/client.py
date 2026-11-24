import requests
from typing import Optional, Dict, Any, List
from .exceptions import APIError, AuthenticationError, RateLimitError
from .models import RadiusCheckResult, ForecastResult

DEFAULT_MIRRORS = [
    "https://floodlock-backend.dahoremugdha.workers.dev",
    "https://floodlock-backend.dakshdadafit.workers.dev",
    "https://floodlock-backend.lanternmech.workers.dev"
]

class FloodLockClient:
    """Official Python SDK client for MeteoFlood & FloodLock Planetary Intelligence."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_urls: Optional[List[str]] = None,
        timeout_seconds: float = 8.0
    ):
        self.api_key = api_key
        self.base_urls = base_urls or list(DEFAULT_MIRRORS)
        self.timeout = timeout_seconds
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "FloodLock-Python-SDK/0.1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        last_error = None

        for base_url in self.base_urls:
            url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
            try:
                res = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=self._headers(),
                    timeout=self.timeout
                )
                if res.status_code == 401 or res.status_code == 403:
                    body = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
                    raise AuthenticationError(body.get("message", "Invalid or missing credentials"), res.status_code, body)
                
                if res.status_code == 429:
                    body = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
                    raise RateLimitError(body.get("message", "Rate limit exceeded"), res.status_code, body)

                if res.status_code >= 400:
                    body = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
                    raise APIError(body.get("message", f"HTTP {res.status_code}"), res.status_code, body)

                return res.json()
            except (AuthenticationError, RateLimitError):
                raise
            except Exception as e:
                last_error = e
                continue

        raise APIError(f"All FloodLock edge mirrors failed. Last error: {last_error}")

    def check_radius(self, lat: float, lon: float, radius_km: float = 150.0) -> RadiusCheckResult:
        """Check flood hazards and perimeter status within a given radius (km)."""
        params = {
            "lat": lat,
            "lon": lon,
            "radius_km": radius_km
        }
        data = self._request("GET", "/api/flood/radius-check", params=params)
        return RadiusCheckResult.from_dict(data)

    def get_forecast(self, lat: float, lon: float) -> ForecastResult:
        """Retrieve real-time 70B parameter ensemble forecast & physical safety floor analysis."""
        params = {
            "lat": lat,
            "lon": lon
        }
        data = self._request("GET", "/api/flood/forecast", params=params)
        return ForecastResult.from_dict(data)

    def ping(self) -> Dict[str, Any]:
        """Check connectivity to edge mirrors."""
        return self._request("GET", "/api/status")

    def get_usage(self) -> Dict[str, Any]:
        """Retrieve live daily quota consumption and remaining queries for this API key or session."""
        return self._request("GET", "/api/user/usage")

# Alias for brand symmetry
MeteoFloodClient = FloodLockClient


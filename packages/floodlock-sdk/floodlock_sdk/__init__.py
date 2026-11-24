"""
FloodLock & MeteoFlood Python SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Official Python client for MeteoFlood & FloodLock: Compound Planetary Hydrology,
70B Parameter Neural Ensemble & Real-Time Inundation Intelligence.

Architected by Lantern Mechatronics / Daksh Dahore.
"""

from .client import FloodLockClient, MeteoFloodClient
from .models import RadiusCheckResult, ForecastResult, Coordinates
from .exceptions import FloodLockError, APIError, AuthenticationError, RateLimitError

__version__ = "0.1.0"
__all__ = [
    "FloodLockClient",
    "MeteoFloodClient",
    "RadiusCheckResult",
    "ForecastResult",
    "Coordinates",
    "FloodLockError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
]


"""
RCK SDK for Python
"""

__version__ = "0.1.0"

# Core configuration
from .config import configure

# High-level API functions
from .api import (
    structured_transform,
    learn_from_examples,
    generate_text,
    generate_image,
    ImageResponse,
    ImageDetails,
)

# Pydantic Models for type hinting and advanced usage
from .model import (
    EndpointModel,
    AttractorInputBase,
    AttractorOutputBase
)

# Custom Exceptions
from .exceptions import (
    RCKException,
    RCKConfigurationError,
    RCKAPIError
)

__all__ = [
    # Configuration
    "configure",
    # High-level API
    "structured_transform",
    "learn_from_examples",
    "generate_text",
    "generate_image",
    # API Response Models
    "ImageResponse",
    "ImageDetails",
    # Base Models for Customization
    "EndpointModel",
    "AttractorInputBase",
    "AttractorOutputBase",
    # Exceptions
    "RCKException",
    "RCKConfigurationError",
    "RCKAPIError",
]

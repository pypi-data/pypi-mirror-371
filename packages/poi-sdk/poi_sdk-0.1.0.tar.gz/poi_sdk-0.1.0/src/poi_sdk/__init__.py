"""
Proof-of-Intent (PoI) Python SDK

A cryptographic framework for creating trustworthy AI agent transactions.
"""

__version__ = "0.1.0"
__author__ = "Giovanny Pietro"
__email__ = "giovanny.pietro@example.com"

from .receipt import PoIReceipt
from .generator import PoIGenerator
from .validator import PoIValidator
from .exceptions import PoIError, PoIValidationError, PoIGenerationError
from .config import PoIConfig

__all__ = [
    "PoIReceipt",
    "PoIGenerator", 
    "PoIValidator",
    "PoIError",
    "PoIValidationError",
    "PoIGenerationError",
    "PoIConfig",
]

"""
Processors for cloud-based document extraction.
"""

from .base_processor import BaseProcessor
from .cloud_processor import CloudProcessor

__all__ = [
    "BaseProcessor",
    "CloudProcessor", 
] 
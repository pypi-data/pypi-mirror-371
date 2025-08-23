"""
Sentinel-2 GEODES Processor

A Python package for searching, downloading, and processing Sentinel-2 satellite imagery
from the GEODES portal (CNES).
"""

__version__ = "0.1.0"
__author__ = "Adam Serghini"

from sentinel2_geodes.core.processor import Sentinel2Processor

__all__ = ["Sentinel2Processor"]

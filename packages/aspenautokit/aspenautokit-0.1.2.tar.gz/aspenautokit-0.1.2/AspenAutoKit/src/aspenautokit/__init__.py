"""
AspenAutoKit - A Python package for automating Aspen Plus simulations.
"""

from .aspen_connection import AspenConnection
from .excel_connection import ExcelReader
from .save_results import ResultsSaver
from .main import parallel_run, linear_run

__version__ = "0.1.0"
__author__ = "Vincent Bailey Ladd"
__email__ = ""

__all__ = [
    "AspenConnection",
    "ExcelReader", 
    "ResultsSaver",
    "close_aspen",
    "parallel_run",
    "linear_run"
]

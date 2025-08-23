"""
Inverse Projections Package

A collection of inverse projection techniques for dimensionality reduction.
Provides methods to map points from low-dimensional spaces back to high-dimensional spaces.
"""

from .nninv import NNinv
from .lamp import ILAMP
from .rbf import RBFinv
from .multilateration import MDSinv
from .gradient_map import get_gradient_map

__version__ = "0.1.0"
__author__ = "InverseProjections Contributors"

__all__ = [
    "NNinv",
    "ILAMP", 
    "RBFinv",
    "MDSinv",
    "get_gradient_map"
]


def main() -> None:
    print("Hello from inverse-projections!")

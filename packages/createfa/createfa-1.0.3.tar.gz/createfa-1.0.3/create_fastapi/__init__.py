"""FastAPI Generator - Un générateur d'applications FastAPI"""

__version__ = "1.0.2"
__author__ = "Bonito Fotso"
__email__ = "bonitofotso55@gmail.com"

from .cli import main
from .generator import FastAPIGenerator

__all__ = ["FastAPIGenerator", "main"]

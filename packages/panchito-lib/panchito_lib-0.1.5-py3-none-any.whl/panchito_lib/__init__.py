"""
My math library, panchito_lib.
This is a library created for my youtube channel: PythonIsGod
"""
from .primes import is_prime

__version__ = "0.1.5"
__author__ = "Pablo Soifer"
__email__ = "pablojapo@proton.me"""
__all__ = ["is_prime"]

def get_version():
    return __version__

def list_functions():
    return __all__

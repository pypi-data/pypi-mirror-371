"""
SageML
===
Library providing all necessary tools to use automatically adjusted Machine Learning techniques.
We aim to simplify the process of user input to maximum.
If unexperienced with machine learning or other domains of artificial intelligence user
will be able to with the use of this library solve problems that they should not be able to
solve with their knowledge, we will know that we fulfilled our goal.
"""
from .sageml import SageML
from .algorithms import __IMPORT_VARIABLE__  # For correct loading of algorithms
del __IMPORT_VARIABLE__

__all__ = ['SageML']

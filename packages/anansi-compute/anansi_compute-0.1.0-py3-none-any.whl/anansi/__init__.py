"""
Anansi Compute - Secure multi-cloud compute orchestration
"""

from .client import configure, compute, run_spark

__version__ = "0.1.0"
__all__ = ["configure", "compute", "run_spark"]
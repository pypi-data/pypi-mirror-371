"""
Sidecar module for PyWhatsWeb

Provides both Node.js and Python sidecar implementations.
"""

from .python_sidecar import start_python_sidecar, PythonSidecar

__all__ = ['start_python_sidecar', 'PythonSidecar']

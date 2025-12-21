"""
Two-Photon Lithography (TPL) Package
=====================================

A comprehensive Python package for two-photon lithography fabrication,
simulation, and optimization.

Author: Zeyad Mustafa
Date: December 2024
BTU Cottbus-Senftenberg

Modules
-------
design : Geometry creation and path planning
core : Hardware control (laser, stage, exposure)
simulation : Physical modeling and prediction
optimization : Parameter tuning and optimization
imaging : Alignment and monitoring
utils : Utility functions and helpers

Example
-------
>>> from tpl.design import Cube, PathPlanner
>>> from tpl.core import ExposureEngine
>>> 
>>> # Create geometry
>>> cube = Cube(size=10, center=(0, 0, 10))
>>> 
>>> # Generate toolpath
>>> planner = PathPlanner(layer_height=0.3, power=20)
>>> toolpath = planner.generate(cube)
>>> 
>>> # Execute fabrication
>>> engine = ExposureEngine()
>>> engine.connect()
>>> engine.execute(toolpath)
"""

__version__ = '1.0.0'
__author__ = 'Zeyad Mustafa'
__email__ = 'zeyad.mustafa@b-tu.de'
__license__ = 'MIT'

# Import main modules for convenience
try:
    from . import design
except ImportError as e:
    import warnings
    warnings.warn(f"Could not import design module: {e}")

try:
    from . import core
except ImportError:
    pass  # Core module may not be implemented yet

try:
    from . import simulation
except ImportError:
    pass

try:
    from . import optimization
except ImportError:
    pass

try:
    from . import utils
except ImportError:
    pass

# Quick access to commonly used classes
try:
    from .design import Geometry, Cube, Sphere, Cylinder
except ImportError:
    pass

__all__ = [
    'design',
    'core',
    'simulation',
    'optimization',
    'utils',
]
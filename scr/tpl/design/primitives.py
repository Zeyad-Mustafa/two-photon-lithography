"""
Geometric primitives for two-photon lithography
================================================

Basic 3D shapes: Cube, Sphere, Cylinder, Cone, etc.

Author: Zeyad Mustafa
Date: December 2024
BTU Cottbus-Senftenberg
"""

import numpy as np
from typing import Union, Tuple
from .geometry import Geometry

try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False


class Cube(Geometry):
    """
    Cube or rectangular box primitive.
    
    Parameters
    ----------
    size : float or tuple
        Edge length(s) in micrometers. 
        If float: cubic with equal sides
        If tuple: (width_x, width_y, height_z)
    center : tuple
        (x, y, z) center position in micrometers
    """
    
    def __init__(self, 
                 size: Union[float, Tuple[float, float, float]],
                 center: Tuple[float, float, float] = (0, 0, 0)):
        
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required. Install with: pip install trimesh")
        
        # Parse size
        if isinstance(size, (int, float)):
            if size <= 0:
                raise ValueError("Size must be positive")
            extents = [size, size, size]
        else:
            if len(size) != 3:
                raise ValueError("Size tuple must have 3 elements (x, y, z)")
            if any(s <= 0 for s in size):
                raise ValueError("All size dimensions must be positive")
            extents = list(size)
        
        # Create box
        mesh = trimesh.creation.box(extents=extents)
        
        # Move to center position
        mesh.apply_translation(center)
        
        super().__init__(mesh)
        
        # Store parameters
        self.size = size
        self.center = center


class Sphere(Geometry):
    """
    Sphere primitive.
    
    Parameters
    ----------
    radius : float
        Sphere radius in micrometers
    center : tuple
        (x, y, z) center position in micrometers
    resolution : int
        Tessellation resolution (subdivisions)
    """
    
    def __init__(self,
                 radius: float,
                 center: Tuple[float, float, float] = (0, 0, 0),
                 resolution: int = 32):
        
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required")
        
        if radius <= 0:
            raise ValueError("Radius must be positive")
        
        if resolution < 4:
            raise ValueError("Resolution must be at least 4")
        
        # Create sphere using icosphere for better tessellation
        mesh = trimesh.creation.icosphere(
            subdivisions=int(np.log2(resolution / 4)),
            radius=radius
        )
        
        # Move to center
        mesh.apply_translation(center)
        
        super().__init__(mesh)
        
        self.radius = radius
        self.center = center
        self.resolution = resolution


class Cylinder(Geometry):
    """
    Cylinder primitive.
    
    Parameters
    ----------
    radius : float
        Cylinder radius in micrometers
    height : float
        Cylinder height in micrometers
    center : tuple
        (x, y, z) center position in micrometers
    resolution : int
        Number of points around circumference
    """
    
    def __init__(self,
                 radius: float,
                 height: float,
                 center: Tuple[float, float, float] = (0, 0, 0),
                 resolution: int = 32):
        
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required")
        
        if radius <= 0:
            raise ValueError("Radius must be positive")
        
        if height <= 0:
            raise ValueError("Height must be positive")
        
        if resolution < 3:
            raise ValueError("Resolution must be at least 3")
        
        # Create cylinder (aligned along z-axis by default)
        mesh = trimesh.creation.cylinder(
            radius=radius,
            height=height,
            sections=resolution
        )
        
        # Move to center position
        mesh.apply_translation(center)
        
        super().__init__(mesh)
        
        self.radius = radius
        self.height = height
        self.center = center
        self.resolution = resolution


class Cone(Geometry):
    """
    Cone or truncated cone primitive.
    
    Parameters
    ----------
    radius_base : float
        Radius at base in micrometers
    radius_top : float
        Radius at top in micrometers (0 for pointed cone)
    height : float
        Cone height in micrometers
    center : tuple
        (x, y, z) center position in micrometers
    resolution : int
        Number of points around circumference
    """
    
    def __init__(self,
                 radius_base: float,
                 radius_top: float,
                 height: float,
                 center: Tuple[float, float, float] = (0, 0, 0),
                 resolution: int = 32):
        
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required")
        
        if radius_base <= 0:
            raise ValueError("Base radius must be positive")
        
        if radius_top < 0:
            raise ValueError("Top radius must be non-negative")
        
        if height <= 0:
            raise ValueError("Height must be positive")
        
        if resolution < 3:
            raise ValueError("Resolution must be at least 3")
        
        # Create cone manually
        # Generate vertices
        theta = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
        
        # Base circle
        base_x = radius_base * np.cos(theta)
        base_y = radius_base * np.sin(theta)
        base_z = np.zeros(resolution) - height / 2
        
        # Top circle (or point)
        if radius_top > 0:
            top_x = radius_top * np.cos(theta)
            top_y = radius_top * np.sin(theta)
        else:
            top_x = np.zeros(resolution)
            top_y = np.zeros(resolution)
        top_z = np.zeros(resolution) + height / 2
        
        # Combine vertices
        vertices = np.vstack([
            np.column_stack([base_x, base_y, base_z]),
            np.column_stack([top_x, top_y, top_z])
        ])
        
        # Generate faces
        faces = []
        
        # Side faces
        for i in range(resolution):
            next_i = (i + 1) % resolution
            # Triangle 1
            faces.append([i, next_i, resolution + i])
            # Triangle 2 (if not pointed cone)
            if radius_top > 0:
                faces.append([next_i, resolution + next_i, resolution + i])
        
        # Base cap
        base_center_idx = len(vertices)
        vertices = np.vstack([vertices, [0, 0, -height/2]])
        for i in range(resolution):
            next_i = (i + 1) % resolution
            faces.append([base_center_idx, next_i, i])
        
        # Top cap (if truncated)
        if radius_top > 0:
            top_center_idx = len(vertices)
            vertices = np.vstack([vertices, [0, 0, height/2]])
            for i in range(resolution):
                next_i = (i + 1) % resolution
                faces.append([top_center_idx, resolution + i, resolution + next_i])
        
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        mesh.fix_normals()
        
        # Move to center
        mesh.apply_translation(center)
        
        super().__init__(mesh)
        
        self.radius_base = radius_base
        self.radius_top = radius_top
        self.height = height
        self.center = center
        self.resolution = resolution


class Torus(Geometry):
    """
    Torus (donut shape) primitive.
    
    Parameters
    ----------
    major_radius : float
        Distance from center to tube center in micrometers
    minor_radius : float
        Tube radius in micrometers
    center : tuple
        (x, y, z) center position in micrometers
    resolution : int
        Tessellation resolution
    """
    
    def __init__(self,
                 major_radius: float,
                 minor_radius: float,
                 center: Tuple[float, float, float] = (0, 0, 0),
                 resolution: int = 32):
        
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required")
        
        if major_radius <= 0:
            raise ValueError("Major radius must be positive")
        
        if minor_radius <= 0:
            raise ValueError("Minor radius must be positive")
        
        if minor_radius >= major_radius:
            raise ValueError("Minor radius must be less than major radius")
        
        # Generate torus vertices
        u = np.linspace(0, 2 * np.pi, resolution)
        v = np.linspace(0, 2 * np.pi, resolution)
        
        U, V = np.meshgrid(u, v)
        
        x = (major_radius + minor_radius * np.cos(V)) * np.cos(U)
        y = (major_radius + minor_radius * np.cos(V)) * np.sin(U)
        z = minor_radius * np.sin(V)
        
        # Flatten and create vertices
        vertices = np.column_stack([
            x.flatten(),
            y.flatten(),
            z.flatten()
        ])
        
        # Generate faces
        faces = []
        for i in range(resolution - 1):
            for j in range(resolution - 1):
                idx = i * resolution + j
                # Two triangles per quad
                faces.append([idx, idx + 1, idx + resolution])
                faces.append([idx + 1, idx + resolution + 1, idx + resolution])
        
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        mesh.fix_normals()
        
        # Move to center
        mesh.apply_translation(center)
        
        super().__init__(mesh)
        
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.center = center
        self.resolution = resolution
"""
Geometry module for two-photon lithography
===========================================

Provides 3D geometry representation and manipulation for TPL fabrication.

Author: Zeyad Mustafa
Date: December 2024
BTU Cottbus-Senftenberg
"""

import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional, Union
import warnings

try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    warnings.warn("trimesh not installed. Some geometry features will be limited.")


class Geometry:
    """
    Base class for 3D geometry representation.
    
    This class provides methods for loading, manipulating, and exporting
    3D geometries for two-photon lithography fabrication.
    
    Attributes
    ----------
    mesh : trimesh.Trimesh
        Internal mesh representation
    """
    
    def __init__(self, mesh=None):
        """
        Initialize geometry from mesh.
        
        Parameters
        ----------
        mesh : trimesh.Trimesh, optional
            Mesh object. If None, creates empty geometry.
        """
        if not TRIMESH_AVAILABLE and mesh is not None:
            raise ImportError("trimesh is required for geometry operations. "
                            "Install with: pip install trimesh")
        
        self.mesh = mesh
        
    @classmethod
    def from_stl(cls, filepath: str) -> 'Geometry':
        """
        Load geometry from STL file.
        
        Parameters
        ----------
        filepath : str
            Path to STL file
            
        Returns
        -------
        Geometry
            Loaded geometry object
        """
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required. Install with: pip install trimesh")
        
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"STL file not found: {filepath}")
        
        if filepath.suffix.lower() not in ['.stl', '.STL']:
            raise ValueError(f"File must be STL format, got: {filepath.suffix}")
        
        mesh = trimesh.load(str(filepath))
        return cls(mesh)
    
    @classmethod
    def from_primitives(cls, primitives: List['Geometry']) -> 'Geometry':
        """
        Combine multiple primitive geometries.
        
        Parameters
        ----------
        primitives : list of Geometry
            List of geometry objects to combine
            
        Returns
        -------
        Geometry
            Combined geometry
        """
        if not primitives:
            raise ValueError("Cannot create geometry from empty primitive list")
        
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required")
        
        # Extract meshes
        meshes = [p.mesh for p in primitives]
        
        # Combine using trimesh
        combined = trimesh.util.concatenate(meshes)
        
        return cls(combined)
    
    @classmethod
    def from_function(cls, func, bounds, resolution=0.5):
        """
        Create geometry from implicit function.
        
        Parameters
        ----------
        func : callable
            Function f(x, y, z) that returns scalar field
        bounds : tuple
            ((x_min, x_max), (y_min, y_max), (z_min, z_max))
        resolution : float
            Grid resolution in micrometers
            
        Returns
        -------
        Geometry
            Generated geometry
        """
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required")
        
        # Create grid
        x = np.arange(bounds[0][0], bounds[0][1], resolution)
        y = np.arange(bounds[1][0], bounds[1][1], resolution)
        z = np.arange(bounds[2][0], bounds[2][1], resolution)
        
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        
        # Evaluate function
        values = func(X, Y, Z)
        
        # Create mesh using marching cubes (requires scikit-image)
        try:
            from skimage import measure
            verts, faces, normals, _ = measure.marching_cubes(values, level=0)
            
            # Scale vertices to actual coordinates
            verts[:, 0] = verts[:, 0] * resolution + bounds[0][0]
            verts[:, 1] = verts[:, 1] * resolution + bounds[1][0]
            verts[:, 2] = verts[:, 2] * resolution + bounds[2][0]
            
            mesh = trimesh.Trimesh(vertices=verts, faces=faces)
            return cls(mesh)
            
        except ImportError:
            raise ImportError("scikit-image required for implicit functions. "
                            "Install with: pip install scikit-image")
    
    @classmethod
    def from_line_segments(cls, segments: List[Tuple], width: float = 0.5):
        """
        Create geometry from line segments (for woodpile structures).
        
        Parameters
        ----------
        segments : list of tuples
            List of ((x1,y1,z1), (x2,y2,z2)) line segments
        width : float
            Line width in micrometers
            
        Returns
        -------
        Geometry
            Geometry created from lines
        """
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required")
        
        cylinders = []
        for start, end in segments:
            # Create cylinder for each line segment
            start = np.array(start)
            end = np.array(end)
            
            direction = end - start
            length = np.linalg.norm(direction)
            
            if length < 1e-6:
                continue
            
            # Create cylinder along z-axis
            cyl = trimesh.creation.cylinder(
                radius=width / 2,
                height=length,
                sections=16
            )
            
            # Rotate to align with direction
            z_axis = np.array([0, 0, 1])
            direction_norm = direction / length
            
            rotation_axis = np.cross(z_axis, direction_norm)
            rotation_angle = np.arccos(np.dot(z_axis, direction_norm))
            
            if np.linalg.norm(rotation_axis) > 1e-6:
                rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
                rotation_matrix = trimesh.transformations.rotation_matrix(
                    rotation_angle, rotation_axis
                )
                cyl.apply_transform(rotation_matrix)
            
            # Translate to position
            center = (start + end) / 2
            cyl.apply_translation(center)
            
            cylinders.append(cyl)
        
        if not cylinders:
            raise ValueError("No valid line segments provided")
        
        combined = trimesh.util.concatenate(cylinders)
        return cls(combined)
    
    def get_bounds(self) -> Tuple[Tuple[float, float], ...]:
        """
        Get bounding box of geometry.
        
        Returns
        -------
        tuple
            ((x_min, x_max), (y_min, y_max), (z_min, z_max))
        """
        if self.mesh is None:
            raise ValueError("Geometry is empty")
        
        bounds = self.mesh.bounds
        return (
            (bounds[0, 0], bounds[1, 0]),
            (bounds[0, 1], bounds[1, 1]),
            (bounds[0, 2], bounds[1, 2])
        )
    
    def get_volume(self) -> float:
        """
        Calculate volume of geometry.
        
        Returns
        -------
        float
            Volume in cubic micrometers
        """
        if self.mesh is None:
            raise ValueError("Geometry is empty")
        
        return self.mesh.volume
    
    def save(self, filepath: str, format: str = None):
        """
        Save geometry to file.
        
        Parameters
        ----------
        filepath : str
            Output file path
        format : str, optional
            File format ('stl', 'obj', etc.). Inferred from extension if None.
        """
        if self.mesh is None:
            raise ValueError("Cannot save empty geometry")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if format is None:
            format = filepath.suffix[1:]  # Remove leading dot
        
        self.mesh.export(str(filepath), file_type=format)
    
    def transform(self, matrix: np.ndarray):
        """
        Apply transformation matrix to geometry.
        
        Parameters
        ----------
        matrix : ndarray
            4x4 transformation matrix
        """
        if self.mesh is None:
            raise ValueError("Cannot transform empty geometry")
        
        self.mesh.apply_transform(matrix)
    
    def scale(self, factor_x: float, factor_y: float, factor_z: float):
        """
        Scale geometry by different factors in each axis.
        
        Parameters
        ----------
        factor_x, factor_y, factor_z : float
            Scaling factors for each axis
        """
        if self.mesh is None:
            raise ValueError("Cannot scale empty geometry")
        
        scale_matrix = np.array([
            [factor_x, 0, 0, 0],
            [0, factor_y, 0, 0],
            [0, 0, factor_z, 0],
            [0, 0, 0, 1]
        ])
        
        self.mesh.apply_transform(scale_matrix)
    
    def slice(self, z_positions: List[float]) -> List['Geometry']:
        """
        Slice geometry at specified z-heights.
        
        Parameters
        ----------
        z_positions : list of float
            Z-heights to slice at
            
        Returns
        -------
        list of Geometry
            Sliced cross-sections
        """
        if self.mesh is None:
            raise ValueError("Cannot slice empty geometry")
        
        slices = []
        for z in z_positions:
            try:
                # Get cross-section at this height
                section = self.mesh.section(
                    plane_origin=[0, 0, z],
                    plane_normal=[0, 0, 1]
                )
                
                if section is not None:
                    # Convert Path2D to 3D mesh for consistency
                    slice_geom = Geometry()
                    slice_geom._section = section  # Store 2D section
                    slice_geom.z_height = z
                    slices.append(slice_geom)
                    
            except Exception as e:
                warnings.warn(f"Failed to slice at z={z}: {e}")
                continue
        
        return slices
    
    def union(self, other: 'Geometry') -> 'Geometry':
        """
        Boolean union with another geometry.
        
        Parameters
        ----------
        other : Geometry
            Geometry to union with
            
        Returns
        -------
        Geometry
            Union result
        """
        if self.mesh is None or other.mesh is None:
            raise ValueError("Cannot perform union on empty geometry")
        
        result = self.mesh.union(other.mesh)
        return Geometry(result)
    
    def intersection(self, other: 'Geometry') -> 'Geometry':
        """
        Boolean intersection with another geometry.
        
        Parameters
        ----------
        other : Geometry
            Geometry to intersect with
            
        Returns
        -------
        Geometry
            Intersection result
        """
        if self.mesh is None or other.mesh is None:
            raise ValueError("Cannot perform intersection on empty geometry")
        
        result = self.mesh.intersection(other.mesh)
        return Geometry(result)
    
    def difference(self, other: 'Geometry') -> 'Geometry':
        """
        Boolean difference (subtract other from self).
        
        Parameters
        ----------
        other : Geometry
            Geometry to subtract
            
        Returns
        -------
        Geometry
            Difference result
        """
        if self.mesh is None or other.mesh is None:
            raise ValueError("Cannot perform difference on empty geometry")
        
        result = self.mesh.difference(other.mesh)
        return Geometry(result)
    
    @property
    def num_vertices(self) -> int:
        """Get number of vertices in mesh."""
        if self.mesh is None:
            return 0
        return len(self.mesh.vertices)
    
    @property
    def num_faces(self) -> int:
        """Get number of faces in mesh."""
        if self.mesh is None:
            return 0
        return len(self.mesh.faces)
    
    def __repr__(self) -> str:
        """String representation."""
        if self.mesh is None:
            return "Geometry(empty)"
        
        bounds = self.get_bounds()
        return (f"Geometry(vertices={self.num_vertices}, "
                f"faces={self.num_faces}, "
                f"volume={self.get_volume():.2f} μm³, "
                f"bounds=({bounds[0][0]:.1f},{bounds[1][0]:.1f},{bounds[2][0]:.1f}) "
                f"to ({bounds[0][1]:.1f},{bounds[1][1]:.1f},{bounds[2][1]:.1f}))")

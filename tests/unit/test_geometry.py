#!/usr/bin/env python3
"""
Unit tests for geometry module
===============================

Tests for the tpl.design.Geometry module and primitive shapes.

Author: Zeyad Mustafa
Date: December 2024
BTU Cottbus-Senftenberg

Run with: pytest tests/unit/test_geometry.py -v
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

# Import modules to test
from tpl.design import Geometry, Cube, Sphere, Cylinder, Cone


class TestCube:
    """Test cases for Cube primitive."""
    
    def test_cube_creation(self):
        """Test basic cube creation."""
        cube = Cube(size=10, center=(0, 0, 0))
        
        assert cube.size == 10
        assert cube.center == (0, 0, 0)
        
    def test_cube_bounds(self):
        """Test cube bounding box calculation."""
        cube = Cube(size=10, center=(0, 0, 10))
        bounds = cube.get_bounds()
        
        # Expected: -5 to 5 in x,y and 5 to 15 in z
        assert bounds[0] == (-5, 5)  # x bounds
        assert bounds[1] == (-5, 5)  # y bounds
        assert bounds[2] == (5, 15)  # z bounds
        
    def test_cube_volume(self):
        """Test cube volume calculation."""
        cube = Cube(size=10, center=(0, 0, 0))
        volume = cube.get_volume()
        
        expected = 10 ** 3  # 1000 μm³
        assert abs(volume - expected) < 0.1
        
    def test_rectangular_cube(self):
        """Test non-uniform cube (rectangular box)."""
        cube = Cube(size=(10, 5, 3), center=(0, 0, 0))
        bounds = cube.get_bounds()
        
        assert bounds[0] == (-5, 5)
        assert bounds[1] == (-2.5, 2.5)
        assert bounds[2] == (-1.5, 1.5)


class TestSphere:
    """Test cases for Sphere primitive."""
    
    def test_sphere_creation(self):
        """Test basic sphere creation."""
        sphere = Sphere(radius=5, center=(0, 0, 0))
        
        assert sphere.radius == 5
        assert sphere.center == (0, 0, 0)
        
    def test_sphere_bounds(self):
        """Test sphere bounding box."""
        sphere = Sphere(radius=5, center=(10, 10, 10))
        bounds = sphere.get_bounds()
        
        assert bounds[0] == (5, 15)
        assert bounds[1] == (5, 15)
        assert bounds[2] == (5, 15)
        
    def test_sphere_volume(self):
        """Test sphere volume calculation."""
        sphere = Sphere(radius=5, center=(0, 0, 0))
        volume = sphere.get_volume()
        
        expected = (4/3) * np.pi * (5 ** 3)
        assert abs(volume - expected) / expected < 0.01  # 1% tolerance
        
    def test_sphere_resolution(self):
        """Test different tessellation resolutions."""
        low_res = Sphere(radius=5, center=(0, 0, 0), resolution=8)
        high_res = Sphere(radius=5, center=(0, 0, 0), resolution=32)
        
        # High resolution should have more vertices
        assert high_res.num_vertices > low_res.num_vertices


class TestCylinder:
    """Test cases for Cylinder primitive."""
    
    def test_cylinder_creation(self):
        """Test basic cylinder creation."""
        cylinder = Cylinder(radius=3, height=10, center=(0, 0, 5))
        
        assert cylinder.radius == 3
        assert cylinder.height == 10
        
    def test_cylinder_bounds(self):
        """Test cylinder bounding box."""
        cylinder = Cylinder(radius=5, height=20, center=(0, 0, 10))
        bounds = cylinder.get_bounds()
        
        # Circular base: -5 to 5 in x,y
        assert bounds[0] == (-5, 5)
        assert bounds[1] == (-5, 5)
        # Height: 0 to 20 in z
        assert bounds[2] == (0, 20)
        
    def test_cylinder_volume(self):
        """Test cylinder volume."""
        cylinder = Cylinder(radius=5, height=10, center=(0, 0, 5))
        volume = cylinder.get_volume()
        
        expected = np.pi * (5 ** 2) * 10
        assert abs(volume - expected) / expected < 0.01


class TestGeometry:
    """Test cases for general Geometry class."""
    
    def test_from_primitives(self):
        """Test creating geometry from multiple primitives."""
        primitives = [
            Cube(size=10, center=(0, 0, 10)),
            Sphere(radius=5, center=(15, 0, 10))
        ]
        
        geometry = Geometry.from_primitives(primitives)
        bounds = geometry.get_bounds()
        
        # Should encompass both shapes
        assert bounds[0][0] <= -5  # Cube left edge
        assert bounds[0][1] >= 20  # Sphere right edge
        
    def test_save_load_stl(self):
        """Test saving and loading STL files."""
        cube = Cube(size=10, center=(0, 0, 10))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_cube.stl"
            
            # Save
            cube.save(str(filepath))
            assert filepath.exists()
            
            # Load
            loaded = Geometry.from_stl(str(filepath))
            
            # Check bounds match
            original_bounds = cube.get_bounds()
            loaded_bounds = loaded.get_bounds()
            
            for i in range(3):
                assert abs(original_bounds[i][0] - loaded_bounds[i][0]) < 0.1
                assert abs(original_bounds[i][1] - loaded_bounds[i][1]) < 0.1
    
    def test_transform_translation(self):
        """Test translating geometry."""
        cube = Cube(size=10, center=(0, 0, 0))
        
        # Translation matrix: move by (5, 5, 5)
        translation = np.array([
            [1, 0, 0, 5],
            [0, 1, 0, 5],
            [0, 0, 1, 5],
            [0, 0, 0, 1]
        ])
        
        cube.transform(translation)
        bounds = cube.get_bounds()
        
        # Center should now be at (5, 5, 5)
        center_x = (bounds[0][0] + bounds[0][1]) / 2
        center_y = (bounds[1][0] + bounds[1][1]) / 2
        center_z = (bounds[2][0] + bounds[2][1]) / 2
        
        assert abs(center_x - 5) < 0.1
        assert abs(center_y - 5) < 0.1
        assert abs(center_z - 5) < 0.1
        
    def test_transform_scaling(self):
        """Test scaling geometry."""
        cube = Cube(size=10, center=(0, 0, 0))
        
        # Scale by 2× in all directions
        cube.scale(2, 2, 2)
        bounds = cube.get_bounds()
        
        # Should be -10 to 10 now
        assert abs(bounds[0][0] - (-10)) < 0.1
        assert abs(bounds[0][1] - 10) < 0.1
        
    def test_transform_rotation(self):
        """Test rotating geometry."""
        cube = Cube(size=10, center=(0, 0, 0))
        
        # 90° rotation around z-axis
        angle = np.pi / 2
        rotation = np.array([
            [np.cos(angle), -np.sin(angle), 0, 0],
            [np.sin(angle),  np.cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        cube.transform(rotation)
        bounds = cube.get_bounds()
        
        # Bounds should still be approximately -5 to 5
        # (cube is symmetric)
        assert abs(bounds[0][0] - (-5)) < 0.1
        assert abs(bounds[0][1] - 5) < 0.1
        
    def test_slicing(self):
        """Test geometry slicing into layers."""
        cube = Cube(size=10, center=(0, 0, 10))
        
        # Slice at 5, 10, 15 μm
        z_positions = [5, 10, 15]
        slices = cube.slice(z_positions)
        
        assert len(slices) == 3
        
        # Middle slice (z=10) should be largest
        # (passes through cube center)
        assert slices[1].get_area() > slices[0].get_area()
        assert slices[1].get_area() > slices[2].get_area()


class TestGeometryOperations:
    """Test geometry boolean and combination operations."""
    
    def test_union(self):
        """Test union of two geometries."""
        cube1 = Cube(size=10, center=(0, 0, 10))
        cube2 = Cube(size=10, center=(5, 0, 10))
        
        union = cube1.union(cube2)
        
        # Union volume should be less than sum
        # (due to overlap)
        total = cube1.get_volume() + cube2.get_volume()
        assert union.get_volume() < total
        
    def test_intersection(self):
        """Test intersection of two geometries."""
        cube1 = Cube(size=10, center=(0, 0, 10))
        cube2 = Cube(size=10, center=(5, 0, 10))
        
        intersection = cube1.intersection(cube2)
        
        # Intersection should be smaller than either cube
        assert intersection.get_volume() < cube1.get_volume()
        assert intersection.get_volume() < cube2.get_volume()
        
    def test_difference(self):
        """Test subtracting one geometry from another."""
        cube = Cube(size=10, center=(0, 0, 10))
        sphere = Sphere(radius=3, center=(0, 0, 10))
        
        # Cube with spherical hole
        result = cube.difference(sphere)
        
        # Result should be smaller than original cube
        assert result.get_volume() < cube.get_volume()


class TestValidation:
    """Test input validation and error handling."""
    
    def test_invalid_size(self):
        """Test that negative sizes raise errors."""
        with pytest.raises(ValueError):
            Cube(size=-10, center=(0, 0, 0))
            
    def test_invalid_radius(self):
        """Test that negative radius raises error."""
        with pytest.raises(ValueError):
            Sphere(radius=-5, center=(0, 0, 0))
            
    def test_invalid_file_format(self):
        """Test loading unsupported file format."""
        with pytest.raises(ValueError):
            Geometry.from_stl("file.txt")
            
    def test_empty_geometry(self):
        """Test that empty geometry is handled."""
        with pytest.raises(ValueError):
            Geometry.from_primitives([])


class TestPerformance:
    """Test performance characteristics (not strict)."""
    
    def test_large_geometry_creation(self):
        """Test creating complex geometry is reasonably fast."""
        import time
        
        start = time.time()
        
        # Create 100 spheres
        primitives = [
            Sphere(radius=1, center=(i, 0, 10), resolution=16)
            for i in range(100)
        ]
        geometry = Geometry.from_primitives(primitives)
        
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 10  # seconds
        
    def test_slicing_performance(self):
        """Test that slicing is reasonably fast."""
        import time
        
        cube = Cube(size=50, center=(0, 0, 25))
        
        # Slice into 100 layers
        z_positions = np.linspace(0, 50, 100)
        
        start = time.time()
        slices = cube.slice(z_positions)
        elapsed = time.time() - start
        
        assert elapsed < 5  # seconds
        assert len(slices) == 100


# Test fixtures and utilities
@pytest.fixture
def sample_cube():
    """Fixture providing a standard test cube."""
    return Cube(size=10, center=(0, 0, 10))


@pytest.fixture
def sample_sphere():
    """Fixture providing a standard test sphere."""
    return Sphere(radius=5, center=(0, 0, 10))


def test_with_fixtures(sample_cube, sample_sphere):
    """Example test using fixtures."""
    # Verify fixtures work
    assert sample_cube.size == 10
    assert sample_sphere.radius == 5
    
    # Combine them
    combined = Geometry.from_primitives([sample_cube, sample_sphere])
    assert combined.get_volume() > 0


# Parametrized tests
@pytest.mark.parametrize("size", [5, 10, 20, 50])
def test_cube_sizes(size):
    """Test cubes of different sizes."""
    cube = Cube(size=size, center=(0, 0, 0))
    volume = cube.get_volume()
    expected = size ** 3
    
    assert abs(volume - expected) < 0.1


@pytest.mark.parametrize("radius,height", [
    (1, 10),
    (5, 20),
    (10, 5),
])
def test_cylinder_dimensions(radius, height):
    """Test cylinders with various dimensions."""
    cylinder = Cylinder(radius=radius, height=height, center=(0, 0, height/2))
    volume = cylinder.get_volume()
    expected = np.pi * radius**2 * height
    
    assert abs(volume - expected) / expected < 0.01


# Integration test
class TestIntegration:
    """Integration tests combining multiple features."""
    
    def test_complete_workflow(self):
        """Test complete geometry workflow."""
        # 1. Create geometry
        cube = Cube(size=10, center=(0, 0, 10))
        
        # 2. Transform it
        cube.scale(1.1, 1.1, 1.0)  # Compensate shrinkage
        
        # 3. Save to file
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "workflow_test.stl"
            cube.save(str(filepath))
            
            # 4. Load it back
            loaded = Geometry.from_stl(str(filepath))
            
            # 5. Verify properties preserved
            original_volume = cube.get_volume()
            loaded_volume = loaded.get_volume()
            
            assert abs(original_volume - loaded_volume) / original_volume < 0.01


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
    
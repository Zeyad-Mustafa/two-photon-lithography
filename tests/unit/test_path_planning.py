#!/usr/bin/env python3
"""
Unit tests for path planning module
====================================

Tests for the tpl.design.PathPlanner module and toolpath generation.

Author: Zeyad Mustafa
Date: December 2024
BTU Cottbus-Senftenberg

Run with: pytest tests/unit/test_path_planning.py -v
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

# Import modules to test
from tpl.design import PathPlanner, Toolpath, Cube, Sphere
from tpl.design.path_planning import (
    RectilinearFill,
    ConcentricFill, 
    SpiralFill
)


class TestPathPlanner:
    """Test cases for PathPlanner class."""
    
    def test_planner_creation(self):
        """Test basic planner initialization."""
        planner = PathPlanner(
            layer_height=0.3,
            hatch_distance=0.5,
            scan_speed=50000,
            power=20
        )
        
        assert planner.layer_height == 0.3
        assert planner.hatch_distance == 0.5
        assert planner.scan_speed == 50000
        assert planner.power == 20
        
    def test_invalid_parameters(self):
        """Test that invalid parameters raise errors."""
        with pytest.raises(ValueError):
            PathPlanner(layer_height=-0.1)  # Negative
            
        with pytest.raises(ValueError):
            PathPlanner(layer_height=0.3, scan_speed=0)  # Zero speed
            
        with pytest.raises(ValueError):
            PathPlanner(layer_height=0.3, power=-5)  # Negative power
            
    def test_generate_simple_cube(self):
        """Test generating path for simple cube."""
        cube = Cube(size=10, center=(0, 0, 10))
        planner = PathPlanner(
            layer_height=0.5,
            hatch_distance=0.5,
            scan_speed=50000,
            power=20
        )
        
        toolpath = planner.generate(cube)
        
        assert toolpath is not None
        assert toolpath.num_points > 0
        assert toolpath.num_layers > 0
        
    def test_first_layer_settings(self):
        """Test first layer power and speed modification."""
        planner = PathPlanner(
            layer_height=0.3,
            scan_speed=50000,
            power=20
        )
        
        planner.set_first_layer(power=26, speed=25000)
        
        assert planner.first_layer_power == 26
        assert planner.first_layer_speed == 25000
        
    def test_region_power_override(self):
        """Test setting different power for specific regions."""
        planner = PathPlanner(layer_height=0.3, power=20)
        
        planner.set_region_power("overhang", power=28)
        
        assert "overhang" in planner.region_powers
        assert planner.region_powers["overhang"] == 28


class TestToolpath:
    """Test cases for Toolpath class."""
    
    @pytest.fixture
    def sample_toolpath(self):
        """Create a sample toolpath for testing."""
        cube = Cube(size=10, center=(0, 0, 10))
        planner = PathPlanner(
            layer_height=0.3,
            hatch_distance=0.5,
            scan_speed=50000,
            power=20
        )
        return planner.generate(cube)
    
    def test_toolpath_properties(self, sample_toolpath):
        """Test basic toolpath properties."""
        assert sample_toolpath.num_points > 0
        assert sample_toolpath.num_layers > 0
        assert sample_toolpath.total_length > 0
        
    def test_get_statistics(self, sample_toolpath):
        """Test statistics calculation."""
        stats = sample_toolpath.get_statistics()
        
        assert "num_points" in stats
        assert "num_layers" in stats
        assert "total_length" in stats
        assert "time_estimate" in stats
        
        # Time should be positive
        assert stats["time_estimate"] > 0
        
    def test_save_load_gcode(self, sample_toolpath):
        """Test saving and loading G-code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_toolpath.gcode"
            
            # Save
            sample_toolpath.save(str(filepath))
            assert filepath.exists()
            
            # Load
            loaded = Toolpath.load(str(filepath))
            
            # Compare key properties
            assert loaded.num_points == sample_toolpath.num_points
            assert abs(loaded.total_length - sample_toolpath.total_length) < 0.1
            
    def test_export_to_csv(self, sample_toolpath):
        """Test CSV export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_coords.csv"
            
            sample_toolpath.export_to_csv(str(filepath))
            assert filepath.exists()
            
            # Check file has content
            with open(filepath, 'r') as f:
                lines = f.readlines()
                assert len(lines) > 1  # Header + data
                assert "x,y,z" in lines[0].lower()
                
    def test_get_coordinates(self, sample_toolpath):
        """Test extracting coordinate array."""
        coords = sample_toolpath.get_coordinates()
        
        assert coords.shape[1] == 3  # x, y, z
        assert coords.shape[0] == sample_toolpath.num_points
        
        # Z should be reasonable (above substrate)
        assert np.all(coords[:, 2] >= 0)


class TestFillPatterns:
    """Test different fill pattern strategies."""
    
    @pytest.fixture
    def test_geometry(self):
        """Simple geometry for testing fill patterns."""
        return Cube(size=10, center=(0, 0, 10))
    
    def test_rectilinear_fill(self, test_geometry):
        """Test rectilinear (straight line) fill pattern."""
        planner = PathPlanner(
            layer_height=0.5,
            hatch_distance=0.5,
            fill_pattern="rectilinear"
        )
        
        toolpath = planner.generate(test_geometry)
        
        # Should have alternating scan directions
        coords = toolpath.get_coordinates()
        assert len(coords) > 0
        
    def test_concentric_fill(self, test_geometry):
        """Test concentric fill pattern."""
        planner = PathPlanner(
            layer_height=0.5,
            hatch_distance=0.5,
            fill_pattern="concentric"
        )
        
        toolpath = planner.generate(test_geometry)
        assert toolpath.num_points > 0
        
    def test_spiral_fill(self, test_geometry):
        """Test spiral fill pattern."""
        planner = PathPlanner(
            layer_height=0.5,
            hatch_distance=0.5,
            fill_pattern="spiral"
        )
        
        toolpath = planner.generate(test_geometry)
        assert toolpath.num_points > 0
        
    def test_invalid_fill_pattern(self):
        """Test that invalid fill pattern raises error."""
        with pytest.raises(ValueError):
            PathPlanner(
                layer_height=0.3,
                fill_pattern="invalid_pattern"
            )


class TestLayering:
    """Test layer generation and slicing."""
    
    def test_layer_height_calculation(self):
        """Test correct number of layers generated."""
        cube = Cube(size=10, center=(0, 0, 10))  # Height: 5-15 μm
        planner = PathPlanner(layer_height=0.5)
        
        toolpath = planner.generate(cube)
        
        # Expected layers: 10 / 0.5 = 20 layers
        expected_layers = int(10 / 0.5)
        assert abs(toolpath.num_layers - expected_layers) <= 1
        
    def test_layer_ordering(self):
        """Test that layers are generated bottom to top."""
        cube = Cube(size=10, center=(0, 0, 10))
        planner = PathPlanner(layer_height=1.0)
        
        toolpath = planner.generate(cube)
        coords = toolpath.get_coordinates()
        
        # First points should have lower z than last points
        first_z = coords[0, 2]
        last_z = coords[-1, 2]
        
        assert last_z > first_z
        
    def test_adaptive_layer_height(self):
        """Test varying layer height for different regions."""
        planner = PathPlanner(layer_height=0.3)
        
        # Set different layer height for top layers
        planner.set_adaptive_layering(
            top_layers=5,
            top_layer_height=0.2
        )
        
        assert planner.adaptive_layering_enabled


class TestOptimization:
    """Test path optimization features."""
    
    def test_travel_optimization(self):
        """Test that travel moves are minimized."""
        cube = Cube(size=10, center=(0, 0, 10))
        
        # Without optimization
        planner_no_opt = PathPlanner(
            layer_height=0.5,
            optimize_travel=False
        )
        toolpath_no_opt = planner_no_opt.generate(cube)
        
        # With optimization
        planner_opt = PathPlanner(
            layer_height=0.5,
            optimize_travel=True
        )
        toolpath_opt = planner_opt.generate(cube)
        
        # Optimized should have shorter total length
        # (fewer travel moves)
        assert toolpath_opt.total_length <= toolpath_no_opt.total_length
        
    def test_bidirectional_scanning(self):
        """Test bidirectional vs unidirectional scanning."""
        cube = Cube(size=10, center=(0, 0, 10))
        
        # Bidirectional (scan both directions)
        planner_bi = PathPlanner(
            layer_height=0.5,
            bidirectional_scan=True
        )
        toolpath_bi = planner_bi.generate(cube)
        
        # Unidirectional (always return to start)
        planner_uni = PathPlanner(
            layer_height=0.5,
            bidirectional_scan=False
        )
        toolpath_uni = planner_uni.generate(cube)
        
        # Bidirectional should be faster
        assert toolpath_bi.time_estimate < toolpath_uni.time_estimate


class TestComplexGeometry:
    """Test path planning for more complex geometries."""
    
    def test_sphere_toolpath(self):
        """Test generating toolpath for sphere."""
        sphere = Sphere(radius=5, center=(0, 0, 10))
        planner = PathPlanner(layer_height=0.3)
        
        toolpath = planner.generate(sphere)
        
        assert toolpath.num_points > 0
        
        # Sphere layers should vary in size
        # (smaller at top and bottom)
        
    def test_multiple_objects(self):
        """Test toolpath for multiple separate objects."""
        from tpl.design import Geometry
        
        objects = [
            Cube(size=5, center=(0, 0, 10)),
            Cube(size=5, center=(10, 0, 10))
        ]
        
        geometry = Geometry.from_primitives(objects)
        planner = PathPlanner(layer_height=0.3)
        
        toolpath = planner.generate(geometry)
        
        # Should handle both objects
        assert toolpath.num_points > 0
        
    def test_hollow_structure(self):
        """Test toolpath for hollow structure."""
        outer = Cube(size=10, center=(0, 0, 10))
        inner = Cube(size=8, center=(0, 0, 10))
        
        hollow = outer.difference(inner)
        
        planner = PathPlanner(
            layer_height=0.5,
            infill_density=0  # No infill (shell only)
        )
        
        toolpath = planner.generate(hollow)
        assert toolpath.num_points > 0


class TestDoseCalculation:
    """Test exposure dose calculations."""
    
    def test_dose_calculation(self):
        """Test that dose is calculated correctly."""
        planner = PathPlanner(
            power=20,           # mW
            scan_speed=50000,   # μm/s
            hatch_distance=0.5  # μm
        )
        
        dose = planner.calculate_dose()
        
        # Dose = Power / (Speed × LineWidth)
        # Approximate formula
        assert dose > 0
        
    def test_dose_for_different_speeds(self):
        """Test dose changes with speed."""
        planner1 = PathPlanner(power=20, scan_speed=50000)
        planner2 = PathPlanner(power=20, scan_speed=100000)
        
        dose1 = planner1.calculate_dose()
        dose2 = planner2.calculate_dose()
        
        # Slower speed = higher dose
        assert dose1 > dose2
        
    def test_dose_uniformity(self):
        """Test that dose is uniform across structure."""
        cube = Cube(size=10, center=(0, 0, 10))
        planner = PathPlanner(
            layer_height=0.3,
            hatch_distance=0.5,
            power=20
        )
        
        toolpath = planner.generate(cube)
        
        # Check dose variation
        doses = toolpath.get_local_doses()
        
        # Standard deviation should be low
        dose_std = np.std(doses)
        dose_mean = np.mean(doses)
        
        variation = dose_std / dose_mean
        assert variation < 0.1  # Less than 10% variation


class TestTimeEstimation:
    """Test fabrication time estimation."""
    
    def test_time_estimate(self):
        """Test that time estimate is reasonable."""
        cube = Cube(size=10, center=(0, 0, 10))
        planner = PathPlanner(
            layer_height=0.5,
            scan_speed=50000,
            power=20
        )
        
        toolpath = planner.generate(cube)
        stats = toolpath.get_statistics()
        
        time_estimate = stats["time_estimate"]
        
        # Should be positive and reasonable
        assert time_estimate > 0
        assert time_estimate < 3600  # Less than 1 hour for small cube
        
    def test_time_scales_with_size(self):
        """Test that time increases with structure size."""
        planner = PathPlanner(layer_height=0.5, scan_speed=50000)
        
        small = Cube(size=5, center=(0, 0, 5))
        large = Cube(size=20, center=(0, 0, 20))
        
        time_small = planner.generate(small).get_statistics()["time_estimate"]
        time_large = planner.generate(large).get_statistics()["time_estimate"]
        
        # Larger structure takes more time
        assert time_large > time_small


# Parametrized tests
@pytest.mark.parametrize("layer_height", [0.2, 0.3, 0.5, 1.0])
def test_various_layer_heights(layer_height):
    """Test path generation with different layer heights."""
    cube = Cube(size=10, center=(0, 0, 10))
    planner = PathPlanner(layer_height=layer_height)
    
    toolpath = planner.generate(cube)
    
    # More layers for smaller layer height
    expected_layers = int(10 / layer_height)
    assert abs(toolpath.num_layers - expected_layers) <= 1


@pytest.mark.parametrize("hatch_distance", [0.3, 0.5, 0.7, 1.0])
def test_various_hatch_distances(hatch_distance):
    """Test different hatch distances."""
    cube = Cube(size=10, center=(0, 0, 10))
    planner = PathPlanner(
        layer_height=0.5,
        hatch_distance=hatch_distance
    )
    
    toolpath = planner.generate(cube)
    
    # Larger hatch distance = fewer points
    assert toolpath.num_points > 0


# Integration test
class TestIntegration:
    """Integration tests for complete workflow."""
    
    def test_complete_workflow(self):
        """Test complete path planning workflow."""
        # 1. Create geometry
        cube = Cube(size=10, center=(0, 0, 10))
        
        # 2. Create planner with optimizations
        planner = PathPlanner(
            layer_height=0.3,
            hatch_distance=0.5,
            scan_speed=50000,
            power=20,
            fill_pattern="rectilinear",
            optimize_travel=True,
            bidirectional_scan=True
        )
        
        # 3. Set first layer
        planner.set_first_layer(power=24, speed=25000)
        
        # 4. Generate toolpath
        toolpath = planner.generate(cube)
        
        # 5. Get statistics
        stats = toolpath.get_statistics()
        
        # 6. Save to file
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "integration_test.gcode"
            toolpath.save(str(filepath))
            
            # 7. Verify file
            assert filepath.exists()
            
            # 8. Load and verify
            loaded = Toolpath.load(str(filepath))
            assert loaded.num_points == toolpath.num_points


# Performance test
@pytest.mark.slow
class TestPerformance:
    """Performance tests (marked slow)."""
    
    def test_large_structure_performance(self):
        """Test that large structures are handled efficiently."""
        import time
        
        large_cube = Cube(size=100, center=(0, 0, 100))
        planner = PathPlanner(layer_height=1.0)
        
        start = time.time()
        toolpath = planner.generate(large_cube)
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 30  # 30 seconds max
        assert toolpath.num_points > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
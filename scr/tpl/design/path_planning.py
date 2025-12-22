"""
Path planning module for two-photon lithography
================================================

Generates toolpaths from 3D geometries for TPL fabrication.

Author: Zeyad Mustafa
Date: December 2024
BTU Cottbus-Senftenberg
"""

import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union
import json
import warnings

from .geometry import Geometry


class PathPlanner:
    """
    Generate fabrication toolpaths from 3D geometries.
    
    Parameters
    ----------
    layer_height : float
        Z-increment between layers in micrometers
    hatch_distance : float
        Spacing between scan lines in micrometers
    scan_speed : float
        Writing speed in μm/s
    power : float
        Laser power in milliwatts
    fill_pattern : str
        Fill strategy: 'rectilinear', 'concentric', or 'spiral'
    optimize_travel : bool
        Minimize travel moves between features
    bidirectional_scan : bool
        Scan both forward and backward (faster)
    """
    
    def __init__(self,
                 layer_height: float = 0.3,
                 hatch_distance: float = 0.5,
                 scan_speed: float = 50000,
                 power: float = 20,
                 fill_pattern: str = "rectilinear",
                 optimize_travel: bool = True,
                 bidirectional_scan: bool = True):
        
        # Validation
        if layer_height <= 0:
            raise ValueError("Layer height must be positive")
        if hatch_distance <= 0:
            raise ValueError("Hatch distance must be positive")
        if scan_speed <= 0:
            raise ValueError("Scan speed must be positive")
        if power < 0:
            raise ValueError("Power cannot be negative")
        
        valid_patterns = ['rectilinear', 'concentric', 'spiral']
        if fill_pattern not in valid_patterns:
            raise ValueError(f"Fill pattern must be one of {valid_patterns}")
        
        self.layer_height = layer_height
        self.hatch_distance = hatch_distance
        self.scan_speed = scan_speed
        self.power = power
        self.fill_pattern = fill_pattern
        self.optimize_travel = optimize_travel
        self.bidirectional_scan = bidirectional_scan
        
        # First layer settings (can be overridden)
        self.first_layer_power = power
        self.first_layer_speed = scan_speed
        
        # Region-specific power overrides
        self.region_powers = {}
        
        # Adaptive layering
        self.adaptive_layering_enabled = False
        
    def set_first_layer(self, power: float, speed: float):
        """
        Set different parameters for first layer (adhesion).
        
        Parameters
        ----------
        power : float
            First layer power in mW
        speed : float
            First layer speed in μm/s
        """
        self.first_layer_power = power
        self.first_layer_speed = speed
        
    def set_region_power(self, region_name: str, power: float):
        """
        Set different power for specific regions.
        
        Parameters
        ----------
        region_name : str
            Name of region
        power : float
            Power for this region in mW
        """
        self.region_powers[region_name] = power
        
    def set_adaptive_layering(self, top_layers: int, top_layer_height: float):
        """
        Enable adaptive layer height for top layers.
        
        Parameters
        ----------
        top_layers : int
            Number of top layers to use different height
        top_layer_height : float
            Layer height for top layers
        """
        self.adaptive_layering_enabled = True
        self.top_layers = top_layers
        self.top_layer_height = top_layer_height
        
    def calculate_dose(self) -> float:
        """
        Calculate exposure dose.
        
        Returns
        -------
        float
            Dose in mJ/cm²
        """
        # Simplified dose calculation
        # Dose ≈ Power / (Speed × LineWidth)
        line_width = self.hatch_distance
        dose = (self.power * 1000) / (self.scan_speed * line_width * 10)  # Approximate
        return dose
        
    def generate(self, geometry: Geometry) -> 'Toolpath':
        """
        Generate toolpath from geometry.
        
        Parameters
        ----------
        geometry : Geometry
            Input geometry to fabricate
            
        Returns
        -------
        Toolpath
            Generated toolpath
        """
        print(f"Generating toolpath for geometry...")
        
        # Get geometry bounds
        bounds = geometry.get_bounds()
        z_min, z_max = bounds[2]
        
        # Calculate layer positions
        num_layers = int(np.ceil((z_max - z_min) / self.layer_height))
        z_positions = np.linspace(z_min, z_max, num_layers)
        
        print(f"  Geometry height: {z_max - z_min:.2f} μm")
        print(f"  Number of layers: {num_layers}")
        print(f"  Layer height: {self.layer_height} μm")
        
        # Slice geometry
        print(f"  Slicing geometry...")
        slices = geometry.slice(z_positions)
        
        # Generate paths for each layer
        all_points = []
        all_powers = []
        all_speeds = []
        
        for layer_idx, (z_pos, slice_geom) in enumerate(zip(z_positions, slices)):
            # Determine parameters for this layer
            is_first_layer = (layer_idx == 0)
            
            if is_first_layer:
                power = self.first_layer_power
                speed = self.first_layer_speed
            else:
                power = self.power
                speed = self.scan_speed
            
            # Generate fill pattern for this slice
            layer_points = self._generate_layer_fill(
                slice_geom, 
                z_pos, 
                layer_idx
            )
            
            if len(layer_points) > 0:
                all_points.extend(layer_points)
                all_powers.extend([power] * len(layer_points))
                all_speeds.extend([speed] * len(layer_points))
        
        print(f"  Total points: {len(all_points)}")
        
        # Create toolpath
        toolpath = Toolpath(
            points=np.array(all_points),
            powers=np.array(all_powers),
            speeds=np.array(all_speeds),
            num_layers=num_layers
        )
        
        # Optimize if requested
        if self.optimize_travel:
            toolpath.optimize()
        
        return toolpath
        
    def _generate_layer_fill(self, 
                            slice_geom: Geometry, 
                            z_pos: float,
                            layer_idx: int) -> List[Tuple[float, float, float]]:
        """
        Generate fill pattern for a single layer.
        
        Parameters
        ----------
        slice_geom : Geometry
            2D slice geometry
        z_pos : float
            Z-position of this layer
        layer_idx : int
            Layer index
            
        Returns
        -------
        list
            List of (x, y, z) points
        """
        if not hasattr(slice_geom, '_section') or slice_geom._section is None:
            return []
        
        section = slice_geom._section
        
        if self.fill_pattern == 'rectilinear':
            return self._rectilinear_fill(section, z_pos, layer_idx)
        elif self.fill_pattern == 'concentric':
            return self._concentric_fill(section, z_pos)
        elif self.fill_pattern == 'spiral':
            return self._spiral_fill(section, z_pos)
        else:
            raise ValueError(f"Unknown fill pattern: {self.fill_pattern}")
    
    def _rectilinear_fill(self, section, z_pos: float, layer_idx: int) -> List:
        """Generate rectilinear (straight line) fill."""
        points = []
        
        # Get bounding box
        bounds = section.bounds
        x_min, y_min = bounds[0]
        x_max, y_max = bounds[1]
        
        # Alternate scan direction based on layer (for better adhesion)
        if layer_idx % 2 == 0:
            # Scan along X
            y_lines = np.arange(y_min, y_max, self.hatch_distance)
            for i, y in enumerate(y_lines):
                if self.bidirectional_scan and i % 2 == 1:
                    # Scan backward
                    points.append((x_max, y, z_pos))
                    points.append((x_min, y, z_pos))
                else:
                    # Scan forward
                    points.append((x_min, y, z_pos))
                    points.append((x_max, y, z_pos))
        else:
            # Scan along Y
            x_lines = np.arange(x_min, x_max, self.hatch_distance)
            for i, x in enumerate(x_lines):
                if self.bidirectional_scan and i % 2 == 1:
                    points.append((x, y_max, z_pos))
                    points.append((x, y_min, z_pos))
                else:
                    points.append((x, y_min, z_pos))
                    points.append((x, y_max, z_pos))
        
        return points
    
    def _concentric_fill(self, section, z_pos: float) -> List:
        """Generate concentric fill (follows contour)."""
        points = []
        
        # Simplified: use bounding box contours
        bounds = section.bounds
        x_min, y_min = bounds[0]
        x_max, y_max = bounds[1]
        
        # Generate concentric rectangles
        offset = 0
        while offset < min(x_max - x_min, y_max - y_min) / 2:
            # Rectangle at this offset
            x0 = x_min + offset
            x1 = x_max - offset
            y0 = y_min + offset
            y1 = y_max - offset
            
            # Draw rectangle
            points.extend([
                (x0, y0, z_pos),
                (x1, y0, z_pos),
                (x1, y1, z_pos),
                (x0, y1, z_pos),
                (x0, y0, z_pos),  # Close loop
            ])
            
            offset += self.hatch_distance
        
        return points
    
    def _spiral_fill(self, section, z_pos: float) -> List:
        """Generate spiral fill."""
        points = []
        
        bounds = section.bounds
        x_min, y_min = bounds[0]
        x_max, y_max = bounds[1]
        
        # Spiral from outside to inside
        x0, x1 = x_min, x_max
        y0, y1 = y_min, y_max
        
        while x0 < x1 and y0 < y1:
            # Right
            for x in np.arange(x0, x1, self.hatch_distance):
                points.append((x, y0, z_pos))
            # Down
            for y in np.arange(y0, y1, self.hatch_distance):
                points.append((x1, y, z_pos))
            # Left
            for x in np.arange(x1, x0, -self.hatch_distance):
                points.append((x, y1, z_pos))
            # Up
            for y in np.arange(y1, y0, -self.hatch_distance):
                points.append((x0, y, z_pos))
            
            # Move inward
            x0 += self.hatch_distance
            y0 += self.hatch_distance
            x1 -= self.hatch_distance
            y1 -= self.hatch_distance
        
        return points


class Toolpath:
    """
    Container for fabrication toolpath.
    
    Attributes
    ----------
    points : ndarray
        Array of (x, y, z) positions in micrometers
    powers : ndarray
        Laser power at each point in mW
    speeds : ndarray
        Scan speed at each point in μm/s
    num_layers : int
        Number of layers in toolpath
    """
    
    def __init__(self,
                 points: np.ndarray,
                 powers: np.ndarray,
                 speeds: np.ndarray,
                 num_layers: int):
        
        self.points = points
        self.powers = powers
        self.speeds = speeds
        self.num_layers = num_layers
        
    @property
    def num_points(self) -> int:
        """Number of points in toolpath."""
        return len(self.points)
    
    @property
    def total_length(self) -> float:
        """Total path length in micrometers."""
        if len(self.points) < 2:
            return 0.0
        
        # Calculate distances between consecutive points
        deltas = np.diff(self.points, axis=0)
        distances = np.sqrt(np.sum(deltas**2, axis=1))
        return np.sum(distances)
    
    @property
    def time_estimate(self) -> float:
        """Estimated fabrication time in seconds."""
        if len(self.points) < 2:
            return 0.0
        
        # Calculate time for each segment
        deltas = np.diff(self.points, axis=0)
        distances = np.sqrt(np.sum(deltas**2, axis=1))
        
        # Time = distance / speed (use average speed for segment)
        avg_speeds = (self.speeds[:-1] + self.speeds[1:]) / 2
        times = distances / avg_speeds
        
        return np.sum(times)
    
    def get_statistics(self) -> Dict:
        """
        Get toolpath statistics.
        
        Returns
        -------
        dict
            Dictionary with statistics
        """
        return {
            'num_points': self.num_points,
            'num_layers': self.num_layers,
            'total_length': self.total_length,
            'time_estimate': self.time_estimate,
            'min_power': np.min(self.powers),
            'max_power': np.max(self.powers),
            'avg_power': np.mean(self.powers),
            'min_speed': np.min(self.speeds),
            'max_speed': np.max(self.speeds),
        }
    
    def get_coordinates(self) -> np.ndarray:
        """
        Get coordinate array.
        
        Returns
        -------
        ndarray
            N×3 array of (x, y, z) coordinates
        """
        return self.points
    
    def get_local_doses(self) -> np.ndarray:
        """
        Calculate local exposure doses.
        
        Returns
        -------
        ndarray
            Dose at each point
        """
        # Simplified dose calculation
        doses = self.powers / self.speeds * 1000  # Arbitrary units
        return doses
    
    def save(self, filepath: str, format: str = None):
        """
        Save toolpath to file.
        
        Parameters
        ----------
        filepath : str
            Output file path
        format : str, optional
            File format ('gcode' or 'json')
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if format is None:
            format = filepath.suffix[1:].lower()
        
        if format == 'gcode':
            self._save_gcode(filepath)
        elif format == 'json':
            self._save_json(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _save_gcode(self, filepath: Path):
        """Save as G-code format."""
        with open(filepath, 'w') as f:
            # Header
            f.write("; Two-Photon Lithography Toolpath\n")
            f.write(f"; Points: {self.num_points}\n")
            f.write(f"; Layers: {self.num_layers}\n")
            f.write(f"; Total length: {self.total_length:.2f} um\n")
            f.write(f"; Estimated time: {self.time_estimate:.1f} s\n")
            f.write("\n")
            
            # Initialize
            f.write("G21 ; Set units to micrometers\n")
            f.write("G90 ; Absolute positioning\n")
            f.write("\n")
            
            # Write points
            for i, (point, power, speed) in enumerate(zip(self.points, self.powers, self.speeds)):
                x, y, z = point
                f.write(f"G1 X{x:.4f} Y{y:.4f} Z{z:.4f} F{speed:.0f} P{power:.2f}\n")
            
            # Footer
            f.write("\n; End of toolpath\n")
    
    def _save_json(self, filepath: Path):
        """Save as JSON format."""
        data = {
            'metadata': {
                'num_points': self.num_points,
                'num_layers': self.num_layers,
                'total_length': float(self.total_length),
                'time_estimate': float(self.time_estimate),
            },
            'toolpath': [
                {
                    'x': float(p[0]),
                    'y': float(p[1]),
                    'z': float(p[2]),
                    'power': float(power),
                    'speed': float(speed),
                }
                for p, power, speed in zip(self.points, self.powers, self.speeds)
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'Toolpath':
        """
        Load toolpath from file.
        
        Parameters
        ----------
        filepath : str
            Input file path
            
        Returns
        -------
        Toolpath
            Loaded toolpath
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Toolpath file not found: {filepath}")
        
        format = filepath.suffix[1:].lower()
        
        if format == 'gcode':
            return cls._load_gcode(filepath)
        elif format == 'json':
            return cls._load_json(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @classmethod
    def _load_gcode(cls, filepath: Path) -> 'Toolpath':
        """Load from G-code format."""
        points = []
        powers = []
        speeds = []
        num_layers = 1
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith('; Layers:'):
                    num_layers = int(line.split(':')[1].strip())
                
                if line.startswith('G1'):
                    # Parse G-code line
                    parts = line.split()
                    x = y = z = power = speed = 0
                    
                    for part in parts[1:]:
                        if part.startswith('X'):
                            x = float(part[1:])
                        elif part.startswith('Y'):
                            y = float(part[1:])
                        elif part.startswith('Z'):
                            z = float(part[1:])
                        elif part.startswith('P'):
                            power = float(part[1:])
                        elif part.startswith('F'):
                            speed = float(part[1:])
                    
                    points.append([x, y, z])
                    powers.append(power)
                    speeds.append(speed)
        
        return cls(
            points=np.array(points),
            powers=np.array(powers),
            speeds=np.array(speeds),
            num_layers=num_layers
        )
    
    @classmethod
    def _load_json(cls, filepath: Path) -> 'Toolpath':
        """Load from JSON format."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        points = []
        powers = []
        speeds = []
        
        for point in data['toolpath']:
            points.append([point['x'], point['y'], point['z']])
            powers.append(point['power'])
            speeds.append(point['speed'])
        
        return cls(
            points=np.array(points),
            powers=np.array(powers),
            speeds=np.array(speeds),
            num_layers=data['metadata']['num_layers']
        )
    
    def export_to_csv(self, filepath: str):
        """
        Export coordinates to CSV.
        
        Parameters
        ----------
        filepath : str
            Output CSV file path
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            # Header
            f.write("x,y,z,power,speed\n")
            
            # Data
            for point, power, speed in zip(self.points, self.powers, self.speeds):
                f.write(f"{point[0]:.4f},{point[1]:.4f},{point[2]:.4f},"
                       f"{power:.2f},{speed:.0f}\n")
    
    def visualize(self):
        """Create 3D visualization of toolpath."""
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
        except ImportError:
            warnings.warn("Matplotlib required for visualization")
            return
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot points colored by layer height (z)
        scatter = ax.scatter(
            self.points[:, 0],
            self.points[:, 1],
            self.points[:, 2],
            c=self.points[:, 2],
            cmap='viridis',
            s=1
        )
        
        ax.set_xlabel('X (μm)')
        ax.set_ylabel('Y (μm)')
        ax.set_zlabel('Z (μm)')
        ax.set_title(f'Toolpath: {self.num_points} points, {self.num_layers} layers')
        
        plt.colorbar(scatter, label='Z height (μm)')
        plt.tight_layout()
        plt.show()
    
    def optimize(self):
        """Optimize toolpath to reduce travel moves."""
        # Simple optimization: reorder points to minimize travel
        # This is a simplified version - full TSP solver would be better
        print("  Optimizing toolpath...")
        # For now, just a placeholder
        # Real implementation would use nearest neighbor or TSP algorithm
        pass


# Fill pattern implementations
class RectilinearFill:
    """Rectilinear (straight line) fill pattern."""
    pass


class ConcentricFill:
    """Concentric fill pattern."""
    pass


class SpiralFill:
    """Spiral fill pattern."""
    pass
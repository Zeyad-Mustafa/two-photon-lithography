# API Reference - Module Documentation

## Introduction

This document provides a comprehensive reference for the Two-Photon Lithography Python package. All modules are organized under the `tpl` package namespace.

**Installation**:
```bash
pip install -e .  # Development mode
# or
pip install two-photon-lithography
```

**Basic usage**:
```python
import tpl
from tpl.design import Geometry, PathPlanner
from tpl.core import ExposureEngine
```

---

## Package Structure

```
tpl/
├── core/              # Hardware control and exposure
├── design/            # Geometry and path generation  
├── simulation/        # Physical modeling
├── optimization/      # Parameter tuning
├── imaging/           # Alignment and monitoring
└── utils/             # Utilities and helpers
```

---

## tpl.core - Hardware Control

### ExposureEngine

Main controller for laser and stage during fabrication.

**Class**: `tpl.core.ExposureEngine`

```python
from tpl.core import ExposureEngine

engine = ExposureEngine(
    laser_port="/dev/ttyUSB0",    # Serial port for laser
    stage_port="/dev/ttyUSB1",     # Serial port for stage
    config_file="config.yaml"      # Optional configuration
)
```

**Methods**:

#### `connect()`
Establish connection to hardware.

```python
engine.connect()
# Returns: True if successful, raises ConnectionError otherwise
```

#### `execute(toolpath, preview=False)`
Execute fabrication from toolpath.

**Parameters**:
- `toolpath` (Toolpath): Generated toolpath object
- `preview` (bool): If True, show preview without executing

```python
engine.execute(toolpath, preview=False)
# Returns: FabricationReport with statistics
```

#### `set_power(power_mw)`
Set laser power.

**Parameters**:
- `power_mw` (float): Laser power in milliwatts

```python
engine.set_power(25.0)  # Set to 25 mW
```

#### `move_to(x, y, z, speed=None)`
Move stage to absolute position.

**Parameters**:
- `x, y, z` (float): Position in micrometers
- `speed` (float, optional): Movement speed in μm/s

```python
engine.move_to(x=100, y=50, z=10, speed=5000)
```

#### `calibrate()`
Run automated calibration routine.

```python
engine.calibrate()
# Interactive calibration wizard
```

---

### LaserControl

Low-level laser control interface.

**Class**: `tpl.core.LaserControl`

```python
from tpl.core import LaserControl

laser = LaserControl(port="/dev/ttyUSB0")
laser.connect()
```

**Methods**:

#### `set_power(power)`
```python
laser.set_power(20.0)  # mW
```

#### `shutter_open()` / `shutter_close()`
```python
laser.shutter_open()
# ... expose ...
laser.shutter_close()
```

#### `get_status()`
```python
status = laser.get_status()
# Returns: dict with power, temperature, mode_lock status
```

---

### StageControl

Positioning stage interface.

**Class**: `tpl.core.StageControl`

```python
from tpl.core import StageControl

stage = StageControl(port="/dev/ttyUSB1")
stage.connect()
```

**Methods**:

#### `move_absolute(x, y, z)`
```python
stage.move_absolute(x=100, y=50, z=10)
```

#### `move_relative(dx, dy, dz)`
```python
stage.move_relative(dx=5, dy=0, dz=0)  # Move 5 μm in x
```

#### `get_position()`
```python
x, y, z = stage.get_position()
```

#### `home()`
```python
stage.home()  # Return to home position
```

---

## tpl.design - Geometry and Path Planning

### Geometry

3D geometry representation and manipulation.

**Class**: `tpl.design.Geometry`

#### Creating Geometries

**From primitives**:
```python
from tpl.design import Geometry, Cube, Sphere, Cylinder

# Single primitive
cube = Cube(size=10, center=(0, 0, 10))

# Multiple primitives
geometry = Geometry.from_primitives([
    Cube(size=10, center=(0, 0, 10)),
    Sphere(radius=5, center=(15, 0, 10))
])
```

**From STL file**:
```python
geometry = Geometry.from_stl("model.stl")
```

**From function**:
```python
def gyroid(x, y, z, scale=5):
    return np.sin(x/scale) * np.cos(y/scale) + \
           np.sin(y/scale) * np.cos(z/scale) + \
           np.sin(z/scale) * np.cos(x/scale)

geometry = Geometry.from_function(
    func=gyroid,
    bounds=((-10, 10), (-10, 10), (0, 20)),
    resolution=0.5
)
```

#### Methods

**`save(filename, format="stl")`**
```python
geometry.save("output.stl")
geometry.save("output.obj", format="obj")
```

**`transform(matrix)`**
```python
import numpy as np

# Rotate 45° around z-axis
angle = np.pi/4
rotation = np.array([
    [np.cos(angle), -np.sin(angle), 0, 0],
    [np.sin(angle),  np.cos(angle), 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])
geometry.transform(rotation)
```

**`scale(factor_x, factor_y, factor_z)`**
```python
geometry.scale(1.1, 1.1, 1.0)  # Compensate xy shrinkage
```

**`get_bounds()`**
```python
(x_min, x_max), (y_min, y_max), (z_min, z_max) = geometry.get_bounds()
```

**`slice(z_positions)`**
```python
slices = geometry.slice([0, 0.5, 1.0, 1.5])  # Create layers
```

---

### Primitive Shapes

**Cube**:
```python
from tpl.design import Cube

cube = Cube(
    size=10,              # Edge length (μm)
    center=(0, 0, 10)     # Center position
)
# Or: size=(10, 5, 3) for rectangular box
```

**Sphere**:
```python
from tpl.design import Sphere

sphere = Sphere(
    radius=5,
    center=(0, 0, 10),
    resolution=32         # Tessellation detail
)
```

**Cylinder**:
```python
from tpl.design import Cylinder

cylinder = Cylinder(
    radius=3,
    height=15,
    center=(0, 0, 10),
    resolution=32
)
```

**Cone**:
```python
from tpl.design import Cone

cone = Cone(
    radius_base=5,
    radius_top=1,
    height=10,
    center=(0, 0, 10)
)
```

---

### PathPlanner

Generate toolpaths from geometry.

**Class**: `tpl.design.PathPlanner`

```python
from tpl.design import PathPlanner

planner = PathPlanner(
    layer_height=0.3,         # μm between layers
    hatch_distance=0.5,       # μm between scan lines
    scan_speed=50000,         # μm/s
    power=20,                 # mW
    fill_pattern="rectilinear"  # or "concentric", "spiral"
)
```

#### Methods

**`generate(geometry)`**
```python
toolpath = planner.generate(geometry)
# Returns: Toolpath object
```

**`set_first_layer(power, speed)`**
```python
planner.set_first_layer(power=30, speed=25000)
```

**`set_region_power(region_name, power)`**
```python
planner.set_region_power("overhang", power=28)
```

**`optimize()`**
```python
planner.optimize()  # Minimize travel moves
```

---

### Toolpath

Container for fabrication instructions.

**Class**: `tpl.design.Toolpath`

```python
# Created by PathPlanner.generate()
toolpath = planner.generate(geometry)
```

#### Methods

**`save(filename, format="gcode")`**
```python
toolpath.save("output.gcode")
toolpath.save("output.json", format="json")
```

**`visualize()`**
```python
toolpath.visualize()  # Interactive 3D preview
```

**`get_statistics()`**
```python
stats = toolpath.get_statistics()
print(f"Total time: {stats['time_estimate']:.1f} seconds")
print(f"Total length: {stats['total_length']:.1f} μm")
```

**`export_to_csv(filename)`**
```python
toolpath.export_to_csv("coordinates.csv")
# Columns: x, y, z, power, speed
```

---

## tpl.simulation - Physical Modeling

### AbsorptionModel

Simulate two-photon absorption.

**Class**: `tpl.simulation.AbsorptionModel`

```python
from tpl.simulation import AbsorptionModel

model = AbsorptionModel(
    wavelength=780,           # nm
    pulse_duration=100,       # fs
    repetition_rate=80e6,     # Hz
    numerical_aperture=1.4
)
```

#### Methods

**`calculate_intensity_distribution(power, z_range)`**
```python
z_positions = np.linspace(-5, 5, 100)  # μm
intensity = model.calculate_intensity_distribution(
    power=20,  # mW
    z_range=z_positions
)
```

**`estimate_voxel_size(power, threshold=0.5)`**
```python
voxel_lateral, voxel_axial = model.estimate_voxel_size(
    power=20,
    threshold=0.5  # Polymerization threshold
)
print(f"Voxel: {voxel_lateral:.0f} × {voxel_axial:.0f} nm")
```

---

### PolymerizationKinetics

Model polymerization dynamics.

**Class**: `tpl.simulation.PolymerizationKinetics`

```python
from tpl.simulation import PolymerizationKinetics

kinetics = PolymerizationKinetics(
    photoresist="IP-Dip",
    photoinitiator_concentration=0.03  # wt fraction
)
```

#### Methods

**`predict_conversion(dose)`**
```python
dose = 1000  # mJ/cm²
conversion = kinetics.predict_conversion(dose)
print(f"Monomer conversion: {conversion*100:.1f}%")
```

**`estimate_feature_size(power, speed, threshold=0.2)`**
```python
width = kinetics.estimate_feature_size(
    power=20,
    speed=50000,
    threshold=0.2
)
```

---

## tpl.optimization - Parameter Tuning

### ParameterOptimizer

Automated parameter optimization.

**Class**: `tpl.optimization.ParameterOptimizer`

```python
from tpl.optimization import ParameterOptimizer

optimizer = ParameterOptimizer(
    engine=engine,
    geometry=test_cube,
    target_metric="resolution"  # or "speed", "quality"
)
```

#### Methods

**`optimize_power(speed_fixed)`**
```python
optimal_power = optimizer.optimize_power(speed_fixed=50000)
```

**`optimize_speed(power_fixed)`**
```python
optimal_speed = optimizer.optimize_speed(power_fixed=25)
```

**`run_full_optimization()`**
```python
result = optimizer.run_full_optimization()
print(f"Optimal power: {result['power']:.1f} mW")
print(f"Optimal speed: {result['speed']:.0f} μm/s")
```

---

### PowerThresholdFinder

Determine power threshold.

**Class**: `tpl.optimization.PowerThresholdFinder`

```python
from tpl.optimization import PowerThresholdFinder

finder = PowerThresholdFinder(
    power_range=(5, 40),
    power_step=5,
    scan_speed=50000
)
```

#### Methods

**`run()`**
```python
finder.run()  # Execute test pattern
```

**`analyze()`**
```python
threshold = finder.analyze()
print(f"Threshold power: {threshold:.1f} mW")
```

---

## tpl.imaging - Alignment and Monitoring

### AlignmentSystem

Camera-based alignment.

**Class**: `tpl.imaging.AlignmentSystem`

```python
from tpl.imaging import AlignmentSystem

alignment = AlignmentSystem(camera_index=0)
```

#### Methods

**`find_focus()`**
```python
z_focus = alignment.find_focus()
```

**`find_substrate()`**
```python
z_substrate = alignment.find_substrate()
```

**`detect_structures()`**
```python
structures = alignment.detect_structures()
# Returns: list of (x, y) positions
```

---

## tpl.utils - Utilities

### Calibration

Calibration utilities.

```python
from tpl.utils import calibrate_power, calibrate_stage

# Power calibration
calibrate_power(engine, target_powers=[10, 20, 30])

# Stage calibration
calibrate_stage(engine, reference_grid="calibration_grid.stl")
```

### FileIO

Import/export utilities.

```python
from tpl.utils import load_stl, save_stl, load_config

geometry = load_stl("model.stl")
config = load_config("settings.yaml")
```

### Visualization

Plotting and visualization.

```python
from tpl.utils import plot_toolpath, plot_geometry, plot_results

plot_geometry(geometry)
plot_toolpath(toolpath, show_travel=True)
```

---

## Complete Example Workflow

```python
# 1. Import modules
from tpl.design import Geometry, Cube, PathPlanner
from tpl.core import ExposureEngine
from tpl.optimization import PowerThresholdFinder

# 2. Create geometry
geometry = Cube(size=10, center=(0, 0, 10))

# 3. Generate toolpath
planner = PathPlanner(
    layer_height=0.3,
    hatch_distance=0.5,
    scan_speed=50000,
    power=25
)
toolpath = planner.generate(geometry)

# 4. Preview
toolpath.visualize()

# 5. Execute fabrication
engine = ExposureEngine()
engine.connect()
engine.execute(toolpath)

# 6. Get report
report = engine.get_last_report()
print(f"Fabrication completed in {report.duration:.1f} seconds")
```

---

## Configuration Files

### YAML Configuration

```yaml
# config.yaml
laser:
  port: "/dev/ttyUSB0"
  wavelength: 780  # nm
  max_power: 50    # mW
  
stage:
  port: "/dev/ttyUSB1"
  resolution: 1    # nm
  max_speed: 100000  # μm/s

material:
  type: "IP-Dip"
  refractive_index: 1.52

default_parameters:
  power: 25
  speed: 50000
  layer_height: 0.3
  hatch_distance: 0.5
```

**Load configuration**:
```python
from tpl.utils import load_config

config = load_config("config.yaml")
engine = ExposureEngine(config=config)
```

---

## Error Handling

All modules raise specific exceptions:

```python
from tpl.core import LaserError, StageError, CalibrationError

try:
    engine.connect()
    engine.execute(toolpath)
except LaserError as e:
    print(f"Laser error: {e}")
    # Handle laser-specific issues
except StageError as e:
    print(f"Stage error: {e}")
    # Handle stage issues
except CalibrationError as e:
    print(f"Calibration needed: {e}")
    engine.calibrate()
```

---

## Type Hints and IDE Support

All modules include type hints for IDE autocomplete:

```python
from typing import Tuple, Optional
from tpl.design import Geometry

def create_structure(size: float, 
                     center: Tuple[float, float, float],
                     power: Optional[float] = None) -> Geometry:
    """
    Create a cube structure.
    
    Args:
        size: Edge length in micrometers
        center: (x, y, z) position
        power: Optional laser power override
        
    Returns:
        Geometry object
    """
    return Cube(size=size, center=center)
```

---

## CLI Tools

Command-line interface tools:

```bash
# Power calibration
tpl-calibrate power --range 10-40 --step 5

# Quick fabrication
tpl-control fabricate model.stl --power 25 --speed 50000

# Simulate structure
tpl-simulate model.stl --power 25 --output simulation.png
```

---

## API Versioning

Current version: **1.0.0**

**Import specific version**:
```python
import tpl
assert tpl.__version__ >= "1.0.0"
```

**Deprecation warnings** are issued for outdated APIs:
```python
# Old API (deprecated in 1.0)
engine.set_laser_power(25)  # DeprecationWarning

# New API
engine.set_power(25)
```

---

## Further Documentation

- **Tutorials**: See [tutorials](../tutorials/) for guided examples
- **Theory**: See [theory](../theory/) for underlying physics
- **Examples**: See [examples](../../examples/) for application code
- **Source Code**: Full source at [GitHub](https://github.com/Zeyad-Mustafa/two-photon-lithography)

---

## Document Information

**Author**: Zeyad Mustafa  
**Affiliation**: BTU Cottbus-Senftenberg, Master's Program in Semiconductor Technology  
**Date**: December 2024  
**Version**: 1.0  
**API Version**: 1.0.0  

**Package Structure**:
- Core modules: Hardware interfacing
- Design modules: Geometry and path generation
- Simulation modules: Physical modeling
- Optimization modules: Parameter tuning
- Utility modules: Helper functions

**Python Requirements**:
- Python 3.8+
- NumPy 1.21+
- SciPy 1.7+
- See `requirements.txt` for complete list

**Contact**: 
- Linkedin: [@Zeyad_Mustafa](https://www.linkedin.com/in/zeyad-mustafa-905793ab/)
- GitHub: [@Zeyad-Mustafa](https://github.com/Zeyad-Mustafa)
- Project: [two-photon-lithography](https://github.com/Zeyad-Mustafa/two-photon-lithography)

**License**: MIT License - Free for academic and research use

**Last Updated**: December 9, 2024
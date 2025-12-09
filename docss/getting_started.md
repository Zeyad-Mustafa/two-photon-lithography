# Getting Started with Two-Photon Lithography Toolkit

This guide will help you install and set up the TPL toolkit, and create your first structure.

## Prerequisites

- **Python 3.8 or higher**
- **pip** package manager
- **Git** (for cloning the repository)
- Basic knowledge of Python and 3D geometry

### Optional
- **Hardware**: Femtosecond laser system, piezo stage, high-NA objective (for actual fabrication)
- **GUI Requirements**: PyQt5 (if using the graphical interface)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Zeyad-Mustafa/two-photon-lithography.git
cd two-photon-lithography
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install the Package

```bash
# Install in development mode with all dependencies
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import tpl; print('TPL Toolkit installed successfully!')"
```

## Quick Start: Your First Structure

Let's create a simple 3D structure and visualize it.

### Example 1: Basic Cube

Create a file called `my_first_structure.py`:

```python
from tpl.design import Geometry
from tpl.utils import visualization
import matplotlib.pyplot as plt

# Create a 10x10x10 μm cube
cube = Geometry.cube(size=10.0, resolution=0.2)

# Visualize the structure
fig = visualization.plot_3d_structure(cube)
plt.show()

# Generate exposure paths
paths = cube.generate_paths(
    laser_power=10.0,      # mW
    scan_speed=100.0,      # μm/s
    line_spacing=0.5       # μm
)

print(f"Generated {len(paths)} exposure lines")
print(f"Estimated fabrication time: {cube.estimate_time(paths):.2f} seconds")
```

Run it:
```bash
python my_first_structure.py
```

### Example 2: Import STL File

```python
from tpl.design import STLConverter
from tpl.design import PathPlanning

# Load your 3D model
converter = STLConverter("path/to/your/model.stl")
structure = converter.to_voxel_grid(resolution=0.1)

# Generate optimized paths
planner = PathPlanning(structure)
paths = planner.optimize_scan_path(
    strategy="nearest_neighbor",  # Minimize stage movement
    laser_power=12.0,
    scan_speed=150.0
)

# Save paths for fabrication
planner.export_gcode("output/fabrication_paths.gcode")
```

### Example 3: Run a Simulation

Before fabricating, simulate the polymerization:

```python
from tpl.simulation import AbsorptionModel
from tpl.design import Geometry

# Create structure
structure = Geometry.sphere(radius=5.0, resolution=0.1)

# Set up simulation parameters
model = AbsorptionModel(
    wavelength=780,           # nm
    pulse_duration=100,       # fs
    repetition_rate=80e6,     # Hz
    numerical_aperture=1.4
)

# Simulate exposure
result = model.simulate_exposure(
    structure=structure,
    laser_power=15.0,
    exposure_time=1.0
)

# Visualize polymerized volume
result.plot_cross_section(plane='xy', z=0)
```

## Configuration

### Default Configuration File

The toolkit uses YAML configuration files. Create `config.yaml`:

```yaml
# Laser Settings
laser:
  wavelength: 780          # nm
  pulse_duration: 100      # fs
  repetition_rate: 80e6    # Hz
  max_power: 50.0          # mW

# Optics
optics:
  objective_na: 1.4
  magnification: 100
  immersion: oil
  working_distance: 0.13   # mm

# Stage
stage:
  type: piezo
  range: [200, 200, 200]   # μm (x, y, z)
  resolution: 0.001        # μm
  speed_max: 1000          # μm/s

# Material (default photoresist)
material:
  name: IP-Dip
  refractive_index: 1.52
  sensitivity: 5.0         # mJ/cm²
  shrinkage: 0.05          # 5%

# Fabrication Defaults
fabrication:
  default_power: 10.0      # mW
  default_speed: 100.0     # μm/s
  line_spacing: 0.3        # μm
  layer_height: 0.2        # μm
```

Load configuration in your scripts:

```python
from tpl.utils import load_config

config = load_config("config.yaml")
print(f"Using laser: {config['laser']['wavelength']} nm")
```

## Simulation-Only Mode

You can use the toolkit without hardware for:
- Design and path planning
- Exposure simulation
- Parameter optimization
- Educational purposes

```python
from tpl import set_mode

# Enable simulation mode (no hardware required)
set_mode("simulation")

# All hardware calls will be simulated
from tpl.core import ExposureEngine
engine = ExposureEngine()  # Creates virtual engine
```

## Hardware Setup

### Connecting to Real Hardware

If you have fabrication hardware:

```python
from tpl.core import LaserControl, StageControl
from tpl.imaging import Alignment

# Initialize hardware
laser = LaserControl(port="/dev/ttyUSB0")
stage = StageControl(port="/dev/ttyUSB1")
camera = Alignment(camera_id=0)

# Calibrate system
from tpl.utils import calibration

calibration.calibrate_laser_power(laser)
calibration.calibrate_stage_accuracy(stage)
calibration.align_focal_plane(camera, stage)
```

See [Hardware Setup Guide](../hardware/README.md) for detailed instructions.

## Running Examples

The `examples/` directory contains ready-to-run scripts:

```bash
# Basic shapes
python examples/basic_shapes/cube.py
python examples/basic_shapes/sphere.py

# Photonic crystals
python examples/photonic_crystals/woodpile_structure.py

# Microfluidics
python examples/microfluidics/channel_network.py
```

## Interactive Jupyter Notebooks

Explore the tutorials interactively:

```bash
# Install Jupyter
pip install jupyter

# Launch notebook server
jupyter notebook

# Open notebooks/01_design_workflow.ipynb
```

## GUI Application (Optional)

Launch the graphical interface:

```bash
# Install GUI dependencies
pip install PyQt5

# Run the application
python gui/main_window.py
```

## Troubleshooting

### Import Errors
```bash
# Ensure package is installed
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

### Hardware Connection Issues
- Check USB permissions (Linux): `sudo usermod -a -G dialout $USER`
- Verify device ports: `ls /dev/tty*`
- Test connections individually before full system

### Visualization Issues
```bash
# Install matplotlib backend
pip install PyQt5  # or
pip install tkinter
```

## Next Steps

Now that you have the toolkit installed:

1. **Learn the basics**: Read [Basic Structure Design Tutorial](tutorials/basic_structure_design.md)
2. **Understand the theory**: Review [Two-Photon Absorption Physics](theory/two_photon_absorption.md)
3. **Explore examples**: Browse the `examples/` directory
4. **Optimize parameters**: Follow [Parameter Optimization Guide](tutorials/parameter_optimization.md)

## Getting Help

- **Documentation**: Browse the [docs/](.) directory
- **Issues**: [GitHub Issues](https://github.com/Zeyad-Mustafa/two-photon-lithography/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Zeyad-Mustafa/two-photon-lithography/discussions)

## Common Commands Reference

```bash
# Installation
pip install -e .

# Run tests
pytest tests/

# Generate documentation
cd docs && make html

# Run examples
python examples/basic_shapes/cube.py

# Start GUI
python gui/main_window.py

# Launch Jupyter
jupyter notebook notebooks/
```

---

**Ready to design structures?** → [Basic Structure Design Tutorial](tutorials/basic_structure_design.md)

**Want to understand the physics?** → [Two-Photon Absorption Theory](theory/two_photon_absorption.md)
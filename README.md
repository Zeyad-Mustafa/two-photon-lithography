# Two-Photon Lithography (TPL) Control System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A comprehensive Python-based control and simulation framework for two-photon lithography fabrication, developed for advanced semiconductor nanofabrication research.

##  Overview

Two-photon lithography (TPL) is a cutting-edge additive manufacturing technique that enables the fabrication of complex 3D nanostructures with sub-micron resolution. This project provides:

- **Hardware Control**: Laser power, stage positioning, and exposure control
- **Design Tools**: CAD import, geometry processing, and toolpath generation
- **Simulation**: Physical modeling of two-photon absorption and polymerization
- **Optimization**: Automated parameter tuning for optimal fabrication results
- **Data Analysis**: Post-processing and characterization tools

##  Key Features

-  High-precision laser control with femtosecond pulse optimization
-  STL/CAD file import and automated slicing
-  Physics-based simulation of absorption and thermal effects
-  Real-time parameter optimization
-  Integrated data visualization and analysis
-  Optional GUI for interactive control
-  Extensive example library (photonic crystals, metamaterials, microfluidics)

##  Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Zeyad-Mustafa/two-photon-lithography.git
cd two-photon-lithography

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Basic Usage

```python
from tpl.design import Geometry, PathPlanner
from tpl.core import ExposureEngine
from tpl.optimization import ParameterTuner

# Load or create geometry
geometry = Geometry.from_stl("designs/my_structure.stl")

# Generate toolpath
planner = PathPlanner(layer_height=0.5, hatch_distance=0.3)
toolpath = planner.generate(geometry)

# Configure exposure parameters
engine = ExposureEngine(
    laser_power=20,  # mW
    scan_speed=50000,  # µm/s
    pulse_frequency=80e6  # Hz
)

# Execute fabrication
engine.execute(toolpath)
```

##  Requirements

### Software
- Python 3.8+
- NumPy, SciPy, Matplotlib
- PySerial (for hardware communication)
- Trimesh (for 3D geometry processing)
- PyYAML (for configuration)

### Hardware (Optional)
- Femtosecond laser (typical: 780 nm, <100 fs pulse width)
- High-NA objective (≥1.4 NA recommended)
- Piezo positioning stage (nm-level precision)
- Photoresist (e.g., IP-Dip, Ormocomp)

##  Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Getting Started Guide](docs/getting_started.md)
- [Theory and Background](docs/theory/)
- [API Reference](docs/api_reference/)
- [Tutorials](docs/tutorials/)
- [Example Projects](docs/examples/)

##  Examples

Explore ready-to-use fabrication examples:

```bash
# Photonic crystal
python examples/photonic_crystals/woodpile_structure.py

# Microfluidic channel
python examples/microfluidics/channel_network.py

# Metamaterial structure
python examples/metamaterials/split_ring_resonator.py
```

## 🔧 Configuration

System parameters can be configured via YAML files in `configs/`:

```yaml
# configs/default_config.yaml
laser:
  wavelength: 780  # nm
  power_range: [1, 100]  # mW
  pulse_width: 80  # fs

stage:
  resolution: 1  # nm
  max_speed: 100000  # µm/s
  
photoresist:
  type: "IP-Dip"
  refractive_index: 1.52
```

##  Research Applications

This framework supports various nanofabrication applications:

- **Photonics**: Waveguides, photonic crystals, optical resonators
- **Metamaterials**: Negative index materials, chiral structures
- **Microfluidics**: Lab-on-chip devices, mixing chambers
- **Biomedical**: Tissue scaffolds, drug delivery systems
- **Mechanical**: MEMS devices, micromechanical structures

##  Project Structure

```
two-photon-lithography/
├── src/tpl/           # Core Python package
├── hardware/          # Hardware specs and firmware
├── examples/          # Fabrication examples
├── tests/             # Unit and integration tests
├── docs/              # Documentation
├── notebooks/         # Jupyter tutorials
└── configs/           # Configuration files
```

##  Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

##  Acknowledgments

Developed as part of semiconductor technology research at BTU Cottbus-Senftenberg.

- Based on research in two-photon polymerization
- Inspired by open-source scientific instrumentation principles
- Community contributions and feedback

##  Contact

**Zeyad Mustafa**  
Master's Program - Semiconductor Technology  
BTU Cottbus-Senftenberg

GitHub: [@Zeyad-Mustafa](https://github.com/Zeyad-Mustafa)

##  Resources

- [Two-Photon Lithography Overview](docs/theory/two_photon_absorption.md)
- [Hardware Setup Guide](hardware/README.md)
- [Material Database](materials/README.md)
- [Troubleshooting Guide](docs/tutorials/troubleshooting.md)

---

**Note**: This is an academic research project. Hardware control features require appropriate safety measures and equipment calibration.
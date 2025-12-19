# Two-Photon Lithography Toolkit

A comprehensive Python package for designing, simulating, and controlling two-photon lithography (TPL) fabrication systems.

## What is Two-Photon Lithography?

Two-photon lithography is an advanced 3D nanofabrication technique that uses femtosecond laser pulses to polymerize photoresist materials with sub-micron resolution. By focusing laser light to a tiny volume, TPL enables the creation of complex 3D structures for applications in photonics, microfluidics, metamaterials, and biomedical devices.

## Key Features

- **Design Tools**: Import and slice 3D CAD models (STL) with intelligent path planning
- **Hardware Control**: Unified interface for laser systems, piezo stages, and imaging
- **Simulation**: Model two-photon absorption, polymerization kinetics, and thermal effects
- **Optimization**: Automated parameter tuning for resolution and fabrication speed
- **Rich Examples**: Pre-built designs for photonic crystals, microfluidics, and more

## Quick Navigation

### Getting Started
- [Installation & Setup](getting_started.md)
- [Basic Tutorial](tutorials/basic_structure_design.md)
- [Example Structures](examples/example_structures.md)

### Theory & Background
- [Two-Photon Absorption Physics](theory/two_photon_absorption.md)
- [Laser Parameters](theory/laser_parameters.md)
- [Photoresist Chemistry](theory/photoresist_chemistry.md)

### Tutorials
- [Designing Your First Structure](tutorials/basic_structure_design.md)
- [Parameter Optimization](tutorials/parameter_optimization.md)
- [Troubleshooting Common Issues](tutorials/troubleshooting.md)

### Reference
- [API Documentation](api_reference/module_documentation.md)
- [Hardware Specifications](../hardware/README.md)
- [Material Database](../materials/README.md)

## System Requirements

**Software**
- Python 3.8+
- NumPy, SciPy, Matplotlib
- Optional: PyQt5 for GUI

**Hardware** (for fabrication)
- Femtosecond laser (typically Ti:Sapphire, ~780nm)
- High-NA objective (≥1.4 NA recommended)
- Piezo positioning stage (sub-nm resolution)
- CMOS/CCD camera for alignment

## Quick Example

```python
from tpl.design import Geometry
from tpl.core import ExposureEngine

# Create a simple cubic structure
structure = Geometry.cube(size=10.0, resolution=0.1)

# Generate optimized exposure path
paths = structure.generate_paths(laser_power=10.0, scan_speed=100.0)

# Execute fabrication (with hardware connected)
engine = ExposureEngine()
engine.fabricate(paths)
```

## Project Structure

```
src/tpl/          # Core Python package
hardware/         # Hardware specs and firmware
materials/        # Photoresist formulations
examples/         # Application-specific examples
data/             # Experimental results
notebooks/        # Interactive tutorials
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

[View License](../LICENSE)

## Citation

If you use this toolkit in your research, please cite:
```
[Citation information to be added]
```

## Support

- **Issues**: [GitHub Issues](https://github.com/Zeyad-Mustafa/two-photon-lithography/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Zeyad-Mustafa/two-photon-lithography/discussions)
- **Documentation**: You're reading it!

---

**Ready to get started?** Head to the [Getting Started Guide](getting_started.md) →

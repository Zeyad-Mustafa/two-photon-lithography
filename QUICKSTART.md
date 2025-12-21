# Quick Start Guide

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Zeyad-Mustafa/two-photon-lithography.git
cd two-photon-lithography
```

### 2. Create virtual environment

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install package in development mode

```bash
pip install -e .
```

## Verify Installation

```bash
python -c "from tpl.design import Cube; print('Success!')"
```

## Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/unit/test_geometry.py -v
```

## Your First Structure

Create a file `my_first_cube.py`:

```python
from tpl.design import Cube

# Create a 10 μm cube
cube = Cube(size=10, center=(0, 0, 10))

# Get properties
print(f"Volume: {cube.get_volume():.2f} μm³")
print(f"Bounds: {cube.get_bounds()}")

# Save to STL
cube.save("output/my_first_cube.stl")
print("Cube saved to output/my_first_cube.stl")
```

Run it:

```bash
python my_first_cube.py
```

## File Structure

After installation, your project should look like:

```
two-photon-lithography/
├── src/
│   └── tpl/
│       ├── __init__.py          ✓ Created
│       ├── design/
│       │   ├── __init__.py      ✓ Created
│       │   ├── geometry.py      ✓ Created
│       │   └── primitives.py    ✓ Created
│       └── core/                (to be implemented)
├── tests/
│   └── unit/
│       ├── test_geometry.py     ✓ Created
│       └── test_path_planning.py ✓ Created
├── examples/
│   ├── basic_shapes/
│   │   └── cube.py              ✓ Created
│   └── photonic_crystals/
│       └── woodpile_structure.py ✓ Created
├── configs/
│   ├── default_config.yaml      ✓ Created
│   └── material_configs/
│       ├── ip_dip.yaml          ✓ Created
│       └── ormocomp.yaml        ✓ Created
├── docs/                        ✓ Created
├── README.md                    ✓ Created
├── requirements.txt             ✓ Created
├── setup.py                     ✓ Created
└── pyproject.toml               ✓ Created
```

## Next Steps

1. **Run examples**:
   ```bash
   python examples/basic_shapes/cube.py
   ```

2. **Read documentation**:
   - [Theory](docs/theory/two_photon_absorption.md)
   - [Tutorials](docs/tutorials/basic_structure_design.md)
   - [API Reference](docs/api_reference/module_documentation.md)

3. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

4. **Explore configurations**:
   - Check `configs/material_configs/ip_dip.yaml`
   - Modify parameters for your system

## Common Issues

### ImportError: No module named 'trimesh'

```bash
pip install trimesh
```

### Tests fail with import errors

Make sure package is installed in development mode:
```bash
pip install -e .
```

### Cannot find configs

Make sure you're running from the project root directory.

## What Works Now

✅ **Geometry creation** - Cube, Sphere, Cylinder, Cone
✅ **File I/O** - Load/save STL files  
✅ **Transformations** - Scale, rotate, translate
✅ **Boolean operations** - Union, intersection, difference
✅ **Tests** - Unit tests for geometry
✅ **Documentation** - Complete theory and tutorials
✅ **Examples** - Working example scripts
✅ **Configurations** - Material and system configs

## What Needs Implementation

⚠️ **PathPlanner** - Toolpath generation (referenced but not implemented)
⚠️ **ExposureEngine** - Hardware control (referenced but not implemented)
⚠️ **Simulation modules** - Physical modeling
⚠️ **Optimization modules** - Parameter tuning

These will be added as the project develops!

## Contact

**Zeyad Mustafa**  
BTU Cottbus-Senftenberg  
GitHub: [@Zeyad-Mustafa](https://github.com/Zeyad-Mustafa)

---

Happy fabricating! 🔬✨
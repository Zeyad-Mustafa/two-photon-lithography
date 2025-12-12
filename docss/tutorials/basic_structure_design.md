# Basic Structure Design Tutorial

## Introduction

This tutorial will guide you through designing and fabricating your first two-photon lithography structures. We'll start with simple geometries and progressively build up to more complex designs. By the end, you'll understand the complete workflow from CAD design to finished structure.

**Prerequisites**:
- Basic understanding of [two-photon absorption](../theory/two_photon_absorption.md)
- TPL system set up and calibrated
- Photoresist prepared (we'll use IP-Dip as example)

**Time Required**: 2-3 hours for complete workflow

## Workflow Overview

```
1. Design → 2. Generate Toolpath → 3. Fabricate → 4. Develop → 5. Characterize
```

## Tutorial 1: Simple Cube (Your First Structure)

### Step 1: Design Parameters

**Target structure**:
- Cube: 10 × 10 × 10 μm
- Material: IP-Dip
- Feature size: ~500 nm lines

**Why start with a cube?**
- ✓ Simple geometry for troubleshooting
- ✓ Tests all three axes equally
- ✓ Easy to measure and verify
- ✓ Quick fabrication (~5 minutes)

### Step 2: Create the Design

**Option A: Python Code**

```python
from tpl.design import Geometry, Cube

# Create a simple cube
cube = Cube(
    size=10.0,  # μm
    center=(0, 0, 10)  # x, y, z in μm (z=10 to keep above substrate)
)

# Save for fabrication
cube.save("designs/my_first_cube.stl")
```

**Option B: CAD Software**

1. Open your CAD software (Fusion 360, SolidWorks, FreeCAD)
2. Create cube: 10 × 10 × 10 μm
3. Export as STL (binary format, fine resolution)
4. Save to `data/designs/stl_files/`

**Important**: Always keep structures >5 μm above substrate for clearance.

### Step 3: Generate Toolpath

```python
from tpl.design import PathPlanner

# Load your geometry
geometry = Geometry.from_stl("designs/my_first_cube.stl")

# Configure path planning
planner = PathPlanner(
    layer_height=0.3,      # μm (z-increment between layers)
    hatch_distance=0.5,    # μm (line spacing within layer)
    scan_speed=50000,      # μm/s
    power=20               # mW
)

# Generate toolpath
toolpath = planner.generate(geometry)
toolpath.save("toolpaths/cube_path.gcode")

# Preview
toolpath.visualize()  # Shows 3D preview of scan path
```

**Key Parameters Explained**:

- **Layer height**: Smaller = better z-resolution, longer time
- **Hatch distance**: Spacing between scan lines (overlap important)
- **Scan speed**: Faster = less dose, lower resolution
- **Power**: Material-dependent, find through testing

### Step 4: Fabrication

```python
from tpl.core import ExposureEngine

# Initialize exposure system
engine = ExposureEngine()
engine.connect()  # Connect to laser and stage

# Load calibration
engine.load_calibration("configs/laser_profiles/default.yaml")

# Execute fabrication
engine.execute(toolpath)
# Progress bar will show: [████████████] 100% | 5:23 elapsed
```

**During fabrication**:
- Monitor laser power stability
- Check stage positioning (no drift)
- Look for fluorescence at focal point (indicates polymerization)
- NO VIBRATIONS - system is very sensitive!

**Estimated time**: ~5 minutes for 10 μm cube

### Step 5: Development

**Protocol for IP-Dip**:

1. **Remove from stage**: Carefully extract substrate with structure
2. **Development bath**: 
   - PGMEA (Propylene glycol monomethyl ether acetate)
   - Immerse for 20 minutes
   - Gentle agitation (swirl every 5 minutes)
3. **Rinse**: 
   - Transfer to IPA (Isopropanol)
   - 2 minutes, gentle swirl
   - Fresh IPA bath: 2 minutes
4. **Drying**: 
   - Critical point drying (CPD) recommended
   - Or: Very slow air drying (risk of collapse)

**Expected result**: Solid 10 μm cube should be visible under optical microscope

### Step 6: Inspection

**Optical microscopy**:
- 50× objective minimum
- Check: Structure present, no debris, proper dimensions

**SEM imaging** (if available):
- Mount on SEM stub (conductive tape)
- Gold/platinum sputter coating (5-10 nm)
- Image at 5-10 kV
- Measure: Line width, layer adhesion, surface quality

**Success criteria**:
- ✓ Cube fully formed (no missing sections)
- ✓ Clean edges
- ✓ Dimensions: 10 ± 1 μm
- ✓ No cracking or delamination

## Tutorial 2: Cylinder (Testing Circular Paths)

### Design

```python
from tpl.design import Cylinder

cylinder = Cylinder(
    radius=5.0,      # μm
    height=15.0,     # μm
    center=(0, 0, 15)
)

cylinder.save("designs/cylinder_test.stl")
```

**New challenge**: Circular scan paths test:
- Stage acceleration limits
- Path smoothness
- Continuous writing vs. point-by-point

### Toolpath Considerations

```python
planner = PathPlanner(
    layer_height=0.3,
    hatch_distance=0.5,
    scan_speed=50000,
    fill_pattern="concentric"  # Better for cylinders than rectilinear
)
```

**Fill patterns**:
- **Rectilinear**: Straight lines, faster
- **Concentric**: Follows contour, smoother for circles
- **Spiral**: Single continuous path, very smooth

## Tutorial 3: Simple Bridge (Overhangs)

### Design Challenge

**Free-standing bridge**:
- Two pillars: 5 × 5 × 10 μm
- Bridge span: 10 μm between pillars
- Bridge cross-section: 2 × 2 μm

```python
from tpl.design import Geometry

# Create custom geometry
bridge = Geometry.from_primitives([
    Cube(size=(5, 5, 10), center=(-7.5, 0, 10)),  # Left pillar
    Cube(size=(5, 5, 10), center=(7.5, 0, 10)),   # Right pillar
    Cube(size=(10, 2, 2), center=(0, 0, 11))      # Bridge span
])

bridge.save("designs/bridge.stl")
```

**Critical considerations**:

**Overhang support**: Bridge has no support underneath!
- Solution: Start with slight incline, or
- Use support structures (removed later)

**Exposure sequence**: Write pillars first, then bridge
```python
planner.set_sequence([
    "pillar_left",
    "pillar_right", 
    "bridge_span"
])
```

**Power adjustment**: May need +20% power for overhang sections
```python
planner.set_region_power("bridge_span", power=24)  # Increased from 20
```

## Tutorial 4: Woodpile Structure (3D Photonic)

### Design Concept

**Woodpile lattice**: Classic 3D photonic crystal
- Layer 1: Lines along X-direction
- Layer 2: Lines along Y-direction (90° rotation)
- Layer 3: Repeat layer 1 (offset by half-period)
- Layer 4: Repeat layer 2 (offset by half-period)

```python
from tpl.design import WoodpileStructure

woodpile = WoodpileStructure(
    line_width=0.5,     # μm
    line_spacing=2.0,   # μm (period)
    layer_height=1.0,   # μm
    num_layers=16,      # 4 complete periods
    size_xy=20          # μm (lateral extent)
)

woodpile.save("designs/woodpile_4x4.stl")
```

### Fabrication Strategy

**Layer-by-layer exposure**:
```python
planner = PathPlanner(
    layer_height=1.0,           # Match design
    scan_speed=100000,          # Faster for simple lines
    power=18,                   # Slightly lower for thin lines
    bidirectional_scan=True     # Write both forward & backward
)
```

**Expected time**: ~10 minutes for 20 μm structure

**Troubleshooting**:
- **Lines break**: Increase power or reduce speed
- **Lines merge**: Reduce power or increase speed/spacing
- **Poor layer adhesion**: Reduce layer height or increase dose

## Design Best Practices

### 1. Feature Size Guidelines

**Minimum features** (IP-Dip, standard conditions):
- Line width: 200 nm (practical), 150 nm (optimal conditions)
- Spacing: 300 nm (reliable), 200 nm (tight)
- Voxel height: 500-800 nm

**If features don't form**:
- Too small → Increase power or reduce speed
- Too large → Decrease power or increase speed

### 2. Aspect Ratio Limits

**Safe aspect ratios**:
- **Vertical structures**: Height/Width < 20:1
- **Horizontal overhangs**: Length/Height < 10:1
- **Gaps/holes**: Diameter > 2× wall thickness

**Beyond these limits**: Risk of collapse, especially during drying

### 3. Structural Integrity

**Strengthen structures**:
```python
# Add internal scaffolding
geometry.add_lattice_fill(
    cell_size=2.0,      # μm
    beam_width=0.5      # μm
)
```

**Support critical regions**:
- Thin walls: Add ribs every 10 μm
- Large overhangs: Temporary supports
- Tall structures: Wider base (pyramid shape)

### 4. Substrate Adhesion

**Improve adhesion**:
1. **Clean substrate**: Piranha or O₂ plasma
2. **Adhesion promoter**: Silane treatment
3. **First layer**: 
   - Lower speed (2× longer exposure)
   - Higher power (+10-20%)
   - Direct contact with substrate

```python
planner.set_first_layer(
    speed=25000,    # Half normal speed
    power=24        # 20% more power
)
```

## Common Mistakes and Solutions

### Mistake 1: Structure doesn't appear after development

**Likely causes**:
- ❌ Power too low → Increase by 5 mW, retry
- ❌ Wrong focal position → Recalibrate z-position
- ❌ Expired photoresist → Use fresh material

### Mistake 2: Structure much larger than designed

**Likely causes**:
- ❌ Power too high → Reduce by 20-30%
- ❌ Speed too slow → Double scan speed
- ❌ Multiple exposure passes → Check for software bug

### Mistake 3: Structure collapses during drying

**Likely causes**:
- ❌ Air drying high aspect ratio → **Must use CPD**
- ❌ Under-polymerization → Increase dose by 30%
- ❌ Over-development → Reduce dev time to 15 min

### Mistake 4: Poor adhesion (structure detaches)

**Likely causes**:
- ❌ Substrate contamination → Clean thoroughly
- ❌ No adhesion promoter → Apply silane
- ❌ First layer under-exposed → Increase first layer power

## Parameter Optimization Workflow

**Systematic approach** for new designs:

### Step 1: Power Sweep (Fixed speed)

```python
powers = [10, 15, 20, 25, 30]  # mW
for power in powers:
    fabricate_test_line(power=power, speed=50000)
```

Result: Find minimum power for complete polymerization

### Step 2: Speed Optimization (Fixed power)

```python
speeds = [20000, 40000, 60000, 80000, 100000]  # μm/s
for speed in speeds:
    fabricate_test_line(power=20, speed=speed)
```

Result: Find maximum speed while maintaining quality

### Step 3: Fine-Tuning (Optimal region)

```python
# Matrix test
for power in [18, 20, 22]:
    for speed in [45000, 50000, 55000]:
        fabricate_test_cube(power=power, speed=speed)
```

Result: Sweet spot for robust fabrication

## Next Steps

**You've learned**:
- ✓ Complete TPL workflow
- ✓ Basic geometry creation
- ✓ Toolpath generation
- ✓ Development procedures
- ✓ Troubleshooting fundamentals

**Continue to**:
- [Parameter Optimization](parameter_optimization.md) - Advanced tuning
- [Complex Geometries](../examples/photonic_crystals/) - Real applications
- [Post-Processing](troubleshooting.md#post-processing) - Improve results

## Quick Reference

### Standard Parameters (IP-Dip)

```yaml
laser:
  power: 20 mW
  wavelength: 780 nm
  
scanning:
  speed: 50000 μm/s
  layer_height: 300 nm
  hatch_distance: 500 nm
  
development:
  developer: PGMEA
  time: 20 minutes
  rinse: IPA, 2×2 minutes
  drying: Critical point drying
```

### Time Estimates

| Structure Type | Size | Fabrication Time |
|----------------|------|------------------|
| Simple cube | 10 μm | 5 minutes |
| Cylinder | 10×15 μm | 8 minutes |
| Bridge | 15 μm span | 10 minutes |
| Woodpile 4×4 | 20 μm | 15 minutes |
| Complex scaffold | 50 μm | 1-2 hours |

---

## Document Information

**Author**: Zeyad Mustafa  
**Affiliation**: BTU Cottbus-Senftenberg, Master's Program in Semiconductor Technology  
**Date**: December 2024  
**Version**: 1.0  
**Tutorial Level**: Beginner  

**Prerequisites**:
- Completed system setup
- Basic Python knowledge (optional)
- Safety training completed

**Learning Outcomes**:
After completing this tutorial, you should be able to:
1. Design basic 3D structures for TPL
2. Generate and optimize toolpaths
3. Execute fabrication reliably
4. Develop and inspect structures
5. Troubleshoot common issues

**Contact**: 
- Linkedin: [@Zeyad_Mustafa](https://www.linkedin.com/in/zeyad-mustafa-905793ab/)
- GitHub: [@Zeyad-Mustafa](https://github.com/Zeyad-Mustafa)
- Project: [two-photon-lithography](https://github.com/Zeyad-Mustafa/two-photon-lithography)

**License**: MIT License - Free for academic and educational use

**Last Updated**: December 9, 2024
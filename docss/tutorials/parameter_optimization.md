# Parameter Optimization Tutorial

## Introduction

Optimizing fabrication parameters is crucial for achieving high-quality structures with reproducible results. This tutorial teaches systematic optimization methods to find the ideal balance between resolution, speed, and structural integrity.

**Prerequisites**:
- Completed [Basic Structure Design](basic_structure_design.md)
- Successfully fabricated simple test structures
- Understanding of laser parameters and photoresist chemistry

**Time Required**: Half day for complete optimization

**Goal**: Establish optimal parameter set for your specific system and material

## Why Optimize?

**System variations** affect results:
- Different laser systems (power, pulse characteristics)
- Photoresist batches and age
- Objective transmission losses
- Environmental conditions

**One size doesn't fit all!** Parameters from literature are starting points, not final values.

## The Optimization Framework

### Three-Stage Approach

```
Stage 1: Power Threshold → Stage 2: Speed Optimization → Stage 3: Resolution Tuning
     (30 min)                      (1 hour)                      (2 hours)
```

## Stage 1: Finding Power Threshold

### Objective

Determine minimum laser power for complete polymerization.

### Method: Power Line Test

**Test structure**: Single horizontal lines at different powers

```python
from tpl.optimization import PowerThresholdFinder

# Automated power sweep
finder = PowerThresholdFinder(
    power_range=(5, 40),      # mW
    power_step=5,             # mW
    scan_speed=50000,         # μm/s fixed
    line_length=20            # μm
)

# Execute test
finder.run()
# Writes 8 lines: 5, 10, 15, 20, 25, 30, 35, 40 mW
```

**Manual approach**:
```python
powers = [5, 10, 15, 20, 25, 30, 35, 40]  # mW
y_position = 0

for power in powers:
    write_line(
        start=(0, y_position, 10),
        end=(20, y_position, 10),
        power=power,
        speed=50000
    )
    y_position += 2  # 2 μm spacing between lines
```

### Development & Analysis

**After development**:
1. Inspect under optical microscope (50×)
2. Identify first power where line is continuous
3. Measure line width for each power

**Expected results**:

| Power (mW) | Result | Line Width (nm) |
|------------|--------|-----------------|
| 5 | Nothing visible | - |
| 10 | Scattered dots | - |
| 15 | Discontinuous line | ~200 |
| 20 | Complete line ← **Threshold** | ~300 |
| 25 | Thick line | ~450 |
| 30 | Very thick line | ~600 |
| 35 | Bloated, bubbles | ~800 |

**Threshold power** (P_th): 20 mW in this example

### Working Power Selection

```
P_working = P_th × 1.3 to 1.5
```

**Example**: P_th = 20 mW → **P_working = 26-30 mW**

**Why multiply?**
- Ensures complete polymerization throughout structure
- Compensates for variations in substrate, resist
- Provides safety margin for reliable fabrication

**Safety margins**:
- 1.2×: Minimal margin, for experienced users
- 1.3-1.4×: **Recommended** for most work
- 1.5×: Conservative, good for critical structures
- >1.5×: Risk of over-exposure

## Stage 2: Speed Optimization

### Objective

Find maximum scan speed while maintaining structure quality.

### Method: Speed Matrix Test

**Test structure**: 5 × 5 × 5 μm cubes at different speeds

```python
from tpl.optimization import SpeedOptimizer

optimizer = SpeedOptimizer(
    power=26,  # From Stage 1 (1.3 × 20 mW)
    speed_range=(20000, 120000),  # μm/s
    speed_step=20000,
    test_geometry="cube",
    cube_size=5
)

optimizer.run()
# Creates 6 cubes at: 20k, 40k, 60k, 80k, 100k, 120k μm/s
```

**Layout**: Arrange cubes in a grid
```python
speeds = [20000, 40000, 60000, 80000, 100000, 120000]
positions = [(i*10, 0, 5) for i in range(len(speeds))]

for speed, pos in zip(speeds, positions):
    write_cube(
        size=5,
        center=pos,
        power=26,
        speed=speed
    )
```

### Evaluation Criteria

**After development**, inspect each cube:

**Structural integrity**:
- ✓ Complete (no missing sections)
- ✓ Sharp edges
- ✓ No visible defects

**Quality metrics**:
1. **Surface finish**: Smooth vs. rough
2. **Dimensional accuracy**: Measure actual size
3. **Mechanical strength**: Gentle probe test

**Scoring system**:

| Speed (μm/s) | Complete? | Surface | Size (μm) | Score |
|--------------|-----------|---------|-----------|-------|
| 20000 | ✓ | Excellent | 5.1 | A+ (overkill) |
| 40000 | ✓ | Excellent | 5.0 | A+ |
| 60000 | ✓ | Good | 4.9 | A |
| 80000 | ✓ | Fair | 4.7 | B |
| 100000 | ✓ | Poor | 4.3 | C |
| 120000 | Incomplete | - | - | F |

**Optimal speed**: 60000 μm/s (highest speed with Grade A)

### Trade-offs

**Slower speeds** (< optimal):
- ✓ Higher quality, more robust
- ✓ Better for complex geometries
- ✗ Longer fabrication time
- ✗ More heat accumulation

**Faster speeds** (> optimal):
- ✓ Shorter fabrication time
- ✓ Less thermal effects
- ✗ Under-polymerization risk
- ✗ Reduced structural integrity

**Application-specific selection**:
- **Prototyping**: Use maximum reliable speed
- **Critical structures**: Use 70-80% of maximum speed
- **Production**: Balance quality and throughput

## Stage 3: Resolution Tuning

### Objective

Achieve smallest feature size while maintaining reliability.

### Method: Resolution Test Pattern

**Test structure**: Lines with decreasing spacing

```python
from tpl.optimization import ResolutionTester

tester = ResolutionTester(
    power=26,
    speed=60000,
    line_spacings=[800, 600, 400, 300, 200, 150, 100],  # nm
    line_length=10  # μm
)

tester.run()
```

**Creates pairs of parallel lines** at each spacing:
```python
spacings = [800, 600, 400, 300, 200, 150, 100]  # nm

for i, spacing in enumerate(spacings):
    y_base = i * 3  # 3 μm between test pairs
    
    # Line 1
    write_line(
        start=(0, y_base, 10),
        end=(10, y_base, 10),
        power=26,
        speed=60000
    )
    
    # Line 2 (parallel, with spacing)
    write_line(
        start=(0, y_base + spacing/1000, 10),  # Convert nm to μm
        end=(10, y_base + spacing/1000, 10),
        power=26,
        speed=60000
    )
```

### Analysis: SEM Required

**Optical microscopy** insufficient for sub-500 nm features

**SEM inspection**:
1. Mount on stub, sputter coat (5 nm Au/Pt)
2. Image at 10-20 kV, 50,000-100,000× magnification
3. Measure actual spacing between lines

**Resolution determination**:

| Spacing (nm) | Result | Image |
|--------------|--------|-------|
| 800 | Two distinct lines | Clear gap |
| 600 | Two distinct lines | Visible gap |
| 400 | Two lines, touching | Barely separated |
| 300 | Merged into one | Single thick line |
| 200 | Merged | - |
| 150 | Merged | - |

**Resolution limit**: **400 nm** (last spacing with distinct lines)

### Fine-Tuning for Resolution

**If resolution insufficient**, try:

**1. Reduce power** (approach threshold):
```python
powers = [24, 26, 28]  # Test around optimal
speeds = [60000]       # Keep speed constant

# Fine power sweep
for power in powers:
    write_resolution_test(power=power, speed=60000)
```

Lower power → smaller voxel → better resolution
But: Risk of incomplete polymerization!

**2. Increase speed**:
```python
powers = [26]
speeds = [60000, 80000, 100000]

# Speed variation
for speed in speeds:
    write_resolution_test(power=26, speed=speed)
```

Higher speed → less dose → smaller features
But: Structure may be weaker!

**3. Reduce layer height and hatch distance**:
```python
PathPlanner(
    layer_height=0.2,      # Was 0.3 μm
    hatch_distance=0.3,    # Was 0.5 μm
    power=26,
    speed=60000
)
```

**Trade-off**: ~2× longer fabrication time

## Advanced Optimization Techniques

### Multi-Parameter Optimization Matrix

**For comprehensive optimization**, test power AND speed together:

```python
from tpl.optimization import ParameterMatrix

matrix = ParameterMatrix(
    powers=[20, 24, 28, 32],         # 4 levels
    speeds=[40000, 60000, 80000],    # 3 levels
    geometry="cube",
    size=5
)

matrix.run()
# Creates 4×3 = 12 test cubes
```

**Layout**: Grid arrangement
```
        40k μm/s    60k μm/s    80k μm/s
20 mW   Cube 1      Cube 2      Cube 3
24 mW   Cube 4      Cube 5      Cube 6
28 mW   Cube 7      Cube 8      Cube 9
32 mW   Cube 10     Cube 11     Cube 12
```

**Analysis**: Visual quality scoring (1-5 scale)

**Result**: Parameter space map showing "sweet spot" region

### Dose Calculation

**Understand exposure dose**:

```
Dose = (Power × Time) / Area
```

For scanning:
```
Dose = Power / (Speed × LineWidth)
```

**Normalized dose** (useful for comparison):
```
D_norm = (P / P_th) × (v_ref / v)
```

Where:
- P_th = threshold power
- v_ref = reference speed (e.g., 50000 μm/s)

**Typical ranges**:
- D_norm < 1.0: Under-polymerization
- D_norm = 1.2-1.5: **Optimal range**
- D_norm > 2.0: Over-polymerization

### Material-Specific Considerations

**Different photoresists** require different parameters:

**IP-Dip**:
- Sensitive: Low threshold (~15-20 mW)
- Fast: High speed possible (>100k μm/s)
- Resolution: Excellent (<200 nm)

**Ormocomp**:
- Less sensitive: Higher threshold (~20-30 mW)
- Slower: Moderate speed (50-80k μm/s)
- Low shrinkage: Dimensional accuracy priority

**SU-8**:
- Poor TPA: Very high power needed (>40 mW)
- Slow: Limited speed (<50k μm/s)
- Robust: Good mechanical properties

**Optimization must be repeated for each material!**

## Environmental Effects

### Temperature Sensitivity

**Ambient temperature** affects polymerization:

**Cold conditions** (<20°C):
- Slower kinetics
- Need +10-20% power or reduced speed
- More viscous resist (flow issues)

**Hot conditions** (>25°C):
- Faster kinetics
- Risk of premature polymerization
- May need -10% power

**Best practice**: Climate-controlled lab (22-24°C)

### Humidity Effects

**High humidity** (>60% RH):
- Water absorption in hygroscopic resists
- Oxygen inhibition reduced (good!)
- Development time may increase

**Low humidity** (<30% RH):
- Electrostatic issues
- Resist may dry on substrate

**Target**: 40-50% RH

## Reproducibility Testing

### Validation Protocol

**After optimization**, verify reproducibility:

```python
# Write 10 identical structures
for i in range(10):
    position = (i*10, 0, 5)
    write_cube(
        size=5,
        center=position,
        power=26,      # Optimized
        speed=60000    # Optimized
    )
```

**Measure**:
1. Feature dimensions (mean ± std)
2. Structural completeness (% success)
3. Surface quality (visual inspection)

**Acceptance criteria**:
- Dimensional variation: <5%
- Success rate: >95%
- Consistent appearance

**If reproducibility poor**:
- Check laser stability
- Verify stage accuracy
- Test fresh photoresist
- Monitor environmental conditions

## Optimization Workflow Summary

### Quick Protocol

**Day 1: Initial screening** (2-3 hours)
1. Power threshold test (30 min fab + 30 min dev + 30 min analysis)
2. Speed optimization (1 hour fab + 30 min dev + 30 min analysis)
3. Select working parameters

**Day 2: Fine-tuning** (3-4 hours)
1. Resolution testing with SEM
2. Multi-parameter matrix
3. Reproducibility validation

**Day 3: Application testing** (ongoing)
1. Fabricate actual target structures
2. Adjust as needed
3. Document final parameters

### Parameter Recording

**Always document** your optimized parameters:

```yaml
# my_optimized_params.yaml
system:
  laser: Ti:Sapphire, 780 nm
  objective: 63×, NA 1.4
  date: 2024-12-09

material:
  resist: IP-Dip
  batch: 2024-10-15
  substrate: Glass coverslip

optimized_parameters:
  power_threshold: 20 mW
  working_power: 26 mW
  optimal_speed: 60000 μm/s
  layer_height: 0.3 μm
  hatch_distance: 0.5 μm
  resolution_limit: 400 nm

development:
  developer: PGMEA
  time: 20 min
  temperature: 22°C

notes: |
  Optimized for general-purpose fabrication.
  Reduce speed to 50k μm/s for critical structures.
  Increase power to 28 mW for thick structures (>50 μm).
```

## Troubleshooting Optimization

### Problem: Can't find clear threshold

**Symptoms**: Gradual transition, no obvious threshold point

**Solutions**:
- Use finer power steps (2-3 mW instead of 5 mW)
- Test longer lines (30-50 μm)
- Check photoresist quality (may be degraded)
- Verify focus position accuracy

### Problem: All speeds fail

**Symptoms**: Incomplete structures at all tested speeds

**Solutions**:
- Increase power by 20-30%
- Reduce speed range (test 10-50k μm/s)
- Check for optical misalignment
- Verify laser pulse characteristics

### Problem: Inconsistent results

**Symptoms**: Same parameters give different outcomes

**Solutions**:
- Check laser power stability
- Monitor temperature (use climate control)
- Test photoresist freshness
- Verify stage positioning accuracy
- Add waiting time between structures (thermal relaxation)

### Problem: Good parameters degrade over time

**Symptoms**: Previously optimal parameters no longer work

**Possible causes**:
- Photoresist aging → Use fresh material
- Laser power drift → Recalibrate
- Objective contamination → Clean optics
- Environmental changes → Monitor conditions

**Action**: Re-run Stage 1 threshold test monthly

## Best Practices Checklist

**Before optimization**:
- [ ] System fully calibrated
- [ ] Fresh photoresist (check expiration)
- [ ] Clean substrate prepared
- [ ] Environment stable (temp, humidity)
- [ ] Sufficient time allocated

**During optimization**:
- [ ] Label all test structures clearly
- [ ] Take photos/notes immediately
- [ ] Use consistent development protocol
- [ ] Process all tests together (same batch)
- [ ] Record environmental conditions

**After optimization**:
- [ ] Document all parameters
- [ ] Validate reproducibility
- [ ] Archive test structures (if possible)
- [ ] Update configuration files
- [ ] Share results with team/community

## Quick Reference Table

### Optimization Targets by Application

| Application | Priority | Target Parameters |
|-------------|----------|-------------------|
| Prototyping | Speed | Max speed, 1.3× threshold |
| Photonic crystals | Resolution | 1.1× threshold, reduced speed |
| Microfluidics | Robustness | 1.5× threshold, moderate speed |
| Mechanical metamaterials | Accuracy | 1.3× threshold, optimized layer height |
| Large structures | Throughput | Max speed, higher power OK |
| Biomedical | Biocompatibility | Minimal power, gentle development |

### Typical Optimization Results

**For IP-Dip on standard system**:
- Threshold: 15-25 mW (depends on system)
- Working power: 20-35 mW
- Speed range: 30-100k μm/s
- Resolution: 200-400 nm
- Layer height: 0.2-0.5 μm

**Remember**: These are typical ranges, not prescriptions!

---

## Document Information

**Author**: Zeyad Mustafa  
**Affiliation**: BTU Cottbus-Senftenberg, Master's Program in Semiconductor Technology  
**Date**: December 2024  
**Version**: 1.0  
**Tutorial Level**: Intermediate  

**Prerequisites**:
- Completed basic structure design tutorial
- Understanding of laser-material interactions
- Access to SEM (for resolution testing)

**Learning Outcomes**:
After completing this tutorial, you should be able to:
1. Systematically optimize fabrication parameters
2. Determine power threshold and working range
3. Balance speed and quality for your application
4. Measure and improve resolution
5. Validate parameter reproducibility
6. Document and maintain optimized settings

**Estimated Time Investment**:
- Initial optimization: 4-6 hours
- Fine-tuning: 2-3 hours
- Validation: 1-2 hours
- **Total**: 1-2 days

**Contact**: 
- Linkedin: [@Zeyad_Mustafa](https://www.linkedin.com/in/zeyad-mustafa-905793ab/)
- GitHub: [@Zeyad-Mustafa](https://github.com/Zeyad-Mustafa)
- Project: [two-photon-lithography](https://github.com/Zeyad-Mustafa/two-photon-lithography)

**License**: MIT License - Free for academic and educational use

**Last Updated**: December 9, 2024
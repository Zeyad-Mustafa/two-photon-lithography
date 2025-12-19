# Laser Parameters for Two-Photon Lithography

## Introduction

The laser system is the heart of any two-photon lithography setup. Selecting and optimizing laser parameters is critical for achieving high-resolution structures with minimal defects. This document provides comprehensive guidance on laser specifications, parameter optimization, and practical considerations for TPL fabrication.

## Essential Laser Requirements

### 1. Wavelength Selection

**Why Near-Infrared (NIR)?**

The ideal wavelength for TPL typically falls in the 700-1000 nm range:

**Advantages of NIR**:
- ✓ Two-photon process accesses UV-equivalent energies (350-500 nm)
- ✓ Deep penetration into photoresists (low single-photon absorption)
- ✓ Minimal linear absorption → reduced heating
- ✓ Less scattering in materials
- ✓ Standard Ti:Sapphire lasers readily available

**Common Wavelengths**:

| Wavelength | Source | Two-Photon Equivalent | Applications |
|------------|--------|----------------------|--------------|
| 780 nm | Ti:Sapphire | 390 nm | Standard TPL, most resists |
| 800 nm | Ti:Sapphire | 400 nm | General purpose |
| 1030 nm | Yb-fiber | 515 nm | Alternative, fiber lasers |
| 1064 nm | Nd:YAG | 532 nm | Less common for TPL |
| 515 nm (SHG) | Doubled Yb | 257.5 nm | Deep UV equivalent |

**Optimal Choice**: **780-800 nm** Ti:Sapphire oscillator
- Best match for most commercial photoresists
- Mature technology, widely available
- Excellent pulse characteristics

### Wavelength-Dependent Considerations

**Photoresist absorption**: Different initiators have peak TPA at different wavelengths

**Dispersion**: Longer wavelengths experience less GVD
```
GVD ∝ λ² (approximately)
```

**Objective transmission**: Some objectives optimized for specific wavelengths

**Practical tip**: Match laser wavelength to photoresist absorption spectrum for maximum efficiency.

### 2. Pulse Duration (τ)

Pulse duration is one of the most critical parameters affecting TPA efficiency.

**Physics of Short Pulses**

Peak power for given average power:
```
P_peak = E_pulse / τ_pulse = P_avg / (f_rep · τ_pulse)
```

For TPL, shorter pulses mean higher peak power → stronger TPA.

**Optimal Range: 50-150 femtoseconds**

**Ultra-short pulses** (<50 fs):
- ✓✓ Extremely high peak intensity
- ✓ Minimal thermal effects
- ✗ Difficult to maintain (dispersion)
- ✗ Risk of ionization/plasma formation
- ✗ Very broad spectral bandwidth

**Short pulses** (50-100 fs):
- ✓ Excellent TPA efficiency
- ✓ Good balance of peak power and stability
- ✓ Manageable dispersion compensation
- ✓ Standard for high-resolution work
- Recommended for critical structures

**Medium pulses** (100-150 fs):
- ✓ Stable, easy to maintain
- ✓ Sufficient for most applications
- ✓ Less sensitive to dispersion
- ✗ Slightly lower peak power
- Recommended for routine fabrication

**Long pulses** (>200 fs):
- ✗ Reduced TPA efficiency
- ✗ May require higher average power
- ✗ Increased thermal damage risk
- Not recommended unless necessary

**Pulse Broadening Effects**

Pulses broaden due to Group Velocity Dispersion (GVD):

```
τ_out² = τ_in² + (GVD · L / τ_in)²
```

**Example**: 100 fs pulse through 10 cm of glass (GVD ≈ 36 fs²/mm):
```
τ_out = √(100² + (36 × 100 / 100)²) = √(10000 + 1296) ≈ 106 fs
```

**Impact on TPA**:
```
I_peak ∝ 1/τ
TPA rate ∝ I² ∝ 1/τ²
```

6 fs broadening → ~12% reduction in TPA efficiency!

**Dispersion Compensation**

**Pre-compensation methods**:
1. **Prism compressor**: Adjustable, broadband
2. **Grating compressor**: High precision
3. **Chirped mirrors**: Compact, fixed compensation
4. **Pulse shaper**: Full control, expensive

**In-situ measurement**: Use autocorrelator or FROG to verify pulse duration at sample.

### 3. Repetition Rate (f_rep)

Repetition rate determines how frequently pulses arrive at the focal spot.

**Standard Rates**:
- Mode-locked Ti:Sapphire: 76-80 MHz
- Fiber lasers: 20-100 MHz  
- Amplified systems: 1 kHz - 1 MHz

**Trade-offs in Repetition Rate**

**High repetition rate** (>50 MHz):

**Advantages**:
- ✓ Smooth, continuous polymerization
- ✓ Better line quality (many pulse overlaps)
- ✓ Lower pulse energy (less damage risk)
- ✓ Efficient use of average power

**Disadvantages**:
- ✗ Heat accumulation in focal volume
- ✗ Potential thermal damage
- ✗ Limited by thermal relaxation time

**Thermal considerations**:
```
τ_thermal ≈ w₀² / (4D_thermal)
```

For typical voxel (w₀ ≈ 300 nm, D_thermal ≈ 10⁻⁷ m²/s):
```
τ_thermal ≈ 225 ns → f_max ≈ 4 MHz for complete cooling
```

At 80 MHz, ~20 pulses arrive before complete cooling → cumulative heating.

**Low repetition rate** (<10 MHz):

**Advantages**:
- ✓ Complete thermal relaxation between pulses
- ✓ Can use higher pulse energies
- ✓ Reduced thermal stress in structures

**Disadvantages**:
- ✗ Fewer pulses per dwell time → need higher dose per pulse
- ✗ Less smooth polymerization
- ✗ May need longer total exposure time

**Optimal Strategy**:

For **standard photoresists** (IP-Dip, Ormocomp):
- 76-80 MHz is optimal (standard Ti:Sapphire)
- Good balance of efficiency and quality

For **temperature-sensitive materials**:
- Consider 10-20 MHz
- May require amplified laser systems

For **fast writing**:
- Higher repetition rate (up to 100 MHz)
- Optimize scan speed to match pulse spacing

### 4. Average Power (P_avg)

Average power determines total energy delivered and fabrication speed.

**Typical Operating Range: 1-50 mW**

Power requirements depend on:
- Photoresist sensitivity
- Scan speed
- Desired feature size
- Objective transmission

**Power Calibration**

Measured power at sample ≠ laser output power

**Power loss sources**:
1. Beam steering optics: ~5% per mirror
2. Dichroic mirrors: 5-15%
3. Objective transmission: 10-30%
4. Immersion interface: 2-5%

**Total transmission**: Often only 50-70% of laser output reaches sample!

**Example**:
- Laser output: 200 mW
- 4 steering mirrors: (0.95)⁴ = 0.81 → 162 mW
- Dichroic: 0.85 → 138 mW
- Objective: 0.70 → 97 mW
- Immersion: 0.95 → **92 mW at sample**

**Always measure power at sample plane!**

**Power Density at Focus**

```
I_avg = P_avg / A_focal = P_avg / (π · w₀²)
```

For w₀ = 250 nm, P_avg = 20 mW:
```
I_avg = 20×10⁻³ / (π × (250×10⁻⁹)²) ≈ 10¹¹ W/m² = 10⁷ W/cm²
```

But peak intensity during pulse is much higher!

**Peak Intensity**

```
I_peak = P_avg / (f_rep · τ_pulse · π · w₀²)
```

For P_avg = 20 mW, f = 80 MHz, τ = 100 fs, w₀ = 250 nm:
```
I_peak ≈ 2×10¹² W/cm²
```

This is above TPA threshold (~10¹² W/cm²) ✓

**Power Optimization Guidelines**

**Too low power** (under-exposure):
- Incomplete polymerization
- Structures wash away during development
- Poor mechanical properties

**Optimal power**:
- Complete polymerization
- Predictable feature sizes
- Good mechanical strength
- Minimal defects

**Too high power** (over-exposure):
- Enlarged features (loss of resolution)
- Thermal damage
- Bubble formation
- Carbonization (extreme cases)

**Finding optimal power** (experimental procedure):

1. **Power sweep**: Write test structures at 5, 10, 15, 20, 25, 30 mW
2. **Develop**: Use standard protocol
3. **Inspect**: SEM imaging
4. **Identify threshold**: Minimum power for complete polymerization
5. **Set working power**: 1.2-1.5× threshold power

### 5. Pulse Energy

Pulse energy determines the dose delivered per pulse.

```
E_pulse = P_avg / f_rep
```

**Typical values**:
- Ti:Sapphire oscillator: 0.1-1 nJ per pulse
- Fiber oscillator: 1-10 nJ per pulse
- Regenerative amplifier: 1-100 μJ per pulse

**Energy Density**

```
F = E_pulse / A_focal [J/cm²]
```

For TPL, typically F ~ 0.01-1 J/cm² per pulse.

**Accumulated Dose**

For scan speed v and pulse spacing d_pulse:

Number of pulses per point:
```
N = f_rep · (w₀ / v)
```

Total dose:
```
D_total = N · F = (f_rep · w₀ / v) · (E_pulse / A_focal)
```

**Example**: v = 50 μm/s, w₀ = 300 nm, f = 80 MHz
```
N = 80×10⁶ × 300×10⁻⁹ / 50×10⁻⁶ = 480 pulses
```

High pulse overlap ensures smooth polymerization.

## Advanced Laser Considerations

### 1. Beam Quality (M²)

M² factor describes how close the beam is to ideal Gaussian:
- M² = 1: Perfect Gaussian (ideal)
- M² = 1-1.2: Excellent (typical for mode-locked lasers)
- M² > 1.5: Poor quality (may degrade resolution)

**Impact on focusing**:
```
w₀ = (M² · λ) / (π · NA)
```

Poor beam quality → larger focal spot → reduced resolution

**Requirements for TPL**: M² < 1.3

### 2. Pointing Stability

Beam pointing instability causes:
- Position errors in fabricated structures
- Dose variations
- Reduced reproducibility

**Acceptable stability**: <1 μrad angular, <5% power fluctuation

**Causes of instability**:
- Temperature variations
- Mechanical vibrations
- Laser cavity drift
- Air turbulence in beam path

**Solutions**:
- Active stabilization systems
- Enclosed beam path
- Temperature-controlled environment
- Vibration isolation

### 3. Polarization Control

**Polarization effects in TPL**:

TPA cross-section depends on polarization relative to molecular orientation:
```
σ_TPA ∝ |ε · μ|²
```

Where ε = polarization direction, μ = transition dipole moment

**Circular polarization**: Often preferred
- Isotropic TPA (orientation-independent)
- Uniform voxel shape
- Less sensitive to sample orientation

**Linear polarization**: Can be advantageous
- Higher TPA for aligned molecules
- Anisotropic structures
- Polarization-dependent devices

**Implementation**:
- Quarter-wave plate for circular polarization
- Half-wave plate for rotation control
- Critical for high-NA objectives (depolarization effects)

### 4. Spectral Bandwidth

**Transform-limited pulses**:
```
Δν · τ ≥ K
```

Where K ≈ 0.44 for Gaussian pulses.

For τ = 100 fs:
```
Δν ≥ 4.4 THz → Δλ ≈ 9 nm at 800 nm
```

**Spectral considerations**:
- Broad spectrum: Chromatic aberration in objectives
- Narrow spectrum: Easier to focus, but limits short pulses
- Photoresist spectral response

**Optimization**: Use wavelength within photoresist peak absorption ±20 nm

## Laser System Types

### 1. Ti:Sapphire Oscillators

**Specifications**:
- Wavelength: 700-1000 nm (tunable)
- Pulse duration: 10-100 fs
- Repetition rate: 76-80 MHz
- Average power: 0.1-2 W
- Pulse energy: ~10 nJ

**Advantages**:
- ✓ Excellent pulse characteristics
- ✓ Tunable wavelength
- ✓ Ultra-short pulses available
- ✓ High beam quality (M² < 1.1)
- ✓ Industry standard

**Disadvantages**:
- ✗ Requires maintenance (alignment)
- ✗ Expensive
- ✗ Large footprint
- ✗ Pump laser needed

**Best for**: High-resolution research, wavelength flexibility needed

### 2. Fiber Lasers

**Specifications**:
- Wavelength: 1030 nm or 1550 nm (fixed)
- Pulse duration: 100-500 fs
- Repetition rate: 20-100 MHz (adjustable)
- Average power: 0.5-10 W
- Pulse energy: 10-100 nJ

**Advantages**:
- ✓ Compact, robust
- ✓ Maintenance-free
- ✓ Good long-term stability
- ✓ Lower cost
- ✓ Higher average power available

**Disadvantages**:
- ✗ Fixed wavelength
- ✗ Longer pulses (typically >200 fs)
- ✗ Less mature for TPL applications

**Best for**: Industrial applications, routine fabrication

### 3. Amplified Systems

**Specifications**:
- Wavelength: 800 nm or 1030 nm
- Pulse duration: 30-200 fs
- Repetition rate: 1 kHz - 1 MHz
- Average power: 1-50 W
- Pulse energy: 1-100 μJ

**Advantages**:
- ✓ Very high pulse energy
- ✓ Adjustable repetition rate
- ✓ Deep penetration possible

**Disadvantages**:
- ✗ Very expensive
- ✗ Complex system
- ✗ Potential for sample damage
- ✗ Overkill for most TPL

**Best for**: Specialized applications, thick samples, nonlinear microscopy

## Laser Power Optimization Strategies

### Method 1: Threshold Determination

**Protocol**:
1. Design simple test structure (line or cube)
2. Fabricate at increasing powers: 5, 10, 15, 20, 25, 30 mW
3. Keep all other parameters constant (speed, spacing)
4. Develop and inspect
5. Identify minimum power for complete structure
6. Optimal power = 1.3× threshold

**Example results**:
- 5 mW: Nothing visible
- 10 mW: Partial structure, weak
- 15 mW: Complete but fragile ← **threshold**
- 20 mW: Robust structure ← **optimal (1.3×)**
- 25 mW: Slightly enlarged features
- 30 mW: Over-exposed, bubbles

### Method 2: Line Width Analysis

**Protocol**:
1. Write single lines at various powers
2. Measure line width with SEM
3. Plot line width vs. power
4. Select power for desired width

**Expected behavior**:
```
w(P) = w₀ · √(ln(P/P_th))
```

Where w₀ is minimum achievable width.

**Optimization**: Choose power where w(P) = target feature size

### Method 3: Dose Matrix

**Protocol**:
1. Create matrix: Power (columns) × Speed (rows)
2. Each cell: 10×10×10 μm test cube
3. Typical ranges:
   - Power: 10-40 mW (5 mW steps)
   - Speed: 20-100 μm/s (20 μm/s steps)
4. Develop and inspect
5. Identify "sweet spot" region

**Result**: Optimal parameter window for robust fabrication

### Method 4: In-Situ Monitoring

**Real-time feedback** during fabrication:

**Fluorescence monitoring**:
- Photoresist emits fluorescence during polymerization
- Monitor with PMT or camera
- Intensity correlates with polymerization degree

**Advantages**:
- ✓ Immediate feedback
- ✓ Can adjust power on-the-fly
- ✓ Detect incomplete polymerization

**Challenges**:
- Fluorescence signal affected by many factors
- Calibration needed
- Additional hardware required

## Safety Considerations

### 1. Laser Safety Classes

**Class 4 Lasers** (typical for TPL):
- Can cause permanent eye damage
- Can ignite materials
- Requires strict safety protocols

**Required safety measures**:
- Safety interlocks on enclosure
- Beam shutters
- Warning signs
- Laser safety goggles (OD 7+ at laser wavelength)
- Training and certification

### 2. Eye Safety

**NIR hazard**: 780-1000 nm passes through cornea, focuses on retina

**Never**:
- ✗ Look at beam or reflections
- ✗ Remove safety goggles during operation
- ✗ Use optical aids (magnifiers) without protection

**Always**:
- ✓ Wear appropriate laser safety goggles
- ✓ Block beam path when not in use
- ✓ Use IR viewing card to locate beam
- ✓ Terminate beam at beam block

### 3. Chemical Safety

Combined laser and photoresist handling:
- Work in ventilated area
- Use appropriate gloves (nitrile)
- Avoid skin contact with uncured resin
- Proper disposal of chemical waste

## Troubleshooting Guide

### Problem: Poor TPA efficiency

**Symptoms**: High power needed, incomplete polymerization

**Possible causes**:
1. Pulse broadening (dispersion)
   - **Solution**: Add/adjust pre-compensation
2. Poor beam quality
   - **Solution**: Check laser mode, clean optics
3. Mismatched wavelength
   - **Solution**: Verify photoresist absorption spectrum
4. Low objective transmission
   - **Solution**: Measure actual power at sample

### Problem: Unstable fabrication

**Symptoms**: Irreproducible results, varying structure quality

**Possible causes**:
1. Power fluctuations
   - **Solution**: Check laser stability, use power meter
2. Pointing instability
   - **Solution**: Improve laser alignment, vibration isolation
3. Environmental factors
   - **Solution**: Temperature control, acoustic isolation
4. Photoresist aging
   - **Solution**: Use fresh resist, proper storage

### Problem: Thermal damage

**Symptoms**: Bubbles, carbonization, deformed structures

**Possible causes**:
1. Too high power
   - **Solution**: Reduce power by 20-30%
2. Too slow scan speed (excessive dose)
   - **Solution**: Increase speed
3. High repetition rate + poor heat dissipation
   - **Solution**: Reduce rep rate or add delays
4. Multiple passes without cooling
   - **Solution**: Add wait time between passes

### Problem: No polymerization

**Symptoms**: Nothing visible after development

**Possible causes**:
1. Power too low
   - **Solution**: Increase power, check optical path
2. Expired photoresist
   - **Solution**: Use fresh material
3. Focal position wrong
   - **Solution**: Recalibrate z-position
4. Oxygen inhibition
   - **Solution**: Inert atmosphere or oxygen scavenger

## Calibration Procedures

### 1. Power Calibration

**Equipment needed**:
- Thermal power meter (calibrated for NIR)
- Neutral density filters (optional)

**Procedure**:
1. Remove sample from stage
2. Place power meter at sample position
3. Measure power at various laser settings
4. Create calibration curve: Laser setting vs. Power at sample
5. Account for objective transmission
6. Update software with calibration

**Frequency**: Weekly or after any optical path change

### 2. Pulse Duration Measurement

**Equipment needed**:
- Autocorrelator or FROG system

**Procedure**:
1. Place measurement device after objective (if possible)
2. Measure pulse duration
3. Compare to specified value
4. Adjust dispersion compensation if needed
5. Verify improvement

**Frequency**: Monthly or when changing wavelength

### 3. Beam Profile Analysis

**Equipment needed**:
- Beam profiler or CCD camera

**Procedure**:
1. Image beam before focusing
2. Check for asymmetry, aberrations
3. Verify Gaussian profile
4. Calculate M² factor
5. Adjust beam shaping if needed

**Frequency**: Quarterly or when resolution degrades

## Performance Metrics

### Key Performance Indicators

**1. Resolution**:
- Lateral: 200-300 nm (typical)
- Axial: 500-800 nm (typical)
- Measurement: SEM of calibration structures

**2. Reproducibility**:
- Feature size variation: <5%
- Structure position: <50 nm
- Measurement: Repeated test structures

**3. Throughput**:
- Voxel rate: 10⁶-10⁸ voxels/second
- Depends on: Power, speed, voxel size
- Measurement: Time to complete standard geometry

**4. Material efficiency**:
- Threshold power: Lower is better
- Dynamic range: Larger is better (under-exposure to over-exposure)
- Measurement: Power sweep analysis

## Recommended Starting Parameters

**For IP-Dip photoresist**:
```yaml
wavelength: 780 nm
pulse_duration: 100 fs
repetition_rate: 80 MHz
average_power: 15-20 mW  # at sample
scan_speed: 50000 μm/s
line_spacing: 200 nm
layer_height: 300 nm
objective: 63×, NA 1.4, oil immersion
```

**For Ormocomp photoresist**:
```yaml
wavelength: 800 nm
pulse_duration: 120 fs
repetition_rate: 80 MHz
average_power: 10-15 mW
scan_speed: 100000 μm/s
line_spacing: 300 nm
layer_height: 500 nm
objective: 100×, NA 1.4, oil immersion
```

**General optimization tip**: Start with these parameters, then systematically optimize one parameter at a time while monitoring structure quality.

## Summary and Best Practices

### Critical Success Factors

1. **Pulse duration**: Keep τ < 150 fs for best TPA
2. **Power calibration**: Always measure at sample
3. **Wavelength matching**: Align with photoresist absorption
4. **Beam quality**: Maintain M² < 1.3
5. **Stability**: Minimize power and pointing fluctuations

### Optimization Workflow

```
1. Set up laser system
   ↓
2. Calibrate power at sample
   ↓
3. Verify pulse duration
   ↓
4. Find threshold power
   ↓
5. Set optimal power (1.3× threshold)
   ↓
6. Optimize scan speed
   ↓
7. Fine-tune for specific geometry
   ↓
8. Validate with test structures
```

### Maintenance Schedule

**Daily**:
- Check power output
- Verify laser mode lock

**Weekly**:
- Power calibration
- Clean optics
- Check pointing stability

**Monthly**:
- Pulse duration verification
- Beam profile analysis
- Update calibration curves

**Quarterly**:
- Full system alignment
- Replace worn components
- Comprehensive performance test

---

**Related Documentation**: 
- [Two-Photon Absorption Theory](two_photon_absorption.md) - Physical principles
- [Photoresist Chemistry](photoresist_chemistry.md) - Material properties
- [Parameter Optimization Tutorial](../tutorials/parameter_optimization.md) - Practical optimization guide
- [Laser Calibration Scripts](../../scripts/calibration/laser_power_calibration.py) - Automated calibration

---

## Document Information

**Author**: Zeyad Mustafa  
**Affiliation**: BTU Cottbus-Senftenberg, Master's Program in Semiconductor Technology  
**Date**: December 2024  
**Version**: 1.0  
**Status**: Active Development  

**Document History**:
- v1.0 (Dec 2024): Initial comprehensive laser parameter documentation
- Future updates: Will include experimental optimization data and advanced techniques

**Contact**: 
- Linkedin: [@Zeyad_Mustafa](https://www.linkedin.com/in/zeyad-mustafa-905793ab/)
- GitHub: [@Zeyad-Mustafa](https://github.com/Zeyad-Mustafa)
- Project: [two-photon-lithography](https://github.com/Zeyad-Mustafa/two-photon-lithography)

**License**: MIT License - Free for academic and research use

**Citation**: 
If you use this documentation in your research, please cite:
```
Mustafa, Z. (2024). Laser Parameters for Two-Photon Lithography. 
Two-Photon Lithography Project Documentation. 
BTU Cottbus-Senftenberg.
https://github.com/Zeyad-Mustafa/two-photon-lithography
```

**Acknowledgments**:
- BTU Cottbus-Senftenberg Semiconductor Technology Department
- Laser safety guidelines based on ANSI Z136 standards
- Optimization procedures derived from extensive experimental work in the field

**Keywords**: Femtosecond laser, pulse parameters, two-photon lithography, laser optimization, Ti:Sapphire laser, beam quality, pulse duration, laser safety

**Last Updated**: December 9, 2024
# Troubleshooting Guide

## Introduction

This guide helps diagnose and fix common issues in two-photon lithography. Problems are organized by symptom, with causes listed from most to least common.

**How to use this guide**:
1. Find your symptom in the table of contents
2. Check causes in order (most common first)
3. Apply suggested solution
4. Re-test with simple structure

**Quick tip**: 80% of problems are power-related or development issues!

## Problem Categories

1. [No Structure After Development](#no-structure-after-development)
2. [Incomplete or Broken Structures](#incomplete-or-broken-structures)
3. [Over-Exposed Structures](#over-exposed-structures)
4. [Structure Collapse](#structure-collapse)
5. [Poor Adhesion](#poor-adhesion)
6. [Resolution Issues](#resolution-issues)
7. [Surface Defects](#surface-defects)
8. [Hardware Problems](#hardware-problems)

---

## No Structure After Development

**Symptom**: Nothing visible under microscope after development

### Cause 1: Insufficient Laser Power (70% of cases)

**Check**: Is power below threshold?

**Test**:
```python
# Quick power test
write_line(power=30, speed=50000, length=20)  # High power
write_line(power=20, speed=50000, length=20)  # Medium
write_line(power=10, speed=50000, length=20)  # Low
```

**Solution**:
- Increase power by 30-50%
- Re-run [power threshold test](parameter_optimization.md#stage-1-finding-power-threshold)
- Check power meter reading at sample

### Cause 2: Wrong Focal Position

**Check**: Is z-position calibrated correctly?

**Test**:
```python
# Write at different z-heights
for z in [8, 9, 10, 11, 12]:  # μm above substrate
    write_cube(size=5, center=(0, 0, z), power=25)
```

**Solution**:
- Recalibrate z-position using interface method
- Write initial structures at z=10-15 μm (safe clearance)
- Check objective immersion (oil contact?)

### Cause 3: Expired/Contaminated Photoresist

**Check**: 
- Color changed (yellowing)?
- Storage temperature correct?
- Opened >3 months ago?

**Solution**:
- Use fresh photoresist batch
- Store at 4°C in dark
- Filter if contamination suspected (0.2 μm PTFE)

### Cause 4: Over-Development

**Check**: Development time too long?

**Test**: Reduce development time by 50%

**Solution**:
- IP-Dip: 15-20 minutes (not 30+)
- Ormocomp: 20-25 minutes
- Use fresh developer (not reused >10 times)

---

## Incomplete or Broken Structures

**Symptom**: Structure partially formed, missing sections, or broken lines

### Cause 1: Borderline Under-Exposure

**Visual signs**: Thin lines, fragile, missing top layers

**Solution**:
- Increase power by 15-20%
- Reduce scan speed by 30%
- Check last layer exposure (often under-dosed)

### Cause 2: Stage Movement Issues

**Check**: Are XY stages moving smoothly?

**Test**: Write simple grid
```python
# Grid test pattern
for x in range(0, 50, 10):
    write_line(start=(x, 0, 10), end=(x, 50, 10))
for y in range(0, 50, 10):
    write_line(start=(0, y, 10), end=(50, y, 10))
```

**Look for**: Irregular spacing, missing sections at turns

**Solution**:
- Check stage controller connection
- Reduce acceleration/deceleration settings
- Verify position feedback is working
- Clean stage mechanics

### Cause 3: Laser Power Fluctuations

**Check**: Is laser power stable?

**Test**: Monitor power with meter over 10 minutes

**Solution**:
- Check laser mode lock quality
- Allow 30 min warm-up before fabrication
- Verify power supply stability
- Check for mechanical vibrations affecting laser

### Cause 4: Gas Bubbles in Resist

**Visual signs**: Voids, missing chunks in random locations

**Solution**:
- Degas photoresist before use (vacuum, 10 minutes)
- Avoid shaking resist bottle
- Let resist settle 30 min after dispensing
- Reduce laser power if boiling occurs

---

## Over-Exposed Structures

**Symptom**: Structures larger than designed, bloated features, merged lines

### Cause 1: Excessive Power

**Visual signs**: Fat lines, rounded features, loss of detail

**Solution**:
- Reduce power by 20-30%
- Increase scan speed by 50%
- Use [dose calculation](parameter_optimization.md#dose-calculation) to find optimal

### Cause 2: Multiple Exposure Passes

**Check**: Is structure being exposed twice?

**Solution**:
- Check toolpath for overlapping segments
- Verify no software duplication bug
- Ensure proper layer offsetting

### Cause 3: Thermal Accumulation

**Visual signs**: Progressive bloating through structure height

**Solution**:
- Reduce repetition rate (if adjustable)
- Add 1-5 second delays between layers
- Reduce scan speed (less heat per unit time)
- Use pulse picker to reduce effective rep rate

---

## Structure Collapse

**Symptom**: Structure forms but collapses during drying or handling

### Cause 1: Air Drying High Aspect Ratio (Most Common!)

**Critical**: Aspect ratio >10:1 **requires** critical point drying

**Solution**:
- **Use CPD** - no exceptions for delicate structures
- If no CPD available: Design thicker features (lower aspect ratio)
- Supercritical drying alternative: Freeze-drying

### Cause 2: Under-Polymerization

**Visual signs**: Soft, gel-like, collapses easily

**Solution**:
- Increase power by 30-40%
- Reduce speed by 50%
- Post-cure: UV flood exposure (15-30 min)
- Thermal annealing if resist allows

### Cause 3: Over-Development

**Check**: Did structure look good before drying?

**Solution**:
- Reduce development time by 30%
- Use gentler developer (IPA instead of acetone)
- Less agitation during development

### Cause 4: Poor Internal Structure

**Design issue**: No scaffolding for large structures

**Solution**:
```python
# Add internal support lattice
geometry.add_lattice_fill(
    cell_size=3.0,      # μm
    beam_width=0.8,     # μm  
    fill_pattern="gyroid"  # Strong topology
)
```

---

## Poor Adhesion

**Symptom**: Structure detaches from substrate, slides around

### Cause 1: Contaminated Substrate

**Most common cause!**

**Solution**:
- Clean with acetone, then IPA, then DI water
- Better: Piranha solution (H₂SO₄:H₂O₂, 3:1) - **CAUTION: Dangerous!**
- Or: Oxygen plasma cleaning (10 min, 100W)
- Always use fresh gloves when handling substrates

### Cause 2: No Adhesion Promoter

**Solution**:
- Apply silane coupling agent:
  - MPTMS (methacrylate-functional silane)
  - Spin coat or vapor deposition
  - Bake 120°C, 20 minutes
- Or use commercial adhesion promoters (TI Prime, etc.)

### Cause 3: First Layer Under-Exposed

**Check**: Do structures attach initially but detach after handling?

**Solution**:
```python
# Increase first layer dose
planner.set_first_layer(
    power=30,       # +30% power
    speed=25000     # Half speed
)
```

### Cause 4: Substrate Material Mismatch

**Check**: What substrate are you using?

**Solutions by substrate**:
- **Glass**: Best adhesion, standard protocols
- **Silicon**: Needs surface oxidation or silanization
- **ITO**: Clean thoroughly, may need adhesion promoter
- **Polymer**: Very difficult, try plasma treatment
- **Metal**: Requires oxide layer or primer

---

## Resolution Issues

**Symptom**: Cannot achieve small features, everything looks blurry

### Cause 1: Too Much Power

**Solution**: Reduce power closer to threshold
- Try 1.1-1.2× threshold instead of 1.5×
- Accept slower speed for better resolution
- Fine-tune in 2 mW increments

### Cause 2: Optical Aberrations

**Check**: 
- Is objective clean?
- Correct immersion medium?
- Cover glass thickness correct?

**Solution**:
- Clean objective front lens (lens paper + isopropanol)
- Use specified immersion oil (n=1.518 for most)
- Match cover glass thickness (typically #1.5 = 170 μm)

### Cause 3: Pulse Broadening (Dispersion)

**Check**: Are pulses arriving broadened?

**Test**: Measure pulse duration at sample (if autocorrelator available)

**Solution**:
- Add dispersion pre-compensation (prism pair)
- Minimize glass in beam path
- Use optimized objectives for 780 nm

### Cause 4: Stage Resolution Limits

**Check**: Minimum step size of positioning stages

**Solution**:
- Verify stage has <10 nm resolution
- Check for backlash in mechanics
- Enable closed-loop feedback if available
- Consider upgrading to piezo stages

---

## Surface Defects

**Symptom**: Rough surfaces, bumps, irregular texture

### Cause 1: Developer Residue

**Visual signs**: White haze, cloudy appearance

**Solution**:
- Better rinsing: 2-3 IPA baths, 2 min each
- Final rinse with fresh IPA
- Gentle agitation during rinse

### Cause 2: Oxygen Inhibition Layer

**Visual signs**: Sticky outer surface, uneven polymerization

**Solution**:
- Work under inert atmosphere (N₂ purge box)
- Use immersion oil during writing (blocks O₂ diffusion)
- Increase photoinitiator concentration (+50%)
- Add oxygen scavenger to resist

### Cause 3: Photoresist Precipitation

**Visual signs**: Particles embedded in structure

**Solution**:
- Filter photoresist (0.2 μm syringe filter)
- Check resist shelf life
- Store properly (4°C, dark, sealed)

### Cause 4: Dust/Contamination

**Solution**:
- Work in clean environment (laminar flow hood ideal)
- Cover resist when not in use
- Clean substrate immediately before use
- Filter all solvents

---

## Hardware Problems

### Laser Issues

**Symptom**: Inconsistent results, power drifts

**Diagnostic**:
```python
# Monitor laser power over time
monitor_power(duration=600, interval=10)  # 10 min, measure every 10s
```

**Solutions**:
- Allow proper warm-up (30-60 minutes)
- Check cooling water flow and temperature
- Verify power supply is stable
- Mode-lock quality: Check for spurious peaks
- Contact laser manufacturer if persistent

### Stage Positioning Errors

**Symptom**: Structures misaligned, shifted, or distorted

**Test**: Write calibration grid
```python
# 50 μm grid, should be perfectly square
write_calibration_grid(size=50, spacing=10)
```

**Measure with SEM**: Check for:
- Scale errors (compression/expansion)
- Rotation
- Non-orthogonality
- Position-dependent errors

**Solutions**:
- Recalibrate stage scaling factors
- Check for mechanical binding
- Verify encoder signals
- Update stage controller firmware

### Focus Drift

**Symptom**: Bottom good, top under-exposed (or vice versa)

**Solution**:
- Check objective immersion oil level
- Verify sample is firmly mounted
- Temperature stabilize system (wait 1 hour)
- Use autofocus routine every layer (if available)
- Check for air currents around sample

---

## Quick Diagnostic Flowchart

```
Problem?
   │
   ├─ Nothing appears → Check: Power, Focus, Development
   │
   ├─ Too big → Check: Reduce power, Increase speed
   │
   ├─ Breaks/collapses → Check: Power too low, CPD needed
   │
   ├─ Falls off → Check: Clean substrate, Adhesion promoter
   │
   └─ Poor resolution → Check: Power (reduce), Optics (clean)
```

## Emergency Quick Fixes

### "I need results TODAY"

**Ultra-safe parameters** (works 90% of time with IP-Dip):
```yaml
power: 30 mW          # High, but safe
speed: 40000 μm/s     # Slow, reliable
layer_height: 0.5 μm  # Conservative
hatch_distance: 0.7 μm
development: 25 min PGMEA
drying: CPD (or very slow air dry)
```

These aren't optimal, but **they work** when you're under pressure.

### "System was working, now broken"

**Check list** (in order):
1. [ ] Laser power at sample (measure!)
2. [ ] Photoresist age (<3 months?)
3. [ ] Substrate clean?
4. [ ] Focus position (recalibrate)
5. [ ] Stage moving correctly?
6. [ ] Temperature changed significantly?

Usually #1 (power) or #2 (resist) is the culprit.

## Preventive Maintenance

**Daily**:
- Check laser power
- Verify stage homing
- Visual inspection of optics

**Weekly**:
- Clean objective
- Test with calibration structure
- Check photoresist quality

**Monthly**:
- Full power calibration
- Stage accuracy verification
- Replace immersion oil
- Clean all optical surfaces

**Quarterly**:
- Professional laser service
- Replace worn components
- Full system recalibration

---

## Getting Help

**Before asking for help**, collect this information:

1. **System details**: Laser, objective, photoresist
2. **Parameters used**: Power, speed, layer height
3. **Images**: Optical and SEM if possible
4. **What you tried**: List attempted solutions
5. **Reproducibility**: Happens always or sometimes?

**Where to get help**:
- GitHub Issues: [Report problems](https://github.com/Zeyad-Mustafa/two-photon-lithography/issues)
- Documentation: Review [theory](../theory/) and [examples](../../examples/)
- Community: TPL research forums, conferences

**Remember**: Most problems have been encountered before!

---

## Document Information

**Author**: Zeyad Mustafa  
**Affiliation**: BTU Cottbus-Senftenberg, Master's Program in Semiconductor Technology  
**Date**: December 2024  
**Version**: 1.0  
**Tutorial Level**: All Levels  

**This guide covers**:
- Common fabrication problems and solutions
- Diagnostic procedures
- Quick fixes for time-critical situations
- Preventive maintenance

**Quick Reference**:
Most common issues (80% of problems):
1. Insufficient power
2. Poor substrate cleaning
3. Wrong development time
4. Incorrect focus position
5. Expired photoresist

**Contact**: 
- Linkedin: [@Zeyad_Mustafa](https://www.linkedin.com/in/zeyad-mustafa-905793ab/)
- GitHub: [@Zeyad-Mustafa](https://github.com/Zeyad-Mustafa)
- Project: [two-photon-lithography](https://github.com/Zeyad-Mustafa/two-photon-lithography)

**License**: MIT License - Free for academic and educational use

**Last Updated**: December 9, 2024
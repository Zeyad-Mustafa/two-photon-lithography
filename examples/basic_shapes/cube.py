#!/usr/bin/env python3
"""
Simple Cube Fabrication Example
================================

This example demonstrates the basic workflow for fabricating a simple cube
structure using two-photon lithography. This is an ideal first structure
for testing and calibration.

Structure: 10 × 10 × 10 μm cube
Material: IP-Dip photoresist
Time: ~5 minutes fabrication

Author: Zeyad Mustafa
Date: December 2024
BTU Cottbus-Senftenberg
"""

import numpy as np
from pathlib import Path

# Import TPL modules
from tpl.design import Cube, PathPlanner
from tpl.core import ExposureEngine
from tpl.utils import load_config, save_results

# Optional: For visualization
try:
    import matplotlib.pyplot as plt
    PLOT_AVAILABLE = True
except ImportError:
    PLOT_AVAILABLE = False
    print("Matplotlib not available. Skipping visualizations.")


def create_simple_cube(size=10.0, center=(0, 0, 10)):
    """
    Create a simple cube geometry.
    
    Parameters
    ----------
    size : float
        Edge length of cube in micrometers
    center : tuple
        (x, y, z) position of cube center in micrometers
        
    Returns
    -------
    Cube
        Geometry object representing the cube
    """
    print(f"Creating cube: {size} × {size} × {size} μm")
    print(f"Center position: {center}")
    
    cube = Cube(
        size=size,
        center=center
    )
    
    # Get and display geometry info
    bounds = cube.get_bounds()
    print(f"\nGeometry bounds:")
    print(f"  X: {bounds[0][0]:.1f} to {bounds[0][1]:.1f} μm")
    print(f"  Y: {bounds[1][0]:.1f} to {bounds[1][1]:.1f} μm")
    print(f"  Z: {bounds[2][0]:.1f} to {bounds[2][1]:.1f} μm")
    
    return cube


def generate_toolpath(geometry, output_dir="output"):
    """
    Generate fabrication toolpath from geometry.
    
    Parameters
    ----------
    geometry : Geometry
        Input geometry to convert to toolpath
    output_dir : str
        Directory for output files
        
    Returns
    -------
    Toolpath
        Generated toolpath object
    """
    print("\n" + "="*60)
    print("GENERATING TOOLPATH")
    print("="*60)
    
    # Configure path planner
    planner = PathPlanner(
        layer_height=0.3,        # μm - z increment between layers
        hatch_distance=0.5,      # μm - spacing between scan lines
        scan_speed=50000,        # μm/s - writing speed
        power=20,                # mW - laser power
        fill_pattern="rectilinear"  # Straight line fill
    )
    
    # Optional: Increase first layer exposure for better adhesion
    planner.set_first_layer(
        power=24,      # +20% power
        speed=25000    # Half speed
    )
    
    print("\nPath planning parameters:")
    print(f"  Layer height: {planner.layer_height} μm")
    print(f"  Hatch distance: {planner.hatch_distance} μm")
    print(f"  Scan speed: {planner.scan_speed} μm/s")
    print(f"  Laser power: {planner.power} mW")
    print(f"  Fill pattern: {planner.fill_pattern}")
    print(f"\n  First layer: {planner.first_layer_power} mW @ {planner.first_layer_speed} μm/s")
    
    # Generate toolpath
    print("\nGenerating toolpath...")
    toolpath = planner.generate(geometry)
    
    # Get statistics
    stats = toolpath.get_statistics()
    print(f"\nToolpath statistics:")
    print(f"  Total points: {stats['num_points']}")
    print(f"  Total length: {stats['total_length']:.1f} μm")
    print(f"  Number of layers: {stats['num_layers']}")
    print(f"  Estimated time: {stats['time_estimate']:.1f} seconds ({stats['time_estimate']/60:.1f} min)")
    
    # Save toolpath
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    toolpath_file = Path(output_dir) / "cube_toolpath.gcode"
    toolpath.save(str(toolpath_file))
    print(f"\nToolpath saved to: {toolpath_file}")
    
    # Also save as CSV for analysis
    csv_file = Path(output_dir) / "cube_coordinates.csv"
    toolpath.export_to_csv(str(csv_file))
    print(f"Coordinates saved to: {csv_file}")
    
    return toolpath


def visualize_toolpath(toolpath):
    """
    Create visualization of the toolpath.
    
    Parameters
    ----------
    toolpath : Toolpath
        Toolpath to visualize
    """
    if not PLOT_AVAILABLE:
        print("\nSkipping visualization (matplotlib not available)")
        return
    
    print("\n" + "="*60)
    print("VISUALIZING TOOLPATH")
    print("="*60)
    
    # Interactive 3D visualization
    print("\nOpening interactive 3D viewer...")
    toolpath.visualize()
    
    # Create 2D projections for documentation
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    coords = toolpath.get_coordinates()
    x = coords[:, 0]
    y = coords[:, 1]
    z = coords[:, 2]
    
    # XY projection (top view)
    axes[0].scatter(x, y, c=z, cmap='viridis', s=1)
    axes[0].set_xlabel('X (μm)')
    axes[0].set_ylabel('Y (μm)')
    axes[0].set_title('Top View (XY)')
    axes[0].set_aspect('equal')
    axes[0].grid(True, alpha=0.3)
    
    # XZ projection (side view)
    axes[1].scatter(x, z, c=y, cmap='viridis', s=1)
    axes[1].set_xlabel('X (μm)')
    axes[1].set_ylabel('Z (μm)')
    axes[1].set_title('Side View (XZ)')
    axes[1].set_aspect('equal')
    axes[1].grid(True, alpha=0.3)
    
    # YZ projection (front view)
    axes[2].scatter(y, z, c=x, cmap='viridis', s=1)
    axes[2].set_xlabel('Y (μm)')
    axes[2].set_ylabel('Z (μm)')
    axes[2].set_title('Front View (YZ)')
    axes[2].set_aspect('equal')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/cube_projections.png', dpi=150)
    print("Projection views saved to: output/cube_projections.png")
    plt.show()


def fabricate(toolpath, config_file="configs/default_config.yaml", dry_run=False):
    """
    Execute fabrication.
    
    Parameters
    ----------
    toolpath : Toolpath
        Toolpath to execute
    config_file : str
        Path to configuration file
    dry_run : bool
        If True, simulate without actual hardware execution
        
    Returns
    -------
    FabricationReport
        Report with fabrication statistics
    """
    print("\n" + "="*60)
    print("FABRICATION")
    print("="*60)
    
    if dry_run:
        print("\n*** DRY RUN MODE - No hardware will be used ***\n")
    
    # Load configuration
    try:
        config = load_config(config_file)
        print(f"Configuration loaded from: {config_file}")
    except FileNotFoundError:
        print(f"Warning: Config file not found. Using default settings.")
        config = None
    
    # Initialize exposure engine
    print("\nInitializing exposure engine...")
    engine = ExposureEngine(config=config)
    
    if not dry_run:
        # Connect to hardware
        print("Connecting to hardware...")
        try:
            engine.connect()
            print("✓ Hardware connected successfully")
        except Exception as e:
            print(f"✗ Hardware connection failed: {e}")
            print("Switching to dry run mode...")
            dry_run = True
    
    # Safety check
    if not dry_run:
        print("\n" + "!"*60)
        print("SAFETY CHECK")
        print("!"*60)
        print("Before starting fabrication, verify:")
        print("  1. Laser safety goggles are worn")
        print("  2. Substrate is properly mounted")
        print("  3. Photoresist is dispensed")
        print("  4. Focus is calibrated")
        print("  5. Area is clear of obstructions")
        
        response = input("\nProceed with fabrication? (yes/no): ")
        if response.lower() != "yes":
            print("Fabrication cancelled by user.")
            return None
    
    # Execute fabrication
    print("\nStarting fabrication...")
    print(f"Structure: 10 × 10 × 10 μm cube")
    print(f"Estimated time: {toolpath.get_statistics()['time_estimate']/60:.1f} minutes")
    
    try:
        report = engine.execute(toolpath, preview=dry_run)
        
        # Display results
        print("\n" + "="*60)
        print("FABRICATION COMPLETE")
        print("="*60)
        print(f"\nDuration: {report.duration:.1f} seconds ({report.duration/60:.1f} min)")
        print(f"Points written: {report.points_written}")
        print(f"Average speed: {report.average_speed:.0f} μm/s")
        print(f"Success: {report.success}")
        
        if report.errors:
            print(f"\nWarnings/Errors:")
            for error in report.errors:
                print(f"  - {error}")
        
        # Save report
        save_results(report, "output/fabrication_report.json")
        print(f"\nReport saved to: output/fabrication_report.json")
        
        return report
        
    except Exception as e:
        print(f"\n✗ Fabrication failed: {e}")
        return None
    finally:
        if not dry_run:
            engine.disconnect()
            print("\nHardware disconnected.")


def main():
    """
    Main execution function.
    """
    print("="*60)
    print("TWO-PHOTON LITHOGRAPHY - SIMPLE CUBE EXAMPLE")
    print("="*60)
    print("\nThis example demonstrates basic TPL workflow:")
    print("  1. Create geometry")
    print("  2. Generate toolpath")
    print("  3. Visualize (optional)")
    print("  4. Fabricate")
    print("\n" + "="*60)
    
    # Step 1: Create geometry
    print("\nSTEP 1: Creating geometry...")
    cube = create_simple_cube(
        size=10.0,        # 10 μm cube
        center=(0, 0, 10) # 10 μm above substrate
    )
    
    # Optional: Save geometry for reference
    cube.save("output/cube_geometry.stl")
    print("Geometry saved to: output/cube_geometry.stl")
    
    # Step 2: Generate toolpath
    print("\nSTEP 2: Generating toolpath...")
    toolpath = generate_toolpath(cube, output_dir="output")
    
    # Step 3: Visualize (optional)
    print("\nSTEP 3: Visualization...")
    response = input("Show toolpath visualization? (yes/no): ")
    if response.lower() == "yes":
        visualize_toolpath(toolpath)
    
    # Step 4: Fabricate
    print("\nSTEP 4: Fabrication...")
    response = input("Proceed with fabrication? (yes/no/dry): ")
    
    if response.lower() == "yes":
        report = fabricate(toolpath, dry_run=False)
    elif response.lower() == "dry":
        report = fabricate(toolpath, dry_run=True)
    else:
        print("\nFabrication skipped.")
        print("\nTo fabricate later, run:")
        print("  python -c \"from tpl.core import ExposureEngine; "
              "from tpl.design import Toolpath; "
              "t = Toolpath.load('output/cube_toolpath.gcode'); "
              "e = ExposureEngine(); e.connect(); e.execute(t)\"")
        report = None
    
    # Summary
    print("\n" + "="*60)
    print("WORKFLOW COMPLETE")
    print("="*60)
    
    if report and report.success:
        print("\n✓ Cube fabrication successful!")
        print("\nNext steps:")
        print("  1. Develop in PGMEA for 20 minutes")
        print("  2. Rinse in IPA (2× 2 minutes)")
        print("  3. Critical point drying")
        print("  4. Inspect with optical microscope")
        print("  5. SEM imaging for detailed analysis")
    else:
        print("\nFabrication was not executed or failed.")
        print("Output files are available in 'output/' directory:")
        print("  - cube_geometry.stl")
        print("  - cube_toolpath.gcode")
        print("  - cube_coordinates.csv")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # Run the example
    main()
    
    print("\n" + "="*60)
    print("For more examples, see:")
    print("  - examples/basic_shapes/sphere.py")
    print("  - examples/basic_shapes/cylinder.py")
    print("  - examples/photonic_crystals/woodpile_structure.py")
    print("="*60)
"""
Stage control module for two-photon lithography
================================================

Interface for controlling XYZ positioning stages.

Author: Zeyad Mustafa
Date: December 2024
BTU Cottbus-Senftenberg
"""

import serial
import time
import numpy as np
from typing import Tuple, Optional
from enum import Enum


class StageError(Exception):
    """Exception for stage-related errors."""
    pass


class StageState(Enum):
    """Stage operational states."""
    DISCONNECTED = 0
    IDLE = 1
    MOVING = 2
    HOMING = 3
    ERROR = 4


class StageControl:
    """
    Control interface for XYZ positioning stage.
    
    Parameters
    ----------
    port : str
        Serial port for stage communication
    baudrate : int
        Serial baud rate
    timeout : float
        Communication timeout in seconds
    mock : bool
        If True, run in simulation mode
    """
    
    def __init__(self,
                 port: str = "/dev/ttyUSB1",
                 baudrate: int = 115200,
                 timeout: float = 10.0,
                 mock: bool = False):
        
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.mock = mock
        
        self._serial = None
        self._connected = False
        self._state = StageState.DISCONNECTED
        
        # Stage specifications (update for your system)
        self.range_x = 200  # μm
        self.range_y = 200  # μm
        self.range_z = 200  # μm
        
        self.resolution = 1  # nm
        self.max_speed = 100000  # μm/s
        
        # Current position (in micrometers)
        self._position = np.array([0.0, 0.0, 0.0])
        self._home_position = np.array([100.0, 100.0, 100.0])
        
        # Movement parameters
        self.default_speed = 50000  # μm/s
        self.acceleration = 50000   # μm/s²
        
    def connect(self) -> bool:
        """
        Connect to stage controller.
        
        Returns
        -------
        bool
            True if successful
        """
        if self.mock:
            print("MOCK MODE: Simulating stage connection")
            self._connected = True
            self._state = StageState.IDLE
            self._position = self._home_position.copy()
            return True
        
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            time.sleep(0.5)
            
            # Verify connection
            response = self._send_command("*IDN?")
            if response:
                print(f"Stage connected: {response}")
                self._connected = True
                self._state = StageState.IDLE
                
                # Read current position
                self._update_position()
                return True
            else:
                raise StageError("No response from stage")
                
        except serial.SerialException as e:
            raise StageError(f"Failed to connect to stage: {e}")
    
    def disconnect(self):
        """Disconnect from stage."""
        if self._serial and self._serial.is_open:
            self._serial.close()
        
        self._connected = False
        self._state = StageState.DISCONNECTED
        
        if self.mock:
            print("MOCK MODE: Stage disconnected")
    
    def home(self):
        """
        Home all axes to reference position.
        
        Raises
        ------
        StageError
            If homing fails
        """
        if not self._connected:
            raise StageError("Stage not connected")
        
        print("Homing stage...")
        self._state = StageState.HOMING
        
        if self.mock:
            print("MOCK MODE: Homing to reference position")
            time.sleep(2)  # Simulate homing time
            self._position = self._home_position.copy()
            self._state = StageState.IDLE
            print(f"  Homed to: {self._position}")
            return
        
        # Send homing command
        response = self._send_command("HOME")
        
        if response and "OK" in response:
            # Wait for homing to complete
            self._wait_for_move_complete()
            self._update_position()
            self._state = StageState.IDLE
            print(f"  Homed to: {self._position}")
        else:
            self._state = StageState.ERROR
            raise StageError(f"Homing failed: {response}")
    
    def move_absolute(self, x: float, y: float, z: float, 
                     speed: Optional[float] = None):
        """
        Move to absolute position.
        
        Parameters
        ----------
        x, y, z : float
            Target position in micrometers
        speed : float, optional
            Movement speed in μm/s
        """
        if not self._connected:
            raise StageError("Stage not connected")
        
        # Validate positions
        if not (0 <= x <= self.range_x):
            raise StageError(f"X position {x} out of range [0, {self.range_x}]")
        if not (0 <= y <= self.range_y):
            raise StageError(f"Y position {y} out of range [0, {self.range_y}]")
        if not (0 <= z <= self.range_z):
            raise StageError(f"Z position {z} out of range [0, {self.range_z}]")
        
        if speed is None:
            speed = self.default_speed
        
        if speed > self.max_speed:
            raise StageError(f"Speed {speed} exceeds maximum {self.max_speed}")
        
        self._state = StageState.MOVING
        
        if self.mock:
            # Simulate movement
            distance = np.linalg.norm([x - self._position[0], 
                                      y - self._position[1], 
                                      z - self._position[2]])
            move_time = distance / speed
            time.sleep(min(move_time / 1000, 0.1))  # Scaled for simulation
            
            self._position = np.array([x, y, z])
            self._state = StageState.IDLE
            return
        
        # Send movement command
        command = f"MOVE ABS X{x:.4f} Y{y:.4f} Z{z:.4f} F{speed:.0f}"
        response = self._send_command(command)
        
        if response and "OK" in response:
            self._wait_for_move_complete()
            self._update_position()
            self._state = StageState.IDLE
        else:
            self._state = StageState.ERROR
            raise StageError(f"Move failed: {response}")
    
    def move_relative(self, dx: float, dy: float, dz: float,
                     speed: Optional[float] = None):
        """
        Move relative to current position.
        
        Parameters
        ----------
        dx, dy, dz : float
            Displacement in micrometers
        speed : float, optional
            Movement speed in μm/s
        """
        current = self.get_position()
        target_x = current[0] + dx
        target_y = current[1] + dy
        target_z = current[2] + dz
        
        self.move_absolute(target_x, target_y, target_z, speed)
    
    def get_position(self) -> Tuple[float, float, float]:
        """
        Get current stage position.
        
        Returns
        -------
        tuple
            (x, y, z) position in micrometers
        """
        if self.mock:
            return tuple(self._position)
        
        if not self._connected:
            raise StageError("Stage not connected")
        
        self._update_position()
        return tuple(self._position)
    
    def set_speed(self, speed: float):
        """
        Set default movement speed.
        
        Parameters
        ----------
        speed : float
            Speed in μm/s
        """
        if speed <= 0 or speed > self.max_speed:
            raise StageError(f"Speed must be between 0 and {self.max_speed}")
        
        self.default_speed = speed
        
        if not self.mock:
            command = f"SPEED {speed:.0f}"
            self._send_command(command)
    
    def stop(self):
        """Emergency stop - halt all movement immediately."""
        if self.mock:
            print("MOCK MODE: Emergency stop")
            self._state = StageState.IDLE
            return
        
        if not self._connected:
            return
        
        self._send_command("STOP")
        self._state = StageState.IDLE
    
    def calibrate(self) -> dict:
        """
        Run stage calibration routine.
        
        Returns
        -------
        dict
            Calibration results
        """
        print("Starting stage calibration...")
        
        if not self._connected:
            raise StageError("Stage not connected")
        
        # Home first
        self.home()
        
        # Test grid of positions
        test_positions = [
            (50, 50, 50),
            (150, 50, 50),
            (150, 150, 50),
            (50, 150, 50),
            (100, 100, 100),
        ]
        
        results = {
            'target_positions': [],
            'measured_positions': [],
            'errors': []
        }
        
        for target in test_positions:
            print(f"  Moving to {target}")
            self.move_absolute(*target)
            time.sleep(0.5)
            
            measured = self.get_position()
            error = np.linalg.norm(np.array(target) - np.array(measured))
            
            results['target_positions'].append(target)
            results['measured_positions'].append(measured)
            results['errors'].append(error)
            
            print(f"    Error: {error:.3f} μm")
        
        # Return to home
        self.home()
        
        avg_error = np.mean(results['errors'])
        max_error = np.max(results['errors'])
        
        print(f"\nCalibration complete:")
        print(f"  Average error: {avg_error:.3f} μm")
        print(f"  Maximum error: {max_error:.3f} μm")
        
        results['average_error'] = avg_error
        results['maximum_error'] = max_error
        
        return results
    
    def _update_position(self):
        """Query and update current position from hardware."""
        if self.mock:
            return
        
        response = self._send_command("POS?")
        
        try:
            # Parse response (format: "X123.4567 Y234.5678 Z345.6789")
            parts = response.strip().split()
            x = float(parts[0][1:])  # Skip 'X' prefix
            y = float(parts[1][1:])
            z = float(parts[2][1:])
            self._position = np.array([x, y, z])
        except (ValueError, IndexError):
            raise StageError(f"Invalid position response: {response}")
    
    def _wait_for_move_complete(self, timeout: float = 30.0):
        """Wait for stage movement to complete."""
        if self.mock:
            return
        
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise StageError("Move timeout")
            
            response = self._send_command("MOVING?")
            
            if response and "NO" in response.upper():
                break
            
            time.sleep(0.1)
    
    def _send_command(self, command: str) -> Optional[str]:
        """Send command to stage and return response."""
        if self.mock:
            # Simulate responses
            if "IDN" in command:
                return "PI E-545 3-Channel Piezo Controller"
            elif "POS" in command:
                return f"X{self._position[0]:.4f} Y{self._position[1]:.4f} Z{self._position[2]:.4f}"
            elif "MOVING" in command:
                return "NO"
            return "OK"
        
        if not self._serial or not self._serial.is_open:
            raise StageError("Serial port not open")
        
        try:
            self._serial.write((command + '\n').encode())
            response = self._serial.readline().decode().strip()
            return response
        except serial.SerialException as e:
            raise StageError(f"Communication error: {e}")
    
    @property
    def is_connected(self) -> bool:
        """Check if stage is connected."""
        return self._connected
    
    @property
    def is_moving(self) -> bool:
        """Check if stage is currently moving."""
        return self._state == StageState.MOVING
    
    def __enter__(self):
        """Context manager entry."""
        if not self._connected:
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __repr__(self) -> str:
        """String representation."""
        pos = tuple(self._position)
        return (f"StageControl(port='{self.port}', "
                f"position=({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}), "
                f"state={self._state.name})")
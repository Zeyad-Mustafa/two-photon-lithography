"""
Laser control module for two-photon lithography
================================================

Interface for controlling femtosecond laser systems.

Author: Zeyad Mustafa
Date: December 2024
BTU Cottbus-Senftenberg
"""

import serial
import time
import warnings
from typing import Dict, Optional, Tuple
from enum import Enum


class LaserState(Enum):
    """Laser operational states."""
    OFF = 0
    STANDBY = 1
    READY = 2
    EMITTING = 3
    ERROR = 4


class LaserError(Exception):
    """Exception for laser-related errors."""
    pass


class LaserControl:
    """
    Control interface for femtosecond laser.
    
    This class provides methods to control laser power, shutter,
    and monitor laser status.
    
    Parameters
    ----------
    port : str
        Serial port for laser communication (e.g., '/dev/ttyUSB0' or 'COM3')
    baudrate : int
        Serial communication baud rate
    timeout : float
        Communication timeout in seconds
    mock : bool
        If True, run in simulation mode without hardware
    """
    
    def __init__(self, 
                 port: str = "/dev/ttyUSB0",
                 baudrate: int = 9600,
                 timeout: float = 5.0,
                 mock: bool = False):
        
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.mock = mock
        
        self._serial = None
        self._connected = False
        self._current_power = 0.0
        self._max_power = 100.0
        self._shutter_open = False
        self._state = LaserState.OFF
        
        # Laser specifications (update for your system)
        self.wavelength = 780  # nm
        self.pulse_duration = 100  # fs
        self.repetition_rate = 80e6  # Hz
        
    def connect(self) -> bool:
        """
        Establish connection to laser controller.
        
        Returns
        -------
        bool
            True if connection successful
            
        Raises
        ------
        LaserError
            If connection fails
        """
        if self.mock:
            print("MOCK MODE: Simulating laser connection")
            self._connected = True
            self._state = LaserState.STANDBY
            return True
        
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            # Wait for initialization
            time.sleep(0.5)
            
            # Verify connection
            response = self._send_command("*IDN?")
            if response:
                print(f"Laser connected: {response}")
                self._connected = True
                self._state = LaserState.STANDBY
                return True
            else:
                raise LaserError("No response from laser")
                
        except serial.SerialException as e:
            raise LaserError(f"Failed to connect to laser: {e}")
    
    def disconnect(self):
        """Close connection to laser."""
        if self._shutter_open:
            self.shutter_close()
        
        if self._serial and self._serial.is_open:
            self._serial.close()
        
        self._connected = False
        self._state = LaserState.OFF
        
        if self.mock:
            print("MOCK MODE: Laser disconnected")
    
    def set_power(self, power: float):
        """
        Set laser power.
        
        Parameters
        ----------
        power : float
            Laser power in milliwatts
            
        Raises
        ------
        LaserError
            If power out of range or laser not ready
        """
        if not self._connected:
            raise LaserError("Laser not connected")
        
        if power < 0 or power > self._max_power:
            raise LaserError(f"Power must be between 0 and {self._max_power} mW")
        
        if self.mock:
            print(f"MOCK MODE: Setting laser power to {power:.2f} mW")
            self._current_power = power
            return
        
        # Send power command (adjust for your laser protocol)
        command = f"POWER {power:.2f}"
        response = self._send_command(command)
        
        if response and "OK" in response:
            self._current_power = power
        else:
            raise LaserError(f"Failed to set power: {response}")
    
    def get_power(self) -> float:
        """
        Get current laser power setting.
        
        Returns
        -------
        float
            Current power in milliwatts
        """
        if self.mock:
            return self._current_power
        
        if not self._connected:
            raise LaserError("Laser not connected")
        
        response = self._send_command("POWER?")
        
        try:
            power = float(response.strip())
            self._current_power = power
            return power
        except (ValueError, AttributeError):
            raise LaserError(f"Invalid power response: {response}")
    
    def shutter_open(self):
        """
        Open laser shutter (enable emission).
        
        Raises
        ------
        LaserError
            If shutter operation fails
        """
        if not self._connected:
            raise LaserError("Laser not connected")
        
        if self.mock:
            print("MOCK MODE: Opening shutter")
            self._shutter_open = True
            self._state = LaserState.EMITTING
            return
        
        response = self._send_command("SHUTTER OPEN")
        
        if response and "OK" in response:
            self._shutter_open = True
            self._state = LaserState.EMITTING
        else:
            raise LaserError(f"Failed to open shutter: {response}")
    
    def shutter_close(self):
        """
        Close laser shutter (disable emission).
        
        Raises
        ------
        LaserError
            If shutter operation fails
        """
        if not self._connected:
            raise LaserError("Laser not connected")
        
        if self.mock:
            print("MOCK MODE: Closing shutter")
            self._shutter_open = False
            self._state = LaserState.READY
            return
        
        response = self._send_command("SHUTTER CLOSE")
        
        if response and "OK" in response:
            self._shutter_open = False
            self._state = LaserState.READY
        else:
            raise LaserError(f"Failed to close shutter: {response}")
    
    def get_status(self) -> Dict:
        """
        Get comprehensive laser status.
        
        Returns
        -------
        dict
            Status information including power, temperature, mode lock, etc.
        """
        if self.mock:
            return {
                'connected': True,
                'state': self._state.name,
                'power': self._current_power,
                'shutter_open': self._shutter_open,
                'temperature': 25.0,
                'mode_lock': True,
                'wavelength': self.wavelength,
                'pulse_duration': self.pulse_duration,
                'repetition_rate': self.repetition_rate,
            }
        
        if not self._connected:
            raise LaserError("Laser not connected")
        
        status = {
            'connected': self._connected,
            'state': self._state.name,
            'power': self.get_power(),
            'shutter_open': self._shutter_open,
        }
        
        # Query additional parameters (adjust commands for your laser)
        try:
            temp_response = self._send_command("TEMP?")
            status['temperature'] = float(temp_response.strip())
        except:
            status['temperature'] = None
        
        try:
            ml_response = self._send_command("MODELOCK?")
            status['mode_lock'] = ("ON" in ml_response)
        except:
            status['mode_lock'] = None
        
        return status
    
    def emergency_stop(self):
        """
        Emergency stop - immediately close shutter and set power to zero.
        """
        try:
            if self._shutter_open:
                self.shutter_close()
            self.set_power(0)
            self._state = LaserState.STANDBY
        except Exception as e:
            warnings.warn(f"Emergency stop encountered error: {e}")
    
    def calibrate_power(self, target_powers: list) -> Dict:
        """
        Calibrate laser power output.
        
        Parameters
        ----------
        target_powers : list
            List of power setpoints to test (mW)
            
        Returns
        -------
        dict
            Calibration data with measured vs. set powers
        """
        if not self._connected:
            raise LaserError("Laser not connected")
        
        print("Starting power calibration...")
        print("NOTE: Place power meter at sample position")
        
        calibration_data = {
            'set_powers': [],
            'measured_powers': [],
            'timestamp': time.time()
        }
        
        for power in target_powers:
            self.set_power(power)
            time.sleep(1)  # Wait for stabilization
            
            if self.mock:
                # Simulate with slight error
                measured = power * (0.95 + 0.1 * (power / 100))
            else:
                measured = float(input(f"Enter measured power for {power} mW setting: "))
            
            calibration_data['set_powers'].append(power)
            calibration_data['measured_powers'].append(measured)
            
            print(f"  {power:.1f} mW → {measured:.1f} mW measured")
        
        return calibration_data
    
    def _send_command(self, command: str) -> Optional[str]:
        """
        Send command to laser and return response.
        
        Parameters
        ----------
        command : str
            Command string
            
        Returns
        -------
        str or None
            Response from laser
        """
        if self.mock:
            # Simulate responses
            if "IDN" in command:
                return "Coherent Chameleon Ultra II"
            elif "POWER" in command:
                if "?" in command:
                    return str(self._current_power)
                else:
                    return "OK"
            elif "SHUTTER" in command:
                return "OK"
            elif "TEMP" in command:
                return "25.0"
            elif "MODELOCK" in command:
                return "ON"
            return "OK"
        
        if not self._serial or not self._serial.is_open:
            raise LaserError("Serial port not open")
        
        try:
            # Send command
            self._serial.write((command + '\r\n').encode())
            
            # Read response
            response = self._serial.readline().decode().strip()
            return response
            
        except serial.SerialException as e:
            raise LaserError(f"Communication error: {e}")
    
    @property
    def is_connected(self) -> bool:
        """Check if laser is connected."""
        return self._connected
    
    @property
    def is_emitting(self) -> bool:
        """Check if laser is currently emitting."""
        return self._shutter_open and self._state == LaserState.EMITTING
    
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
        status = "connected" if self._connected else "disconnected"
        return (f"LaserControl(port='{self.port}', "
                f"state={self._state.name}, "
                f"power={self._current_power:.2f}mW, "
                f"status={status})")
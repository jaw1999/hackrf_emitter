import subprocess
import json
import time
import threading
import numpy as np
from typing import Dict, Any, Optional

try:
    import hackrf
    HACKRF_AVAILABLE = True
except ImportError:
    HACKRF_AVAILABLE = False
    print("Warning: pyhackrf not available. Install with: pip install pyhackrf")

class HackRFController:
    """Controller for HackRF device operations"""
    
    def __init__(self):
        self.device = None
        self.device_connected = False
        self.current_frequency = 0
        self.current_sample_rate = 0
        self.current_gain = 0
        self.transmission_active = False
        self._lock = threading.Lock()
        self._transmission_thread = None
        self._stop_transmission = threading.Event()
        self._hackrf_process = None
        
    def initialize(self) -> bool:
        """Initialize HackRF device connection"""
        try:
            # Check if hackrf_transfer command is available
            try:
                result = subprocess.run(['hackrf_transfer', '--help'], 
                                      capture_output=True, timeout=5)
                hackrf_cmd_available = result.returncode == 0
            except:
                hackrf_cmd_available = False
            
            if not hackrf_cmd_available:
                print("hackrf_transfer command not found. Please install HackRF tools.")
                print("Running in simulation mode.")
                self.device_connected = True  # Allow simulation mode
                return True
            
            # Check if device is actually connected
            try:
                result = subprocess.run(['hackrf_info'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("HackRF device found and initialized")
                    print("Real RF transmission enabled!")
                else:
                    print("HackRF device not found, running in simulation mode.")
            except:
                print("Could not check HackRF device status, running in simulation mode.")
            
            self.device_connected = True
            return True
                
        except Exception as e:
            print(f"Error initializing HackRF: {e}")
            print("Running in simulation mode.")
            self.device_connected = True  # Allow simulation mode
            return True
    
    def is_connected(self) -> bool:
        """Check if HackRF device is connected"""
        return self.device_connected
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get HackRF device information"""
        if not self.device_connected:
            return {'error': 'Device not connected'}
        
        try:
            # If we're transmitting, don't call hackrf_info as it will conflict
            if self.transmission_active:
                info = {
                    'status': 'connected',
                    'info': 'HackRF Device (Transmitting)',
                    'current_frequency': self.current_frequency,
                    'current_sample_rate': self.current_sample_rate,
                    'current_gain': self.current_gain,
                    'board_id': 'HackRF One',
                    'firmware_version': 'Transmitting...',
                    'transmission_active': True
                }
            else:
                # Only call hackrf_info when not transmitting
                try:
                    result = subprocess.run(['hackrf_info'], 
                                          capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        # Parse device info from hackrf_info output
                        info = {
                            'status': 'connected',
                            'info': result.stdout.strip(),
                            'current_frequency': self.current_frequency,
                            'current_sample_rate': self.current_sample_rate,
                            'current_gain': self.current_gain,
                            'board_id': 'HackRF One',
                            'firmware_version': 'Hardware Connected',
                            'transmission_active': False
                        }
                    else:
                        raise Exception("Device not found")
                except:
                    # Simulation mode
                    info = {
                        'status': 'connected',
                        'info': 'HackRF Device (Simulation Mode)',
                        'current_frequency': self.current_frequency,
                        'current_sample_rate': self.current_sample_rate,
                        'current_gain': self.current_gain,
                        'board_id': 'HackRF One (Simulated)',
                        'firmware_version': 'Simulation',
                        'transmission_active': False
                    }
            return info
                
        except Exception as e:
            return {'error': f'Error getting device info: {e}'}
    
    def set_frequency(self, frequency_hz: int) -> bool:
        """Set transmission frequency"""
        if not self.device_connected:
            return False
        
        try:
            with self._lock:
                self.current_frequency = frequency_hz
                print(f"Frequency set to {frequency_hz} Hz")
                return True
        except Exception as e:
            print(f"Error setting frequency: {e}")
            return False
    
    def set_sample_rate(self, sample_rate: int) -> bool:
        """Set sample rate"""
        if not self.device_connected:
            return False
        
        try:
            with self._lock:
                self.current_sample_rate = sample_rate
                print(f"Sample rate set to {sample_rate} Hz")
                return True
        except Exception as e:
            print(f"Error setting sample rate: {e}")
            return False
    
    def set_gain(self, gain_db: int) -> bool:
        """Set transmission gain"""
        if not self.device_connected:
            return False
        
        try:
            with self._lock:
                self.current_gain = gain_db
                print(f"Gain set to {gain_db} dB")
                return True
        except Exception as e:
            print(f"Error setting gain: {e}")
            return False
    
    def start_transmission(self, signal_data: bytes, frequency: int, 
                          sample_rate: int, gain: int) -> bool:
        """Start signal transmission"""
        if not self.device_connected:
            return False
        
        if self.transmission_active:
            return False
        
        try:
            # Configure device parameters without lock (they have their own locks)
            self.set_frequency(frequency)
            self.set_sample_rate(sample_rate)
            self.set_gain(gain)
            
            with self._lock:
                self.transmission_active = True
                self.current_frequency = frequency
                self.current_sample_rate = sample_rate
                self.current_gain = gain
                
                # Check if we can use real HackRF transmission
                try:
                    # Test if hackrf_transfer is available
                    result = subprocess.run(['hackrf_transfer', '-h'], 
                                 capture_output=True, timeout=2)
                    can_transmit = True
                    print("HackRF transfer available - using real transmission")
                except Exception as e:
                    can_transmit = False
                    print(f"HackRF transfer not available: {e} - using simulation mode")
                
                if can_transmit:
                    # Convert bytes back to complex samples for HackRF
                    # The signal_data is uint8, convert to complex I/Q
                    samples_uint8 = np.frombuffer(signal_data, dtype=np.uint8)
                    
                    # Convert to complex I/Q (assuming interleaved I,Q format)
                    if len(samples_uint8) % 2 == 1:
                        # Ensure even number of samples
                        samples_uint8 = samples_uint8[:-1]
                    
                    # Reshape to I,Q pairs and convert to complex
                    iq_samples = samples_uint8.reshape(-1, 2)
                    i_samples = (iq_samples[:, 0].astype(np.float32) - 127.5) / 127.5
                    q_samples = (iq_samples[:, 1].astype(np.float32) - 127.5) / 127.5
                    complex_samples = i_samples + 1j * q_samples
                    
                    # Start transmission thread
                    self._stop_transmission.clear()
                    self._transmission_thread = threading.Thread(
                        target=self._transmit_samples, 
                        args=(complex_samples,)
                    )
                    self._transmission_thread.daemon = True
                    self._transmission_thread.start()
                    
                    print(f"HackRF transmission started at {frequency} Hz")
                else:
                    # Simulation mode
                    print(f"Transmission started at {frequency} Hz (simulation)")
                
                return True
                
        except Exception as e:
            print(f"Error starting transmission: {e}")
            self.transmission_active = False
            return False
    
    def _transmit_samples(self, samples: np.ndarray) -> None:
        """Transmit samples using HackRF (runs in separate thread)"""
        try:
            # Check if hackrf_transfer is available
            try:
                result = subprocess.run(['hackrf_transfer', '-h'], 
                             capture_output=True, timeout=2)
                can_transmit = True
                print("HackRF transfer available for samples transmission")
            except Exception as e:
                can_transmit = False
                print(f"HackRF transfer not available for samples: {e}")
            
            if can_transmit:
                # For real transmission, we'll use hackrf_transfer command
                self._transmit_with_hackrf_transfer(samples)
            else:
                # Simulation mode - just wait for the duration
                duration = len(samples) / self.current_sample_rate
                print(f"Simulating transmission for {duration:.2f} seconds...")
                
                start_time = time.time()
                while (time.time() - start_time < duration and 
                       not self._stop_transmission.is_set()):
                    time.sleep(0.1)
                
        except Exception as e:
            print(f"Error during transmission: {e}")
        finally:
            # Always clear transmission active flag
            self.transmission_active = False
    
    def _transmit_with_hackrf_transfer(self, samples: np.ndarray) -> None:
        """Use hackrf_transfer command for actual RF transmission"""
        try:
            # Convert complex samples to HackRF format (8-bit I/Q)
            i_data = np.real(samples) * 127 + 127
            q_data = np.imag(samples) * 127 + 127
            
            # Clip to valid range
            i_data = np.clip(i_data, 0, 255).astype(np.uint8)
            q_data = np.clip(q_data, 0, 255).astype(np.uint8)
            
            # Interleave I and Q
            iq_data = np.empty(len(samples) * 2, dtype=np.uint8)
            iq_data[0::2] = i_data
            iq_data[1::2] = q_data
            
            # Save to temporary file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as tmp_file:
                tmp_file.write(iq_data.tobytes())
                tmp_filename = tmp_file.name
            
            try:
                # Build hackrf_transfer command
                cmd = [
                    'hackrf_transfer',
                    '-t', tmp_filename,  # transmit from file
                    '-f', str(int(self.current_frequency)),  # frequency
                    '-s', str(int(self.current_sample_rate)),  # sample rate
                    '-x', str(int(self.current_gain)),  # TX VGA gain
                    '-a', '1',  # enable TX amplifier
                ]
                
                print(f"Starting HackRF transmission: {' '.join(cmd)}")
                print(f"Signal file size: {os.path.getsize(tmp_filename)} bytes")
                
                # Start hackrf_transfer process
                self._hackrf_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                print(f"HackRF process started with PID: {self._hackrf_process.pid}")
                
                # Monitor the process
                while (self._hackrf_process.poll() is None and 
                       not self._stop_transmission.is_set()):
                    time.sleep(0.1)
                
                # If stop was requested, terminate the process
                if self._stop_transmission.is_set():
                    print("Stop requested, terminating HackRF process")
                    self._hackrf_process.terminate()
                    self._hackrf_process.wait(timeout=5)
                
                # Get process output
                stdout, stderr = self._hackrf_process.communicate()
                print(f"HackRF transmission completed with return code: {self._hackrf_process.returncode}")
                if stdout:
                    print(f"STDOUT: {stdout}")
                if stderr:
                    print(f"STDERR: {stderr}")
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_filename)
                except:
                    pass
                
        except Exception as e:
            print(f"Error in hackrf_transfer transmission: {e}")
    
    def stop_transmission(self) -> bool:
        """Stop signal transmission"""
        if not self.transmission_active:
            return True
        
        try:
            with self._lock:
                self._stop_transmission.set()
                
                # If using hackrf_transfer, terminate the process
                if hasattr(self, '_hackrf_process') and self._hackrf_process:
                    try:
                        self._hackrf_process.terminate()
                        self._hackrf_process.wait(timeout=5)
                    except:
                        pass
                
                if self._transmission_thread and self._transmission_thread.is_alive():
                    self._transmission_thread.join(timeout=2)
                
                self.transmission_active = False
                print("Transmission stopped")
                return True
        except Exception as e:
            print(f"Error stopping transmission: {e}")
            return False
    
    def generate_sine_wave(self, baseband_freq: float, duration: float, 
                          sample_rate: int = 2000000) -> bytes:
        """Generate sine wave signal data
        
        Args:
            baseband_freq: Baseband frequency in Hz (e.g., 1000 for 1kHz tone)
            duration: Duration in seconds
            sample_rate: Sample rate in Hz
        """
        num_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, num_samples, False)
        
        # Generate complex sine wave (I/Q format) at baseband frequency
        # For a carrier signal, we typically want a baseband tone
        if baseband_freq == 0:
            # DC signal (carrier only)
            signal = np.ones(num_samples, dtype=np.complex64)
        else:
            # Generate baseband tone
            signal = np.exp(1j * 2 * np.pi * baseband_freq * t)
        
        # Convert to 8-bit I/Q format
        i_data = (np.real(signal) * 127 + 127).astype(np.uint8)
        q_data = (np.imag(signal) * 127 + 127).astype(np.uint8)
        
        # Interleave I and Q samples
        iq_data = np.empty(num_samples * 2, dtype=np.uint8)
        iq_data[0::2] = i_data
        iq_data[1::2] = q_data
        
        return iq_data.tobytes()
    
    def generate_fm_signal(self, carrier_freq: float, mod_freq: float, 
                          mod_depth: float, duration: float, 
                          sample_rate: int = 2000000) -> bytes:
        """Generate FM modulated signal"""
        num_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, num_samples, False)
        
        # FM modulation
        mod_signal = mod_depth * np.sin(2 * np.pi * mod_freq * t)
        phase = 2 * np.pi * carrier_freq * t / sample_rate + mod_signal
        fm_signal = np.exp(1j * phase)
        
        # Convert to 8-bit I/Q format
        i_data = (np.real(fm_signal) * 127 + 127).astype(np.uint8)
        q_data = (np.imag(fm_signal) * 127 + 127).astype(np.uint8)
        
        # Interleave I and Q samples
        iq_data = np.empty(num_samples * 2, dtype=np.uint8)
        iq_data[0::2] = i_data
        iq_data[1::2] = q_data
        
        return iq_data.tobytes()
    
    def generate_am_signal(self, carrier_freq: float, mod_freq: float, 
                          mod_depth: float, duration: float, 
                          sample_rate: int = 2000000) -> bytes:
        """Generate AM modulated signal"""
        num_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, num_samples, False)
        
        # AM modulation
        mod_signal = mod_depth * np.sin(2 * np.pi * mod_freq * t)
        am_signal = (1 + mod_signal) * np.exp(1j * 2 * np.pi * carrier_freq * t / sample_rate)
        
        # Convert to 8-bit I/Q format
        i_data = (np.real(am_signal) * 127 + 127).astype(np.uint8)
        q_data = (np.imag(am_signal) * 127 + 127).astype(np.uint8)
        
        # Interleave I and Q samples
        iq_data = np.empty(num_samples * 2, dtype=np.uint8)
        iq_data[0::2] = i_data
        iq_data[1::2] = q_data
        
        return iq_data.tobytes()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self.stop_transmission()
        except:
            pass 
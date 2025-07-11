"""
ExpressLRS (ELRS) Protocol Implementation
Realistic ExpressLRS signal generation with proper LoRa modulation, 
frequency hopping, and packet structures for RC applications.
"""

import numpy as np
import time
import threading
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class ELRSConfig:
    """ExpressLRS configuration parameters"""
    frequency: float
    bandwidth: int  # Hz
    spreading_factor: int
    coding_rate: str
    packet_rate: int  # Hz
    power_level: int  # dBm
    hop_interval: float  # seconds
    sync_word: int
    preamble_length: int


class ELRSProtocol:
    """ExpressLRS protocol implementation with realistic signal generation"""
    
    # ELRS frequency configurations for different bands
    FREQUENCY_CONFIGS = {
        '433': {
            'center_freq': 433.42e6,
            'channels': [433.42e6, 434.42e6, 435.42e6],
            'bandwidth': 250000,  # 250 kHz
            'max_power': 100,  # mW
        },
        '868': {
            'center_freq': 868.4e6,
            'channels': [868.1e6, 868.3e6, 868.5e6, 868.7e6, 868.9e6],
            'bandwidth': 250000,
            'max_power': 25,  # mW (EU regulations)
        },
        '915': {
            'center_freq': 915.5e6,
            'channels': [903.4e6, 905.4e6, 907.4e6, 909.4e6, 911.4e6, 
                        913.4e6, 915.4e6, 917.4e6, 919.4e6, 921.4e6],
            'bandwidth': 500000,  # 500 kHz
            'max_power': 1000,  # mW (FCC Part 15)
        },
        '2400': {
            'center_freq': 2440e6,
            'channels': [2400e6, 2410e6, 2420e6, 2430e6, 2440e6, 
                        2450e6, 2460e6, 2470e6, 2480e6],
            'bandwidth': 2000000,  # 2 MHz
            'max_power': 250,  # mW
        }
    }
    
    # Packet rate configurations (realistic ELRS rates)
    PACKET_RATES = {
        25: {'sf': 12, 'bw': 250000, 'cr': '4/5', 'interval': 0.04},
        50: {'sf': 11, 'bw': 250000, 'cr': '4/5', 'interval': 0.02},
        100: {'sf': 10, 'bw': 250000, 'cr': '4/5', 'interval': 0.01},
        200: {'sf': 9, 'bw': 250000, 'cr': '4/5', 'interval': 0.005},
        333: {'sf': 8, 'bw': 500000, 'cr': '4/5', 'interval': 0.003},
        500: {'sf': 7, 'bw': 500000, 'cr': '4/5', 'interval': 0.002},
    }
    
    def __init__(self, band: str = '433'):
        """Initialize ELRS protocol for specified band"""
        self.band = band
        self.config = self.FREQUENCY_CONFIGS.get(band, self.FREQUENCY_CONFIGS['433'])
        self.channels = self.config['channels']
        self.current_channel = 0
        self.hop_sequence = self._generate_hop_sequence()
        self.sync_word = 0x12345678  # ELRS sync word
        
    def _generate_hop_sequence(self) -> List[int]:
        """Generate pseudo-random frequency hopping sequence"""
        # Simplified FHSS sequence generation
        np.random.seed(0x12345678)  # Use sync word as seed
        sequence = list(range(len(self.channels)))
        np.random.shuffle(sequence)
        return sequence * 100  # Repeat sequence
    
    def _generate_lora_chirp(self, duration: float, bandwidth: float, 
                           spreading_factor: int, sample_rate: int, 
                           is_upchirp: bool = True) -> np.ndarray:
        """Generate LoRa chirp signal"""
        num_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, num_samples, False)
        
        # LoRa chirp parameters
        f_start = -bandwidth / 2
        f_end = bandwidth / 2
        
        if not is_upchirp:
            f_start, f_end = f_end, f_start
        
        # Linear frequency sweep (chirp)
        freq_slope = (f_end - f_start) / duration
        instantaneous_freq = f_start + freq_slope * t
        
        # Generate chirp signal
        phase = 2 * np.pi * (f_start * t + 0.5 * freq_slope * t**2)
        chirp = np.cos(phase)
        
        return chirp
    
    def _generate_preamble(self, config: ELRSConfig, sample_rate: int) -> np.ndarray:
        """Generate ELRS preamble with upchirps and sync word"""
        preamble_duration = config.preamble_length / (config.bandwidth / (2**config.spreading_factor))
        symbol_duration = (2**config.spreading_factor) / config.bandwidth
        
        # Generate upchirps
        upchirps = []
        for _ in range(config.preamble_length):
            chirp = self._generate_lora_chirp(
                symbol_duration, config.bandwidth, 
                config.spreading_factor, sample_rate, True
            )
            upchirps.append(chirp)
        
        # Sync word detection chirps
        sync_chirps = []
        for _ in range(2):  # 2.25 sync chirps
            chirp = self._generate_lora_chirp(
                symbol_duration, config.bandwidth, 
                config.spreading_factor, sample_rate, False
            )
            sync_chirps.append(chirp)
        
        # Combine all chirps
        preamble = np.concatenate(upchirps + sync_chirps)
        return preamble
    
    def _encode_packet_data(self, control_data: Dict[str, Any]) -> bytes:
        """Encode RC control data into ELRS packet format"""
        # ELRS packet structure:
        # - Header (1 byte): packet type, sequence number
        # - RC Channels (variable): 10-16 bit per channel
        # - Telemetry request (1 bit)
        # - CRC (2 bytes)
        
        packet = bytearray()
        
        # Header
        packet_type = 0b00000000  # RC packet
        sequence = control_data.get('sequence', 0) & 0x0F
        header = (packet_type << 4) | sequence
        packet.append(header)
        
        # RC Channels (4 primary channels, 11-bit each)
        channels = [
            control_data.get('roll', 1500),     # Aileron
            control_data.get('pitch', 1500),    # Elevator  
            control_data.get('throttle', 1000), # Throttle
            control_data.get('yaw', 1500),      # Rudder
        ]
        
        # Pack channels (11-bit each, 44 bits total = 5.5 bytes)
        channel_data = 0
        for i, channel in enumerate(channels):
            # Convert 1000-2000 µs to 11-bit (0-2047)
            channel_val = int((channel - 1000) * 2047 / 1000)
            channel_val = max(0, min(2047, channel_val))
            channel_data |= (channel_val << (i * 11))
        
        # Pack into bytes
        for i in range(6):  # 44 bits = 6 bytes (with padding)
            packet.append((channel_data >> (i * 8)) & 0xFF)
        
        # Additional channels (aux channels)
        aux_channels = control_data.get('aux_channels', [1500] * 4)
        for aux in aux_channels:
            # 8-bit aux channels
            aux_val = int((aux - 1000) * 255 / 1000)
            aux_val = max(0, min(255, aux_val))
            packet.append(aux_val)
        
        # Telemetry request bit (simplified)
        telemetry_req = control_data.get('telemetry_request', False)
        packet.append(0x01 if telemetry_req else 0x00)
        
        # CRC-16 (simplified)
        crc = self._calculate_crc16(packet)
        packet.append(crc & 0xFF)
        packet.append((crc >> 8) & 0xFF)
        
        return bytes(packet)
    
    def _calculate_crc16(self, data: bytearray) -> int:
        """Calculate CRC-16 for packet integrity"""
        # Simple CRC-16-CCITT implementation
        crc = 0xFFFF
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return crc
    
    def _modulate_packet(self, packet_data: bytes, config: ELRSConfig, 
                        sample_rate: int) -> np.ndarray:
        """Modulate packet data using LoRa modulation"""
        symbol_duration = (2**config.spreading_factor) / config.bandwidth
        
        # Convert packet to symbols
        symbols = []
        for byte in packet_data:
            # Split byte into symbols based on spreading factor
            if config.spreading_factor <= 8:
                symbols.append(byte)
            else:
                # For higher SF, split bytes into smaller symbols
                for i in range(0, 8, config.spreading_factor):
                    symbol = (byte >> i) & ((1 << config.spreading_factor) - 1)
                    symbols.append(symbol)
        
        # Generate modulated signal
        modulated_signal = []
        for symbol in symbols:
            # Each symbol is represented by a chirp with specific start frequency
            start_freq = -config.bandwidth/2 + (symbol * config.bandwidth / (2**config.spreading_factor))
            
            # Generate symbol chirp
            num_samples = int(symbol_duration * sample_rate)
            t = np.linspace(0, symbol_duration, num_samples, False)
            
            freq_slope = config.bandwidth / symbol_duration
            instantaneous_freq = start_freq + freq_slope * t
            
            # Handle frequency wrap-around
            instantaneous_freq = np.mod(instantaneous_freq + config.bandwidth/2, config.bandwidth) - config.bandwidth/2
            
            phase = 2 * np.pi * np.cumsum(instantaneous_freq) / sample_rate
            symbol_signal = np.cos(phase)
            
            modulated_signal.append(symbol_signal)
        
        return np.concatenate(modulated_signal)
    
    def generate_elrs_transmission(self, duration: float, packet_rate: int, 
                                 power_level: int, sample_rate: int = 2000000,
                                 flight_mode: str = 'manual') -> np.ndarray:
        """Generate realistic ELRS transmission with frequency hopping"""
        
        # Get packet rate configuration
        rate_config = self.PACKET_RATES.get(packet_rate, self.PACKET_RATES[25])
        
        # Create ELRS configuration
        config = ELRSConfig(
            frequency=self.config['center_freq'],
            bandwidth=rate_config['bw'],
            spreading_factor=rate_config['sf'],
            coding_rate=rate_config['cr'],
            packet_rate=packet_rate,
            power_level=power_level,
            hop_interval=rate_config['interval'],
            sync_word=self.sync_word,
            preamble_length=8
        )
        
        # Calculate timing
        packet_interval = 1.0 / packet_rate
        num_packets = int(duration / packet_interval)
        
        # Generate signal
        total_samples = int(duration * sample_rate)
        signal = np.zeros(total_samples)
        
        # Simulate realistic RC control data
        control_data = self._generate_control_data(duration, flight_mode)
        
        for packet_num in range(num_packets):
            packet_start_time = packet_num * packet_interval
            packet_start_sample = int(packet_start_time * sample_rate)
            
            # Get current control data
            current_control = {
                'sequence': packet_num % 16,
                'roll': control_data['roll'][packet_num % len(control_data['roll'])],
                'pitch': control_data['pitch'][packet_num % len(control_data['pitch'])],
                'throttle': control_data['throttle'][packet_num % len(control_data['throttle'])],
                'yaw': control_data['yaw'][packet_num % len(control_data['yaw'])],
                'aux_channels': [1500, 1200, 1800, 1500],
                'telemetry_request': packet_num % 10 == 0  # Request telemetry every 10th packet
            }
            
            # Encode packet
            packet_data = self._encode_packet_data(current_control)
            
            # Generate preamble
            preamble = self._generate_preamble(config, sample_rate)
            
            # Modulate packet
            modulated_packet = self._modulate_packet(packet_data, config, sample_rate)
            
            # Combine preamble and packet
            packet_signal = np.concatenate([preamble, modulated_packet])
            
            # Apply maximum power scaling for HackRF output
            power_scale = 1.0  # Use maximum signal amplitude
            packet_signal *= power_scale
            
            # Add to main signal (with bounds checking)
            end_sample = min(packet_start_sample + len(packet_signal), total_samples)
            actual_length = end_sample - packet_start_sample
            signal[packet_start_sample:end_sample] = packet_signal[:actual_length]
            
            # Frequency hop for next packet
            self.current_channel = (self.current_channel + 1) % len(self.channels)
        
        return signal
    
    def _generate_control_data(self, duration: float, flight_mode: str) -> Dict[str, List[int]]:
        """Generate realistic RC control data for different flight modes"""
        num_samples = int(duration * 50)  # 50 Hz control update rate
        t = np.linspace(0, duration, num_samples)
        
        if flight_mode == 'manual':
            # Manual flight with pilot inputs
            roll = 1500 + 200 * np.sin(2 * np.pi * 0.5 * t) + 50 * np.random.randn(num_samples)
            pitch = 1500 + 150 * np.sin(2 * np.pi * 0.3 * t) + 30 * np.random.randn(num_samples)
            throttle = 1300 + 200 * np.sin(2 * np.pi * 0.1 * t) + 20 * np.random.randn(num_samples)
            yaw = 1500 + 100 * np.sin(2 * np.pi * 0.7 * t) + 40 * np.random.randn(num_samples)
            
        elif flight_mode == 'acro':
            # Aggressive acrobatic flying
            roll = 1500 + 400 * np.sin(2 * np.pi * 2 * t) * np.sin(2 * np.pi * 0.1 * t)
            pitch = 1500 + 300 * np.sin(2 * np.pi * 1.5 * t) * np.cos(2 * np.pi * 0.15 * t)
            throttle = 1000 + 800 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * t))
            yaw = 1500 + 300 * np.sin(2 * np.pi * 3 * t)
            
        elif flight_mode == 'stabilized':
            # Gentle stabilized flight
            roll = 1500 + 100 * np.sin(2 * np.pi * 0.2 * t) + 20 * np.random.randn(num_samples)
            pitch = 1500 + 80 * np.sin(2 * np.pi * 0.25 * t) + 15 * np.random.randn(num_samples)
            throttle = 1400 + 100 * np.sin(2 * np.pi * 0.05 * t) + 10 * np.random.randn(num_samples)
            yaw = 1500 + 50 * np.sin(2 * np.pi * 0.1 * t) + 25 * np.random.randn(num_samples)
            
        else:  # Default to hover
            # Hovering with small corrections
            roll = 1500 + 30 * np.random.randn(num_samples)
            pitch = 1500 + 30 * np.random.randn(num_samples)
            throttle = 1500 + 50 * np.random.randn(num_samples)
            yaw = 1500 + 20 * np.random.randn(num_samples)
        
        # Clamp values to valid RC range
        roll = np.clip(roll, 1000, 2000).astype(int).tolist()
        pitch = np.clip(pitch, 1000, 2000).astype(int).tolist()
        throttle = np.clip(throttle, 1000, 2000).astype(int).tolist()
        yaw = np.clip(yaw, 1000, 2000).astype(int).tolist()
        
        return {
            'roll': roll,
            'pitch': pitch,
            'throttle': throttle,
            'yaw': yaw
        }
    
    def get_frequency_list(self) -> List[float]:
        """Get list of frequencies used in this band"""
        return self.channels
    
    def get_band_info(self) -> Dict[str, Any]:
        """Get information about current band"""
        return {
            'band': self.band,
            'center_frequency': self.config['center_freq'],
            'channels': self.channels,
            'bandwidth': self.config['bandwidth'],
            'max_power': self.config['max_power'],
            'num_channels': len(self.channels)
        } 
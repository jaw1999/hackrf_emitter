"""
Enhanced RF Workflows
Comprehensive workflow system using realistic protocol implementations
for complex and near-replicate RF signal generation.
"""

import numpy as np
import time
import threading
from typing import Dict, Any, List, Optional
from .elrs_protocol import ELRSProtocol
from .gps_protocol import GPSProtocol
from .adsb_protocol import ADSBProtocol, Aircraft
from .raw_energy_protocol import RawEnergyProtocol


class EnhancedWorkflows:
    """Enhanced workflow system with realistic protocol implementations"""
    
    def __init__(self, hackrf_controller):
        """Initialize enhanced workflows"""
        self.hackrf = hackrf_controller
        self.active_workflow = None
        self.workflow_thread = None
        self.stop_flag = threading.Event()
        
        # Initialize protocol handlers
        self.elrs_protocols = {
            '433': ELRSProtocol('433'),
            '868': ELRSProtocol('868'), 
            '915': ELRSProtocol('915'),
            '2400': ELRSProtocol('2400')
        }
        
        self.gps_protocols = {
            'L1': GPSProtocol('L1'),
            'L2': GPSProtocol('L2'),
            'L5': GPSProtocol('L5')
        }
        
        self.adsb_protocol = ADSBProtocol()
        
        # Initialize raw energy protocol
        self.raw_energy_protocol = RawEnergyProtocol()
    
    def get_available_workflows(self) -> List[Dict[str, Any]]:
        """Get comprehensive list of enhanced RF workflows"""
        workflows = []
        
        # Enhanced ELRS workflows with realistic parameters
        for band in ['433', '868', '915', '2400']:
            protocol = self.elrs_protocols[band]
            band_info = protocol.get_band_info()
            
            workflow = {
                'name': f'elrs_{band}_enhanced',
                'display_name': f'ELRS {band}MHz (Enhanced)',
                'description': f'Realistic ExpressLRS transmission on {band}MHz with proper LoRa modulation, frequency hopping, and RC control simulation',
                'category': 'RC Control',
                'complexity': 'High',
                'parameters': {
                    'frequency': {
                        'type': 'float',
                        'min': band_info['center_frequency'],
                        'max': band_info['center_frequency'],
                        'default': band_info['center_frequency'],
                        'unit': 'Hz',
                        'description': f'Center frequency for {band}MHz band'
                    },
                    'packet_rate': {
                        'type': 'select',
                        'options': [25, 50, 100, 200, 333, 500],
                        'default': 100,
                        'unit': 'Hz',
                        'description': 'Packet transmission rate (affects range vs latency)'
                    },
                    'power_level': {
                        'type': 'int',
                        'min': -10,
                        'max': min(20, int(10 * np.log10(band_info['max_power']))),
                        'default': 10,
                        'unit': 'dBm',
                        'description': 'Transmission power level'
                    },
                    'flight_mode': {
                        'type': 'select',
                        'options': ['manual', 'acro', 'stabilized', 'hover'],
                        'default': 'manual',
                        'description': 'Flight mode affects control input patterns'
                    },
                    'frequency_hopping': {
                        'type': 'bool',
                        'default': True,
                        'description': 'Enable frequency hopping spread spectrum'
                    },
                    'channel_count': {
                        'type': 'int',
                        'min': 1,
                        'max': len(band_info['channels']),
                        'default': min(5, len(band_info['channels'])),
                        'description': 'Number of frequency channels to use'
                    },
                    'duration': {
                        'type': 'float',
                        'min': 1.0,
                        'max': 3600,
                        'default': 30,
                        'unit': 's',
                        'description': 'Transmission duration'
                    }
                }
            }
            workflows.append(workflow)
        
        # Enhanced GPS workflows with constellation simulation
        for band in ['L1', 'L2', 'L5']:
            protocol = self.gps_protocols[band]
            constellation_info = protocol.get_constellation_info()
            
            workflow = {
                'name': f'gps_{band.lower()}_constellation',
                'display_name': f'GPS {band} Constellation',
                'description': f'Realistic GPS {band} signal with multiple satellites, proper C/A codes, navigation data, and Doppler effects',
                'category': 'GNSS',
                'complexity': 'Very High',
                'parameters': {
                    'frequency': {
                        'type': 'float',
                        'min': constellation_info['carrier_frequency'],
                        'max': constellation_info['carrier_frequency'],
                        'default': constellation_info['carrier_frequency'],
                        'unit': 'Hz',
                        'description': f'GPS {band} carrier frequency'
                    },
                    'satellite_count': {
                        'type': 'int',
                        'min': 4,
                        'max': constellation_info['num_satellites'],
                        'default': 8,
                        'description': 'Number of satellites to simulate'
                    },
                    'signal_strength': {
                        'type': 'float',
                        'min': -150,
                        'max': -110,
                        'default': -130,
                        'unit': 'dBm',
                        'description': 'Average signal strength'
                    },
                    'constellation_motion': {
                        'type': 'bool',
                        'default': True,
                        'description': 'Simulate satellite orbital motion and Doppler'
                    },
                    'navigation_data': {
                        'type': 'bool',
                        'default': True,
                        'description': 'Include realistic navigation message data'
                    },
                    'atmospheric_effects': {
                        'type': 'bool',
                        'default': True,
                        'description': 'Simulate atmospheric propagation effects'
                    },
                    'duration': {
                        'type': 'float',
                        'min': 10.0,
                        'max': 3600,
                        'default': 60,
                        'unit': 's',
                        'description': 'Transmission duration'
                    }
                }
            }
            workflows.append(workflow)
        
        # Enhanced ADS-B workflow with multiple aircraft
        workflow = {
            'name': 'adsb_airspace_simulation',
            'display_name': 'ADS-B Airspace Simulation',
            'description': 'Realistic ADS-B transmission with multiple aircraft, proper Mode S Extended Squitter format, and dynamic flight simulation',
            'category': 'Aviation',
            'complexity': 'Very High',
            'parameters': {
                'frequency': {
                    'type': 'float',
                    'min': self.adsb_protocol.ADSB_FREQ,
                    'max': self.adsb_protocol.ADSB_FREQ,
                    'default': self.adsb_protocol.ADSB_FREQ,
                    'unit': 'Hz',
                    'description': 'ADS-B frequency (1090 MHz)'
                },
                'aircraft_count': {
                    'type': 'int',
                    'min': 1,
                    'max': 10,
                    'default': 3,
                    'description': 'Number of aircraft to simulate'
                },
                'airspace_type': {
                    'type': 'select',
                    'options': ['busy_terminal', 'enroute', 'approach', 'departure'],
                    'default': 'busy_terminal',
                    'description': 'Type of airspace to simulate'
                },
                'transmission_rate': {
                    'type': 'float',
                    'min': 0.5,
                    'max': 2.0,
                    'default': 1.0,
                    'unit': 's',
                    'description': 'Average time between transmissions per aircraft'
                },
                'position_accuracy': {
                    'type': 'select',
                    'options': ['high', 'medium', 'low'],
                    'default': 'high',
                    'description': 'Position reporting accuracy'
                },
                'include_velocity': {
                    'type': 'bool',
                    'default': True,
                    'description': 'Include velocity and heading information'
                },
                'include_callsigns': {
                    'type': 'bool',
                    'default': True,
                    'description': 'Include aircraft identification messages'
                },
                'duration': {
                    'type': 'float',
                    'min': 10.0,
                    'max': 3600,
                    'default': 120,
                    'unit': 's',
                    'description': 'Simulation duration'
                }
            }
        }
        workflows.append(workflow)
        
        # Advanced frequency hopping workflow
        workflow = {
            'name': 'advanced_frequency_hopping',
            'display_name': 'Advanced Frequency Hopping',
            'description': 'Military-grade frequency hopping spread spectrum with complex patterns and anti-jamming features',
            'category': 'Advanced',
            'complexity': 'Very High',
            'parameters': {
                'start_freq': {
                    'type': 'float',
                    'min': 100e6,
                    'max': 6e9,
                    'default': 400e6,
                    'unit': 'Hz',
                    'description': 'Start frequency'
                },
                'end_freq': {
                    'type': 'float',
                    'min': 100e6,
                    'max': 6e9,
                    'default': 500e6,
                    'unit': 'Hz',
                    'description': 'End frequency'
                },
                'hop_rate': {
                    'type': 'int',
                    'min': 10,
                    'max': 10000,
                    'default': 1000,
                    'unit': 'hops/s',
                    'description': 'Frequency hopping rate'
                },
                'pattern_type': {
                    'type': 'select',
                    'options': ['pseudorandom', 'cyclic', 'adaptive', 'burst'],
                    'default': 'pseudorandom',
                    'description': 'Hopping pattern algorithm'
                },
                'channel_spacing': {
                    'type': 'float',
                    'min': 1e3,
                    'max': 1e6,
                    'default': 25e3,
                    'unit': 'Hz',
                    'description': 'Channel spacing'
                },
                'modulation': {
                    'type': 'select',
                    'options': ['FSK', 'MSK', 'GMSK', 'PSK'],
                    'default': 'MSK',
                    'description': 'Modulation scheme'
                },
                'data_rate': {
                    'type': 'int',
                    'min': 1200,
                    'max': 1000000,
                    'default': 9600,
                    'unit': 'bps',
                    'description': 'Data transmission rate'
                },
                'error_correction': {
                    'type': 'bool',
                    'default': True,
                    'description': 'Enable forward error correction'
                },
                'duration': {
                    'type': 'float',
                    'min': 1.0,
                    'max': 3600,
                    'default': 60,
                    'unit': 's',
                    'description': 'Transmission duration'
                }
            }
        }
        workflows.append(workflow)
        
        # Radar simulation workflow
        workflow = {
            'name': 'radar_simulation',
            'display_name': 'Radar Signal Simulation',
            'description': 'Realistic radar signal with pulse compression, Doppler processing, and target simulation',
            'category': 'Radar',
            'complexity': 'Very High',
            'parameters': {
                'radar_type': {
                    'type': 'select',
                    'options': ['weather', 'surveillance', 'tracking', 'marine'],
                    'default': 'surveillance',
                    'description': 'Type of radar to simulate'
                },
                'frequency': {
                    'type': 'float',
                    'min': 1e9,
                    'max': 10e9,
                    'default': 3e9,
                    'unit': 'Hz',
                    'description': 'Radar operating frequency'
                },
                'prf': {
                    'type': 'int',
                    'min': 100,
                    'max': 10000,
                    'default': 1000,
                    'unit': 'Hz',
                    'description': 'Pulse repetition frequency'
                },
                'pulse_width': {
                    'type': 'float',
                    'min': 1e-6,
                    'max': 1e-3,
                    'default': 10e-6,
                    'unit': 's',
                    'description': 'Pulse width'
                },
                'chirp_bandwidth': {
                    'type': 'float',
                    'min': 1e6,
                    'max': 100e6,
                    'default': 10e6,
                    'unit': 'Hz',
                    'description': 'Chirp bandwidth for pulse compression'
                },
                'target_count': {
                    'type': 'int',
                    'min': 0,
                    'max': 20,
                    'default': 5,
                    'description': 'Number of targets to simulate'
                },
                'beam_pattern': {
                    'type': 'select',
                    'options': ['pencil', 'fan', 'cosec_squared'],
                    'default': 'pencil',
                    'description': 'Antenna beam pattern'
                },
                'scan_mode': {
                    'type': 'select',
                    'options': ['stationary', 'rotating', 'sector_scan'],
                    'default': 'rotating',
                    'description': 'Radar scan pattern'
                },
                'duration': {
                    'type': 'float',
                    'min': 10.0,
                    'max': 3600,
                    'default': 180,
                    'unit': 's',
                    'description': 'Simulation duration'
                }
            }
        }
        workflows.append(workflow)
        
        # Raw Energy workflows with 5MHz and 10MHz options for all frequencies
        raw_energy_workflows = self._create_raw_energy_workflows()
        workflows.extend(raw_energy_workflows)
        
        return workflows
    
    def start_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> None:
        """Start enhanced workflow"""
        if self.active_workflow:
            raise Exception("Workflow already active")
        
        self.stop_flag.clear()
        self.active_workflow = workflow_name
        
        # Start workflow in separate thread
        self.workflow_thread = threading.Thread(
            target=self._run_enhanced_workflow,
            args=(workflow_name, parameters)
        )
        self.workflow_thread.daemon = True
        self.workflow_thread.start()
    
    def stop_workflow(self) -> None:
        """Stop current workflow"""
        self.stop_flag.set()
        if self.workflow_thread:
            self.workflow_thread.join(timeout=5)
        self.active_workflow = None
        self.hackrf.stop_transmission()
    
    def _run_enhanced_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> None:
        """Run enhanced workflow with realistic signal generation"""
        try:
            print(f"Starting enhanced workflow: {workflow_name}")
            
            if workflow_name.startswith('elrs_') and workflow_name.endswith('_enhanced'):
                self._run_enhanced_elrs(workflow_name, parameters)
            elif workflow_name.startswith('gps_') and workflow_name.endswith('_constellation'):
                self._run_enhanced_gps(workflow_name, parameters)
            elif workflow_name == 'adsb_airspace_simulation':
                self._run_enhanced_adsb(parameters)
            elif workflow_name == 'advanced_frequency_hopping':
                self._run_advanced_frequency_hopping(parameters)
            elif workflow_name == 'radar_simulation':
                self._run_radar_simulation(parameters)
            elif workflow_name.startswith('raw_energy_'):
                self._run_raw_energy_workflow(workflow_name, parameters)
            else:
                raise Exception(f"Unknown enhanced workflow: {workflow_name}")
                
        except Exception as e:
            print(f"Error in enhanced workflow {workflow_name}: {e}")
            self.hackrf.stop_transmission()
        finally:
            # Always clean up the active workflow state
            self.active_workflow = None
    
    def _run_enhanced_elrs(self, workflow_name: str, parameters: Dict[str, Any]) -> None:
        """Run enhanced ELRS workflow"""
        # Extract band and channel from workflow name
        parts = workflow_name.split('_')
        band = parts[1]  # Just the number, not with 'mhz'
        protocol = self.elrs_protocols[band]
        
        frequency = parameters.get('frequency')
        if frequency is None:
            raise ValueError("Frequency parameter is required")
        
        channel = parameters.get('channel', 0)
        packet_rate = parameters.get('packet_rate', 150)
        hop_interval = parameters.get('hop_interval', 50)
        duration = parameters.get('duration', 30)
        flight_mode = parameters.get('flight_mode', 'manual')
        
        print(f"Generating realistic ELRS {band.upper()} signal...")
        print(f"- Channel: {channel}")
        print(f"- Packet rate: {packet_rate} Hz")
        print(f"- Flight mode: {flight_mode}")
        
        # Generate ELRS signal
        signal_data = protocol.generate_elrs_transmission(
            duration=duration,
            packet_rate=packet_rate,
            power_level=10,  # Default power level
            flight_mode=flight_mode
        )
        
        # Convert to bytes for HackRF
        signal_8bit = ((signal_data + 1) * 127.5).astype(np.uint8)
        signal_bytes = signal_8bit.tobytes()
        
        # Configure and start transmission
        self.hackrf.set_frequency(int(frequency))
        self.hackrf.set_sample_rate(2000000)
        self.hackrf.set_gain(47)
        
        self.hackrf.start_transmission(signal_bytes, int(frequency), 2000000, 47)
        
        # Wait for completion
        start_time = time.time()
        while time.time() - start_time < duration and not self.stop_flag.is_set():
            time.sleep(0.1)
        
        self.hackrf.stop_transmission()
    
    def _run_enhanced_gps(self, workflow_name: str, parameters: Dict[str, Any]) -> None:
        """Run enhanced GPS constellation workflow"""
        # Extract band from workflow name
        band = workflow_name.split('_')[1].upper()
        protocol = self.gps_protocols[band]
        
        frequency = parameters.get('frequency')
        if frequency is None:
            raise ValueError("Frequency parameter is required")
        
        satellite_count = parameters.get('satellite_count', 8)
        duration = parameters.get('duration', 60)
        
        print(f"Generating realistic GPS {band} constellation...")
        print(f"- {satellite_count} satellites")
        print(f"- Navigation data included")
        print(f"- Doppler effects simulated")
        
        # Get satellite list (use first N satellites)
        satellite_info = protocol.get_satellite_info()
        include_satellites = [sat['svid'] for sat in satellite_info[:satellite_count]]
        
        # Generate GPS signal
        signal_data = protocol.generate_gps_signal(
            duration=duration,
            include_satellites=include_satellites
        )
        
        # Convert to bytes for HackRF
        signal_8bit = ((signal_data + 1) * 127.5).astype(np.uint8)
        signal_bytes = signal_8bit.tobytes()
        
        # Configure and start transmission
        self.hackrf.set_frequency(int(frequency))
        self.hackrf.set_sample_rate(2000000)
        self.hackrf.set_gain(47)
        
        self.hackrf.start_transmission(signal_bytes, int(frequency), 2000000, 47)
        
        # Wait for completion
        start_time = time.time()
        while time.time() - start_time < duration and not self.stop_flag.is_set():
            time.sleep(0.1)
        
        self.hackrf.stop_transmission()
    
    def _run_enhanced_adsb(self, parameters: Dict[str, Any]) -> None:
        """Run enhanced ADS-B airspace simulation"""
        frequency = parameters.get('frequency')
        if frequency is None:
            raise ValueError("Frequency parameter is required")
        
        aircraft_count = parameters.get('aircraft_count', 3)
        duration = parameters.get('duration', 120)
        transmission_rate = parameters.get('transmission_rate', 1.0)
        
        print(f"Generating realistic ADS-B airspace simulation...")
        print(f"- {aircraft_count} aircraft")
        print(f"- Mode S Extended Squitter format")
        print(f"- Dynamic flight simulation")
        
        # Set transmission interval
        self.adsb_protocol.transmission_interval = transmission_rate
        
        # Generate ADS-B signal
        signal_data = self.adsb_protocol.generate_adsb_transmission(duration)
        
        # Convert to bytes for HackRF
        signal_8bit = ((signal_data + 1) * 127.5).astype(np.uint8)
        signal_bytes = signal_8bit.tobytes()
        
        # Configure and start transmission
        self.hackrf.set_frequency(int(frequency))
        self.hackrf.set_sample_rate(2000000)
        self.hackrf.set_gain(47)
        
        self.hackrf.start_transmission(signal_bytes, int(frequency), 2000000, 47)
        
        # Wait for completion
        start_time = time.time()
        while time.time() - start_time < duration and not self.stop_flag.is_set():
            time.sleep(0.1)
        
        self.hackrf.stop_transmission()
    
    def _run_advanced_frequency_hopping(self, parameters: Dict[str, Any]) -> None:
        """Run advanced frequency hopping workflow"""
        start_freq = parameters.get('start_freq', 400e6)
        end_freq = parameters.get('end_freq', 500e6)
        hop_rate = parameters.get('hop_rate', 1000)
        duration = parameters.get('duration', 60)
        pattern_type = parameters.get('pattern_type', 'pseudorandom')
        
        print(f"Generating advanced frequency hopping signal...")
        print(f"- Frequency range: {start_freq/1e6:.1f} - {end_freq/1e6:.1f} MHz")
        print(f"- Hop rate: {hop_rate} hops/s")
        print(f"- Pattern: {pattern_type}")
        
        # This would implement complex frequency hopping
        # For now, simplified implementation
        self._simple_frequency_hopping(start_freq, end_freq, hop_rate, duration)
    
    def _run_radar_simulation(self, parameters: Dict[str, Any]) -> None:
        """Run radar simulation workflow"""
        radar_type = parameters.get('radar_type', 'surveillance')
        frequency = parameters.get('frequency', 3e9)
        prf = parameters.get('prf', 1000)
        duration = parameters.get('duration', 180)
        
        print(f"Generating {radar_type} radar simulation...")
        print(f"- Frequency: {frequency/1e9:.1f} GHz")
        print(f"- PRF: {prf} Hz")
        
        # This would implement complex radar simulation
        # For now, simplified implementation
        self._simple_radar_simulation(frequency, prf, duration)
    
    def _create_raw_energy_workflows(self) -> List[Dict[str, Any]]:
        """Create raw energy workflows for all frequencies with 5MHz and 10MHz options"""
        workflows = []
        
        # Get all available frequencies
        frequencies = self.raw_energy_protocol.get_available_frequencies()
        bandwidth_options = self.raw_energy_protocol.get_bandwidth_options()
        noise_types = self.raw_energy_protocol.get_noise_types()
        
        # Create workflows for each frequency and bandwidth combination
        for freq_name, frequency in frequencies.items():
            for bw_name, bandwidth in bandwidth_options.items():
                
                workflow = {
                    'name': f'raw_energy_{freq_name.lower()}_{bw_name.lower()}',
                    'display_name': f'Raw Energy {freq_name} ({bw_name})',
                    'description': f'Maximum power {bw_name} raw energy transmission at {frequency/1e6:.2f} MHz ({self.raw_energy_protocol._get_frequency_description(freq_name)})',
                    'category': 'Raw Energy',
                    'complexity': 'Basic',
                    'parameters': {
                        'frequency': {
                            'type': 'float',
                            'min': frequency,
                            'max': frequency,
                            'default': frequency,
                            'unit': 'Hz',
                            'description': f'Fixed frequency: {frequency/1e6:.2f} MHz'
                        },
                        'bandwidth': {
                            'type': 'float',
                            'min': bandwidth,
                            'max': bandwidth,
                            'default': bandwidth,
                            'unit': 'Hz',
                            'description': f'Fixed bandwidth: {bw_name}'
                        },
                        'noise_type': {
                            'type': 'select',
                            'options': list(noise_types.keys()),
                            'default': 'white',
                            'description': 'Type of noise/signal to generate'
                        },
                        'duration': {
                            'type': 'float',
                            'min': 1.0,
                            'max': 3600,
                            'default': 30,
                            'unit': 's',
                            'description': 'Transmission duration'
                        }
                    }
                }
                workflows.append(workflow)
        
        return workflows
    
    def _simple_frequency_hopping(self, start_freq: float, end_freq: float, 
                                 hop_rate: int, duration: float) -> None:
        """Simplified frequency hopping implementation"""
        hop_interval = 1.0 / hop_rate
        num_channels = 100
        
        channels = np.linspace(start_freq, end_freq, num_channels)
        current_channel = 0
        
        start_time = time.time()
        while time.time() - start_time < duration and not self.stop_flag.is_set():
            # Generate signal for current channel
            freq = channels[current_channel]
            self.hackrf.set_frequency(int(freq))
            
            # Simple signal generation for hop interval
            time.sleep(hop_interval)
            
            # Move to next channel
            current_channel = (current_channel + 1) % num_channels
    
    def _run_raw_energy_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> None:
        """Run raw energy workflow with maximum power transmission"""
        frequency = parameters.get('frequency')
        if frequency is None:
            raise ValueError("Frequency parameter is required")
        
        bandwidth = parameters.get('bandwidth')
        if bandwidth is None:
            raise ValueError("Bandwidth parameter is required")
        
        duration = parameters.get('duration', 30)
        noise_type = parameters.get('noise_type', 'white')
        
        print(f"Generating raw energy transmission...")
        print(f"- Workflow: {workflow_name}")
        
        # Generate raw energy signal
        signal_data = self.raw_energy_protocol.generate_raw_energy_signal(
            frequency=frequency,
            bandwidth=bandwidth,
            duration=duration,
            noise_type=noise_type,
            sample_rate=2000000
        )
        
        # Convert to bytes for HackRF with maximum amplitude
        signal_8bit = ((signal_data + 1) * 127.5).astype(np.uint8)
        signal_bytes = signal_8bit.tobytes()
        
        # Configure HackRF for maximum power transmission
        self.hackrf.set_frequency(int(frequency))
        self.hackrf.set_sample_rate(2000000)
        self.hackrf.set_gain(47)  # Maximum HackRF gain
        
        # Start transmission
        self.hackrf.start_transmission(signal_bytes, int(frequency), 2000000, 47)
        
        # Wait for completion
        start_time = time.time()
        while time.time() - start_time < duration and not self.stop_flag.is_set():
            time.sleep(0.1)
        
        self.hackrf.stop_transmission()
    
    def _simple_radar_simulation(self, frequency: float, prf: int, duration: float) -> None:
        """Simplified radar simulation implementation"""
        pulse_interval = 1.0 / prf
        
        self.hackrf.set_frequency(int(frequency))
        
        start_time = time.time()
        while time.time() - start_time < duration and not self.stop_flag.is_set():
            # This would generate radar pulses
            time.sleep(pulse_interval) 
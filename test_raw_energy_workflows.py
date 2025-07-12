#!/usr/bin/env python3
"""
Test script for Raw Energy Workflows
Demonstrates all available raw energy transmissions with 5MHz and 10MHz bandwidth options
"""

import sys
import os

# Add backend to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from rf_workflows.raw_energy_protocol import RawEnergyProtocol
    from rf_workflows.enhanced_workflows import EnhancedWorkflows
    from rf_workflows.hackrf_controller import HackRFController
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the hackrf_emitter root directory")
    sys.exit(1)


def test_raw_energy_protocol():
    """Test raw energy protocol directly"""
    print("=" * 80)
    print("RAW ENERGY PROTOCOL TEST")
    print("=" * 80)
    
    protocol = RawEnergyProtocol()
    
    # Show all available frequencies
    frequencies = protocol.get_available_frequencies()
    print(f"\nAvailable Frequencies ({len(frequencies)} total):")
    print("-" * 60)
    
    # Group by band
    bands = {}
    for freq_name, frequency in frequencies.items():
        band = protocol._get_frequency_band(frequency)
        if band not in bands:
            bands[band] = []
        bands[band].append((freq_name, frequency))
    
    for band, freq_list in sorted(bands.items()):
        print(f"\n{band} Band:")
        for freq_name, frequency in sorted(freq_list, key=lambda x: x[1]):
            description = protocol._get_frequency_description(freq_name)
            print(f"  {freq_name:15} {frequency/1e6:8.2f} MHz - {description}")
    
    # Show bandwidth options
    bandwidth_options = protocol.get_bandwidth_options()
    print(f"\nBandwidth Options:")
    print("-" * 30)
    for bw_name, bandwidth in bandwidth_options.items():
        print(f"  {bw_name}: {bandwidth/1e6:.0f} MHz")
    
    # Show noise types
    noise_types = protocol.get_noise_types()
    print(f"\nNoise Types:")
    print("-" * 50)
    for noise_type, description in noise_types.items():
        print(f"  {noise_type:10} - {description}")


def test_enhanced_workflows():
    """Test enhanced workflows integration"""
    print("\n" + "=" * 80)
    print("ENHANCED WORKFLOWS INTEGRATION TEST")
    print("=" * 80)
    
    # Mock HackRF controller for testing
    class MockHackRFController:
        def set_frequency(self, freq): pass
        def set_sample_rate(self, rate): pass
        def set_gain(self, gain): pass
        def start_transmission(self, data, freq, rate, gain): pass
        def stop_transmission(self): pass
    
    hackrf = MockHackRFController()
    enhanced_workflows = EnhancedWorkflows(hackrf)
    
    # Get all workflows
    all_workflows = enhanced_workflows.get_available_workflows()
    
    # Filter raw energy workflows
    raw_energy_workflows = [w for w in all_workflows if w['name'].startswith('raw_energy_')]
    
    print(f"\nRaw Energy Workflows ({len(raw_energy_workflows)} total):")
    print("-" * 80)
    
    # Group by frequency band
    workflow_bands = {}
    for workflow in raw_energy_workflows:
        freq = workflow['parameters']['frequency']['default']
        band = RawEnergyProtocol()._get_frequency_band(freq)
        if band not in workflow_bands:
            workflow_bands[band] = []
        workflow_bands[band].append(workflow)
    
    for band, workflows in sorted(workflow_bands.items()):
        print(f"\n{band} Band ({len(workflows)} workflows):")
        for workflow in sorted(workflows, key=lambda x: x['parameters']['frequency']['default']):
            freq = workflow['parameters']['frequency']['default']
            bw = workflow['parameters']['bandwidth']['default']
            print(f"  {workflow['name']:50} {freq/1e6:8.2f} MHz ({bw/1e6:.0f} MHz BW)")
            print(f"    {workflow['description']}")
    
    # Show workflow parameters example
    if raw_energy_workflows:
        example_workflow = raw_energy_workflows[0]
        print(f"\nExample Workflow Parameters ({example_workflow['name']}):")
        print("-" * 60)
        for param_name, param_info in example_workflow['parameters'].items():
            print(f"  {param_name:12} {param_info['type']:8} {param_info.get('description', '')}")
            if 'options' in param_info:
                print(f"               Options: {param_info['options']}")


def show_frequency_coverage():
    """Show frequency coverage summary"""
    print("\n" + "=" * 80)
    print("FREQUENCY COVERAGE SUMMARY")
    print("=" * 80)
    
    protocol = RawEnergyProtocol()
    frequencies = protocol.get_available_frequencies()
    
    # Calculate total workflows
    bandwidth_options = protocol.get_bandwidth_options()
    total_workflows = len(frequencies) * len(bandwidth_options)
    
    print(f"\nTotal Raw Energy Workflows: {total_workflows}")
    print(f"Frequencies Covered: {len(frequencies)}")
    print(f"Bandwidth Options: {len(bandwidth_options)} (5MHz, 10MHz)")
    print(f"Noise Types: {len(protocol.get_noise_types())}")
    
    # Show frequency range
    freq_values = list(frequencies.values())
    min_freq = min(freq_values)
    max_freq = max(freq_values)
    
    print(f"\nFrequency Range:")
    print(f"  Minimum: {min_freq/1e6:.2f} MHz")
    print(f"  Maximum: {max_freq/1e6:.2f} MHz")
    print(f"  Span: {(max_freq - min_freq)/1e6:.2f} MHz")
    
    # Key features
    print(f"\nKey Features:")
    print(f"  • Maximum HackRF gain: 47 dB")
    print(f"  • Maximum signal amplitude: 1.0 (no power reduction)")
    print(f"  • Configurable noise types: white, pink, shaped, chirp, multitone")
    print(f"  • Bandwidth-limited filtering")
    print(f"  • All major RF bands covered: VHF, UHF, SHF")
    print(f"  • GPS, ADS-B, AIS frequencies included")
    print(f"  • ELRS now uses advanced frequency sweeping (see ELRS Jamming workflows)")


def show_usage_examples():
    """Show usage examples"""
    print("\n" + "=" * 80)
    print("USAGE EXAMPLES")
    print("=" * 80)
    
    examples = [
        {
            'name': 'GPS L1 Jamming Simulation (5MHz)',
            'workflow': 'raw_energy_gps_l1_5mhz',
            'frequency': '1575.42 MHz',
            'purpose': 'Test GPS receiver robustness'
        },
        {
            'name': 'AIS Channel Testing (5MHz)',
            'workflow': 'raw_energy_ais_ch1_5mhz',
            'frequency': '161.975 MHz',
            'purpose': 'Test AIS receiver interference tolerance'
        },
        {
            'name': 'ADS-B Signal Analysis (5MHz)',
            'workflow': 'raw_energy_adsb_5mhz',
            'frequency': '1090 MHz',
            'purpose': 'Analyze ADS-B receiver sensitivity'
        },
        {
            'name': 'S-Band Radar Testing (10MHz)',
            'workflow': 'raw_energy_s_band_10mhz',
            'frequency': '3000 MHz',
            'purpose': 'High-power S-band signal generation'
        }
    ]
    
    print("\nCommon Use Cases:")
    print("-" * 50)
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}")
        print(f"   Workflow: {example['workflow']}")
        print(f"   Frequency: {example['frequency']}")
        print(f"   Purpose: {example['purpose']}")
    
    print("\nWorkflow Parameters:")
    print("-" * 30)
    print("  • frequency: Fixed frequency for each workflow")
    print("  • bandwidth: Fixed bandwidth (5MHz or 10MHz)")
    print("  • noise_type: white, pink, shaped, chirp, multitone")
    print("  • duration: Transmission duration (1-3600 seconds)")


if __name__ == "__main__":
    print("Raw Energy Workflows Test Suite")
    print("Testing maximum power wideband transmissions")
    
    test_raw_energy_protocol()
    test_enhanced_workflows()
    show_frequency_coverage()
    show_usage_examples()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("Raw energy workflows ready for maximum power transmission!")
    print("=" * 80) 
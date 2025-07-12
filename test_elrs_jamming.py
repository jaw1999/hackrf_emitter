#!/usr/bin/env python3
"""
Test Script for Enhanced ELRS Jamming
Demonstrates frequency sweeping, barrage, and adaptive jamming techniques
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from rf_workflows.elrs_jamming_protocol import ELRSJammingProtocol, ELRSJammingConfig
from rf_workflows.enhanced_workflows import EnhancedWorkflows

def test_elrs_jamming_capabilities():
    """Test and demonstrate ELRS jamming capabilities"""
    
    print("=" * 80)
    print("🚁 ELRS JAMMING PROTOCOL TEST")
    print("=" * 80)
    
    # Test all ELRS bands
    bands = ['433', '868', '915', '2400']
    
    for band in bands:
        print(f"\n📡 Testing ELRS {band}MHz Band")
        print("-" * 50)
        
        # Initialize jamming protocol
        jammer = ELRSJammingProtocol(band)
        band_info = jammer.get_band_info()
        recommendations = jammer.get_jamming_recommendations()
        
        print(f"📊 Band Information:")
        print(f"  • Channels: {len(band_info['channels'])}")
        print(f"  • Bandwidth per channel: {band_info['bandwidth']/1000:.0f} kHz")
        print(f"  • Frequency range: {min(band_info['channels'])/1e6:.2f} - {max(band_info['channels'])/1e6:.2f} MHz")
        print(f"  • Max power: {band_info['max_power']} mW")
        
        print(f"\n🎯 Recommended Strategy: {recommendations[band]['strategy'].replace('_', ' ').title()}")
        print(f"  • Pattern: {recommendations[band]['pattern']}")
        print(f"  • Hop rate: {recommendations[band]['hop_rate']} Hz")
        print(f"  • Power: {recommendations[band]['power']} dBm")
        
        # Show frequency hopping sequences
        hop_sequences = jammer._generate_hop_sequences()
        print(f"\n🔀 Available Hopping Patterns:")
        for pattern, sequence in hop_sequences.items():
            print(f"  • {pattern.title()}: {len(sequence)} hops, starts with channels {sequence[:5]}...")
    
    print(f"\n" + "=" * 80)
    print("🎛️  WORKFLOW INTEGRATION TEST")
    print("=" * 80)
    
    # Mock HackRF controller for testing
    class MockHackRF:
        def set_frequency(self, freq): pass
        def set_sample_rate(self, rate): pass
        def set_gain(self, gain): pass
        def start_transmission(self, data, freq, rate, gain): pass
        def stop_transmission(self): pass
    
    # Test enhanced workflows
    workflows = EnhancedWorkflows(MockHackRF())
    available_workflows = workflows.get_available_workflows()
    
    # Filter ELRS jamming workflows
    elrs_jammers = [w for w in available_workflows if 'ELRS' in w['category'] and 'Jamming' in w['category']]
    
    print(f"🚁 Found {len(elrs_jammers)} ELRS Jamming Workflows:")
    
    for workflow in elrs_jammers:
        print(f"\n📋 {workflow['display_name']}")
        print(f"   Category: {workflow['category']}")
        print(f"   Complexity: {workflow['complexity']}")
        print(f"   Description: {workflow['description'][:100]}...")
        
        # Show key parameters
        key_params = []
        for param_name, param_info in workflow['parameters'].items():
            if param_name in ['sweep_pattern', 'hop_rate', 'power_level', 'coverage_strategy']:
                default = param_info.get('default', 'N/A')
                unit = param_info.get('unit', '')
                key_params.append(f"{param_name}: {default} {unit}".strip())
        
        if key_params:
            print(f"   Key params: {', '.join(key_params)}")

def demonstrate_jamming_patterns():
    """Demonstrate different jamming patterns"""
    
    print(f"\n" + "=" * 80)
    print("🎯 JAMMING PATTERN DEMONSTRATION")
    print("=" * 80)
    
    # Focus on 915MHz band (most common)
    jammer = ELRSJammingProtocol('915')
    band_info = jammer.get_band_info()
    channels = band_info['channels']
    
    print(f"📡 ELRS 915MHz Band Analysis:")
    print(f"  • Total channels: {len(channels)}")
    print(f"  • Frequency span: {(max(channels) - min(channels))/1e6:.1f} MHz")
    print(f"  • Channel spacing: {(channels[1] - channels[0])/1e3:.0f} kHz")
    
    # Show different jamming signal types
    print(f"\n🔊 Jamming Signal Types:")
    signal_types = {
        'broadband_noise': 'White noise across full bandwidth - most effective',
        'chirp_sweep': 'Linear frequency chirp - good against LoRa',
        'multitone': 'Multiple sine waves - targeted interference',
        'pulsed_noise': 'High-power noise bursts - energy efficient'
    }
    
    for signal_type, description in signal_types.items():
        print(f"  • {signal_type.replace('_', ' ').title()}: {description}")
    
    # Demonstrate pattern effectiveness
    print(f"\n⚡ Pattern Effectiveness Analysis:")
    
    effectiveness = {
        'sequential': {
            'speed': 'Medium',
            'coverage': 'Complete',
            'predictability': 'High',
            'effectiveness': 'Good for slow ELRS systems'
        },
        'pseudorandom': {
            'speed': 'Fast',
            'coverage': 'Complete',
            'predictability': 'Low',
            'effectiveness': 'Excellent - mimics real ELRS'
        },
        'adaptive': {
            'speed': 'Variable',
            'coverage': 'Focused',
            'predictability': 'Very Low',
            'effectiveness': 'Maximum - targets active channels'
        },
        'burst': {
            'speed': 'Very Fast',
            'coverage': 'Rapid',
            'predictability': 'Medium',
            'effectiveness': 'Good for disrupting sync'
        }
    }
    
    for pattern, info in effectiveness.items():
        print(f"\n  🎯 {pattern.title()} Pattern:")
        for metric, value in info.items():
            print(f"     {metric.title()}: {value}")

def show_frequency_coverage():
    """Show detailed frequency coverage for each band"""
    
    print(f"\n" + "=" * 80)
    print("📊 FREQUENCY COVERAGE ANALYSIS")
    print("=" * 80)
    
    bands = ['433', '868', '915', '2400']
    
    for band in bands:
        jammer = ELRSJammingProtocol(band)
        band_info = jammer.get_band_info()
        channels = band_info['channels']
        
        print(f"\n📡 ELRS {band}MHz Band Frequency Map:")
        print(f"{'Channel':<8} {'Frequency':<12} {'MHz':<8} {'Usage'}")
        print("-" * 45)
        
        for i, freq in enumerate(channels[:10]):  # Show first 10 channels
            usage = "Primary" if i < 5 else "Secondary"
            print(f"{i+1:<8} {freq:<12.0f} {freq/1e6:<8.3f} {usage}")
        
        if len(channels) > 10:
            print(f"... and {len(channels) - 10} more channels")
        
        # Show coverage statistics
        freq_span = max(channels) - min(channels)
        channel_spacing = freq_span / (len(channels) - 1) if len(channels) > 1 else 0
        
        print(f"\n📈 Coverage Statistics:")
        print(f"  • Total bandwidth: {freq_span/1e6:.2f} MHz")
        print(f"  • Average channel spacing: {channel_spacing/1e3:.0f} kHz")
        print(f"  • Bandwidth per channel: {band_info['bandwidth']/1e3:.0f} kHz")
        print(f"  • Coverage efficiency: {(len(channels) * band_info['bandwidth'] / freq_span * 100):.1f}%")

if __name__ == "__main__":
    try:
        print("🚁 Starting ELRS Jamming Protocol Test Suite")
        print("This demonstrates the enhanced frequency sweeping capabilities\n")
        
        test_elrs_jamming_capabilities()
        demonstrate_jamming_patterns()
        show_frequency_coverage()
        
        print(f"\n" + "=" * 80)
        print("✅ ELRS JAMMING TEST COMPLETE")
        print("=" * 80)
        print("\n🎯 Key Improvements:")
        print("  • Frequency sweeping instead of single-channel jamming")
        print("  • Multiple jamming patterns (sequential, pseudorandom, adaptive, burst)")
        print("  • Real-time traffic adaptation")
        print("  • Simultaneous multi-channel barrage capability")
        print("  • 20-24 channels per band for complete coverage")
        print("  • Optimized hop rates and power levels per band")
        print("\n🚀 This system is now much more effective against ELRS!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc() 
#!/usr/bin/env python3
"""
Test Script for Drone Video Link Jamming
Demonstrates video jamming capabilities for 1.2 GHz and 5.8 GHz FPV frequencies
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from rf_workflows.drone_video_jamming_protocol import DroneVideoJammingProtocol, DroneVideoJammingConfig
from rf_workflows.enhanced_workflows import EnhancedWorkflows

def test_drone_video_jamming_capabilities():
    """Test and demonstrate drone video jamming capabilities"""
    
    print("=" * 80)
    print("🎥 DRONE VIDEO LINK JAMMING PROTOCOL TEST")
    print("=" * 80)
    
    # Test all drone video bands
    bands = ['1200', '5800']
    
    for band in bands:
        print(f"\n📡 Testing {band} Video Band")
        print("-" * 50)
        
        # Initialize jamming protocol
        jammer = DroneVideoJammingProtocol(band)
        band_info = jammer.get_band_info()
        recommendations = jammer.get_jamming_recommendations()
        
        print(f"📊 Band Information:")
        print(f"  • Name: {band_info['name']}")
        print(f"  • Channels: {len(band_info['channels'])}")
        print(f"  • Bandwidth per channel: {band_info['bandwidth']/1e6:.1f} MHz")
        print(f"  • Frequency range: {min(band_info['channels'])/1e6:.1f} - {max(band_info['channels'])/1e6:.1f} MHz")
        print(f"  • Max power: {band_info['max_power']} mW")
        print(f"  • Description: {band_info['description']}")
        
        print(f"\n🎯 Recommended Strategy: {recommendations[band]['strategy'].replace('_', ' ').title()}")
        print(f"  • Pattern: {recommendations[band]['pattern']}")
        print(f"  • Hop rate: {recommendations[band]['hop_rate']} Hz")
        print(f"  • Power: {recommendations[band]['power']} dBm")
        print(f"  • Description: {recommendations[band]['description']}")
        
        # Show frequency hopping sequences
        hop_sequences = jammer._generate_hop_sequences()
        print(f"\n🔀 Available Hopping Patterns:")
        for pattern, sequence in hop_sequences.items():
            print(f"  • {pattern.title()}: {len(sequence)} hops, starts with channels {sequence[:5]}...")
        
        # Show some key video frequencies
        print(f"\n📺 Key Video Frequencies:")
        if band == '5800':
            print(f"  • Race Band (R1-R8): Common for FPV racing")
            print(f"  • ImmersionRC (I): Popular brand frequencies")
            print(f"  • Fatshark (F): Popular goggle frequencies")
            print(f"  • Bands A-E: Standard FPV channel allocations")
        else:
            print(f"  • Long-range FPV: 1.2-1.4 GHz range")
            print(f"  • Better penetration than 5.8 GHz")
            print(f"  • Wider channels for higher data rates")
    
    print(f"\n" + "=" * 80)
    print("🎛️  WORKFLOW INTEGRATION TEST")
    print("=" * 80)
    
    # Mock HackRF controller for testing
    class MockHackRF:
        def set_frequency(self, freq): 
            print(f"  📡 Setting frequency to {freq/1e6:.1f} MHz")
        def set_sample_rate(self, rate): 
            print(f"  📊 Setting sample rate to {rate/1e6:.1f} MHz")
        def set_gain(self, gain): 
            print(f"  📈 Setting gain to {gain} dB")
        def start_transmission(self, data, freq, rate, gain): 
            print(f"  🚀 Starting transmission on {freq/1e6:.1f} MHz @ {gain} dB")
            return True
        def stop_transmission(self): 
            print(f"  🛑 Stopping transmission")
    
    # Test enhanced workflows
    workflows = EnhancedWorkflows(MockHackRF())
    available_workflows = workflows.get_available_workflows()
    
    # Filter drone video jamming workflows
    video_jammers = [w for w in available_workflows if 'Drone Video Jamming' in w.get('category', '')]
    
    print(f"🎥 Found {len(video_jammers)} Drone Video Jamming Workflows:")
    
    for workflow in video_jammers:
        print(f"\n📋 {workflow['display_name']}")
        print(f"   Category: {workflow['category']}")
        print(f"   Complexity: {workflow['complexity']}")
        print(f"   Description: {workflow['description'][:100]}...")
        
        # Show key parameters
        key_params = []
        for param_name, param_info in workflow['parameters'].items():
            if param_name in ['sweep_pattern', 'hop_rate', 'power_level', 'jamming_type']:
                default = param_info.get('default', 'N/A')
                unit = param_info.get('unit', '')
                key_params.append(f"{param_name}: {default} {unit}".strip())
        
        if key_params:
            print(f"   Key params: {', '.join(key_params)}")

def demonstrate_video_jamming_patterns():
    """Demonstrate different video jamming patterns"""
    
    print(f"\n" + "=" * 80)
    print("🎯 VIDEO JAMMING PATTERN DEMONSTRATION")
    print("=" * 80)
    
    # Focus on 5.8 GHz band (most common for FPV)
    jammer = DroneVideoJammingProtocol('5800')
    band_info = jammer.get_band_info()
    channels = band_info['channels']
    
    print(f"📡 {band_info['name']} Analysis:")
    print(f"  • Total channels: {len(channels)}")
    print(f"  • Frequency span: {(max(channels) - min(channels))/1e6:.1f} MHz")
    print(f"  • Channel spacing: ~{(channels[1] - channels[0])/1e6:.1f} MHz")
    print(f"  • Bandwidth per channel: {band_info['bandwidth']/1e6:.1f} MHz")
    
    # Show different jamming signal types
    print(f"\n🔊 Video Jamming Signal Types:")
    signal_types = {
        'video_noise': 'Wideband noise optimized for video disruption',
        'video_pulse': 'Pulsed jamming targeting video frame timing',
        'video_sweep': 'Frequency sweep across video bandwidth',
        'video_multitone': 'Multiple tones for comprehensive disruption'
    }
    
    for signal_type, description in signal_types.items():
        print(f"  • {signal_type.replace('_', ' ').title()}: {description}")
    
    # Demonstrate pattern effectiveness
    print(f"\n⚡ Pattern Effectiveness Analysis:")
    patterns = {
        'race_focus': 'Prioritizes race band (R1-R8) - most effective for racing drones',
        'sequential': 'Sequential sweep - methodical coverage of all channels',
        'pseudorandom': 'Random pattern - unpredictable disruption',
        'adaptive': 'Traffic-aware - focuses on active video channels',
        'barrage': 'Rapid cycling - maximum disruption in minimal time'
    }
    
    for pattern, description in patterns.items():
        print(f"  • {pattern.title()}: {description}")
    
    print(f"\n🎯 Video Jamming Optimization:")
    print(f"  • 5.8 GHz: Race band focus for maximum FPV disruption")
    print(f"  • 1.2 GHz: Center frequency focus for long-range video")
    print(f"  • Timing: 100-200ms dwell time for effective video disruption")
    print(f"  • Power: 47 dBm maximum for comprehensive coverage")
    print(f"  • Bandwidth: 5-10 MHz per channel for complete video disruption")

def show_frequency_coverage():
    """Show frequency coverage for both bands"""
    
    print(f"\n" + "=" * 80)
    print("📊 FREQUENCY COVERAGE ANALYSIS")
    print("=" * 80)
    
    for band in ['1200', '5800']:
        jammer = DroneVideoJammingProtocol(band)
        band_info = jammer.get_band_info()
        channels = band_info['channels']
        
        print(f"\n📡 {band_info['name']} Coverage:")
        print(f"  • Total channels: {len(channels)}")
        print(f"  • Frequency range: {min(channels)/1e6:.1f} - {max(channels)/1e6:.1f} MHz")
        print(f"  • Total bandwidth: {(max(channels) - min(channels))/1e6:.1f} MHz")
        print(f"  • Channel bandwidth: {band_info['bandwidth']/1e6:.1f} MHz")
        
        # Show frequency distribution
        freq_groups = {}
        for freq in channels:
            freq_mhz = int(freq / 1e6)
            if freq_mhz not in freq_groups:
                freq_groups[freq_mhz] = 0
            freq_groups[freq_mhz] += 1
        
        print(f"  • Frequency distribution:")
        for freq_mhz in sorted(freq_groups.keys()):
            count = freq_groups[freq_mhz]
            print(f"    - {freq_mhz} MHz: {count} channels")

if __name__ == "__main__":
    try:
        print("🎥 Starting Drone Video Jamming Protocol Test Suite")
        print("This demonstrates the video link jamming capabilities for FPV drones\n")
        
        test_drone_video_jamming_capabilities()
        demonstrate_video_jamming_patterns()
        show_frequency_coverage()
        
        print(f"\n" + "=" * 80)
        print("✅ DRONE VIDEO JAMMING TEST COMPLETE")
        print("=" * 80)
        print("\n🎯 Key Capabilities Added:")
        print("  • 1.2 GHz FPV video jamming for long-range drones")
        print("  • 5.8 GHz FPV video jamming targeting race bands")
        print("  • Video-optimized jamming patterns and signal types")
        print("  • Race band focus for maximum FPV racing disruption")
        print("  • Barrage mode for rapid multi-channel video disruption")
        print("  • Integration with existing HackRF workflow system")
        print("\n🚀 System now supports comprehensive drone video link jamming!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc() 
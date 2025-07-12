#!/usr/bin/env python3
"""
Test script for wideband signal cache system
Verifies that signals are pre-generated and ready for instant transmission
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from rf_workflows.wideband_signal_cache import get_signal_cache, initialize_signal_cache
from rf_workflows.enhanced_workflows import EnhancedWorkflows
from rf_workflows.hackrf_controller import HackRFController
import time

def test_signal_cache():
    """Test the signal cache system"""
    print("🎯 Testing Wideband Signal Cache System")
    print("=" * 50)
    
    # Initialize cache
    cache = get_signal_cache()
    
    # Check initial status
    status = cache.get_cache_status()
    print(f"Initial cache status:")
    print(f"  Files: {status['existing_files']}/{status['total_files']}")
    print(f"  Total size: {status['total_size_mb']:.1f} MB")
    print(f"  Cache directory: {status['cache_dir']}")
    
    # Test specific signal retrieval
    print(f"\n--- Testing Signal Retrieval ---")
    
    # Test 10 MHz, 5 second signal
    test_configs = [
        {'bandwidth': 10000000, 'duration': 5.0},
        {'bandwidth': 5000000, 'duration': 10.0}, 
        {'bandwidth': 10000000, 'duration': 30.0}
    ]
    
    for config in test_configs:
        print(f"\nTesting {config['bandwidth']/1e6:.0f} MHz, {config['duration']}s signal:")
        
        start_time = time.time()
        signal_path = cache.get_or_cache_signal(config['bandwidth'], config['duration'])
        elapsed = time.time() - start_time
        
        if signal_path:
            file_size_mb = os.path.getsize(signal_path) / 1e6
            print(f"  ✅ Signal ready in {elapsed:.3f}s")
            print(f"  File: {os.path.basename(signal_path)}")
            print(f"  Size: {file_size_mb:.1f} MB")
        else:
            print(f"  ❌ Signal not available")
    
    # Final cache status
    final_status = cache.get_cache_status()
    print(f"\nFinal cache status:")
    print(f"  Files: {final_status['existing_files']}/{final_status['total_files']}")
    print(f"  Total size: {final_status['total_size_mb']:.1f} MB")

def test_enhanced_workflows_integration():
    """Test integration with enhanced workflows"""
    print("\n🔗 Testing Enhanced Workflows Integration")
    print("=" * 50)
    
    # Create HackRF controller and enhanced workflows
    hackrf = HackRFController()
    workflows = EnhancedWorkflows(hackrf)
    
    # Check that cache was initialized
    cache = get_signal_cache()
    status = cache.get_cache_status()
    
    print(f"Enhanced workflows initialized with cache:")
    print(f"  Cache files: {status['existing_files']}")
    print(f"  Cache size: {status['total_size_mb']:.1f} MB")
    
    # Test drone video workflow availability
    available_workflows = workflows.get_available_workflows()
    drone_workflows = [w for w in available_workflows if 'drone_video' in w['name']]
    
    print(f"\nDrone video workflows available: {len(drone_workflows)}")
    for workflow in drone_workflows:
        print(f"  - {workflow['display_name']}")

def test_instant_transmission_simulation():
    """Test instant transmission capability"""
    print("\n⚡ Testing Instant Transmission Simulation")
    print("=" * 50)
    
    # Import the drone video protocol
    from rf_workflows.drone_video_jamming_protocol import DroneVideoJammingProtocol
    
    # Test with cached signals
    jammer = DroneVideoJammingProtocol(band='5800')
    
    # Test different scenarios
    test_scenarios = [
        {'bandwidth': 10000000, 'duration': 5.0, 'description': '10 MHz, 5s (should be instant)'},
        {'bandwidth': 5000000, 'duration': 10.0, 'description': '5 MHz, 10s (should be instant)'},
        {'bandwidth': 20000000, 'duration': 3.0, 'description': '20 MHz, 3s (may need generation)'}
    ]
    
    for scenario in test_scenarios:
        print(f"\n--- {scenario['description']} ---")
        
        start_time = time.time()
        
        # Test the single channel jammer
        jammer.start_single_channel_jammer(
            frequency=5658e6,  # Race band R1
            duration=scenario['duration'],
            power_level=47,
            bandwidth=scenario['bandwidth'],
            jamming_type='video_noise'
        )
        
        elapsed = time.time() - start_time
        print(f"Total time: {elapsed:.2f}s")
        
        # Check if it was instant (no generation delay)
        if elapsed < 1.0:
            print("✅ INSTANT transmission (cached signal used)")
        else:
            print("⚠️  Generation delay detected")

def main():
    """Run all signal cache tests"""
    print("🎯 HackRF Signal Cache System Test Suite")
    print("=" * 60)
    
    try:
        # Test the cache system
        test_signal_cache()
        
        # Test enhanced workflows integration
        test_enhanced_workflows_integration()
        
        # Test instant transmission
        test_instant_transmission_simulation()
        
        print("\n✅ All signal cache tests completed successfully!")
        print("🔴 HackRF LED should turn RED instantly when using cached signals!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
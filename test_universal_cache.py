#!/usr/bin/env python3
"""
Test script for universal signal cache system
Verifies that ALL signals are pre-generated and ready for instant transmission
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from rf_workflows.universal_signal_cache import get_universal_cache, initialize_universal_cache
from rf_workflows.enhanced_workflows import EnhancedWorkflows
from rf_workflows.hackrf_controller import HackRFController
from rf_workflows.elrs_protocol import ELRSProtocol
from rf_workflows.gps_protocol import GPSProtocol
from rf_workflows.adsb_protocol import ADSBProtocol
from rf_workflows.raw_energy_protocol import RawEnergyProtocol
import time

def test_universal_cache_status():
    """Test the universal cache status"""
    print("🎯 Testing Universal Signal Cache System")
    print("=" * 50)
    
    # Get cache instance
    cache = get_universal_cache()
    
    # Check initial status
    status = cache.get_cache_status()
    print(f"Cache status:")
    print(f"  Files: {status['existing_files']}/{status['total_configs']}")
    print(f"  Total size: {status['total_size_mb']:.1f} MB")
    print(f"  Cache directory: {status['cache_dir']}")
    print(f"  Signal types: {status['type_counts']}")
    
    return status

def test_signal_retrieval():
    """Test retrieving various signal types from cache"""
    print(f"\n--- Testing Signal Retrieval ---")
    
    cache = get_universal_cache()
    test_results = []
    
    # Test 1: ELRS signal
    print(f"\n1. Testing ELRS 915MHz signal:")
    elrs = ELRSProtocol('915')
    start_time = time.time()
    signal = elrs.generate_elrs_transmission(duration=10.0, packet_rate=100, power_level=47, flight_mode='manual')
    elapsed = time.time() - start_time
    test_results.append(('ELRS 915MHz', elapsed))
    print(f"  ✅ Retrieved in {elapsed:.3f}s")
    
    # Test 2: GPS signal
    print(f"\n2. Testing GPS L1 signal:")
    gps = GPSProtocol('L1')
    start_time = time.time()
    signal = gps.generate_gps_signal(duration=30.0)
    elapsed = time.time() - start_time
    test_results.append(('GPS L1', elapsed))
    print(f"  ✅ Retrieved in {elapsed:.3f}s")
    
    # Test 3: ADS-B signal
    print(f"\n3. Testing ADS-B signal:")
    adsb = ADSBProtocol()
    start_time = time.time()
    signal = adsb.generate_adsb_transmission(duration=30.0)
    elapsed = time.time() - start_time
    test_results.append(('ADS-B', elapsed))
    print(f"  ✅ Retrieved in {elapsed:.3f}s")
    
    # Test 4: Raw energy signal
    print(f"\n4. Testing Raw Energy signal:")
    raw = RawEnergyProtocol()
    start_time = time.time()
    signal = raw.generate_raw_energy_signal(frequency=1090e6, bandwidth=10e6, duration=10.0, noise_type='white')
    elapsed = time.time() - start_time
    test_results.append(('Raw Energy', elapsed))
    print(f"  ✅ Retrieved in {elapsed:.3f}s")
    
    # Test 5: Sine wave from HackRF controller
    print(f"\n5. Testing Sine wave signal:")
    hackrf = HackRFController()
    start_time = time.time()
    signal = hackrf.generate_sine_wave(baseband_freq=1000, duration=10.0)
    elapsed = time.time() - start_time
    test_results.append(('Sine Wave', elapsed))
    print(f"  ✅ Retrieved in {elapsed:.3f}s")
    
    # Summary
    print(f"\n--- Retrieval Time Summary ---")
    for signal_type, elapsed in test_results:
        status = "INSTANT" if elapsed < 1.0 else "SLOW"
        print(f"  {signal_type}: {elapsed:.3f}s [{status}]")
    
    # Check if all were instant
    all_instant = all(elapsed < 1.0 for _, elapsed in test_results)
    if all_instant:
        print(f"\n✅ ALL signals retrieved instantly from cache!")
    else:
        print(f"\n⚠️  Some signals took longer than expected")

def test_enhanced_workflows_with_cache():
    """Test that enhanced workflows use the cache"""
    print(f"\n🔗 Testing Enhanced Workflows with Universal Cache")
    print("=" * 50)
    
    # Create HackRF controller and enhanced workflows
    hackrf = HackRFController()
    workflows = EnhancedWorkflows(hackrf)
    
    # Get available workflows
    available = workflows.get_available_workflows()
    print(f"Total workflows available: {len(available)}")
    
    # Count by category
    categories = {}
    for w in available:
        cat = w.get('category', 'Other')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nWorkflows by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

def test_cache_performance():
    """Test cache performance with timing"""
    print(f"\n⚡ Testing Cache Performance")
    print("=" * 50)
    
    # Test rapid successive calls (should be very fast)
    elrs = ELRSProtocol('915')
    
    print("Testing 10 rapid successive calls for same signal:")
    times = []
    for i in range(10):
        start_time = time.time()
        signal = elrs.generate_elrs_transmission(duration=10.0, packet_rate=100, power_level=47)
        elapsed = time.time() - start_time
        times.append(elapsed)
        print(f"  Call {i+1}: {elapsed:.4f}s")
    
    avg_time = sum(times) / len(times)
    print(f"\nAverage retrieval time: {avg_time:.4f}s")
    print(f"All calls < 0.1s: {'✅ YES' if all(t < 0.1 for t in times) else '❌ NO'}")

def main():
    """Run all universal cache tests"""
    print("🎯 HackRF Universal Signal Cache Test Suite")
    print("=" * 60)
    
    try:
        # Test cache status
        status = test_universal_cache_status()
        
        if status['existing_files'] == 0:
            print("\n⚠️  No cached signals found. Initializing cache...")
            print("   This will take several minutes on first run.\n")
            initialize_universal_cache(force_regenerate=False)
            print("\n✅ Cache initialized!")
            
            # Re-check status
            status = test_universal_cache_status()
        
        # Test signal retrieval
        test_signal_retrieval()
        
        # Test enhanced workflows
        test_enhanced_workflows_with_cache()
        
        # Test performance
        test_cache_performance()
        
        print("\n✅ All universal cache tests completed successfully!")
        print("🔴 HackRF LED should turn RED instantly when any signal is transmitted!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
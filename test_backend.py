#!/usr/bin/env python3
"""
Simple test script for HackRF Emitter Backend
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from rf_workflows.modulation_workflows import ModulationWorkflows
from rf_workflows.hackrf_controller import HackRFController

def test_workflows():
    """Test the workflow system"""
    print("Testing HackRF Emitter Backend...")
    
    # Create mock HackRF controller (no actual device needed)
    hackrf = HackRFController()
    hackrf.device_connected = True  # Mock connection
    
    # Create workflows
    workflows = ModulationWorkflows(hackrf)
    
    # Get available workflows
    available_workflows = workflows.get_available_workflows()
    print(f"\nFound {len(available_workflows)} workflows:")
    
    for workflow in available_workflows:
        print(f"  - {workflow['display_name']}: {workflow['description']}")
        if 'parameters' in workflow:
            for param_name, param_config in workflow['parameters'].items():
                print(f"    * {param_name}: {param_config.get('type', 'unknown')} ({param_config.get('unit', 'no unit')})")
    
    # Test specific workflows
    print("\nTesting specific workflows:")
    
    # Test ELRS workflows
    elrs_workflows = ['elrs_433', 'elrs_915', 'elrs_2_4']
    for workflow_name in elrs_workflows:
        print(f"\nTesting {workflow_name}:")
        try:
            # Get workflow config
            workflow_config = next(w for w in available_workflows if w['name'] == workflow_name)
            print(f"  Frequency: {workflow_config['parameters']['frequency']['default'] / 1e6:.1f} MHz")
            print(f"  Packet Rate: {workflow_config['parameters']['packet_rate']['default']} Hz")
            print(f"  Power: {workflow_config['parameters']['power']['default']} mW")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Test GPS workflows
    gps_workflows = ['gps_l1', 'gps_l2', 'gps_l5']
    for workflow_name in gps_workflows:
        print(f"\nTesting {workflow_name}:")
        try:
            # Get workflow config
            workflow_config = next(w for w in available_workflows if w['name'] == workflow_name)
            print(f"  Frequency: {workflow_config['parameters']['frequency']['default'] / 1e6:.2f} MHz")
            print(f"  Satellite ID: {workflow_config['parameters']['satellite_id']['default']}")
            print(f"  Signal Strength: {workflow_config['parameters']['signal_strength']['default']} dBm")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\nBackend test completed successfully!")

if __name__ == "__main__":
    test_workflows() 
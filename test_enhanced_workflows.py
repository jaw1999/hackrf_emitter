#!/usr/bin/env python3
"""
Test script for Enhanced RF Workflows
Demonstrates the realistic signal generation capabilities
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from rf_workflows.modulation_workflows import ModulationWorkflows
from rf_workflows.hackrf_controller import HackRFController
import json

def test_enhanced_workflows():
    """Test the enhanced workflow system"""
    print("Testing Enhanced RF Workflows...")
    print("=" * 50)
    
    # Create mock HackRF controller
    hackrf = HackRFController()
    hackrf.device_connected = True  # Mock connection
    
    # Create workflows system
    workflows = ModulationWorkflows(hackrf)
    
    # Get available workflows
    available_workflows = workflows.get_available_workflows()
    print(f"\nFound {len(available_workflows)} total workflows:")
    
    # Categorize workflows
    categories = {}
    for workflow in available_workflows:
        category = workflow.get('category', 'Basic')
        if category not in categories:
            categories[category] = []
        categories[category].append(workflow)
    
    # Display workflows by category
    for category, cat_workflows in categories.items():
        print(f"\n{category} Workflows ({len(cat_workflows)}):")
        for workflow in cat_workflows:
            complexity = workflow.get('complexity', 'Basic')
            print(f"  ✓ {workflow['display_name']} [{complexity}]")
            print(f"    {workflow['description']}")
            
            # Show key parameters
            params = workflow.get('parameters', {})
            key_params = []
            for param_name, param_config in list(params.items())[:3]:  # Show first 3 params
                unit = param_config.get('unit', '')
                default = param_config.get('default', 'N/A')
                key_params.append(f"{param_name}: {default} {unit}".strip())
            
            if key_params:
                print(f"    Key params: {', '.join(key_params)}")
            print()
    
    # Test specific enhanced workflows
    print("\nTesting Enhanced Workflow Details:")
    print("-" * 40)
    
    # Test ELRS workflow
    elrs_workflows = [w for w in available_workflows if 'elrs' in w['name'] and 'enhanced' in w['name']]
    if elrs_workflows:
        elrs = elrs_workflows[0]
        print(f"ELRS Enhanced Workflow: {elrs['display_name']}")
        print(f"Parameters: {len(elrs['parameters'])} total")
        
        # Show parameter details
        for param_name, param_config in elrs['parameters'].items():
            param_type = param_config.get('type', 'unknown')
            description = param_config.get('description', 'No description')
            print(f"  - {param_name} ({param_type}): {description}")
    
    # Test GPS workflow
    gps_workflows = [w for w in available_workflows if 'gps' in w['name'] and 'constellation' in w['name']]
    if gps_workflows:
        gps = gps_workflows[0]
        print(f"\nGPS Enhanced Workflow: {gps['display_name']}")
        print(f"Parameters: {len(gps['parameters'])} total")
        
    # Test ADS-B workflow
    adsb_workflows = [w for w in available_workflows if 'adsb' in w['name']]
    if adsb_workflows:
        adsb = adsb_workflows[0]
        print(f"\nADS-B Enhanced Workflow: {adsb['display_name']}")
        print(f"Parameters: {len(adsb['parameters'])} total")
    
    # Show workflow complexity distribution
    complexity_count = {}
    for workflow in available_workflows:
        complexity = workflow.get('complexity', 'Basic')
        complexity_count[complexity] = complexity_count.get(complexity, 0) + 1
    
    print(f"\nWorkflow Complexity Distribution:")
    for complexity, count in complexity_count.items():
        print(f"  {complexity}: {count} workflows")
    
    # Protocol-specific information
    print(f"\nProtocol Information:")
    print("-" * 20)
    
    # Test protocol access through enhanced workflows
    enhanced = workflows.enhanced_workflows
    
    # ELRS protocol info
    print("ELRS Protocols:")
    for band, protocol in enhanced.elrs_protocols.items():
        band_info = protocol.get_band_info()
        print(f"  {band}MHz: {len(band_info['channels'])} channels, "
              f"max power: {band_info['max_power']}mW")
    
    # GPS protocol info
    print("\nGPS Protocols:")
    for band, protocol in enhanced.gps_protocols.items():
        constellation_info = protocol.get_constellation_info()
        print(f"  {band}: {constellation_info['num_satellites']} satellites, "
              f"freq: {constellation_info['carrier_frequency']/1e6:.2f}MHz")
    
    # ADS-B protocol info
    aircraft_list = enhanced.adsb_protocol.get_aircraft_list()
    print(f"\nADS-B Protocol: {len(aircraft_list)} aircraft simulated")
    for aircraft in aircraft_list:
        print(f"  {aircraft['callsign']} ({aircraft['icao']}): "
              f"Alt {aircraft['altitude']}ft, Vel {aircraft['velocity']}kts")
    
    print(f"\nEnhanced Workflow System Test Complete!")
    print(f"Ready for realistic RF signal generation.")

def test_workflow_parameters():
    """Test workflow parameter validation and formatting"""
    print("\nTesting Workflow Parameter System:")
    print("-" * 35)
    
    # Create workflow system
    hackrf = HackRFController()
    hackrf.device_connected = True
    workflows = ModulationWorkflows(hackrf)
    
    # Get an enhanced workflow
    available = workflows.get_available_workflows()
    enhanced_workflows = [w for w in available if w.get('complexity') in ['High', 'Very High']]
    
    if enhanced_workflows:
        workflow = enhanced_workflows[0]
        print(f"Analyzing: {workflow['display_name']}")
        
        # Show parameter types and validation
        params = workflow['parameters']
        print(f"Parameters ({len(params)} total):")
        
        for name, config in params.items():
            param_type = config['type']
            print(f"\n  {name} ({param_type}):")
            
            if param_type == 'select':
                options = config.get('options', [])
                print(f"    Options: {options}")
                
            elif param_type in ['int', 'float']:
                min_val = config.get('min')
                max_val = config.get('max')
                default = config.get('default')
                unit = config.get('unit', '')
                
                print(f"    Range: {min_val} - {max_val} {unit}")
                print(f"    Default: {default} {unit}")
                
            elif param_type == 'bool':
                default = config.get('default', False)
                print(f"    Default: {default}")
            
            description = config.get('description', '')
            if description:
                print(f"    Description: {description}")

if __name__ == "__main__":
    test_enhanced_workflows()
    test_workflow_parameters() 
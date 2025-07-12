from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json
import threading
import time
from datetime import datetime

from rf_workflows.hackrf_controller import HackRFController
from rf_workflows.modulation_workflows import ModulationWorkflows
from rf_workflows.universal_signal_cache import initialize_universal_cache, get_universal_cache
from utils.config_manager import ConfigManager
from utils.safety_manager import SafetyManager

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, 
    cors_allowed_origins="*",
    ping_timeout=60,  # Increase ping timeout to 60 seconds
    ping_interval=25,  # Keep default ping interval
    async_mode='threading'  # Use threading for better compatibility
)

# Initialize managers
config_manager = ConfigManager()
safety_manager = SafetyManager()
hackrf_controller = HackRFController()
modulation_workflows = ModulationWorkflows(hackrf_controller)

# Global state
current_workflow = None
is_transmitting = False
transmission_thread = None

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status"""
    return jsonify({
        'is_transmitting': is_transmitting,
        'current_workflow': current_workflow,
        'hackrf_connected': hackrf_controller.is_connected(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    """Get available RF workflows"""
    workflows = modulation_workflows.get_available_workflows()
    return jsonify(workflows)

@app.route('/api/start_workflow', methods=['POST'])
def start_workflow():
    """Start a specific RF workflow"""
    global current_workflow, is_transmitting, transmission_thread
    
    try:
        data = request.get_json()
        workflow_name = data.get('workflow')
        parameters = data.get('parameters', {})
        
        # Safety checks - REMOVED for unrestricted operation
        # if not safety_manager.validate_parameters(workflow_name, parameters):
        #     return jsonify({'error': 'Invalid parameters or safety violation'}), 400
        
        if is_transmitting:
            return jsonify({'error': 'Already transmitting'}), 400
        
        # Set initial state
        is_transmitting = True
        current_workflow = workflow_name
        
        # Emit initial status
        socketio.emit('workflow_status', {
            'status': 'starting',
            'workflow': workflow_name,
            'timestamp': datetime.now().isoformat()
        })
        
        # Start workflow in background thread
        def run_workflow():
            global is_transmitting, current_workflow
            
            try:
                # Emit running status
                socketio.emit('workflow_status', {
                    'status': 'running',
                    'workflow': workflow_name,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Start the actual workflow
                modulation_workflows.start_workflow(workflow_name, parameters)
                
                # Wait for the workflow to complete
                while modulation_workflows.active_workflow is not None:
                    time.sleep(0.1)
                
            except Exception as e:
                print(f"Workflow error: {e}")
                socketio.emit('workflow_error', {
                    'error': str(e),
                    'workflow': workflow_name,
                    'timestamp': datetime.now().isoformat()
                })
            finally:
                # Always clean up state
                print(f"Workflow {workflow_name} completed, cleaning up state")
                is_transmitting = False
                current_workflow = None
                socketio.emit('workflow_status', {
                    'status': 'stopped',
                    'workflow': workflow_name,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"Emitted stopped status for {workflow_name}")
        
        transmission_thread = threading.Thread(target=run_workflow)
        transmission_thread.daemon = True
        transmission_thread.start()
        
        return jsonify({'message': f'Started {workflow_name} workflow'})
        
    except Exception as e:
        # Reset state on error
        is_transmitting = False
        current_workflow = None
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop_workflow', methods=['POST'])
def stop_workflow():
    """Stop current RF workflow"""
    global is_transmitting, current_workflow, transmission_thread
    
    try:
        if not is_transmitting:
            return jsonify({'message': 'No active workflow'})
        
        # Stop the modulation workflow
        modulation_workflows.stop_workflow()
        
        # Wait for the transmission thread to finish (with timeout)
        if transmission_thread and transmission_thread.is_alive():
            transmission_thread.join(timeout=5)
        
        # Update state
        is_transmitting = False
        current_workflow = None
        
        socketio.emit('workflow_status', {
            'status': 'stopped',
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({'message': 'Workflow stopped'})
        
    except Exception as e:
        # Force cleanup on error
        is_transmitting = False
        current_workflow = None
        return jsonify({'error': str(e)}), 500

@app.route('/api/frequency_bands', methods=['GET'])
def get_frequency_bands():
    """Get available frequency bands"""
    bands = config_manager.get_frequency_bands()
    return jsonify(bands)

@app.route('/api/safety_limits', methods=['GET'])
def get_safety_limits():
    """Get current safety limits"""
    limits = safety_manager.get_limits()
    return jsonify(limits)

@app.route('/api/device_info', methods=['GET'])
def get_device_info():
    """Get HackRF device information"""
    info = hackrf_controller.get_device_info()
    return jsonify(info)

@app.route('/api/library', methods=['GET'])
def get_library():
    """Get the list of all cached signals and their metadata"""
    cache = get_universal_cache()
    # Return a list of dicts for each cached signal
    signals = [signal.__dict__ for signal in cache.cached_signals.values()]
    return jsonify(signals)

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'message': 'Connected to HackRF Emitter'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    print("Starting HackRF Emitter Backend...")
    print("API available at: http://localhost:5000")
    print("WebSocket available at: ws://localhost:5000")
    
    # Initialize universal signal cache on startup
    print("\n🚀 Initializing Universal Signal Cache...")
    try:
        def init_cache_background():
            """Initialize cache in background to not block startup"""
            try:
                initialize_universal_cache(force_regenerate=False)
                print("✅ Universal Signal Cache ready - all signals pre-generated!")
            except Exception as e:
                print(f"⚠️  Cache initialization failed: {e}")
                print("   Signals will be generated on-demand (slower first transmission)")
        
        # Start cache initialization in background thread
        cache_thread = threading.Thread(target=init_cache_background)
        cache_thread.daemon = True
        cache_thread.start()
        
    except Exception as e:
        print(f"⚠️  Could not start cache initialization: {e}")
    
    # Initialize HackRF connection
    try:
        hackrf_controller.initialize()
        print("HackRF device initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize HackRF device: {e}")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True) 
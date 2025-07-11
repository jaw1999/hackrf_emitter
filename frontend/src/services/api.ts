import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export interface SystemStatus {
  is_transmitting: boolean;
  current_workflow: string | null;
  hackrf_connected: boolean;
  timestamp: string;
}

export interface Workflow {
  name: string;
  display_name: string;
  description: string;
  category?: string;
  complexity?: string;
  parameters: Record<string, any>;
}

export interface DeviceInfo {
  status: string;
  info?: string;
  current_frequency?: number;
  current_sample_rate?: number;
  current_gain?: number;
  error?: string;
}

export interface FrequencyBand {
  name: string;
  start_freq: number;
  end_freq: number;
  description: string;
}

export interface SafetyLimits {
  max_power_dbm: number;
  max_gain: number;
  min_gain: number;
  max_duration: number;
  min_duration: number;
  frequency_range: {
    min: number;
    max: number;
  };
  restricted_frequencies: Array<{
    start: number;
    end: number;
    description: string;
  }>;
}

export const apiService = {
  // System status
  getStatus: async (): Promise<SystemStatus> => {
    const response = await api.get('/status');
    return response.data;
  },

  // Workflows
  getWorkflows: async (): Promise<Workflow[]> => {
    const response = await api.get('/workflows');
    return response.data;
  },

  startWorkflow: async (workflow: string, parameters: Record<string, any>): Promise<any> => {
    const response = await api.post('/start_workflow', {
      workflow,
      parameters,
    });
    return response.data;
  },

  stopWorkflow: async (): Promise<any> => {
    const response = await api.post('/stop_workflow');
    return response.data;
  },

  // Device information
  getDeviceInfo: async (): Promise<DeviceInfo> => {
    const response = await api.get('/device_info');
    return response.data;
  },

  // Frequency bands
  getFrequencyBands: async (): Promise<FrequencyBand[]> => {
    const response = await api.get('/frequency_bands');
    return response.data;
  },

  // Safety limits
  getSafetyLimits: async (): Promise<SafetyLimits> => {
    const response = await api.get('/safety_limits');
    return response.data;
  },
};

export default apiService; 
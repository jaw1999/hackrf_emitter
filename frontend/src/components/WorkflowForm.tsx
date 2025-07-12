import React, { useState, useEffect } from 'react';
import { PlayIcon, ExclamationTriangleIcon, FireIcon, BoltIcon } from '@heroicons/react/24/outline';
import { Workflow } from '../services/api';

interface WorkflowFormProps {
  workflow: Workflow;
  onSubmit: (workflowName: string, parameters: Record<string, any>) => void;
  onCancel: () => void;
}

const WorkflowForm: React.FC<WorkflowFormProps> = ({ workflow, onSubmit, onCancel }) => {
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Initialize parameters with defaults
    const initialParams: Record<string, any> = {};
    Object.entries(workflow.parameters).forEach(([key, param]) => {
      const p = param as any;
      // Handle select parameters with object options
      if (p.type === 'select' && p.options && p.options.length > 0) {
        const firstOption = p.options[0];
        if (typeof firstOption === 'object' && firstOption.value !== undefined) {
          // For object options, use the default index to find the value
          const defaultIndex = p.default || 0;
          initialParams[key] = p.options[defaultIndex]?.value || firstOption.value;
        } else {
          // For string options, use the default value directly
          initialParams[key] = p.default || firstOption;
        }
      } else {
        initialParams[key] = p.default;
      }
    });
    setParameters(initialParams);
  }, [workflow]);

  const handleParameterChange = (key: string, value: any) => {
    setParameters(prev => ({
      ...prev,
      [key]: value
    }));
    
    // Clear error for this parameter
    if (errors[key]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[key];
        return newErrors;
      });
    }
  };

  const validateParameters = (): boolean => {
    const newErrors: Record<string, string> = {};

    Object.entries(workflow.parameters).forEach(([key, param]) => {
      const value = parameters[key];
      const p = param as any;
      
      if (p.type === 'float' || p.type === 'int') {
        const numValue = parseFloat(value);
        
        if (isNaN(numValue)) {
          newErrors[key] = 'Must be a valid number';
        } else if (p.min !== undefined && numValue < p.min) {
          newErrors[key] = `Minimum value is ${p.min}`;
        } else if (p.max !== undefined && numValue > p.max) {
          newErrors[key] = `Maximum value is ${p.max}`;
        }
      } else if (p.type === 'string') {
        if (!value || value.trim() === '') {
          newErrors[key] = 'This field is required';
        }
      }
    });

    // Safety checks - REMOVED FOR UNRESTRICTED OPERATION
    // All frequency and power restrictions have been disabled

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateParameters()) {
      return;
    }

    setLoading(true);
    try {
      await onSubmit(workflow.name, parameters);
    } catch (error) {
      console.error('Error submitting workflow:', error);
    } finally {
      setLoading(false);
    }
  };

      const renderParameterInput = (key: string, param: any) => {
        const value = parameters[key];
        const error = errors[key];
        const isPowerLevel = key === 'power_level' && isELRSJamming;

        if (param.type === 'float' || param.type === 'int') {
            return (
                <div key={key} className={isPowerLevel ? 'bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-950 dark:to-red-950 rounded-lg p-3 border border-orange-200 dark:border-orange-700' : ''}>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        <div className="flex items-center space-x-2">
                          <span>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                          {isPowerLevel && (
                            <div className="flex items-center space-x-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 px-2 py-1 rounded-full text-xs font-bold">
                              <FireIcon className="h-3 w-3" />
                              <span>MAX POWER</span>
                            </div>
                          )}
                        </div>
                        {param.unit && <span className="text-gray-500 dark:text-gray-400 ml-1">({param.unit})</span>}
                    </label>
                    <input
                        type="number"
                        value={value}
                        onChange={(e) => handleParameterChange(key, param.type === 'int' ? parseInt(e.target.value) : parseFloat(e.target.value))}
                        min={param.min}
                        max={param.max}
                        step={param.type === 'int' ? 1 : 'any'}
                        className={`input-field ${error ? 'border-danger-300 focus:border-danger-500 focus:ring-danger-500' : ''} ${isPowerLevel ? 'border-orange-300 dark:border-orange-600 focus:border-orange-500 focus:ring-orange-500' : ''}`}
                    />
                    {error && <p className="mt-1 text-sm text-danger-600 dark:text-danger-400">{error}</p>}
                    {isPowerLevel && (
                        <p className="mt-1 text-xs text-orange-700 dark:text-orange-300 font-medium">
                          🔥 Maximum HackRF gain for optimal jamming effectiveness
                        </p>
                    )}
                    {param.description && !isPowerLevel && (
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{param.description}</p>
                    )}
                </div>
            );
        }

        if (param.type === 'select') {
            const isSweepPattern = key === 'sweep_pattern' && isELRSJamming;
            const isTargetChannel = key === 'target_channel';
            const isBandwidth = key === 'bandwidth';
            const specialClass = isSweepPattern ? 'bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 rounded-lg p-3 border border-blue-200 dark:border-blue-700' 
                                : isTargetChannel ? 'bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950 rounded-lg p-3 border border-purple-200 dark:border-purple-700' 
                                : isBandwidth ? 'bg-gradient-to-r from-green-50 to-teal-50 dark:from-green-950 dark:to-teal-950 rounded-lg p-3 border border-green-200 dark:border-green-700'
                                : '';
            return (
                <div key={key} className={specialClass}>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        <div className="flex items-center space-x-2">
                          <span>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                          {isSweepPattern && (
                            <div className="flex items-center space-x-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded-full text-xs font-bold">
                              <BoltIcon className="h-3 w-3" />
                              <span>PATTERN</span>
                            </div>
                          )}
                          {isTargetChannel && (
                            <div className="flex items-center space-x-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 px-2 py-1 rounded-full text-xs font-bold">
                              <span>🎯</span>
                              <span>CHANNEL</span>
                            </div>
                          )}
                          {isBandwidth && (
                            <div className="flex items-center space-x-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded-full text-xs font-bold">
                              <span>📡</span>
                              <span>BANDWIDTH</span>
                            </div>
                          )}
                        </div>
                    </label>
                    <select
                        value={value}
                        onChange={(e) => {
                            // For select parameters that should be integers (like target_channel, bandwidth), convert to int
                            const newValue = (key === 'target_channel' || key === 'bandwidth') ? parseInt(e.target.value) : e.target.value;
                            handleParameterChange(key, newValue);
                        }}
                        className={`input-field ${error ? 'border-danger-300 focus:border-danger-500 focus:ring-danger-500' : ''} ${isSweepPattern ? 'border-blue-300 dark:border-blue-600 focus:border-blue-500 focus:ring-blue-500' : ''} ${isTargetChannel ? 'border-purple-300 dark:border-purple-600 focus:border-purple-500 focus:ring-purple-500' : ''} ${isBandwidth ? 'border-green-300 dark:border-green-600 focus:border-green-500 focus:ring-green-500' : ''}`}
                    >
                        {param.options.map((option: any) => {
                            // Handle both string options and object options with value/label
                            if (typeof option === 'object' && option.value !== undefined && option.label !== undefined) {
                                return (
                                    <option key={option.value} value={option.value}>
                                        {option.label}
                                    </option>
                                );
                            } else {
                                // Handle string options (legacy format)
                                return (
                                    <option key={option} value={option}>
                                        {option.charAt(0).toUpperCase() + option.slice(1).replace(/_/g, ' ')}
                                    </option>
                                );
                            }
                        })}
                    </select>
                    {error && <p className="mt-1 text-sm text-danger-600 dark:text-danger-400">{error}</p>}
                    {isSweepPattern && (
                        <p className="mt-1 text-xs text-blue-700 dark:text-blue-300 font-medium">
                          ⚡ Pseudorandom pattern mimics real ELRS behavior for maximum effectiveness
                        </p>
                    )}
                    {isTargetChannel && (
                        <p className="mt-1 text-xs text-purple-700 dark:text-purple-300 font-medium">
                          🎯 Target specific video channel for precision jamming
                        </p>
                    )}
                    {isBandwidth && (
                        <p className="mt-1 text-xs text-green-700 dark:text-green-300 font-medium">
                          📡 10 MHz covers full video feed, 5 MHz for narrower targeting
                        </p>
                    )}
                    {param.description && !isSweepPattern && !isTargetChannel && !isBandwidth && (
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{param.description}</p>
                    )}
                </div>
            );
        }

        if (param.type === 'string') {
            return (
                <div key={key}>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </label>
                    <input
                        type="text"
                        value={value}
                        onChange={(e) => handleParameterChange(key, e.target.value)}
                        className={`input-field ${error ? 'border-danger-300 focus:border-danger-500 focus:ring-danger-500' : ''}`}
                    />
                    {error && <p className="mt-1 text-sm text-danger-600 dark:text-danger-400">{error}</p>}
                    {param.description && (
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{param.description}</p>
                    )}
                </div>
            );
        }

        if (param.type === 'bool') {
            return (
                <div key={key}>
                    <label className="flex items-center space-x-2">
                        <input
                            type="checkbox"
                            checked={value}
                            onChange={(e) => handleParameterChange(key, e.target.checked)}
                            className="rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500"
                        />
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                    </label>
                    {param.description && (
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{param.description}</p>
                    )}
                </div>
            );
        }

        return null;
    };

  const isELRSJamming = workflow.category === 'ELRS Jamming';

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Enhanced Safety Information Banner */}
      {isELRSJamming ? (
        <div className="rounded-lg bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-950 dark:to-red-950 border border-orange-200 dark:border-orange-700 p-4">
          <div className="flex items-start space-x-3">
            <FireIcon className="h-5 w-5 text-orange-600 dark:text-orange-400 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-orange-800 dark:text-orange-200 flex items-center space-x-2">
                <span>Maximum Power ELRS Jamming Workflow</span>
                <div className="flex items-center space-x-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 px-2 py-1 rounded-full text-xs font-bold">
                  <BoltIcon className="h-3 w-3" />
                  <span>47 dBm</span>
                </div>
              </h3>
              <p className="mt-1 text-sm text-orange-700 dark:text-orange-300">
                This workflow uses maximum HackRF power (47 dBm gain) with advanced frequency sweeping across multiple channels. 
                Ensure proper antenna, cooling, and RF safety precautions. Verify compliance with local regulations.
              </p>
              <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-orange-700 dark:text-orange-300">
                <div className="flex items-center space-x-1">
                  <BoltIcon className="h-3 w-3" />
                  <span>Maximum HackRF gain: 47 dB</span>
                </div>
                <div className="flex items-center space-x-1">
                  <BoltIcon className="h-3 w-3" />
                  <span>Frequency sweeping across 20-24 channels</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="rounded-lg bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-700 p-4">
          <div className="flex items-start space-x-3">
            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">Safety Information</h3>
              <p className="mt-1 text-sm text-yellow-700 dark:text-yellow-300">
                Please ensure your parameters comply with local RF regulations. 
                System restrictions have been disabled for advanced users.
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Parameters */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Parameters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(workflow.parameters).map(([key, param]) => 
            renderParameterInput(key, param as any)
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          type="button"
          onClick={onCancel}
          className="btn-secondary"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading || Object.keys(errors).length > 0}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <PlayIcon className="h-4 w-4" />
          <span>{loading ? 'Starting...' : `Start ${workflow.display_name}`}</span>
        </button>
      </div>
    </form>
  );
};

export default WorkflowForm; 
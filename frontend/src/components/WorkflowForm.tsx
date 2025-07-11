import React, { useState, useEffect } from 'react';
import { PlayIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { Workflow, apiService, SafetyLimits } from '../services/api';

interface WorkflowFormProps {
  workflow: Workflow;
  onSubmit: (workflowName: string, parameters: Record<string, any>) => void;
  onCancel: () => void;
}

const WorkflowForm: React.FC<WorkflowFormProps> = ({ workflow, onSubmit, onCancel }) => {
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [safetyLimits, setSafetyLimits] = useState<SafetyLimits | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Initialize parameters with defaults
    const initialParams: Record<string, any> = {};
    Object.entries(workflow.parameters).forEach(([key, param]) => {
      initialParams[key] = (param as any).default;
    });
    setParameters(initialParams);

    // Load safety limits
    apiService.getSafetyLimits().then(setSafetyLimits);
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

        if (param.type === 'float' || param.type === 'int') {
            return (
                <div key={key}>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        {param.unit && <span className="text-gray-500 dark:text-gray-400 ml-1">({param.unit})</span>}
                    </label>
                    <input
                        type="number"
                        value={value}
                        onChange={(e) => handleParameterChange(key, param.type === 'int' ? parseInt(e.target.value) : parseFloat(e.target.value))}
                        min={param.min}
                        max={param.max}
                        step={param.type === 'int' ? 1 : 'any'}
                        className={`input-field ${error ? 'border-danger-300 focus:border-danger-500 focus:ring-danger-500' : ''}`}
                    />
                    {error && <p className="mt-1 text-sm text-danger-600 dark:text-danger-400">{error}</p>}
                    {param.description && (
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

        return null;
    };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Safety Information Banner */}
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
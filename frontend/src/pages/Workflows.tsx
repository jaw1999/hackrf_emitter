import React, { useState, useEffect } from 'react';
import {
  PlayIcon,
  StopIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  SignalIcon,
  SparklesIcon,
  ChartBarIcon,
  WifiIcon,
  GlobeAltIcon,
  BeakerIcon,
  AcademicCapIcon,
  LightBulbIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  BoltIcon,
  FireIcon,
  XMarkIcon,
  ClockIcon,
  CogIcon
} from '@heroicons/react/24/outline';
import { useSocket } from '../contexts/SocketContext';
import { apiService, Workflow, SystemStatus } from '../services/api';
import WorkflowForm from '../components/WorkflowForm';

// Category icons and colors
const categoryConfig: { [key: string]: { icon: React.ComponentType<any>; color: string; bgColor: string } } = {
  'RC Control': { icon: WifiIcon, color: 'text-blue-600', bgColor: 'bg-blue-50 dark:bg-blue-900/20' },
  'ELRS Jamming': { icon: BoltIcon, color: 'text-yellow-600', bgColor: 'bg-yellow-50 dark:bg-yellow-900/20' },
  'GNSS': { icon: GlobeAltIcon, color: 'text-green-600', bgColor: 'bg-green-50 dark:bg-green-900/20' },
  'Aviation': { icon: SignalIcon, color: 'text-purple-600', bgColor: 'bg-purple-50 dark:bg-purple-900/20' },
  'Advanced': { icon: SparklesIcon, color: 'text-indigo-600', bgColor: 'bg-indigo-50 dark:bg-indigo-900/20' },
  'Radar': { icon: ChartBarIcon, color: 'text-red-600', bgColor: 'bg-red-50 dark:bg-red-900/20' },
  'Raw Energy': { icon: FireIcon, color: 'text-orange-600', bgColor: 'bg-orange-50 dark:bg-orange-900/20' },
  'Drone Video Jamming': { icon: FireIcon, color: 'text-pink-600', bgColor: 'bg-pink-50 dark:bg-pink-900/20' },
  'Uncategorized': { icon: BeakerIcon, color: 'text-gray-600', bgColor: 'bg-gray-50 dark:bg-gray-900/20' }
};

// Complexity badges
const complexityConfig: { [key: string]: { color: string; icon: React.ComponentType<any>; description: string } } = {
  'Basic': { 
    color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 border-green-200 dark:border-green-700', 
    icon: AcademicCapIcon,
    description: 'Simple setup, safe parameters'
  },
  'Medium': { 
    color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 border-blue-200 dark:border-blue-700', 
    icon: LightBulbIcon,
    description: 'Intermediate level'
  },
  'High': { 
    color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200 border-orange-200 dark:border-orange-700', 
    icon: ShieldCheckIcon,
    description: 'Advanced - requires RF knowledge'
  },
  'Very High': { 
    color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 border-red-200 dark:border-red-700', 
    icon: ExclamationTriangleIcon,
    description: 'Expert level - use with caution'
  }
};

const Workflows: React.FC = () => {
  const { isConnected, workflowStatus, currentWorkflow } = useSocket();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // UI state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [workflowsData, statusData] = await Promise.all([
          apiService.getWorkflows(),
          apiService.getStatus()
        ]);
        setWorkflows(workflowsData);
        setSystemStatus(statusData);
      } catch (error) {
        console.error('Error fetching workflows:', error);
        setError('Failed to load workflows');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(() => {
      apiService.getStatus().then(setSystemStatus).catch(console.error);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // Clear messages after 5 seconds
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  useEffect(() => {
    if (error && !error.includes('Failed to load')) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  // Status tracking
  const isTransmitting = workflowStatus === 'running' || 
    (workflowStatus !== 'stopped' && systemStatus?.is_transmitting) || false;
  const activeWorkflow = workflowStatus === 'stopped' ? null : 
    (currentWorkflow || systemStatus?.current_workflow);

  const handleStartWorkflow = async (workflowName: string, parameters: Record<string, any>) => {
    try {
      setError(null);
      await apiService.startWorkflow(workflowName, parameters);
      setShowForm(false);
      setSelectedWorkflow(null);
      setSuccess(`Started ${workflowName} successfully!`);
    } catch (error) {
      console.error('Error starting workflow:', error);
      setError(`Failed to start workflow: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleStopWorkflow = async () => {
    try {
      setError(null);
      await apiService.stopWorkflow();
      setSuccess('Workflow stopped successfully!');
    } catch (error) {
      console.error('Error stopping workflow:', error);
      setError(`Failed to stop workflow: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const openWorkflowForm = (workflow: Workflow) => {
    setSelectedWorkflow(workflow);
    setShowForm(true);
  };

  // Get unique categories
  const categories = ['all', ...Array.from(new Set(workflows.map(w => w.category || 'Uncategorized')))];

  // Filter workflows
  const filteredWorkflows = workflows.filter(workflow => {
    const matchesSearch = workflow.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         workflow.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || workflow.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  // Group workflows by category for stats
  const categoryStats = workflows.reduce((acc, workflow) => {
    const category = workflow.category || 'Uncategorized';
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const formatFrequency = (freq: number): string => {
    if (freq >= 1e9) {
      return `${(freq / 1e9).toFixed(2)} GHz`;
    } else if (freq >= 1e6) {
      return `${(freq / 1e6).toFixed(2)} MHz`;
    } else if (freq >= 1e3) {
      return `${(freq / 1e3).toFixed(2)} kHz`;
    }
    return `${freq} Hz`;
  };

  const getParameterDisplayValue = (key: string, param: any): string => {
    if (key === 'frequency' && typeof param.default === 'number') {
      return formatFrequency(param.default);
    }
    if (key === 'sample_rate' && typeof param.default === 'number') {
      return `${(param.default / 1e6).toFixed(1)} MS/s`;
    }
    if (key === 'tx_gain' || key === 'gain') {
      return `${param.default} dB`;
    }
    if (key === 'duration' && typeof param.default === 'number') {
      return `${param.default}s`;
    }
    return `${param.default}${param.unit ? ` ${param.unit}` : ''}`;
  };

  const getParameterFriendlyName = (key: string): string => {
    const nameMap: { [key: string]: string } = {
      'frequency': 'Frequency',
      'sample_rate': 'Sample Rate',
      'tx_gain': 'TX Gain',
      'gain': 'Gain',
      'duration': 'Duration',
      'bandwidth': 'Bandwidth',
      'modulation': 'Modulation',
      'data_rate': 'Data Rate'
    };
    return nameMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p className="text-gray-600 dark:text-gray-400">Loading RF workflows...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900 dark:to-blue-900 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">RF Workflows</h1>
            <p className="text-gray-600 dark:text-gray-400 mb-2">
              {filteredWorkflows.length} of {workflows.length} workflows available
            </p>
            <div className="flex items-center space-x-4 text-sm">
              <span className={`flex items-center space-x-2 ${isConnected ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
              </span>
              <span className="text-gray-500 dark:text-gray-400">
                {Object.keys(categoryStats).length} categories
              </span>
            </div>
          </div>
          {isTransmitting && (
            <button
              onClick={handleStopWorkflow}
              className="btn-danger flex items-center space-x-2"
            >
              <StopIcon className="h-5 w-5" />
              <span>Stop Transmission</span>
            </button>
          )}
        </div>
      </div>

      {/* Status Messages */}
      {success && (
        <div className="rounded-lg bg-green-50 dark:bg-green-900 border-l-4 border-green-400 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="ml-3 text-sm font-medium text-green-800 dark:text-green-200">{success}</p>
          </div>
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 dark:bg-red-900 border-l-4 border-red-400 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="ml-3 text-sm font-medium text-red-800 dark:text-red-200">{error}</p>
          </div>
        </div>
      )}

      {/* Active Workflow Banner */}
      {isTransmitting && activeWorkflow && (
        <div className="rounded-xl bg-gradient-to-r from-primary-50 to-green-50 dark:from-primary-900 dark:to-green-900 border border-primary-200 dark:border-primary-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-primary-600 rounded-full animate-pulse"></div>
              <div>
                <h3 className="font-semibold text-primary-800 dark:text-primary-200">
                  📡 Transmission Active: {activeWorkflow}
                </h3>
                <p className="text-sm text-primary-600 dark:text-primary-400">
                  Started at {new Date().toLocaleTimeString()}
                </p>
              </div>
            </div>
            <button
              onClick={handleStopWorkflow}
              className="btn-danger flex items-center space-x-2 text-sm"
            >
              <StopIcon className="h-4 w-4" />
              <span>Stop</span>
            </button>
          </div>
        </div>
      )}

      {/* Connection Warning */}
      {!isConnected && (
        <div className="rounded-lg bg-red-50 dark:bg-red-900 border-l-4 border-red-400 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">Connection Lost</h3>
                <p className="text-sm text-red-700 dark:text-red-300">Unable to connect to the backend service</p>
              </div>
            </div>
            <button 
              onClick={() => window.location.reload()} 
              className="btn-primary bg-red-600 hover:bg-red-700 text-white px-3 py-1 text-sm"
            >
              Reconnect
            </button>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search workflows by name or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10 pr-4 w-full"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* Category Filter */}
          <div className="relative sm:w-48">
            <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="input-field pl-10 appearance-none w-full"
            >
              <option value="all">All Categories</option>
              {categories.slice(1).map(category => (
                <option key={category} value={category}>
                  {category} ({categoryStats[category] || 0})
                </option>
              ))}
            </select>
          </div>

          {/* View Mode Toggle */}
          <div className="flex border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-2 text-sm font-medium transition-colors ${
                viewMode === 'grid'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 text-sm font-medium transition-colors ${
                viewMode === 'list'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              List
            </button>
          </div>
        </div>
        
        {(searchTerm || selectedCategory !== 'all') && (
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Showing {filteredWorkflows.length} of {workflows.length} workflows
            </p>
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('all');
              }}
              className="text-sm text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300"
            >
              Clear filters
            </button>
          </div>
        )}
      </div>

      {/* Workflows Grid/List */}
      {filteredWorkflows.length === 0 ? (
        <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-xl shadow-sm">
          <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No workflows found</h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            Try adjusting your search criteria or clearing the filters.
          </p>
          <button
            onClick={() => {
              setSearchTerm('');
              setSelectedCategory('all');
            }}
            className="btn-primary"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className={viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
          : 'space-y-4'
        }>
          {filteredWorkflows.map(workflow => {
            const category = workflow.category || 'Uncategorized';
            const categoryData = categoryConfig[category] || categoryConfig['Uncategorized'];
            const CategoryIcon = categoryData.icon;
            const complexityData = complexityConfig[workflow.complexity || 'Basic'];
            const ComplexityIcon = complexityData.icon;
            
            // Get key parameters for preview
            const keyParams = Object.entries(workflow.parameters).slice(0, 2);
            
            return (
              <div
                key={workflow.name}
                className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:shadow-lg transition-all duration-200 ${
                  viewMode === 'list' ? 'flex items-center p-4' : 'p-6'
                }`}
              >
                {viewMode === 'grid' ? (
                  // Grid View
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${categoryData.bgColor}`}>
                          <CategoryIcon className={`h-5 w-5 ${categoryData.color}`} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-base leading-tight">
                            {workflow.display_name}
                          </h3>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{category}</p>
                        </div>
                      </div>
                      <div className={`px-2 py-1 text-xs font-medium rounded-full border ${complexityData.color} flex items-center space-x-1`}>
                        <ComplexityIcon className="h-3 w-3" />
                        <span>{workflow.complexity || 'Basic'}</span>
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                      {workflow.description}
                    </p>

                    {/* Key Parameters */}
                    {keyParams.length > 0 && (
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3">
                        <div className="space-y-2">
                          {keyParams.map(([key, param]) => (
                            <div key={key} className="flex justify-between items-center text-xs">
                              <span className="text-gray-600 dark:text-gray-400">
                                {getParameterFriendlyName(key)}:
                              </span>
                              <span className="text-gray-900 dark:text-gray-100 font-medium">
                                {getParameterDisplayValue(key, param)}
                              </span>
                            </div>
                          ))}
                          {Object.keys(workflow.parameters).length > 2 && (
                            <p className="text-xs text-gray-500 dark:text-gray-400 italic">
                              +{Object.keys(workflow.parameters).length - 2} more configurable
                            </p>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Action Button */}
                    <button
                      onClick={() => openWorkflowForm(workflow)}
                      disabled={!isConnected || isTransmitting}
                      className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-sm py-2.5 font-medium"
                    >
                      <PlayIcon className="h-4 w-4" />
                      <span>Launch Workflow</span>
                    </button>
                  </div>
                ) : (
                  // List View
                  <div className="flex items-center space-x-4 w-full">
                    <div className={`p-2 rounded-lg ${categoryData.bgColor}`}>
                      <CategoryIcon className={`h-5 w-5 ${categoryData.color}`} />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3 mb-1">
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                          {workflow.display_name}
                        </h3>
                        <div className={`px-2 py-1 text-xs font-medium rounded-full border ${complexityData.color} flex items-center space-x-1`}>
                          <ComplexityIcon className="h-3 w-3" />
                          <span>{workflow.complexity || 'Basic'}</span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{workflow.description}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                        <span>{category}</span>
                        {keyParams.length > 0 && (
                          <span>• {getParameterFriendlyName(keyParams[0][0])}: {getParameterDisplayValue(keyParams[0][0], keyParams[0][1])}</span>
                        )}
                        <span>• {Object.keys(workflow.parameters).length} parameters</span>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => openWorkflowForm(workflow)}
                      disabled={!isConnected || isTransmitting}
                      className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 text-sm py-2 px-4 font-medium"
                    >
                      <PlayIcon className="h-4 w-4" />
                      <span>Launch</span>
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Workflow Form Modal */}
      {showForm && selectedWorkflow && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
                    <CogIcon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                      Configure {selectedWorkflow.display_name}
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400 mt-1">
                      {selectedWorkflow.description}
                    </p>
                    {selectedWorkflow.complexity && (
                      <div className="flex items-center space-x-2 mt-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${complexityConfig[selectedWorkflow.complexity].color}`}>
                          {selectedWorkflow.complexity} Level
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {complexityConfig[selectedWorkflow.complexity].description}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => setShowForm(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              <WorkflowForm
                workflow={selectedWorkflow}
                onSubmit={handleStartWorkflow}
                onCancel={() => setShowForm(false)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Workflows; 
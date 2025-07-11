import React, { useState, useEffect } from 'react';
import {
  PlayIcon,
  StopIcon,
  CogIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ClockIcon,
  SignalIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  InformationCircleIcon,
  SparklesIcon,
  ChartBarIcon,
  WifiIcon,
  GlobeAltIcon,
  RadioIcon,
  BeakerIcon,
  StarIcon,
  AcademicCapIcon,
  LightBulbIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { useSocket } from '../contexts/SocketContext';
import { apiService, Workflow, SystemStatus } from '../services/api';
import WorkflowForm from '../components/WorkflowForm';

// Category icons mapping with enhanced visual appeal
const categoryIcons: { [key: string]: React.ComponentType<any> } = {
  'Basic': BeakerIcon,
  'Modulation': RadioIcon,
  'RC Control': WifiIcon,
  'GNSS': GlobeAltIcon,
  'Aviation': SignalIcon,
  'Advanced': SparklesIcon,
  'Radar': ChartBarIcon,
  'Raw Energy': SparklesIcon,
  'Uncategorized': CogIcon
};

// Enhanced complexity system with better descriptions
const complexityInfo: { [key: string]: { color: string; icon: React.ComponentType<any>; description: string } } = {
  'Basic': { 
    color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 border-green-200 dark:border-green-700', 
    icon: AcademicCapIcon,
    description: 'Perfect for beginners - simple setup, safe parameters'
  },
  'Medium': { 
    color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 border-blue-200 dark:border-blue-700', 
    icon: LightBulbIcon,
    description: 'Intermediate level - some RF knowledge helpful'
  },
  'High': { 
    color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200 border-orange-200 dark:border-orange-700', 
    icon: ShieldCheckIcon,
    description: 'Advanced - requires good understanding of RF principles'
  },
  'Very High': { 
    color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 border-red-200 dark:border-red-700', 
    icon: ExclamationTriangleIcon,
    description: 'Expert level - use with caution, verify parameters carefully'
  }
};

// Workflow recommendations for new users
const recommendedWorkflows = ['Basic FM Transmission', 'BPSK Test Signal', 'Frequency Sweep'];

const Workflows: React.FC = () => {
  const { isConnected, workflowStatus, currentWorkflow } = useSocket();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Enhanced UI state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedComplexity, setSelectedComplexity] = useState<string>('all');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [showGettingStarted, setShowGettingStarted] = useState(true);
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
        
        // Auto-expand categories that have workflows, prioritizing Basic category
        const categories = new Set(workflowsData.map(w => w.category || 'Uncategorized'));
        if (categories.has('Basic')) {
          setExpandedCategories(new Set(['Basic']));
        } else {
          setExpandedCategories(categories);
        }
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

  // Clear success/error messages after 5 seconds
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

  // Merge real-time socket data with API data
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

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  // Get unique categories and complexities
  const categories = ['all', ...Array.from(new Set(workflows.map(w => w.category || 'Uncategorized')))];
  const complexities = ['all', ...Array.from(new Set(workflows.map(w => w.complexity || 'Basic')))];

  // Filter workflows
  const filteredWorkflows = workflows.filter(workflow => {
    const matchesSearch = workflow.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         workflow.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || workflow.category === selectedCategory;
    const matchesComplexity = selectedComplexity === 'all' || workflow.complexity === selectedComplexity;
    
    return matchesSearch && matchesCategory && matchesComplexity;
  });

  // Group workflows by category
  const groupedWorkflows = filteredWorkflows.reduce((acc, workflow) => {
    const category = workflow.category || 'Uncategorized';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(workflow);
    return acc;
  }, {} as Record<string, Workflow[]>);

  // Sort categories by importance (Basic first, then by workflow count)
  const sortedCategories = Object.keys(groupedWorkflows).sort((a, b) => {
    if (a === 'Basic') return -1;
    if (b === 'Basic') return 1;
    return groupedWorkflows[b].length - groupedWorkflows[a].length;
  });

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
      {/* Enhanced Header with Better Context */}
      <div className="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900 dark:to-blue-900 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">RF Workflows</h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-1">
              Ready-to-use radio frequency transmission patterns
            </p>
            <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
              <span>{filteredWorkflows.length} workflows available</span>
              <span>•</span>
              <span>{sortedCategories.length} categories</span>
              <span>•</span>
              <span className={`flex items-center space-x-1 ${isConnected ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
              </span>
            </div>
          </div>
          {isTransmitting && (
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border-l-4 border-red-500">
              <button
                onClick={handleStopWorkflow}
                className="btn-danger flex items-center space-x-2 animate-pulse mb-2"
              >
                <StopIcon className="h-5 w-5" />
                <span>Emergency Stop</span>
              </button>
              <p className="text-xs text-gray-600 dark:text-gray-400">Click to immediately halt transmission</p>
            </div>
          )}
        </div>
      </div>

      {/* Status Messages with Better Styling */}
      {success && (
        <div className="rounded-lg bg-green-50 dark:bg-green-900 border-l-4 border-green-400 p-4 shadow-sm">
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
        <div className="rounded-lg bg-red-50 dark:bg-red-900 border-l-4 border-red-400 p-4 shadow-sm">
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

      {/* Enhanced Active Workflow Banner */}
      {isTransmitting && activeWorkflow && (
        <div className="rounded-xl bg-gradient-to-r from-primary-50 to-green-50 dark:from-primary-900 dark:to-green-900 border border-primary-200 dark:border-primary-700 p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                <div className="relative">
                  <div className="w-4 h-4 bg-primary-600 rounded-full animate-pulse"></div>
                  <div className="absolute top-0 left-0 w-4 h-4 bg-primary-400 rounded-full animate-ping"></div>
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-primary-800 dark:text-primary-200 mb-1">
                  📡 Transmission Active
                </h3>
                <p className="text-primary-700 dark:text-primary-300 font-medium">
                  Running: <span className="font-bold">{activeWorkflow}</span>
                </p>
                <p className="text-sm text-primary-600 dark:text-primary-400 mt-1">
                  <ClockIcon className="inline h-4 w-4 mr-1" />
                  Started at {new Date().toLocaleTimeString()}
                </p>
              </div>
            </div>
            <div className="text-right">
              <button
                onClick={handleStopWorkflow}
                className="btn-danger flex items-center space-x-2 mb-2"
              >
                <StopIcon className="h-4 w-4" />
                <span>Stop Transmission</span>
              </button>
              <p className="text-xs text-primary-600 dark:text-primary-400">
                Always verify transmission parameters comply with local regulations
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Connection Status with Action */}
      {!isConnected && (
        <div className="rounded-lg bg-red-50 dark:bg-red-900 border-l-4 border-red-400 p-4 shadow-sm">
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

      {/* Getting Started Guide for New Users */}
      {showGettingStarted && !isTransmitting && (
        <div className="bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-xl p-6 shadow-sm">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <LightBulbIcon className="h-6 w-6 text-blue-600 dark:text-blue-400 mt-1" />
              <div>
                <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">New to RF Workflows?</h3>
                <p className="text-blue-800 dark:text-blue-200 mb-3">
                  Start with these beginner-friendly workflows to get familiar with the system:
                </p>
                <div className="flex flex-wrap gap-2">
                  {workflows.filter(w => recommendedWorkflows.includes(w.display_name)).map(workflow => (
                    <button
                      key={workflow.name}
                      onClick={() => openWorkflowForm(workflow)}
                      className="bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200 px-3 py-1 rounded-full text-sm hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors flex items-center space-x-1"
                      disabled={!isConnected || isTransmitting}
                    >
                      <StarIcon className="h-3 w-3" />
                      <span>{workflow.display_name}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <button
              onClick={() => setShowGettingStarted(false)}
              className="text-blue-400 hover:text-blue-600 dark:hover:text-blue-300"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Enhanced Search and Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Find Workflows</h2>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">View:</span>
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-primary-100 text-primary-600 dark:bg-primary-900 dark:text-primary-400' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'}`}
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-primary-100 text-primary-600 dark:bg-primary-900 dark:text-primary-400' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'}`}
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Enhanced Search */}
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10 pr-4"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          {/* Category Filter with Icons */}
          <div className="relative">
            <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="input-field pl-10 appearance-none"
            >
              <option value="all">All Categories</option>
              {categories.slice(1).map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          {/* Complexity Filter with Better Labels */}
          <div className="relative">
            <AcademicCapIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <select
              value={selectedComplexity}
              onChange={(e) => setSelectedComplexity(e.target.value)}
              className="input-field pl-10 appearance-none"
            >
              <option value="all">All Skill Levels</option>
              {complexities.slice(1).map(complexity => (
                <option key={complexity} value={complexity}>
                  {complexity} Level
                </option>
              ))}
            </select>
          </div>
        </div>
        
        {(searchTerm || selectedCategory !== 'all' || selectedComplexity !== 'all') && (
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Showing {filteredWorkflows.length} of {workflows.length} workflows
            </p>
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('all');
                setSelectedComplexity('all');
              }}
              className="text-sm text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300"
            >
              Clear all filters
            </button>
          </div>
        )}
      </div>

      {/* Workflows by Category */}
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
              setSelectedComplexity('all');
            }}
            className="btn-primary"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {sortedCategories.map(category => {
            const categoryWorkflows = groupedWorkflows[category];
            const Icon = categoryIcons[category] || CogIcon;
            const isExpanded = expandedCategories.has(category);

            return (
              <div key={category} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                {/* Enhanced Category Header */}
                <button
                  onClick={() => toggleCategory(category)}
                  className="w-full px-6 py-5 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors group"
                >
                  <div className="flex items-center space-x-4">
                    <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg group-hover:bg-primary-200 dark:group-hover:bg-primary-800 transition-colors">
                      <Icon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                    </div>
                    <div className="text-left">
                      <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">{category}</h2>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {categoryWorkflows.length} workflow{categoryWorkflows.length !== 1 ? 's' : ''} available
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {category === 'Basic' && (
                      <span className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 px-2 py-1 rounded-full text-xs font-medium">
                        Recommended
                      </span>
                    )}
                    {isExpanded ? (
                      <ChevronUpIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <ChevronDownIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </div>
                </button>

                {/* Enhanced Category Workflows */}
                {isExpanded && (
                  <div className="px-6 pb-6 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                    <div className={`mt-6 ${viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}`}>
                      {categoryWorkflows.map(workflow => {
                        const complexityData = complexityInfo[workflow.complexity || 'Basic'];
                        const ComplexityIcon = complexityData.icon;
                        
                        return (
                          <div
                            key={workflow.name}
                            className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-all hover:border-primary-300 dark:hover:border-primary-600 ${viewMode === 'list' ? 'flex items-center p-4' : 'p-5'}`}
                          >
                            {viewMode === 'grid' ? (
                              <>
                                {/* Enhanced Workflow Header */}
                                <div className="flex items-start justify-between mb-4">
                                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-lg leading-tight">
                                    {workflow.display_name}
                                  </h3>
                                  <div className={`ml-3 px-3 py-1 text-xs font-medium rounded-full border ${complexityData.color} flex items-center space-x-1`}>
                                    <ComplexityIcon className="h-3 w-3" />
                                    <span>{workflow.complexity || 'Basic'}</span>
                                  </div>
                                </div>

                                {/* Enhanced Description */}
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">
                                  {workflow.description}
                                </p>

                                {/* Enhanced Key Parameters Preview */}
                                <div className="mb-5 bg-gray-50 dark:bg-gray-900 rounded-lg p-3">
                                  <h4 className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Key Parameters</h4>
                                  <div className="space-y-1">
                                    {Object.entries(workflow.parameters).slice(0, 3).map(([key, param]) => (
                                      <div key={key} className="flex justify-between items-center text-xs">
                                        <span className="text-gray-600 dark:text-gray-400">
                                          {getParameterFriendlyName(key)}:
                                        </span>
                                        <span className="text-gray-900 dark:text-gray-100 font-medium">
                                          {getParameterDisplayValue(key, param)}
                                        </span>
                                      </div>
                                    ))}
                                    {Object.keys(workflow.parameters).length > 3 && (
                                      <p className="text-xs text-gray-500 dark:text-gray-400 italic pt-1">
                                        +{Object.keys(workflow.parameters).length - 3} more configurable
                                      </p>
                                    )}
                                  </div>
                                </div>

                                {/* Enhanced Action Button */}
                                <button
                                  onClick={() => openWorkflowForm(workflow)}
                                  disabled={!isConnected || isTransmitting}
                                  className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-sm py-3 font-medium"
                                >
                                  <PlayIcon className="h-4 w-4" />
                                  <span>Configure & Launch</span>
                                </button>
                              </>
                            ) : (
                              <>
                                {/* List View Layout */}
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center space-x-3 mb-1">
                                    <h3 className="font-semibold text-gray-900 dark:text-gray-100 truncate">
                                      {workflow.display_name}
                                    </h3>
                                    <div className={`px-2 py-1 text-xs font-medium rounded-full border ${complexityData.color} flex items-center space-x-1`}>
                                      <ComplexityIcon className="h-3 w-3" />
                                      <span>{workflow.complexity || 'Basic'}</span>
                                    </div>
                                  </div>
                                  <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                                    {workflow.description}
                                  </p>
                                </div>
                                <div className="ml-4">
                                  <button
                                    onClick={() => openWorkflowForm(workflow)}
                                    disabled={!isConnected || isTransmitting}
                                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 text-sm px-4 py-2"
                                  >
                                    <PlayIcon className="h-4 w-4" />
                                    <span>Launch</span>
                                  </button>
                                </div>
                              </>
                            )}
                          </div>
                        );
                      })}
                    </div>
                    
                    {/* Category-specific guidance */}
                    {category === 'Basic' && (
                      <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200 dark:border-blue-700">
                        <div className="flex items-start space-x-2">
                          <InformationCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                          <div>
                            <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100">Getting Started Tip</h4>
                            <p className="text-sm text-blue-800 dark:text-blue-200 mt-1">
                              These workflows are perfect for learning. They use safe, well-tested parameters and include detailed descriptions.
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Enhanced Workflow Form Modal */}
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
                    <div className="flex items-center space-x-2 mt-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${complexityInfo[selectedWorkflow.complexity || 'Basic'].color}`}>
                        {selectedWorkflow.complexity || 'Basic'} Level
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {complexityInfo[selectedWorkflow.complexity || 'Basic'].description}
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setShowForm(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
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
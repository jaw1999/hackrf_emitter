import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Workflows from './pages/Workflows';
import DeviceInfoPage from './pages/DeviceInfo';
import Settings from './pages/Settings';
import Library from './pages/Library';

function App() {
  return (
    <div className="App">
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/workflows" element={<Workflows />} />
          <Route path="/device" element={<DeviceInfoPage />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/library" element={<Library />} />
        </Routes>
      </Layout>
    </div>
  );
}

export default App; 
import React, { useState, useEffect } from 'react';
import { Activity, Server, ShieldAlert, RefreshCw, LayoutDashboard, Users, CreditCard, Settings, Layers, Command, ClipboardList, Rocket, Database, Briefcase } from './components/Icons';
import { generateTimeSeriesData, mockSecurityEvents, mockTopEndpoints, mockSummary, mockHealth, mockUsers, mockInvoices, mockMicroservices, mockIncidents, mockDeployments } from './utils/mockData';
import { ServiceType, TimeSeriesPoint } from './types';
import DashboardPage from './pages/DashboardPage';
import MetricsPage from './pages/MetricsPage';
import SecurityPage from './pages/SecurityPage';
import HealthPage from './pages/HealthPage';
import UserManagementPage from './pages/UserManagementPage';
import FinancePage from './pages/FinancePage';
import SettingsPage from './pages/SettingsPage';
import ServicesPage from './pages/ServicesPage';
import ConsolePage from './pages/ConsolePage';
import IncidentsPage from './pages/IncidentsPage';
import DeploymentsPage from './pages/DeploymentsPage';
import DatabasePage from './pages/DatabasePage';
import JobsPage from './pages/JobsPage';

// Logo Component
const Logo = () => (
  <div className="flex items-center gap-3">
    <div className="w-10 h-10 bg-gradient-to-br from-primary to-lime-600 rounded-xl flex items-center justify-center text-dark-950 shadow-[0_0_15px_rgba(138,206,0,0.3)]">
      <div className="font-mono font-bold text-lg leading-none mt-1 mr-1">{'>_'}</div>
    </div>
    <div>
      <div className="font-bold text-xl text-white tracking-tight leading-none">KSysAdmin</div>
      <div className="text-[10px] font-semibold text-primary uppercase tracking-widest opacity-80">Unified Console</div>
    </div>
  </div>
);

const App: React.FC = () => {
  const [selectedService, setSelectedService] = useState<ServiceType>('all');
  const [timeRange, setTimeRange] = useState<number>(7); // Days
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // State for data
  const [metricsData, setMetricsData] = useState<TimeSeriesPoint[]>([]);

  const loadData = () => {
    setIsRefreshing(true);
    // Simulate API call delay
    setTimeout(() => {
      setMetricsData(generateTimeSeriesData(timeRange));
      setLastUpdated(new Date());
      setIsRefreshing(false);
    }, 600);
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Auto refresh 30s
    return () => clearInterval(interval);
  }, [selectedService, timeRange]);

  const navButtonClass = (id: string) => `
    w-full flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200
    ${activeTab === id 
      ? 'bg-primary/10 text-primary shadow-[0_0_20px_rgba(138,206,0,0.05)] border border-primary/20' 
      : 'text-slate-400 hover:bg-dark-800 hover:text-white'}
  `;

  // Page title mapping
  const pageTitles: Record<string, string> = {
    dashboard: 'Dashboard',
    services: 'Service Architecture',
    metrics: 'System Metrics',
    console: 'Command Center',
    incidents: 'Incident Response',
    deployments: 'Release Management',
    database: 'Data Explorer',
    jobs: 'Jobs & Queues',
    security: 'Security Center',
    health: 'Infrastructure Health',
    users: 'User Management',
    finance: 'Finance & Invoicing',
    settings: 'System Configuration'
  };

  return (
    <div className="min-h-screen flex bg-dark-950 text-slate-200 selection:bg-primary/30 selection:text-white">
      {/* Sidebar */}
      <aside className="w-72 bg-dark-900 border-r border-dark-800 hidden md:flex flex-col fixed h-full z-10 shadow-xl overflow-y-auto custom-scrollbar">
        <div className="p-8 pb-4">
          <Logo />
        </div>
        
        <nav className="px-4 space-y-6 flex-1 py-4">
          <div>
            <h3 className="px-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Technical Ops</h3>
            <div className="space-y-1">
              <button onClick={() => setActiveTab('dashboard')} className={navButtonClass('dashboard')}>
                <LayoutDashboard className="w-5 h-5" />
                Dashboard
              </button>
              <button onClick={() => setActiveTab('services')} className={navButtonClass('services')}>
                <Layers className="w-5 h-5" />
                Services & Topology
              </button>
              <button onClick={() => setActiveTab('metrics')} className={navButtonClass('metrics')}>
                <Activity className="w-5 h-5" />
                Metrics
              </button>
              <button onClick={() => setActiveTab('jobs')} className={navButtonClass('jobs')}>
                <Briefcase className="w-5 h-5" />
                Jobs & Queues
              </button>
              <button onClick={() => setActiveTab('security')} className={navButtonClass('security')}>
                <ShieldAlert className="w-5 h-5" />
                Security
              </button>
              <button onClick={() => setActiveTab('health')} className={navButtonClass('health')}>
                <Server className="w-5 h-5" />
                System Health
              </button>
              <button onClick={() => setActiveTab('incidents')} className={navButtonClass('incidents')}>
                <ClipboardList className="w-5 h-5" />
                Incidents
              </button>
              <button onClick={() => setActiveTab('deployments')} className={navButtonClass('deployments')}>
                <Rocket className="w-5 h-5" />
                Deployments
              </button>
            </div>
          </div>

          <div>
            <h3 className="px-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Business Mgmt</h3>
            <div className="space-y-1">
              <button onClick={() => setActiveTab('users')} className={navButtonClass('users')}>
                <Users className="w-5 h-5" />
                User Accounts
              </button>
              <button onClick={() => setActiveTab('finance')} className={navButtonClass('finance')}>
                <CreditCard className="w-5 h-5" />
                Finance & Invoices
              </button>
            </div>
          </div>
          
          <div>
            <h3 className="px-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Admin</h3>
            <div className="space-y-1">
               <button onClick={() => setActiveTab('database')} className={navButtonClass('database')}>
                <Database className="w-5 h-5" />
                Data Explorer
              </button>
              <button onClick={() => setActiveTab('console')} className={navButtonClass('console')}>
                <Command className="w-5 h-5" />
                Command Center
              </button>
              <button onClick={() => setActiveTab('settings')} className={navButtonClass('settings')}>
                <Settings className="w-5 h-5" />
                Configuration
              </button>
            </div>
          </div>
        </nav>

        <div className="p-4 border-t border-dark-800/50 mt-auto">
          <div className="bg-dark-950/50 rounded-xl p-4 border border-dark-800">
            <h4 className="text-xs font-bold text-slate-500 uppercase mb-4 tracking-wider">System Status</h4>
            <div className="space-y-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400">Database</span>
                <span className="flex items-center gap-2 text-primary font-mono text-xs bg-primary/10 px-2 py-1 rounded-md border border-primary/20">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
                  {mockHealth.database.latency}ms
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400">Redis</span>
                <span className="flex items-center gap-2 text-primary font-mono text-xs bg-primary/10 px-2 py-1 rounded-md border border-primary/20">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
                  {mockHealth.redis.latency}ms
                </span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 md:ml-72 p-6 md:p-8 overflow-y-auto">
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">{pageTitles[activeTab]}</h1>
            <p className="text-slate-400 mt-1 flex items-center gap-2 text-sm">
              <span className="w-2 h-2 rounded-full bg-primary"></span>
              {['users', 'finance', 'settings'].includes(activeTab) ? 'Management Console' : 'System operational'} • Last updated {lastUpdated.toLocaleTimeString()}
            </p>
          </div>
          
          <div className="flex flex-wrap items-center gap-3">
            {!['health', 'users', 'finance', 'settings', 'services', 'console', 'incidents', 'deployments', 'database', 'jobs'].includes(activeTab) && (
              <select 
                className="bg-dark-900 border border-dark-800 text-slate-300 text-sm rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary/50 focus:border-primary/50 outline-none hover:border-dark-700 transition-colors cursor-pointer"
                value={selectedService}
                onChange={(e) => setSelectedService(e.target.value as ServiceType)}
              >
                <option value="all">All Services</option>
                <option value="auth">Auth Service</option>
                <option value="payment">Payment Service</option>
                <option value="admin">Admin Service</option>
              </select>
            )}

            {!['users', 'finance', 'settings', 'services', 'console', 'incidents', 'deployments', 'database', 'jobs'].includes(activeTab) && (
              <select 
                className="bg-dark-900 border border-dark-800 text-slate-300 text-sm rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary/50 focus:border-primary/50 outline-none hover:border-dark-700 transition-colors cursor-pointer"
                value={timeRange}
                onChange={(e) => setTimeRange(Number(e.target.value))}
              >
                <option value={1}>Last 24 Hours</option>
                <option value={7}>Last 7 Days</option>
                <option value={30}>Last 30 Days</option>
              </select>
            )}

            <button 
              onClick={loadData}
              className={`p-2.5 rounded-lg border border-dark-800 bg-dark-900 text-slate-400 hover:text-primary hover:border-primary/30 transition-all shadow-lg ${isRefreshing ? 'animate-spin text-primary border-primary/30' : ''}`}
              title="Refresh Data"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Content Render Logic */}
        {activeTab === 'dashboard' && (
          <DashboardPage 
            metricsData={metricsData} 
            summary={mockSummary} 
            topEndpoints={mockTopEndpoints} 
            securityEvents={mockSecurityEvents} 
          />
        )}
        {activeTab === 'services' && <ServicesPage services={mockMicroservices} />}
        {activeTab === 'metrics' && <MetricsPage data={metricsData} />}
        {activeTab === 'jobs' && <JobsPage />}
        {activeTab === 'security' && <SecurityPage events={mockSecurityEvents} />}
        {activeTab === 'health' && <HealthPage />}
        {activeTab === 'incidents' && <IncidentsPage incidents={mockIncidents} />}
        {activeTab === 'deployments' && <DeploymentsPage deployments={mockDeployments} />}
        {activeTab === 'database' && <DatabasePage />}
        {activeTab === 'users' && <UserManagementPage users={mockUsers} />}
        {activeTab === 'finance' && <FinancePage invoices={mockInvoices} />}
        {activeTab === 'console' && <ConsolePage />}
        {activeTab === 'settings' && <SettingsPage />}
      </main>
    </div>
  );
};

export default App;
import React, { useState } from 'react';
import { Settings, Save, Bell, Lock, Database, Sliders, Cpu, Globe, Zap, AlertTriangle } from '../components/Icons';

const SettingsPage: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState('system');
  const [isSaving, setIsSaving] = useState(false);
  
  // Mock State for Settings
  const [settings, setSettings] = useState({
    // System Tuning
    maxThreads: 64,
    gcThreshold: 85,
    asyncWorkers: 16,
    logLevel: 'INFO',
    maintenanceMode: false,
    
    // Network
    tcpKeepAlive: 300,
    maxConnections: 10000,
    requestTimeout: 30,
    corsOrigins: '*',
    
    // Security
    rateLimitWindow: 60,
    rateLimitMax: 1000,
    banDuration: 3600,
    ipWhitelist: '127.0.0.1, 192.168.1.100',
    jwtExpiration: 7200,
    
    // Database
    dbPoolSize: 20,
    dbIdleTimeout: 10000,
    cacheTtl: 300,
    redisCompression: true,
    
    // Feature Flags
    enableBetaFeatures: false,
    enableAuditLog: true,
    enableWebhooks: true,
  });

  const handleSave = () => {
    setIsSaving(true);
    setTimeout(() => setIsSaving(false), 1000);
  };

  const handleInputChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const categories = [
    { id: 'system', name: 'System Tuning', icon: <Cpu className="w-4 h-4" /> },
    { id: 'network', name: 'Network Layer', icon: <Globe className="w-4 h-4" /> },
    { id: 'security', name: 'Security Policies', icon: <Lock className="w-4 h-4" /> },
    { id: 'database', name: 'Database & Cache', icon: <Database className="w-4 h-4" /> },
    { id: 'flags', name: 'Feature Flags', icon: <Zap className="w-4 h-4" /> },
    { id: 'raw', name: 'Raw Configuration', icon: <Settings className="w-4 h-4" /> },
  ];

  const renderContent = () => {
    switch(activeCategory) {
      case 'system':
        return (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="bg-dark-950/50 p-4 rounded-lg border border-dark-800 mb-6">
              <h3 className="text-white font-medium flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                Kernel & Runtime Parameters
              </h3>
              <p className="text-sm text-slate-400">Modifying these values directly impacts the application runtime behavior. Incorrect settings may cause instability.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Max Worker Threads</label>
                <input 
                  type="number" 
                  value={settings.maxThreads}
                  onChange={(e) => handleInputChange('maxThreads', parseInt(e.target.value))}
                  className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none"
                />
                <p className="text-xs text-slate-500">Maximum concurrent threads for the worker pool.</p>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Async Workers</label>
                <input 
                  type="number" 
                  value={settings.asyncWorkers}
                  onChange={(e) => handleInputChange('asyncWorkers', parseInt(e.target.value))}
                  className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">GC Threshold (%)</label>
                <div className="flex items-center gap-4">
                  <input 
                    type="range" 
                    min="50" max="95"
                    value={settings.gcThreshold}
                    onChange={(e) => handleInputChange('gcThreshold', parseInt(e.target.value))}
                    className="flex-1 accent-primary h-2 bg-dark-800 rounded-lg appearance-none cursor-pointer"
                  />
                  <span className="text-sm font-mono text-primary w-12 text-right">{settings.gcThreshold}%</span>
                </div>
                <p className="text-xs text-slate-500">Trigger garbage collection when heap usage exceeds this value.</p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Log Level</label>
                <select 
                  value={settings.logLevel}
                  onChange={(e) => handleInputChange('logLevel', e.target.value)}
                  className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none"
                >
                  <option value="DEBUG">DEBUG (Verbose)</option>
                  <option value="INFO">INFO (Standard)</option>
                  <option value="WARN">WARN (Issues only)</option>
                  <option value="ERROR">ERROR (Critical only)</option>
                </select>
              </div>
            </div>

            <div className="pt-4 border-t border-dark-800">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-white font-medium">Maintenance Mode</h4>
                  <p className="text-sm text-slate-500">Reject all incoming traffic with a 503 Service Unavailable.</p>
                </div>
                <button 
                  onClick={() => handleInputChange('maintenanceMode', !settings.maintenanceMode)}
                  className={`w-12 h-6 rounded-full transition-colors relative ${settings.maintenanceMode ? 'bg-red-500' : 'bg-dark-700'}`}
                >
                  <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${settings.maintenanceMode ? 'left-7' : 'left-1'}`}></span>
                </button>
              </div>
            </div>
          </div>
        );

      case 'network':
        return (
          <div className="space-y-6 animate-in fade-in duration-300">
             <div className="grid grid-cols-1 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">CORS Origins</label>
                  <input 
                    type="text" 
                    value={settings.corsOrigins}
                    onChange={(e) => handleInputChange('corsOrigins', e.target.value)}
                    className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none font-mono text-sm"
                  />
                  <p className="text-xs text-slate-500">Comma separated list of allowed origins. Use * for wildcard.</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Max Connections</label>
                    <input 
                      type="number" 
                      value={settings.maxConnections}
                      onChange={(e) => handleInputChange('maxConnections', parseInt(e.target.value))}
                      className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">TCP Keep-Alive (s)</label>
                    <input 
                      type="number" 
                      value={settings.tcpKeepAlive}
                      onChange={(e) => handleInputChange('tcpKeepAlive', parseInt(e.target.value))}
                      className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Request Timeout (s)</label>
                    <input 
                      type="number" 
                      value={settings.requestTimeout}
                      onChange={(e) => handleInputChange('requestTimeout', parseInt(e.target.value))}
                      className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none"
                    />
                  </div>
                </div>
             </div>
          </div>
        );

      case 'security':
        return (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
               <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">Global Rate Limit</label>
                  <div className="flex gap-2">
                    <input 
                      type="number" 
                      value={settings.rateLimitMax}
                      onChange={(e) => handleInputChange('rateLimitMax', parseInt(e.target.value))}
                      className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none"
                    />
                    <span className="flex items-center text-sm text-slate-400 whitespace-nowrap">req / {settings.rateLimitWindow}s</span>
                  </div>
               </div>
               
               <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">Ban Duration (s)</label>
                  <input 
                    type="number" 
                    value={settings.banDuration}
                    onChange={(e) => handleInputChange('banDuration', parseInt(e.target.value))}
                    className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none"
                  />
               </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">IP Whitelist</label>
              <textarea 
                rows={3}
                value={settings.ipWhitelist}
                onChange={(e) => handleInputChange('ipWhitelist', e.target.value)}
                className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none font-mono text-xs"
              />
              <p className="text-xs text-slate-500">CIDR notation or single IPs. One per line or comma separated.</p>
            </div>
            
            <div className="space-y-2">
               <label className="text-sm font-medium text-slate-300">JWT Token Expiration</label>
               <select 
                  value={settings.jwtExpiration}
                  onChange={(e) => handleInputChange('jwtExpiration', parseInt(e.target.value))}
                  className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none"
                >
                  <option value={3600}>1 Hour</option>
                  <option value={7200}>2 Hours</option>
                  <option value={86400}>24 Hours</option>
                  <option value={604800}>7 Days</option>
                </select>
            </div>
          </div>
        );

      case 'database':
        return (
           <div className="space-y-6 animate-in fade-in duration-300">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                 <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">DB Connection Pool</label>
                    <input 
                       type="number" 
                       value={settings.dbPoolSize}
                       onChange={(e) => handleInputChange('dbPoolSize', parseInt(e.target.value))}
                       className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none"
                    />
                 </div>
                 <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Pool Idle Timeout (ms)</label>
                    <input 
                       type="number" 
                       value={settings.dbIdleTimeout}
                       onChange={(e) => handleInputChange('dbIdleTimeout', parseInt(e.target.value))}
                       className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none"
                    />
                 </div>
                 <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Global Cache TTL (s)</label>
                    <input 
                       type="number" 
                       value={settings.cacheTtl}
                       onChange={(e) => handleInputChange('cacheTtl', parseInt(e.target.value))}
                       className="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:ring-1 focus:ring-primary outline-none"
                    />
                 </div>
                 <div className="flex items-center justify-between p-4 border border-dark-700 rounded-lg bg-dark-900">
                    <div>
                       <div className="text-sm font-medium text-white">Redis Compression</div>
                       <div className="text-xs text-slate-500">Compress values larger than 1KB</div>
                    </div>
                    <button 
                       onClick={() => handleInputChange('redisCompression', !settings.redisCompression)}
                       className={`w-10 h-5 rounded-full transition-colors relative ${settings.redisCompression ? 'bg-primary' : 'bg-dark-700'}`}
                    >
                       <span className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${settings.redisCompression ? 'left-6' : 'left-1'}`}></span>
                    </button>
                 </div>
              </div>
           </div>
        );

      case 'raw':
        return (
          <div className="space-y-4 animate-in fade-in duration-300 h-[500px] flex flex-col">
            <div className="flex-1 bg-dark-950 border border-dark-800 rounded-lg p-4 font-mono text-xs text-slate-300 overflow-auto custom-scrollbar">
              <pre contentEditable suppressContentEditableWarning className="outline-none h-full">
                {JSON.stringify(settings, null, 2)}
              </pre>
            </div>
            <p className="text-xs text-amber-500 flex items-center gap-2">
               <AlertTriangle className="w-3 h-3" />
               Changes made here override all UI settings. Invalid JSON will be rejected.
            </p>
          </div>
        );

      default:
        return (
           <div className="space-y-6 animate-in fade-in duration-300">
              {['enableBetaFeatures', 'enableAuditLog', 'enableWebhooks'].map((flag) => (
                 <div key={flag} className="flex items-center justify-between p-4 border border-dark-800 rounded-xl bg-dark-900 hover:border-dark-700 transition-colors">
                    <div>
                       <h4 className="text-white font-medium capitalize">{flag.replace(/([A-Z])/g, ' $1').trim()}</h4>
                       <p className="text-sm text-slate-500">Toggle the status of this feature flag globally.</p>
                    </div>
                    <button 
                       onClick={() => handleInputChange(flag, !settings[flag as keyof typeof settings])}
                       className={`w-12 h-6 rounded-full transition-colors relative ${settings[flag as keyof typeof settings] ? 'bg-primary' : 'bg-dark-700'}`}
                    >
                       <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${settings[flag as keyof typeof settings] ? 'left-7' : 'left-1'}`}></span>
                    </button>
                 </div>
              ))}
           </div>
        );
    }
  };

  return (
    <div className="animate-in fade-in duration-500 flex flex-col lg:flex-row gap-8 h-[calc(100vh-140px)]">
      {/* Settings Sidebar */}
      <div className="w-full lg:w-64 shrink-0 space-y-2">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
              activeCategory === cat.id 
                ? 'bg-dark-800 text-white border border-dark-700 shadow-lg' 
                : 'text-slate-400 hover:text-white hover:bg-dark-900'
            }`}
          >
            {cat.icon}
            {cat.name}
          </button>
        ))}
      </div>

      {/* Settings Content Area */}
      <div className="flex-1 flex flex-col bg-dark-900 rounded-xl border border-dark-800 shadow-xl overflow-hidden">
        {/* Toolbar */}
        <div className="p-6 border-b border-dark-800 flex justify-between items-center bg-dark-950/30">
          <div>
             <h2 className="text-xl font-bold text-white tracking-tight">{categories.find(c => c.id === activeCategory)?.name}</h2>
             <p className="text-sm text-slate-500 mt-1">Advanced configuration and tuning parameters.</p>
          </div>
          <button 
            onClick={handleSave}
            disabled={isSaving}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm transition-all shadow-lg ${
               isSaving 
               ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 cursor-wait' 
               : 'bg-primary text-dark-950 hover:bg-lime-400 shadow-[0_0_15px_rgba(138,206,0,0.3)]'
            }`}
          >
            {isSaving ? (
               <>Saving...</>
            ) : (
               <><Save className="w-4 h-4" /> Save Changes</>
            )}
          </button>
        </div>

        {/* Scrollable Form Area */}
        <div className="flex-1 overflow-y-auto p-6 custom-scrollbar relative">
           {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
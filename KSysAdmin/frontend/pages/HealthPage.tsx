import React from 'react';
import ResourceChart from '../components/charts/ResourceChart';
import { generateResourceData, mockDetailedHealth, mockHealthLogs } from '../utils/mockData';

const HealthPage: React.FC = () => {
  const resourceData = generateResourceData();

  return (
    <div className="animate-in fade-in duration-500 space-y-8">
       {/* System Status Grid */}
       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {mockDetailedHealth.map((item) => (
             <div key={item.name} className="bg-dark-900 border border-dark-800 rounded-xl p-4 flex flex-col hover:border-primary/20 transition-colors shadow-lg">
                <div className="flex justify-between items-start mb-3">
                   <div className="font-semibold text-white text-sm">{item.name}</div>
                   <div className={`w-2.5 h-2.5 rounded-full ${item.status === 'healthy' ? 'bg-primary shadow-[0_0_8px_rgba(138,206,0,0.6)]' : 'bg-red-500'}`}></div>
                </div>
                <div className="flex-1 space-y-1">
                   <div className="flex justify-between text-xs text-slate-400">
                      <span>Type</span>
                      <span className="text-slate-200">{item.type}</span>
                   </div>
                   <div className="flex justify-between text-xs text-slate-400">
                      <span>Uptime</span>
                      <span className="text-slate-200">{item.uptime}</span>
                   </div>
                   <div className="flex justify-between text-xs text-slate-400">
                      <span>Latency</span>
                      <span className="text-slate-200">{item.latency}ms</span>
                   </div>
                   <div className="flex justify-between text-xs text-slate-400">
                      <span>Version</span>
                      <span className="text-slate-200">{item.version}</span>
                   </div>
                </div>
             </div>
          ))}
       </div>

       {/* Resource Usage & Logs */}
       <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-dark-900 rounded-xl border border-dark-800 p-6 shadow-lg">
             <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-white">Resource Usage</h3>
                <div className="flex gap-4">
                   <span className="flex items-center gap-2 text-xs text-slate-400"><span className="w-2 h-2 rounded-full bg-primary"></span> CPU</span>
                   <span className="flex items-center gap-2 text-xs text-slate-400"><span className="w-2 h-2 rounded-full bg-cyan-400"></span> Memory</span>
                </div>
             </div>
             <ResourceChart data={resourceData} />
          </div>

          <div className="lg:col-span-1 bg-dark-900 rounded-xl border border-dark-800 flex flex-col shadow-lg overflow-hidden">
             <div className="p-4 border-b border-dark-800 bg-dark-950/50">
                <h3 className="text-sm font-semibold text-white font-mono">System Logs</h3>
             </div>
             <div className="flex-1 p-4 overflow-y-auto max-h-[300px] font-mono text-xs space-y-3 custom-scrollbar">
                {mockHealthLogs.map((log) => (
                   <div key={log.id} className="flex gap-3">
                      <span className="text-slate-500 shrink-0">{log.time}</span>
                      <span className={`shrink-0 font-bold w-12 ${
                         log.level === 'INFO' ? 'text-primary' : 
                         log.level === 'WARN' ? 'text-amber-400' : 'text-red-400'
                      }`}>[{log.level}]</span>
                      <span className="text-slate-300">{log.message}</span>
                   </div>
                ))}
             </div>
          </div>
       </div>
    </div>
  );
};

export default HealthPage;
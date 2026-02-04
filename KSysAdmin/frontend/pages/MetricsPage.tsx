import React, { useState } from 'react';
import MetricsChart from '../components/charts/MetricsChart';
import DonutChart from '../components/charts/DonutChart';
import TopEndpoints from '../components/TopEndpoints';
import LogTable from '../components/LogTable';
import { TimeSeriesPoint } from '../types';
import { mockStatusCodeData, mockTopEndpoints, generateAccessLogs } from '../utils/mockData';

interface MetricsPageProps {
  data: TimeSeriesPoint[];
}

const MetricsPage: React.FC<MetricsPageProps> = ({ data }) => {
  // Generate more logs to demonstrate pagination
  const [logs] = useState(() => generateAccessLogs(150));

  return (
    <div className="animate-in fade-in duration-500 space-y-8">
       {/* Header Stats */}
       <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-dark-900 p-6 rounded-xl border border-dark-800 shadow-lg">
             <div className="text-slate-400 text-sm mb-1 font-medium">Peak Request Rate</div>
             <div className="flex items-end gap-2">
                <div className="text-2xl font-bold text-white tracking-tight">4,203</div>
                <div className="text-xs text-slate-500 mb-1.5">req/sec</div>
             </div>
             <div className="mt-3 text-xs font-medium text-primary bg-primary/10 inline-block px-2 py-0.5 rounded border border-primary/20">+15% from yesterday</div>
          </div>
          <div className="bg-dark-900 p-6 rounded-xl border border-dark-800 shadow-lg">
             <div className="text-slate-400 text-sm mb-1 font-medium">Total Errors (24h)</div>
             <div className="flex items-end gap-2">
                <div className="text-2xl font-bold text-white tracking-tight">1,204</div>
             </div>
             <div className="mt-3 text-xs font-medium text-emerald-400 bg-emerald-500/10 inline-block px-2 py-0.5 rounded border border-emerald-500/20">-5% decrease</div>
          </div>
          <div className="bg-dark-900 p-6 rounded-xl border border-dark-800 shadow-lg">
             <div className="text-slate-400 text-sm mb-1 font-medium">Avg Process Time</div>
             <div className="flex items-end gap-2">
                <div className="text-2xl font-bold text-white tracking-tight">45ms</div>
             </div>
             <div className="mt-3 text-xs font-medium text-slate-400 bg-slate-800 inline-block px-2 py-0.5 rounded border border-slate-700">Stable vs last week</div>
          </div>
       </div>

       {/* Charts Grid */}
       <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-dark-900 rounded-xl border border-dark-800 p-6 shadow-lg">
             <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-white tracking-tight">Request Volume History</h3>
                <select className="bg-dark-950 border border-dark-800 text-xs text-slate-300 rounded px-2 py-1 outline-none">
                   <option>Requests</option>
                   <option>Bandwidth</option>
                </select>
             </div>
             <MetricsChart data={data} />
          </div>
          <div className="lg:col-span-1 bg-dark-900 rounded-xl border border-dark-800 p-6 shadow-lg">
             <h3 className="text-lg font-bold text-white tracking-tight mb-6">Response Codes</h3>
             <DonutChart data={mockStatusCodeData} />
             <div className="mt-6 space-y-3">
                {mockStatusCodeData.map((item) => (
                   <div key={item.name} className="flex justify-between items-center text-sm border-b border-dark-800 pb-2 last:border-0 hover:bg-dark-800/30 px-2 rounded transition-colors">
                      <div className="flex items-center gap-2.5 text-slate-300">
                         <span className="w-2.5 h-2.5 rounded-sm shadow-sm" style={{backgroundColor: item.color}}></span>
                         {item.name}
                      </div>
                      <span className="font-mono text-slate-400 font-medium">{item.value.toLocaleString()}</span>
                   </div>
                ))}
             </div>
          </div>
       </div>

       {/* Top Endpoints & Logs Grid */}
       <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[600px]">
          <div className="lg:col-span-1 h-full">
             <TopEndpoints data={mockTopEndpoints} />
          </div>
          <div className="lg:col-span-2 h-full">
             <LogTable logs={logs} />
          </div>
       </div>
    </div>
  );
};

export default MetricsPage;
import React from 'react';
import { SecurityEvent } from '../types';
import { ShieldAlert, AlertTriangle } from '../components/Icons';

interface SecurityPageProps {
  events: SecurityEvent[];
}

const SecurityPage: React.FC<SecurityPageProps> = ({ events }) => {
  return (
    <div className="animate-in fade-in duration-500 space-y-8">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-red-500/10 border border-red-500/20 p-6 rounded-xl flex items-center justify-between">
           <div>
              <div className="text-red-400 text-sm font-medium">Active Threats</div>
              <div className="text-3xl font-bold text-white mt-1">{events.length}</div>
           </div>
           <ShieldAlert className="w-10 h-10 text-red-500" />
        </div>
        <div className="bg-dark-900 border border-dark-800 p-6 rounded-xl">
           <div className="text-slate-400 text-sm font-medium">Failed Logins (24h)</div>
           <div className="text-3xl font-bold text-white mt-1">482</div>
           <div className="text-xs text-amber-500 mt-2">Spike detected at 04:00 AM</div>
        </div>
        <div className="bg-dark-900 border border-dark-800 p-6 rounded-xl">
           <div className="text-slate-400 text-sm font-medium">Banned IPs</div>
           <div className="text-3xl font-bold text-white mt-1">12</div>
           <div className="text-xs text-slate-500 mt-2">Last ban: 10 mins ago</div>
        </div>
      </div>

      {/* Detailed Table */}
      <div className="bg-dark-900 rounded-xl border border-dark-800 shadow-lg overflow-hidden">
        <div className="p-6 border-b border-dark-800 flex justify-between items-center">
           <h3 className="text-lg font-semibold text-white">Recent Security Violations</h3>
           <button className="text-xs bg-dark-800 hover:bg-dark-700 text-slate-300 px-3 py-1.5 rounded transition-colors">Export Log</button>
        </div>
        <div className="overflow-x-auto">
           <table className="w-full text-left text-sm">
              <thead className="bg-dark-950 text-slate-400">
                 <tr>
                    <th className="px-6 py-4 font-medium">Timestamp</th>
                    <th className="px-6 py-4 font-medium">Event Type</th>
                    <th className="px-6 py-4 font-medium">Source</th>
                    <th className="px-6 py-4 font-medium">Details</th>
                    <th className="px-6 py-4 font-medium text-right">Status</th>
                 </tr>
              </thead>
              <tbody className="divide-y divide-dark-800">
                 {events.map((event) => (
                    <tr key={event.id} className="hover:bg-dark-800/50 transition-colors">
                       <td className="px-6 py-4 text-slate-400 font-mono text-xs">
                          {new Date(event.timestamp).toLocaleString()}
                       </td>
                       <td className="px-6 py-4">
                          <span className={`inline-flex items-center gap-2 font-medium ${
                             event.severity === 'high' ? 'text-red-400' : 
                             event.severity === 'medium' ? 'text-amber-400' : 'text-slate-300'
                          }`}>
                             {event.severity === 'high' && <AlertTriangle className="w-3 h-3" />}
                             {event.type.replace('_', ' ')}
                          </span>
                       </td>
                       <td className="px-6 py-4 font-mono text-slate-400">{event.sourceIp}</td>
                       <td className="px-6 py-4 text-slate-300 max-w-xs truncate">{event.details}</td>
                       <td className="px-6 py-4 text-right">
                          <span className="inline-flex items-center px-2 py-1 rounded bg-dark-800 text-xs font-medium text-slate-400 border border-dark-700">
                             Blocked
                          </span>
                       </td>
                    </tr>
                 ))}
                 {events.length === 0 && (
                    <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-500">No recent violations found.</td></tr>
                 )}
              </tbody>
           </table>
        </div>
      </div>
    </div>
  );
};

export default SecurityPage;
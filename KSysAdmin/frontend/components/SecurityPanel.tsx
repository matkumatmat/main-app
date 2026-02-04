import React from 'react';
import { ShieldAlert } from './Icons';
import { SecurityEvent } from '../types';

interface SecurityPanelProps {
  events: SecurityEvent[];
}

const SecurityPanel: React.FC<SecurityPanelProps> = ({ events }) => {
  return (
    <div className="bg-dark-900 rounded-xl border border-dark-800 shadow-lg overflow-hidden h-full">
      <div className="p-5 border-b border-dark-800 flex items-center justify-between">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <ShieldAlert className="text-primary w-5 h-5" />
          Security Alerts
        </h3>
        <span className="text-xs font-bold bg-red-500/10 text-red-500 border border-red-500/20 px-2.5 py-1 rounded-full">
          {events.length} Active
        </span>
      </div>
      <div className="overflow-y-auto max-h-[300px] custom-scrollbar">
        {events.length === 0 ? (
          <div className="p-8 text-center text-slate-500">No active threats detected.</div>
        ) : (
          <table className="w-full text-sm text-left">
            <thead className="bg-dark-950/50 text-slate-400 font-medium">
              <tr>
                <th className="px-5 py-3">Type</th>
                <th className="px-5 py-3">Source IP</th>
                <th className="px-5 py-3">Time</th>
                <th className="px-5 py-3 text-right">Severity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-800">
              {events.map((event) => (
                <tr key={event.id} className="hover:bg-dark-800 transition-colors">
                  <td className="px-5 py-3">
                    <span className="font-medium text-slate-200">{event.type.replace('_', ' ')}</span>
                    <div className="text-xs text-slate-500 mt-0.5">{event.details}</div>
                  </td>
                  <td className="px-5 py-3 text-slate-400 font-mono tracking-wide">{event.sourceIp}</td>
                  <td className="px-5 py-3 text-slate-500">
                    {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td className="px-5 py-3 text-right">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-bold capitalize border
                      ${event.severity === 'high' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
                        event.severity === 'medium' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 
                        'bg-slate-700/30 text-slate-400 border-slate-700'}`}>
                      {event.severity}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default SecurityPanel;
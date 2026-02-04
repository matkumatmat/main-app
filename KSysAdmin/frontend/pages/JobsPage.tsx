import React, { useState } from 'react';
import { Briefcase, PlayCircle, PauseCircle, StopCircle, RefreshCw, Repeat, CheckCircle, X, Clock, Layers, Activity } from '../components/Icons';
import { mockQueues, mockWorkers, mockJobs } from '../utils/mockData';
import { QueueStats, Job } from '../types';

const JobsPage: React.FC = () => {
  const [queues, setQueues] = useState<QueueStats[]>(mockQueues);
  const [activeTab, setActiveTab] = useState<'active' | 'completed' | 'failed'>('active');

  const totalActive = queues.reduce((acc, q) => acc + q.active, 0);
  const totalWaiting = queues.reduce((acc, q) => acc + q.waiting, 0);
  const totalFailed = queues.reduce((acc, q) => acc + q.failed, 0);

  const filteredJobs = mockJobs.filter(job => {
    if (activeTab === 'active') return job.status === 'active' || job.status === 'waiting';
    if (activeTab === 'completed') return job.status === 'completed';
    if (activeTab === 'failed') return job.status === 'failed';
    return true;
  });

  const toggleQueuePause = (queueName: string) => {
    setQueues(prev => prev.map(q => q.name === queueName ? { ...q, paused: !q.paused } : q));
  };

  const getStatusBadge = (status: Job['status']) => {
    switch(status) {
      case 'active': return <span className="text-xs font-bold text-blue-400 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded uppercase">Active</span>;
      case 'completed': return <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded uppercase">Done</span>;
      case 'failed': return <span className="text-xs font-bold text-red-400 bg-red-500/10 border border-red-500/20 px-2 py-0.5 rounded uppercase">Failed</span>;
      case 'waiting': return <span className="text-xs font-bold text-slate-400 bg-slate-700/30 border border-slate-700 px-2 py-0.5 rounded uppercase">Queued</span>;
      default: return null;
    }
  };

  return (
    <div className="animate-in fade-in duration-500 space-y-8">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-dark-900 border border-dark-800 p-6 rounded-xl shadow-lg flex items-center justify-between">
           <div>
              <div className="text-slate-400 text-sm font-medium mb-1">Active Jobs</div>
              <div className="text-2xl font-bold text-white">{totalActive}</div>
           </div>
           <div className="p-3 bg-blue-500/10 text-blue-400 rounded-lg">
              <Activity className="w-6 h-6" />
           </div>
        </div>
        <div className="bg-dark-900 border border-dark-800 p-6 rounded-xl shadow-lg flex items-center justify-between">
           <div>
              <div className="text-slate-400 text-sm font-medium mb-1">Enqueued</div>
              <div className="text-2xl font-bold text-white">{totalWaiting}</div>
           </div>
           <div className="p-3 bg-slate-800 text-slate-300 rounded-lg">
              <Layers className="w-6 h-6" />
           </div>
        </div>
        <div className="bg-dark-900 border border-dark-800 p-6 rounded-xl shadow-lg flex items-center justify-between">
           <div>
              <div className="text-slate-400 text-sm font-medium mb-1">Failed (24h)</div>
              <div className="text-2xl font-bold text-white">{totalFailed}</div>
           </div>
           <div className="p-3 bg-red-500/10 text-red-400 rounded-lg">
              <X className="w-6 h-6" />
           </div>
        </div>
        <div className="bg-dark-900 border border-dark-800 p-6 rounded-xl shadow-lg flex items-center justify-between">
           <div>
              <div className="text-slate-400 text-sm font-medium mb-1">Workers Online</div>
              <div className="text-2xl font-bold text-white">{mockWorkers.length}</div>
           </div>
           <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg">
              <Briefcase className="w-6 h-6" />
           </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         {/* Main Job List */}
         <div className="lg:col-span-2 bg-dark-900 rounded-xl border border-dark-800 shadow-lg flex flex-col overflow-hidden h-[600px]">
            <div className="p-5 border-b border-dark-800 flex justify-between items-center bg-dark-950/30">
               <div className="flex gap-4">
                  <button 
                     onClick={() => setActiveTab('active')} 
                     className={`text-sm font-medium px-3 py-1.5 rounded-lg transition-colors ${activeTab === 'active' ? 'bg-dark-800 text-white' : 'text-slate-400 hover:text-white'}`}
                  >
                     Active & Queued
                  </button>
                  <button 
                     onClick={() => setActiveTab('completed')} 
                     className={`text-sm font-medium px-3 py-1.5 rounded-lg transition-colors ${activeTab === 'completed' ? 'bg-dark-800 text-white' : 'text-slate-400 hover:text-white'}`}
                  >
                     Completed
                  </button>
                  <button 
                     onClick={() => setActiveTab('failed')} 
                     className={`text-sm font-medium px-3 py-1.5 rounded-lg transition-colors ${activeTab === 'failed' ? 'bg-dark-800 text-white' : 'text-slate-400 hover:text-white'}`}
                  >
                     Failed
                  </button>
               </div>
               <button className="p-2 text-slate-400 hover:text-white bg-dark-800 rounded-lg transition-colors">
                  <RefreshCw className="w-4 h-4" />
               </button>
            </div>
            
            <div className="flex-1 overflow-auto custom-scrollbar">
               <table className="w-full text-left text-sm">
                  <thead className="bg-dark-950 text-slate-500 font-semibold sticky top-0 z-10 border-b border-dark-800">
                     <tr>
                        <th className="px-5 py-3">Job ID</th>
                        <th className="px-5 py-3">Queue</th>
                        <th className="px-5 py-3">Arguments</th>
                        <th className="px-5 py-3">Status</th>
                        <th className="px-5 py-3 text-right">Created</th>
                        {activeTab === 'failed' && <th className="px-5 py-3 text-right">Actions</th>}
                     </tr>
                  </thead>
                  <tbody className="divide-y divide-dark-800">
                     {filteredJobs.map(job => (
                        <tr key={job.id} className="hover:bg-dark-800/50 transition-colors">
                           <td className="px-5 py-3 font-mono text-xs text-slate-300">
                              <div className="font-bold text-white mb-0.5">{job.name}</div>
                              <span className="text-slate-500">{job.id}</span>
                           </td>
                           <td className="px-5 py-3">
                              <span className="text-xs bg-dark-950 px-2 py-1 rounded border border-dark-800 text-slate-400">{job.queue}</span>
                           </td>
                           <td className="px-5 py-3">
                              <code className="text-xs text-amber-100/70 bg-dark-950 px-2 py-1 rounded block max-w-[200px] truncate">
                                 {job.args}
                              </code>
                              {job.error && <div className="text-xs text-red-400 mt-1 max-w-[200px] truncate">{job.error}</div>}
                           </td>
                           <td className="px-5 py-3">
                              {getStatusBadge(job.status)}
                              {job.attempts > 0 && <span className="ml-2 text-xs text-slate-500">Try: {job.attempts}</span>}
                           </td>
                           <td className="px-5 py-3 text-right text-xs text-slate-500">
                              {new Date(job.timestamp).toLocaleTimeString()}
                              {job.duration && <div className="text-slate-400 font-mono mt-0.5">{job.duration}</div>}
                           </td>
                           {activeTab === 'failed' && (
                              <td className="px-5 py-3 text-right">
                                 <button className="text-xs bg-dark-800 hover:bg-dark-700 text-white px-2 py-1 rounded flex items-center gap-1 ml-auto transition-colors">
                                    <Repeat className="w-3 h-3" /> Retry
                                 </button>
                              </td>
                           )}
                        </tr>
                     ))}
                     {filteredJobs.length === 0 && (
                        <tr><td colSpan={6} className="text-center p-8 text-slate-500">No jobs found in this category.</td></tr>
                     )}
                  </tbody>
               </table>
            </div>
         </div>

         {/* Sidebar: Queues & Workers */}
         <div className="space-y-6">
            {/* Queue List */}
            <div className="bg-dark-900 rounded-xl border border-dark-800 shadow-lg p-5">
               <h3 className="font-bold text-white mb-4 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-primary" /> Queues
               </h3>
               <div className="space-y-4">
                  {queues.map(q => (
                     <div key={q.name} className="bg-dark-950/50 p-3 rounded-lg border border-dark-800">
                        <div className="flex justify-between items-center mb-2">
                           <div className="font-medium text-slate-200 text-sm">{q.name}</div>
                           <button 
                              onClick={() => toggleQueuePause(q.name)}
                              className={`p-1 rounded hover:bg-dark-800 transition-colors ${q.paused ? 'text-amber-400' : 'text-slate-500 hover:text-white'}`}
                              title={q.paused ? "Resume Queue" : "Pause Queue"}
                           >
                              {q.paused ? <PlayCircle className="w-4 h-4" /> : <PauseCircle className="w-4 h-4" />}
                           </button>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-center text-xs">
                           <div className="bg-dark-900 rounded p-1">
                              <div className="text-blue-400 font-bold">{q.active}</div>
                              <div className="text-slate-600 text-[10px] uppercase">Act</div>
                           </div>
                           <div className="bg-dark-900 rounded p-1">
                              <div className="text-slate-300 font-bold">{q.waiting}</div>
                              <div className="text-slate-600 text-[10px] uppercase">Wait</div>
                           </div>
                           <div className="bg-dark-900 rounded p-1">
                              <div className="text-red-400 font-bold">{q.failed}</div>
                              <div className="text-slate-600 text-[10px] uppercase">Fail</div>
                           </div>
                        </div>
                     </div>
                  ))}
               </div>
            </div>

            {/* Worker List */}
            <div className="bg-dark-900 rounded-xl border border-dark-800 shadow-lg p-5">
               <h3 className="font-bold text-white mb-4 flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-primary" /> Workers
               </h3>
               <div className="space-y-3">
                  {mockWorkers.map(w => (
                     <div key={w.id} className="flex items-center justify-between text-sm p-2 hover:bg-dark-800/50 rounded transition-colors">
                        <div className="flex items-center gap-2">
                           <div className={`w-2 h-2 rounded-full ${w.status === 'busy' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`}></div>
                           <div>
                              <div className="text-slate-300 font-mono text-xs">{w.id}</div>
                              <div className="text-[10px] text-slate-500">PID: {w.pid}</div>
                           </div>
                        </div>
                        <div className="text-right">
                           <div className="text-xs text-slate-400">{w.cpuUsage}% CPU</div>
                           <div className="text-[10px] text-slate-600">{w.ramUsage}% RAM</div>
                        </div>
                     </div>
                  ))}
               </div>
            </div>
         </div>
      </div>
    </div>
  );
};

export default JobsPage;
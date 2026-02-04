import React from 'react';
import { Deployment } from '../types';
import { Rocket, GitCommit, Check, X, RotateCcw, Clock, Loader, Activity } from '../components/Icons';

interface DeploymentsPageProps {
  deployments: Deployment[];
}

const DeploymentsPage: React.FC<DeploymentsPageProps> = ({ deployments }) => {
  const activeDeployment = deployments.find(d => d.status === 'in_progress');
  const pastDeployments = deployments.filter(d => d.status !== 'in_progress');

  return (
    <div className="animate-in fade-in duration-500 space-y-8">
      {/* Active Deployment Card */}
      <div className="bg-dark-900 rounded-xl border border-dark-800 p-6 shadow-lg relative overflow-hidden group">
        <div className="absolute top-0 left-0 w-full h-1 bg-dark-800">
           {activeDeployment && <div className="h-full bg-primary animate-progress-indeterminate"></div>}
        </div>
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div>
             <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-1">
                <Rocket className={`w-5 h-5 ${activeDeployment ? 'text-primary animate-pulse' : 'text-slate-500'}`} />
                {activeDeployment ? 'Deployment in Progress' : 'No Active Deployments'}
             </h2>
             {activeDeployment ? (
                <div className="text-sm text-slate-400">
                   Deploying <span className="text-white font-medium">{activeDeployment.service}</span> version <span className="font-mono text-primary">{activeDeployment.version}</span>
                </div>
             ) : (
                <div className="text-sm text-slate-500">All systems operational. Ready for new releases.</div>
             )}
          </div>
          
          {activeDeployment && (
             <div className="flex items-center gap-4">
                <div className="text-right">
                   <div className="text-xs text-slate-500 uppercase font-bold tracking-wider">Step 3/5</div>
                   <div className="text-sm text-white">Swapping Containers...</div>
                </div>
                <div className="w-12 h-12 rounded-full border-4 border-dark-800 border-t-primary animate-spin"></div>
             </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* History Column */}
        <div className="lg:col-span-2 space-y-6">
           <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Deployment History</h3>
              <div className="flex gap-2">
                 <select className="bg-dark-950 border border-dark-800 text-slate-300 text-sm rounded-lg px-3 py-1.5 outline-none">
                    <option>All Services</option>
                    <option>Auth Service</option>
                    <option>Payment Service</option>
                 </select>
              </div>
           </div>

           <div className="space-y-4">
              {pastDeployments.map((deploy) => (
                 <div key={deploy.id} className="bg-dark-900 border border-dark-800 rounded-xl p-5 hover:border-primary/20 transition-all flex flex-col sm:flex-row gap-4 sm:items-center">
                    {/* Status Icon */}
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                       deploy.status === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                       deploy.status === 'failed' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                       'bg-slate-800 text-slate-400'
                    }`}>
                       {deploy.status === 'success' ? <Check className="w-5 h-5" /> : <X className="w-5 h-5" />}
                    </div>

                    {/* Details */}
                    <div className="flex-1">
                       <div className="flex items-center gap-2 mb-1">
                          <span className="font-bold text-white text-sm">{deploy.service}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-dark-950 border border-dark-800 text-slate-300">
                             {deploy.version}
                          </span>
                       </div>
                       <div className="text-xs text-slate-400 flex items-center gap-2">
                          <span className="flex items-center gap-1"><GitCommit className="w-3 h-3" /> {deploy.commitHash}</span>
                          <span>•</span>
                          <span>{deploy.message}</span>
                       </div>
                    </div>

                    {/* Meta & Actions */}
                    <div className="flex items-center gap-6 sm:justify-end w-full sm:w-auto mt-2 sm:mt-0 border-t sm:border-t-0 border-dark-800 pt-3 sm:pt-0">
                       <div className="text-right">
                          <div className="text-xs text-slate-500">{new Date(deploy.timestamp).toLocaleDateString()}</div>
                          <div className="text-[10px] text-slate-600 font-medium">by {deploy.author}</div>
                       </div>
                       
                       <div className="text-right min-w-[60px]">
                          <div className="text-xs text-slate-300">{deploy.duration}</div>
                          <div className="text-[10px] text-slate-600">duration</div>
                       </div>

                       <button 
                          title="Rollback to this version"
                          className="p-2 rounded-lg hover:bg-dark-800 text-slate-500 hover:text-white transition-colors"
                        >
                          <RotateCcw className="w-4 h-4" />
                       </button>
                    </div>
                 </div>
              ))}
           </div>
        </div>

        {/* Sidebar Stats */}
        <div className="space-y-6">
           <div className="bg-dark-900 border border-dark-800 rounded-xl p-6 shadow-lg">
              <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                 <Activity className="w-4 h-4 text-primary" /> Pipeline Health
              </h3>
              <div className="space-y-4">
                 <div>
                    <div className="flex justify-between text-xs mb-1">
                       <span className="text-slate-400">Success Rate</span>
                       <span className="text-emerald-400 font-medium">92%</span>
                    </div>
                    <div className="h-1.5 w-full bg-dark-800 rounded-full overflow-hidden">
                       <div className="h-full bg-emerald-500 w-[92%]"></div>
                    </div>
                 </div>
                 <div>
                    <div className="flex justify-between text-xs mb-1">
                       <span className="text-slate-400">Avg Deploy Time</span>
                       <span className="text-slate-200 font-medium">1m 45s</span>
                    </div>
                    <div className="h-1.5 w-full bg-dark-800 rounded-full overflow-hidden">
                       <div className="h-full bg-blue-500 w-[45%]"></div>
                    </div>
                 </div>
              </div>
           </div>

           <div className="bg-dark-900 border border-dark-800 rounded-xl p-6 shadow-lg">
              <h3 className="font-semibold text-white mb-4">Pending Approvals</h3>
              <div className="space-y-3">
                 <div className="bg-dark-950/50 p-3 rounded-lg border border-dark-800 border-l-2 border-l-amber-500">
                    <div className="text-xs font-bold text-slate-200 mb-0.5">Payment Svc v1.5.0</div>
                    <div className="text-[10px] text-slate-500 mb-2">Needs sign-off from QA</div>
                    <div className="flex gap-2">
                       <button className="flex-1 bg-primary/10 hover:bg-primary/20 text-primary text-[10px] font-bold py-1.5 rounded transition-colors">Approve</button>
                       <button className="flex-1 bg-dark-800 hover:bg-dark-700 text-slate-400 text-[10px] font-bold py-1.5 rounded transition-colors">Reject</button>
                    </div>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};

export default DeploymentsPage;
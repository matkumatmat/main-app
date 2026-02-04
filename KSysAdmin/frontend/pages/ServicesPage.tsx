import React from 'react';
import { Microservice } from '../types';
import { Layers, Share2, GitBranch, Box, Activity, ArrowRight, Cpu, Database } from '../components/Icons';
import ServiceTopology from '../components/ServiceTopology';

interface ServicesPageProps {
  services: Microservice[];
}

const ServicesPage: React.FC<ServicesPageProps> = ({ services }) => {
  return (
    <div className="animate-in fade-in duration-500 space-y-8">
      {/* Service Topology Map */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Share2 className="w-5 h-5 text-primary" />
            Service Topology Map
          </h2>
          <div className="text-xs text-slate-400">
            Real-time dependency visualization
          </div>
        </div>
        <ServiceTopology services={services} />
      </div>

      {/* Service Fleet Grid */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Layers className="w-5 h-5 text-primary" />
          Service Fleet Status
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((svc) => (
            <div key={svc.id} className="bg-dark-900 border border-dark-800 rounded-xl p-6 hover:border-primary/20 transition-all shadow-lg group">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-lg ${
                    svc.status === 'healthy' ? 'bg-primary/10 text-primary' : 
                    svc.status === 'degraded' ? 'bg-amber-500/10 text-amber-400' : 'bg-red-500/10 text-red-400'
                  }`}>
                    <Box className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-base">{svc.name}</h3>
                    <div className="text-xs text-slate-400 font-mono">{svc.id}</div>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider border ${
                   svc.status === 'healthy' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                   svc.status === 'degraded' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'
                }`}>
                  {svc.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-dark-950/50 p-2.5 rounded-lg border border-dark-800">
                  <div className="text-[10px] text-slate-500 mb-1 flex items-center gap-1"><GitBranch className="w-3 h-3"/> Version</div>
                  <div className="text-sm font-mono text-slate-200">{svc.version}</div>
                </div>
                <div className="bg-dark-950/50 p-2.5 rounded-lg border border-dark-800">
                  <div className="text-[10px] text-slate-500 mb-1 flex items-center gap-1"><Layers className="w-3 h-3"/> Replicas</div>
                  <div className="text-sm font-mono text-slate-200">{svc.replicas} / {svc.replicas}</div>
                </div>
              </div>

              <div className="space-y-3">
                 <div>
                    <div className="flex justify-between text-xs mb-1">
                       <span className="text-slate-400 flex items-center gap-1"><Cpu className="w-3 h-3" /> CPU Usage</span>
                       <span className={svc.cpuUsage > 70 ? 'text-amber-400' : 'text-slate-300'}>{svc.cpuUsage}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-dark-800 rounded-full overflow-hidden">
                       <div 
                          className={`h-full rounded-full ${svc.cpuUsage > 70 ? 'bg-amber-400' : 'bg-primary'}`} 
                          style={{ width: `${svc.cpuUsage}%` }}
                        ></div>
                    </div>
                 </div>

                 <div>
                    <div className="flex justify-between text-xs mb-1">
                       <span className="text-slate-400 flex items-center gap-1"><Database className="w-3 h-3" /> Mem Usage</span>
                       <span className={svc.memoryUsage > 80 ? 'text-red-400' : 'text-slate-300'}>{svc.memoryUsage}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-dark-800 rounded-full overflow-hidden">
                       <div 
                          className={`h-full rounded-full ${svc.memoryUsage > 80 ? 'bg-red-400' : 'bg-cyan-400'}`} 
                          style={{ width: `${svc.memoryUsage}%` }}
                        ></div>
                    </div>
                 </div>
              </div>

              <div className="mt-4 pt-4 border-t border-dark-800 flex justify-between items-center">
                 <div className="text-xs text-slate-500">
                    Uptime: <span className="text-slate-300">{svc.uptime}</span>
                 </div>
                 <button className="text-xs text-primary hover:text-white flex items-center gap-1 transition-colors">
                    View Logs <ArrowRight className="w-3 h-3" />
                 </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ServicesPage;
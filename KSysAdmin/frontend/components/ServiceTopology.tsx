import React from 'react';
import { Microservice } from '../types';
import { ArrowRight, Database, Globe, Lock, CreditCard, ShieldAlert } from './Icons';

interface ServiceTopologyProps {
  services: Microservice[];
}

const ServiceTopology: React.FC<ServiceTopologyProps> = ({ services }) => {
  // Hardcoded visual layout for the topology map
  // In a real app, you'd use a graph library like react-flow
  
  const getIcon = (id: string) => {
    if (id.includes('db')) return <Database className="w-5 h-5" />;
    if (id.includes('gateway')) return <Globe className="w-5 h-5" />;
    if (id.includes('auth')) return <Lock className="w-5 h-5" />;
    if (id.includes('payment')) return <CreditCard className="w-5 h-5" />;
    return <ShieldAlert className="w-5 h-5" />;
  };

  const getStatusColor = (status: string) => {
    if (status === 'degraded') return 'text-amber-400 border-amber-500/50 shadow-[0_0_15px_rgba(251,191,36,0.2)]';
    if (status === 'down') return 'text-red-400 border-red-500/50 shadow-[0_0_15px_rgba(248,113,113,0.2)]';
    return 'text-primary border-primary/50 shadow-[0_0_15px_rgba(138,206,0,0.2)]';
  };

  return (
    <div className="relative w-full h-[500px] bg-dark-950/50 rounded-xl border border-dark-800 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:20px_20px] opacity-20"></div>
      
      <div className="relative z-10 w-full h-full flex flex-col items-center justify-center p-8">
        {/* Tier 1: Gateway */}
        <div className="mb-16 relative">
          <div className={`w-48 p-4 bg-dark-900 border rounded-xl flex items-center gap-3 ${getStatusColor('healthy')}`}>
            <div className="p-2 bg-dark-800 rounded-lg">
              {getIcon('nginx_gateway')}
            </div>
            <div>
              <div className="text-sm font-bold text-white">API Gateway</div>
              <div className="text-[10px] text-slate-400">nginx_gateway • v1.12.0</div>
            </div>
          </div>
          {/* Connectors */}
          <div className="absolute top-full left-1/2 -translate-x-1/2 h-16 w-px bg-slate-700/50"></div>
          <div className="absolute top-full left-1/2 -translate-x-1/2 mt-16 h-px w-[300px] bg-slate-700/50"></div>
          <div className="absolute top-full left-1/2 -translate-x-1/2 mt-16 h-8 w-px bg-slate-700/50 -ml-[150px]"></div>
          <div className="absolute top-full left-1/2 -translate-x-1/2 mt-16 h-8 w-px bg-slate-700/50 ml-[150px]"></div>
          <div className="absolute top-full left-1/2 -translate-x-1/2 mt-16 h-8 w-px bg-slate-700/50"></div>
        </div>

        {/* Tier 2: Services */}
        <div className="flex gap-8 mb-16 relative">
          {/* Auth */}
          <div className={`w-40 p-3 bg-dark-900 border rounded-xl flex flex-col gap-2 ${getStatusColor('healthy')}`}>
            <div className="flex justify-between items-start">
              <div className="p-1.5 bg-dark-800 rounded-lg">{getIcon('auth')}</div>
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></div>
                <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse delay-75"></div>
              </div>
            </div>
            <div>
              <div className="text-xs font-bold text-white">Auth Service</div>
              <div className="text-[10px] text-slate-400">25% CPU</div>
            </div>
            {/* Connection to DB */}
            <div className="absolute top-full left-20 h-16 w-px bg-slate-700/50 transform translate-x-4"></div>
          </div>

          {/* Payment */}
          <div className={`w-40 p-3 bg-dark-900 border rounded-xl flex flex-col gap-2 ${getStatusColor('degraded')}`}>
            <div className="flex justify-between items-start">
              <div className="p-1.5 bg-dark-800 rounded-lg">{getIcon('payment')}</div>
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></div>
              </div>
            </div>
            <div>
              <div className="text-xs font-bold text-white">Payment Svc</div>
              <div className="text-[10px] text-amber-400">High Latency</div>
            </div>
             {/* Connection to DB */}
             <div className="absolute top-full left-1/2 h-16 w-px bg-slate-700/50"></div>
          </div>

          {/* Admin */}
          <div className={`w-40 p-3 bg-dark-900 border rounded-xl flex flex-col gap-2 ${getStatusColor('healthy')}`}>
             <div className="flex justify-between items-start">
              <div className="p-1.5 bg-dark-800 rounded-lg">{getIcon('admin')}</div>
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-primary"></div>
              </div>
            </div>
            <div>
              <div className="text-xs font-bold text-white">Admin Svc</div>
              <div className="text-[10px] text-slate-400">Idle</div>
            </div>
             {/* Connection to DB */}
             <div className="absolute top-full right-20 h-16 w-px bg-slate-700/50 transform -translate-x-4"></div>
          </div>
        </div>

        {/* Tier 3: Data */}
        <div className="flex gap-16 relative">
          <div className={`w-48 p-3 bg-dark-900 border rounded-xl flex items-center gap-3 ${getStatusColor('healthy')}`}>
            <div className="p-2 bg-dark-800 rounded-lg">
              <Database className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <div className="text-xs font-bold text-white">Redis Cluster</div>
              <div className="text-[10px] text-slate-400">Cache Hit: 94%</div>
            </div>
          </div>

          <div className={`w-48 p-3 bg-dark-900 border rounded-xl flex items-center gap-3 ${getStatusColor('healthy')}`}>
             <div className="p-2 bg-dark-800 rounded-lg">
              <Database className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <div className="text-xs font-bold text-white">PostgreSQL Primary</div>
              <div className="text-[10px] text-slate-400">IOPS: 4.2k</div>
            </div>
          </div>
        </div>

        {/* Legend/Key overlay */}
        <div className="absolute bottom-4 right-4 bg-dark-900/90 border border-dark-800 p-3 rounded-lg backdrop-blur-sm text-[10px]">
           <div className="flex items-center gap-2 mb-1">
              <span className="w-2 h-2 rounded-full bg-primary"></span> Healthy
           </div>
           <div className="flex items-center gap-2 mb-1">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span> Degraded
           </div>
           <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-slate-600"></span> Connector
           </div>
        </div>
      </div>
    </div>
  );
};

export default ServiceTopology;
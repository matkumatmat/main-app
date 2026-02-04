import React from 'react';
import TerminalWindow from '../components/TerminalWindow';
import { Terminal, Command, Zap } from '../components/Icons';

const ConsolePage: React.FC = () => {
  return (
    <div className="animate-in fade-in duration-500 h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Command className="w-5 h-5 text-primary" />
          Intelligent Command Center
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Direct CLI access to KSysAdmin kernel and microservices fleet.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1">
         {/* Sidebar for Quick Actions */}
         <div className="hidden lg:flex flex-col gap-4">
            <div className="bg-dark-900 border border-dark-800 rounded-xl p-4 shadow-lg">
               <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Quick Scripts</h3>
               <div className="space-y-2">
                  <button className="w-full text-left px-3 py-2 text-sm text-slate-300 hover:bg-dark-800 rounded-lg transition-colors flex items-center gap-2 group">
                     <Zap className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
                     Restart Auth Svc
                  </button>
                  <button className="w-full text-left px-3 py-2 text-sm text-slate-300 hover:bg-dark-800 rounded-lg transition-colors flex items-center gap-2 group">
                     <Zap className="w-4 h-4 text-primary group-hover:scale-110 transition-transform" />
                     Flush Redis
                  </button>
                  <button className="w-full text-left px-3 py-2 text-sm text-slate-300 hover:bg-dark-800 rounded-lg transition-colors flex items-center gap-2 group">
                     <Zap className="w-4 h-4 text-red-400 group-hover:scale-110 transition-transform" />
                     Emergency Stop
                  </button>
               </div>
            </div>

            <div className="bg-dark-900 border border-dark-800 rounded-xl p-4 shadow-lg flex-1">
               <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Active Sessions</h3>
               <div className="space-y-3">
                  <div className="flex items-center gap-3 p-2 bg-dark-800/50 rounded-lg border border-dark-700/50">
                     <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                     <div className="text-xs">
                        <div className="text-white font-mono">admin@tty1</div>
                        <div className="text-slate-500">192.168.1.5 • 2m ago</div>
                     </div>
                  </div>
               </div>
            </div>
         </div>

         {/* Main Terminal */}
         <div className="lg:col-span-3">
            <TerminalWindow />
            <div className="mt-4 flex gap-4 text-xs text-slate-500 font-mono">
               <span><span className="text-white font-bold">Ctrl+C</span> to cancel</span>
               <span><span className="text-white font-bold">Ctrl+L</span> to clear</span>
               <span><span className="text-white font-bold">Up/Down</span> history</span>
            </div>
         </div>
      </div>
    </div>
  );
};

export default ConsolePage;
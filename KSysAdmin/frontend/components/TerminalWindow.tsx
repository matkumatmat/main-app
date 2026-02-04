import React, { useState, useRef, useEffect } from 'react';
import { Microservice, SystemHealth } from '../types';
import { mockMicroservices, mockHealth } from '../utils/mockData';

interface TerminalWindowProps {
  initialCommand?: string;
}

interface HistoryItem {
  id: string;
  type: 'command' | 'output' | 'error';
  content: React.ReactNode;
}

const TerminalWindow: React.FC<TerminalWindowProps> = ({ initialCommand = '' }) => {
  const [history, setHistory] = useState<HistoryItem[]>([
    { id: 'init-1', type: 'output', content: 'KSysAdmin Command Center v2.4.1' },
    { id: 'init-2', type: 'output', content: 'Type "help" for available commands.' },
    { id: 'init-3', type: 'output', content: '---------------------------------' },
  ]);
  const [input, setInput] = useState(initialCommand);
  const [isProcessing, setIsProcessing] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  // Focus input on click
  const handleContainerClick = () => {
    inputRef.current?.focus();
  };

  const executeCommand = async (cmd: string) => {
    const trimmedCmd = cmd.trim();
    if (!trimmedCmd) return;

    // Add command to history
    setHistory(prev => [...prev, { id: Date.now().toString(), type: 'command', content: trimmedCmd }]);
    setIsProcessing(true);
    setInput('');

    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));

    const parts = trimmedCmd.split(' ');
    const command = parts[0].toLowerCase();
    const args = parts.slice(1);

    let output: React.ReactNode = '';
    let type: 'output' | 'error' = 'output';

    switch (command) {
      case 'help':
        output = (
          <div className="space-y-1 text-slate-300">
            <div className="grid grid-cols-[120px_1fr] gap-4">
               <span className="text-primary font-bold">status</span>
               <span>Show system health summary</span>
            </div>
            <div className="grid grid-cols-[120px_1fr] gap-4">
               <span className="text-primary font-bold">services</span>
               <span>List all microservices</span>
            </div>
            <div className="grid grid-cols-[120px_1fr] gap-4">
               <span className="text-primary font-bold">inspect</span>
               <span>Show detailed JSON of a service [id]</span>
            </div>
             <div className="grid grid-cols-[120px_1fr] gap-4">
               <span className="text-primary font-bold">logs</span>
               <span>Fetch last logs for a service [id]</span>
            </div>
            <div className="grid grid-cols-[120px_1fr] gap-4">
               <span className="text-primary font-bold">restart</span>
               <span>Simulate a service restart [id]</span>
            </div>
            <div className="grid grid-cols-[120px_1fr] gap-4">
               <span className="text-primary font-bold">whoami</span>
               <span>Display current user context</span>
            </div>
            <div className="grid grid-cols-[120px_1fr] gap-4">
               <span className="text-primary font-bold">clear</span>
               <span>Clear terminal history</span>
            </div>
          </div>
        );
        break;

      case 'clear':
        setHistory([]);
        setIsProcessing(false);
        return;

      case 'whoami':
        output = 'admin@ksysadmin (Role: SuperAdmin)';
        break;

      case 'status':
        output = (
           <div className="space-y-1">
              <div>System Status: <span className="text-emerald-400">OPERATIONAL</span></div>
              <div>Database Latency: {mockHealth.database.latency}ms</div>
              <div>Redis Latency: {mockHealth.redis.latency}ms</div>
              <div>Last Updated: {mockHealth.lastUpdated}</div>
           </div>
        );
        break;

      case 'services':
         output = (
            <table className="w-full max-w-lg text-left">
               <thead>
                  <tr className="text-slate-500 border-b border-slate-700">
                     <th className="pb-1">ID</th>
                     <th className="pb-1">Name</th>
                     <th className="pb-1">Status</th>
                  </tr>
               </thead>
               <tbody>
                  {mockMicroservices.map(svc => (
                     <tr key={svc.id}>
                        <td className="py-0.5 text-primary">{svc.id}</td>
                        <td className="py-0.5">{svc.name}</td>
                        <td className={`py-0.5 ${svc.status === 'healthy' ? 'text-emerald-400' : svc.status === 'degraded' ? 'text-amber-400' : 'text-red-400'}`}>{svc.status}</td>
                     </tr>
                  ))}
               </tbody>
            </table>
         );
         break;

      case 'inspect':
         if (!args[0]) {
            type = 'error';
            output = 'Usage: inspect <service_id>';
         } else {
            const svc = mockMicroservices.find(s => s.id === args[0]);
            if (svc) {
               output = <pre className="text-xs text-amber-100">{JSON.stringify(svc, null, 2)}</pre>;
            } else {
               type = 'error';
               output = `Service '${args[0]}' not found.`;
            }
         }
         break;

      case 'restart':
         if (!args[0]) {
             type = 'error';
             output = 'Usage: restart <service_id>';
         } else {
             const svc = mockMicroservices.find(s => s.id === args[0]);
             if (svc) {
                // Simulate progressive output
                setHistory(prev => [...prev, { id: Date.now().toString(), type: 'output', content: `Sending SIGTERM to ${args[0]}...` }]);
                await new Promise(r => setTimeout(r, 800));
                setHistory(prev => [...prev, { id: Date.now().toString(), type: 'output', content: `Waiting for pods to terminate...` }]);
                await new Promise(r => setTimeout(r, 1200));
                setHistory(prev => [...prev, { id: Date.now().toString(), type: 'output', content: `Starting new replicas (0/${svc.replicas})...` }]);
                await new Promise(r => setTimeout(r, 800));
                output = <span className="text-emerald-400">Successfully restarted {args[0]}. New uptime: 0s.</span>;
             } else {
                type = 'error';
                output = `Service '${args[0]}' not found.`;
             }
         }
         break;
      
      case 'logs':
         if (!args[0]) {
             type = 'error';
             output = 'Usage: logs <service_id>';
         } else {
             const svc = mockMicroservices.find(s => s.id === args[0]);
             if (svc) {
                 output = (
                    <div className="space-y-0.5 text-xs text-slate-400">
                       <div className="text-slate-500">Fetching last 5 log lines for {args[0]}...</div>
                       <div>[2024-03-10T14:20:01Z] [INFO] Request received method=GET path=/health</div>
                       <div>[2024-03-10T14:20:05Z] [INFO] Processing payment batch_id=99281</div>
                       <div>[2024-03-10T14:20:12Z] [WARN] Connection pool utilization &gt; 80%</div>
                       <div>[2024-03-10T14:20:15Z] [INFO] Database query executed duration=45ms</div>
                       <div>[2024-03-10T14:20:22Z] [INFO] Health check passed</div>
                    </div>
                 );
             } else {
                type = 'error';
                output = `Service '${args[0]}' not found.`;
             }
         }
         break;

      default:
        type = 'error';
        output = `Command not found: ${command}. Type "help" for assistance.`;
    }

    setHistory(prev => [...prev, { id: Date.now().toString(), type, content: output }]);
    setIsProcessing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      executeCommand(input);
    }
  };

  return (
    <div 
      className="bg-[#0c0c0c] rounded-xl border border-dark-800 shadow-2xl overflow-hidden flex flex-col h-[600px] font-mono text-sm"
      onClick={handleContainerClick}
    >
      <div className="bg-dark-900 border-b border-dark-800 p-2 flex items-center justify-between px-4 select-none">
        <div className="flex items-center gap-2">
           <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-amber-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-emerald-500/80"></div>
           </div>
           <span className="text-xs text-slate-400 ml-3">admin@ksysadmin: ~</span>
        </div>
        <div className="text-xs text-slate-600">bash</div>
      </div>

      <div 
         ref={scrollRef}
         className="flex-1 p-4 overflow-y-auto custom-scrollbar text-slate-200 space-y-2"
      >
         {history.map((item) => (
            <div key={item.id} className={`${item.type === 'error' ? 'text-red-400' : ''}`}>
               {item.type === 'command' && (
                  <div className="flex items-center gap-2 text-slate-400 mb-1">
                     <span className="text-emerald-500 font-bold">➜</span>
                     <span className="text-blue-400">~</span>
                     <span className="text-white">{item.content}</span>
                  </div>
               )}
               {item.type !== 'command' && (
                  <div className="ml-5">{item.content}</div>
               )}
            </div>
         ))}
         
         <div className="flex items-center gap-2 mt-2">
            <span className="text-emerald-500 font-bold">➜</span>
            <span className="text-blue-400">~</span>
            <div className="relative flex-1">
               <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={isProcessing}
                  autoFocus
                  className="w-full bg-transparent border-none outline-none text-white caret-transparent"
                  autoComplete="off"
                  spellCheck="false"
               />
               {/* Custom blinking cursor to look cooler */}
               {!isProcessing && (
                  <div 
                     className="absolute top-0 bottom-0 w-2.5 bg-slate-400/50 animate-pulse pointer-events-none"
                     style={{ left: `${input.length * 8.5}px` }} 
                  ></div>
               )}
            </div>
         </div>
      </div>
    </div>
  );
};

export default TerminalWindow;
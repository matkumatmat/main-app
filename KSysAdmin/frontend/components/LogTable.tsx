import React, { useState, useEffect } from 'react';
import { AccessLog } from '../types';
import { Search, Terminal, ChevronLeft, ChevronRight } from './Icons';

interface LogTableProps {
  logs: AccessLog[];
}

const LogTable: React.FC<LogTableProps> = ({ logs }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  
  const filteredLogs = logs.filter(log => 
    log.request_id.includes(searchTerm) || 
    log.url.includes(searchTerm) || 
    log.remote_ip.includes(searchTerm) ||
    String(log.status).includes(searchTerm)
  );

  const totalPages = Math.ceil(filteredLogs.length / itemsPerPage);
  
  // Reset to first page when search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  const startIndex = (currentPage - 1) * itemsPerPage;
  const currentLogs = filteredLogs.slice(startIndex, startIndex + itemsPerPage);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  const getStatusColor = (status: number) => {
    if (status >= 500) return 'text-red-500 bg-red-500/10 border-red-500/20';
    if (status >= 400) return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
    return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
  };

  const formatLatency = (val: number | string) => {
    const num = Number(val);
    const ms = (num * 1000).toFixed(1);
    const color = num > 0.1 ? 'text-amber-400' : 'text-slate-400';
    return <span className={`${color} font-mono`}>{ms}ms</span>;
  };

  return (
    <div className="bg-dark-900 rounded-xl border border-dark-800 shadow-lg flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="p-5 border-b border-dark-800 flex flex-col sm:flex-row justify-between gap-4 bg-dark-950/30">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
            <Terminal className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-bold text-white tracking-tight">Live Traffic Inspector</h3>
            <p className="text-xs text-slate-500 mt-0.5">Real-time access logs & latency metrics</p>
          </div>
        </div>
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input 
            type="text" 
            placeholder="Search req ID, IP, URL..." 
            className="w-full bg-dark-900 border border-dark-700 text-white pl-10 pr-4 py-2 rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary/50 outline-none transition-all placeholder:text-slate-600"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>
      
      {/* Table Content */}
      <div className="flex-1 overflow-x-auto custom-scrollbar">
        <table className="w-full text-left text-xs">
          <thead className="bg-dark-950/50 text-slate-500 font-semibold border-b border-dark-800 sticky top-0 z-10 backdrop-blur-sm">
            <tr>
              <th className="px-5 py-3.5 whitespace-nowrap">Time</th>
              <th className="px-5 py-3.5">Status</th>
              <th className="px-5 py-3.5 w-1/3">Method / URL</th>
              <th className="px-5 py-3.5">Service</th>
              <th className="px-5 py-3.5 text-right">Proxy Latency</th>
              <th className="px-5 py-3.5 text-right">App Latency</th>
              <th className="px-5 py-3.5 text-right">Client IP</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-800/50">
            {currentLogs.map((log) => (
              <tr key={log.request_id} className="hover:bg-dark-800/40 transition-colors group">
                <td className="px-5 py-3 text-slate-400 whitespace-nowrap font-mono">
                  {new Date(log.timestamp).toLocaleTimeString([], {hour12: false, hour:'2-digit', minute:'2-digit', second:'2-digit'})}
                </td>
                <td className="px-5 py-3">
                  <span className={`px-2 py-0.5 rounded-md border text-[10px] font-bold tracking-wide ${getStatusColor(log.status)}`}>
                    {log.status}
                  </span>
                </td>
                <td className="px-5 py-3">
                   <div className="flex flex-col gap-0.5">
                      <div className="flex items-center gap-2">
                         <span className={`font-bold uppercase tracking-wider text-[10px] w-10 ${log.method === 'GET' ? 'text-blue-400' : log.method === 'POST' ? 'text-emerald-400' : log.method === 'DELETE' ? 'text-red-400' : 'text-amber-400'}`}>
                           {log.method}
                         </span>
                         <span className="text-slate-300 truncate max-w-[240px] font-medium" title={log.url}>{log.url}</span>
                      </div>
                      <div className="text-[10px] text-slate-600 font-mono truncate max-w-[200px] select-all group-hover:text-slate-500 transition-colors">
                        {log.request_id}
                      </div>
                   </div>
                </td>
                <td className="px-5 py-3">
                   <span className="text-slate-400 text-[11px] bg-dark-950 px-2 py-1 rounded border border-dark-800">
                     {log.service}
                   </span>
                </td>
                <td className="px-5 py-3 text-right">
                   {formatLatency(log.nginx_latency_s)}
                </td>
                <td className="px-5 py-3 text-right">
                   {formatLatency(log.backend_latency_s)}
                </td>
                <td className="px-5 py-3 text-right text-slate-500 font-mono">
                   {log.remote_ip}
                </td>
              </tr>
            ))}
            {filteredLogs.length === 0 && (
               <tr>
                 <td colSpan={7} className="p-12 text-center text-slate-500 italic">
                   No logs found matching "{searchTerm}"
                 </td>
               </tr>
            )}
            {/* Fill empty rows to maintain height if needed, or leave dynamic */}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="p-4 border-t border-dark-800 flex flex-col sm:flex-row items-center justify-between gap-4 bg-dark-950/30">
        <span className="text-xs text-slate-500">
          Showing <span className="text-slate-300 font-medium">{filteredLogs.length > 0 ? startIndex + 1 : 0}</span> to <span className="text-slate-300 font-medium">{Math.min(startIndex + itemsPerPage, filteredLogs.length)}</span> of <span className="text-slate-300 font-medium">{filteredLogs.length}</span> entries
        </span>
        
        <div className="flex items-center gap-2">
          <button 
            onClick={() => handlePageChange(currentPage - 1)} 
            disabled={currentPage === 1}
            className="p-1.5 rounded-lg border border-dark-700 text-slate-400 hover:text-white hover:bg-dark-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          
          <div className="flex items-center gap-1">
             {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                // Simple logic to show window of pages, centered around current
                let pageNum = i + 1;
                if (totalPages > 5) {
                   if (currentPage > 3) pageNum = currentPage - 2 + i;
                   if (pageNum > totalPages) pageNum = totalPages - 4 + i;
                }
                
                return (
                  <button
                    key={pageNum}
                    onClick={() => handlePageChange(pageNum)}
                    className={`w-7 h-7 rounded-lg text-xs font-medium border transition-colors ${
                      currentPage === pageNum 
                        ? 'bg-primary/10 border-primary/30 text-primary' 
                        : 'bg-transparent border-transparent text-slate-500 hover:text-slate-300 hover:bg-dark-800'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
             })}
          </div>

          <button 
            onClick={() => handlePageChange(currentPage + 1)} 
            disabled={currentPage === totalPages || totalPages === 0}
            className="p-1.5 rounded-lg border border-dark-700 text-slate-400 hover:text-white hover:bg-dark-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default LogTable;
import React, { useState } from 'react';
import { Database, Table, Key, Code, Search, RefreshCw, Filter, Trash2, Play, AlertTriangle } from '../components/Icons';
import { mockDbTables, mockRedisKeys } from '../utils/mockData';
import { DbTable, RedisKey } from '../types';

const DatabasePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'postgres' | 'redis'>('postgres');
  const [selectedTable, setSelectedTable] = useState<DbTable | null>(mockDbTables[0]);
  const [selectedKey, setSelectedKey] = useState<RedisKey | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sqlQuery, setSqlQuery] = useState('SELECT * FROM users LIMIT 10;');
  const [viewMode, setViewMode] = useState<'browse' | 'query'>('browse');

  // Postgres Logic
  const filteredTables = mockDbTables.filter(t => t.name.toLowerCase().includes(searchQuery.toLowerCase()));

  // Redis Logic
  const filteredKeys = mockRedisKeys.filter(k => k.key.toLowerCase().includes(searchQuery.toLowerCase()));

  const handleRunQuery = () => {
    // Fake query execution
  };

  return (
    <div className="animate-in fade-in duration-500 h-[calc(100vh-140px)] flex flex-col">
      {/* Top Bar */}
      <div className="flex items-center justify-between mb-6 shrink-0">
        <div>
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
             <Database className="w-5 h-5 text-primary" />
             Data Explorer
          </h2>
          <p className="text-xs text-slate-400 mt-1">Directly inspect database tables and cache keys.</p>
        </div>
        <div className="bg-dark-900 border border-dark-800 rounded-lg p-1 flex">
           <button 
             onClick={() => setActiveTab('postgres')}
             className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === 'postgres' ? 'bg-primary text-dark-950 shadow-sm' : 'text-slate-400 hover:text-white'}`}
           >
             PostgreSQL
           </button>
           <button 
             onClick={() => setActiveTab('redis')}
             className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === 'redis' ? 'bg-red-500 text-white shadow-sm' : 'text-slate-400 hover:text-white'}`}
           >
             Redis Cache
           </button>
        </div>
      </div>

      <div className="flex-1 flex gap-6 overflow-hidden">
         {/* Sidebar */}
         <div className="w-64 bg-dark-900 border border-dark-800 rounded-xl flex flex-col overflow-hidden shrink-0">
            <div className="p-4 border-b border-dark-800">
               <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input 
                     type="text" 
                     placeholder={activeTab === 'postgres' ? "Search tables..." : "Search keys..."}
                     value={searchQuery}
                     onChange={(e) => setSearchQuery(e.target.value)}
                     className="w-full bg-dark-950 border border-dark-700 text-white pl-9 pr-3 py-2 rounded-lg text-sm focus:border-primary/50 outline-none"
                  />
               </div>
            </div>
            
            <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-1">
               {activeTab === 'postgres' ? (
                  filteredTables.map(table => (
                     <button
                        key={table.name}
                        onClick={() => { setSelectedTable(table); setViewMode('browse'); }}
                        className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center justify-between group transition-colors ${selectedTable?.name === table.name ? 'bg-primary/10 text-primary' : 'text-slate-400 hover:bg-dark-800 hover:text-white'}`}
                     >
                        <div className="flex items-center gap-2">
                           <Table className="w-4 h-4 opacity-70" />
                           {table.name}
                        </div>
                        <span className="text-[10px] bg-dark-950 px-1.5 rounded border border-dark-800 opacity-60 group-hover:opacity-100">{table.rowCount}</span>
                     </button>
                  ))
               ) : (
                  filteredKeys.map(item => (
                     <button
                        key={item.key}
                        onClick={() => setSelectedKey(item)}
                        className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors truncate ${selectedKey?.key === item.key ? 'bg-red-500/10 text-red-400' : 'text-slate-400 hover:bg-dark-800 hover:text-white'}`}
                     >
                        <Key className="w-4 h-4 opacity-70 shrink-0" />
                        <span className="truncate">{item.key}</span>
                     </button>
                  ))
               )}
            </div>
            
            {/* Sidebar Footer */}
            <div className="p-3 border-t border-dark-800 text-[10px] text-slate-500 text-center">
               {activeTab === 'postgres' ? 'Connected to pg-primary-01' : 'Connected to redis-cache-01'}
            </div>
         </div>

         {/* Main Content Area */}
         <div className="flex-1 bg-dark-900 border border-dark-800 rounded-xl flex flex-col overflow-hidden shadow-lg">
            {activeTab === 'postgres' && selectedTable && (
               <>
                  <div className="border-b border-dark-800 p-4 flex items-center justify-between bg-dark-950/30">
                     <div className="flex items-center gap-4">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                           <Table className="w-5 h-5 text-slate-400" />
                           {selectedTable.name}
                        </h3>
                        <div className="flex gap-2">
                           <button 
                             onClick={() => setViewMode('browse')} 
                             className={`text-xs px-3 py-1 rounded border transition-colors ${viewMode === 'browse' ? 'bg-dark-800 border-dark-600 text-white' : 'border-transparent text-slate-500 hover:text-slate-300'}`}
                           >
                             Browse Data
                           </button>
                           <button 
                             onClick={() => setViewMode('query')} 
                             className={`text-xs px-3 py-1 rounded border transition-colors ${viewMode === 'query' ? 'bg-dark-800 border-dark-600 text-white' : 'border-transparent text-slate-500 hover:text-slate-300'}`}
                           >
                             SQL Console
                           </button>
                        </div>
                     </div>
                     <div className="flex items-center gap-3">
                        <span className="text-xs text-slate-500">
                           <span className="text-white font-mono">{selectedTable.rowCount}</span> rows • <span className="text-white font-mono">{selectedTable.size}</span>
                        </span>
                        <button className="p-1.5 text-slate-400 hover:text-white bg-dark-800 hover:bg-dark-700 rounded-lg transition-colors">
                           <RefreshCw className="w-4 h-4" />
                        </button>
                     </div>
                  </div>

                  {viewMode === 'browse' ? (
                     <div className="flex-1 overflow-auto custom-scrollbar">
                        <table className="w-full text-left text-sm whitespace-nowrap">
                           <thead className="bg-dark-950 text-slate-400 sticky top-0 z-10 border-b border-dark-800">
                              <tr>
                                 {selectedTable.columns.map(col => (
                                    <th key={col.name} className="px-6 py-3 font-medium">
                                       <div className="flex items-center gap-2">
                                          {col.isPrimaryKey && <Key className="w-3 h-3 text-amber-500" />}
                                          {col.name}
                                          <span className="text-[10px] font-normal text-slate-600 ml-1 bg-dark-900 px-1 rounded">{col.type}</span>
                                       </div>
                                    </th>
                                 ))}
                              </tr>
                           </thead>
                           <tbody className="divide-y divide-dark-800">
                              {selectedTable.data.map((row, i) => (
                                 <tr key={i} className="hover:bg-dark-800/50 transition-colors">
                                    {selectedTable.columns.map(col => (
                                       <td key={col.name} className="px-6 py-3 font-mono text-xs text-slate-300">
                                          {String(row[col.name])}
                                       </td>
                                    ))}
                                 </tr>
                              ))}
                           </tbody>
                        </table>
                     </div>
                  ) : (
                     <div className="flex-1 flex flex-col">
                        <div className="h-1/3 bg-dark-950 p-4 border-b border-dark-800 flex flex-col">
                           <div className="flex justify-between items-center mb-2">
                              <span className="text-xs font-bold text-slate-500 uppercase">Query Editor</span>
                              <button 
                                 onClick={handleRunQuery}
                                 className="bg-primary text-dark-950 px-3 py-1 rounded text-xs font-bold hover:bg-lime-400 flex items-center gap-1"
                              >
                                 <Play className="w-3 h-3" /> Run
                              </button>
                           </div>
                           <textarea 
                              value={sqlQuery}
                              onChange={(e) => setSqlQuery(e.target.value)}
                              className="flex-1 bg-transparent text-slate-300 font-mono text-sm outline-none resize-none"
                              spellCheck="false"
                           />
                        </div>
                        <div className="flex-1 bg-dark-900 p-8 flex items-center justify-center text-slate-500">
                           <div className="text-center">
                              <Code className="w-12 h-12 mx-auto mb-3 opacity-20" />
                              <p>Run query to see results</p>
                           </div>
                        </div>
                     </div>
                  )}
               </>
            )}

            {activeTab === 'redis' && (
               selectedKey ? (
                  <div className="flex flex-col h-full">
                     <div className="border-b border-dark-800 p-6">
                        <div className="flex items-start justify-between">
                           <div>
                              <div className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-1">Key</div>
                              <h3 className="text-xl font-mono text-white font-bold break-all">{selectedKey.key}</h3>
                           </div>
                           <button className="text-red-400 hover:text-red-300 hover:bg-red-500/10 p-2 rounded-lg transition-colors">
                              <Trash2 className="w-5 h-5" />
                           </button>
                        </div>
                        
                        <div className="flex gap-6 mt-6">
                           <div className="bg-dark-950 p-3 rounded-lg border border-dark-800 min-w-[100px]">
                              <div className="text-[10px] text-slate-500 uppercase mb-1">Type</div>
                              <div className="text-sm font-mono text-purple-400 font-bold uppercase">{selectedKey.type}</div>
                           </div>
                           <div className="bg-dark-950 p-3 rounded-lg border border-dark-800 min-w-[100px]">
                              <div className="text-[10px] text-slate-500 uppercase mb-1">TTL</div>
                              <div className={`text-sm font-mono font-bold ${selectedKey.ttl > 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
                                 {selectedKey.ttl === -1 ? 'No Expiry' : `${selectedKey.ttl}s`}
                              </div>
                           </div>
                           <div className="bg-dark-950 p-3 rounded-lg border border-dark-800 min-w-[100px]">
                              <div className="text-[10px] text-slate-500 uppercase mb-1">Size</div>
                              <div className="text-sm font-mono text-slate-300 font-bold">{selectedKey.size}</div>
                           </div>
                        </div>
                     </div>
                     
                     <div className="flex-1 p-6 overflow-hidden flex flex-col">
                        <div className="flex justify-between items-center mb-2">
                           <span className="text-xs font-bold text-slate-500 uppercase">Value</span>
                           <span className="text-[10px] text-slate-600 bg-dark-950 px-2 py-0.5 rounded border border-dark-800">JSON</span>
                        </div>
                        <div className="flex-1 bg-dark-950 rounded-lg border border-dark-800 p-4 overflow-auto custom-scrollbar">
                           <pre className="text-sm font-mono text-slate-300 whitespace-pre-wrap">
                              {typeof selectedKey.value === 'object' 
                                 ? JSON.stringify(selectedKey.value, null, 2) 
                                 : String(selectedKey.value)}
                           </pre>
                        </div>
                     </div>
                  </div>
               ) : (
                  <div className="flex-1 flex items-center justify-center text-slate-500">
                     <div className="text-center">
                        <Key className="w-16 h-16 mx-auto mb-4 opacity-10" />
                        <p>Select a key from the sidebar to inspect</p>
                     </div>
                  </div>
               )
            )}
         </div>
      </div>
    </div>
  );
};

export default DatabasePage;
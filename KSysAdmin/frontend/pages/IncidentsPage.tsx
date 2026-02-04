import React, { useState } from 'react';
import { Incident } from '../types';
import { Columns, Plus, AlertTriangle, CheckCircle, Clock, Calendar, MessageSquare, Search } from '../components/Icons';

interface IncidentsPageProps {
  incidents: Incident[];
}

const IncidentsPage: React.FC<IncidentsPageProps> = ({ incidents: initialIncidents }) => {
  const [incidents, setIncidents] = useState<Incident[]>(initialIncidents);
  const [draggedId, setDraggedId] = useState<string | null>(null);

  const columns: { id: Incident['status']; title: string; color: string }[] = [
    { id: 'Open', title: 'Open Issues', color: 'border-red-500/50' },
    { id: 'Investigating', title: 'In Progress', color: 'border-amber-500/50' },
    { id: 'Resolved', title: 'Resolved', color: 'border-emerald-500/50' },
  ];

  const handleDragStart = (e: React.DragEvent, id: string) => {
    setDraggedId(id);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault(); // Necessary for onDrop to fire
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e: React.DragEvent, status: Incident['status']) => {
    e.preventDefault();
    if (draggedId) {
      setIncidents(prev => prev.map(inc => 
        inc.id === draggedId ? { ...inc, status, updatedAt: new Date().toISOString() } : inc
      ));
      setDraggedId(null);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'Critical': return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'Major': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      default: return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
    }
  };

  return (
    <div className="animate-in fade-in duration-500 h-[calc(100vh-140px)] flex flex-col">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 shrink-0">
        <div>
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Columns className="w-5 h-5 text-primary" />
            Incident Response Center
          </h2>
          <div className="text-xs text-slate-400 mt-1">
            Drag and drop tickets to update their status.
          </div>
        </div>
        
        <div className="flex items-center gap-3 w-full sm:w-auto">
           <div className="relative flex-1 sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input 
                 type="text" 
                 placeholder="Search incidents..." 
                 className="w-full bg-dark-900 border border-dark-800 text-white pl-9 pr-4 py-2 rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary/50 outline-none transition-all placeholder:text-slate-600"
              />
           </div>
           <button className="bg-primary text-dark-950 px-4 py-2 rounded-lg text-sm font-bold hover:bg-lime-400 transition-colors shadow-[0_0_15px_rgba(138,206,0,0.3)] flex items-center gap-2">
             <Plus className="w-4 h-4" /> New Incident
           </button>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden pb-4">
        <div className="flex gap-6 h-full min-w-[1000px]">
          {columns.map(col => (
            <div 
              key={col.id}
              className="flex-1 flex flex-col bg-dark-950/30 rounded-xl border border-dark-800/50 min-w-[300px]"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, col.id)}
            >
              {/* Column Header */}
              <div className={`p-4 border-b border-dark-800/50 flex items-center justify-between border-t-2 ${col.color} rounded-t-xl bg-dark-900`}>
                <div className="font-semibold text-slate-200 text-sm flex items-center gap-2">
                  {col.title}
                  <span className="bg-dark-800 text-slate-400 px-2 py-0.5 rounded-full text-xs">
                    {incidents.filter(i => i.status === col.id).length}
                  </span>
                </div>
                {col.id === 'Open' && <AlertTriangle className="w-4 h-4 text-slate-500" />}
                {col.id === 'Investigating' && <Clock className="w-4 h-4 text-slate-500" />}
                {col.id === 'Resolved' && <CheckCircle className="w-4 h-4 text-slate-500" />}
              </div>

              {/* Column Body */}
              <div className="flex-1 p-3 overflow-y-auto custom-scrollbar space-y-3 bg-dark-950/20">
                {incidents.filter(i => i.status === col.id).map(incident => (
                  <div
                    key={incident.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, incident.id)}
                    className="bg-dark-900 border border-dark-800 rounded-lg p-4 cursor-move hover:border-primary/30 hover:shadow-lg transition-all group active:scale-[0.98] active:border-primary"
                  >
                    <div className="flex justify-between items-start mb-2">
                       <span className={`text-[10px] px-2 py-0.5 rounded border font-bold uppercase tracking-wider ${getSeverityColor(incident.severity)}`}>
                          {incident.severity}
                       </span>
                       <span className="text-xs font-mono text-slate-500">{incident.id}</span>
                    </div>
                    
                    <h4 className="text-sm font-medium text-white mb-2 leading-snug group-hover:text-primary transition-colors">
                       {incident.title}
                    </h4>
                    
                    <p className="text-xs text-slate-400 line-clamp-2 mb-3">
                       {incident.description}
                    </p>

                    <div className="flex items-center gap-2 mb-3">
                       <span className="text-[10px] bg-dark-950 px-2 py-1 rounded text-slate-400 border border-dark-800 truncate max-w-[120px]">
                          {incident.service}
                       </span>
                    </div>

                    <div className="flex items-center justify-between pt-3 border-t border-dark-800/50 mt-auto">
                       <div className="flex items-center gap-3">
                          {incident.assignee ? (
                             <div className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center text-[10px] font-bold" title={`Assigned to ${incident.assignee}`}>
                                {incident.assignee.split(' ').map(n => n[0]).join('')}
                             </div>
                          ) : (
                             <div className="w-6 h-6 rounded-full border border-dashed border-slate-600 flex items-center justify-center text-slate-600 hover:text-slate-400 hover:border-slate-400 cursor-pointer text-[10px]">
                                <Plus className="w-3 h-3" />
                             </div>
                          )}
                          <div className="text-[10px] text-slate-500 flex items-center gap-1">
                             <MessageSquare className="w-3 h-3" /> {incident.comments}
                          </div>
                       </div>
                       
                       <div className="text-[10px] text-slate-600 flex items-center gap-1" title={new Date(incident.updatedAt).toLocaleString()}>
                          <Calendar className="w-3 h-3" />
                          {new Date(incident.updatedAt).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                       </div>
                    </div>
                  </div>
                ))}
                
                {incidents.filter(i => i.status === col.id).length === 0 && (
                   <div className="h-24 border-2 border-dashed border-dark-800 rounded-lg flex items-center justify-center text-slate-600 text-xs">
                      No {col.title.toLowerCase()}
                   </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default IncidentsPage;
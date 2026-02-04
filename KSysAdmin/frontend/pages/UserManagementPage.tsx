import React, { useState, useEffect } from 'react';
import { User } from '../types';
import { Search, MoreHorizontal, Users, Edit, MessageSquare, Ban } from '../components/Icons';

interface UserManagementPageProps {
  users: User[];
}

const UserManagementPage: React.FC<UserManagementPageProps> = ({ users }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [actionMenuOpen, setActionMenuOpen] = useState<string | null>(null);

  // Close menu on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (actionMenuOpen && !(event.target as Element).closest('.action-menu-trigger') && !(event.target as Element).closest('.action-menu-dropdown')) {
        setActionMenuOpen(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [actionMenuOpen]);

  const filteredUsers = users.filter(user => 
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.merchantId.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="animate-in fade-in duration-500 space-y-6">
      {/* Header Actions */}
      <div className="flex flex-col md:flex-row justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input 
            type="text" 
            placeholder="Search by name, email or merchant ID..." 
            className="w-full bg-dark-900 border border-dark-800 text-white pl-10 pr-4 py-2.5 rounded-xl focus:ring-2 focus:ring-primary/50 focus:border-primary/50 outline-none transition-all placeholder:text-slate-600"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex gap-3">
          <button className="bg-dark-900 border border-dark-800 text-slate-300 hover:text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors">Export CSV</button>
          <button className="bg-primary text-dark-950 px-4 py-2 rounded-xl text-sm font-bold hover:bg-lime-400 transition-colors shadow-[0_0_15px_rgba(138,206,0,0.3)]">
            + Add New User
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-dark-900 rounded-xl border border-dark-800 shadow-lg overflow-visible">
        <div className="overflow-x-auto min-h-[400px]">
          <table className="w-full text-left text-sm">
            <thead className="bg-dark-950/50 text-slate-400 font-medium">
              <tr>
                <th className="px-6 py-4">User Details</th>
                <th className="px-6 py-4">Merchant ID</th>
                <th className="px-6 py-4">Subscription</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Last Login</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-800">
              {filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-dark-800/50 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-dark-800 flex items-center justify-center text-xs font-bold text-slate-400 border border-dark-700">
                        {user.name.charAt(0)}
                      </div>
                      <div>
                        <div className="font-medium text-white flex items-center gap-2">
                           {user.name}
                           {user.userType === 'Anonymous' && (
                              <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 rounded border border-slate-700">Anon</span>
                           )}
                        </div>
                        <div className="text-xs text-slate-500">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-slate-400 text-xs bg-dark-950 px-2 py-1 rounded border border-dark-800 select-all">
                       {user.merchantId}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                     <span className="text-slate-300">{user.subscriptionPlan}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium
                      ${user.status === 'Active' ? 'text-primary bg-primary/10' : 
                        user.status === 'Suspended' ? 'text-red-400 bg-red-500/10' : 
                        'text-amber-400 bg-amber-500/10'}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${
                        user.status === 'Active' ? 'bg-primary' : 
                        user.status === 'Suspended' ? 'bg-red-400' : 'bg-amber-400'
                      }`}></span>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-500 font-mono text-xs">
                    {user.lastLogin}
                  </td>
                  <td className="px-6 py-4 text-right relative">
                    <button 
                      onClick={() => setActionMenuOpen(actionMenuOpen === user.id ? null : user.id)}
                      className="action-menu-trigger p-1.5 text-slate-500 hover:text-white hover:bg-dark-700 rounded transition-colors"
                    >
                      <MoreHorizontal className="w-5 h-5" />
                    </button>
                    {actionMenuOpen === user.id && (
                       <div className="action-menu-dropdown absolute right-8 top-0 mt-8 w-40 bg-dark-900 border border-dark-800 rounded-xl shadow-2xl z-50 overflow-hidden ring-1 ring-white/5 animate-in fade-in zoom-in-95 duration-100">
                          <div className="py-1">
                             <button className="w-full text-left px-4 py-2.5 text-sm text-slate-300 hover:bg-dark-800 hover:text-white flex items-center gap-2 transition-colors">
                                <Edit className="w-4 h-4 text-slate-500" /> Edit
                             </button>
                             <button className="w-full text-left px-4 py-2.5 text-sm text-slate-300 hover:bg-dark-800 hover:text-white flex items-center gap-2 transition-colors">
                                <MessageSquare className="w-4 h-4 text-slate-500" /> Message
                             </button>
                             <div className="h-px bg-dark-800 my-1"></div>
                             <button className="w-full text-left px-4 py-2.5 text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 flex items-center gap-2 transition-colors">
                                <Ban className="w-4 h-4 opacity-70" /> Suspend
                             </button>
                          </div>
                       </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredUsers.length === 0 && (
            <div className="p-12 text-center text-slate-500">
              <Users className="w-12 h-12 mx-auto mb-3 opacity-20" />
              <p>No users found matching "{searchTerm}"</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserManagementPage;
import React from 'react';
import { Invoice } from '../types';
import { CreditCard, FileText, Activity } from '../components/Icons';
import StatsCard from '../components/StatsCard';

interface FinancePageProps {
  invoices: Invoice[];
}

const FinancePage: React.FC<FinancePageProps> = ({ invoices }) => {
  const totalRevenue = invoices
    .filter(i => i.status === 'Paid')
    .reduce((acc, curr) => acc + curr.amount, 0);

  const pendingAmount = invoices
    .filter(i => i.status === 'Pending')
    .reduce((acc, curr) => acc + curr.amount, 0);

  return (
    <div className="animate-in fade-in duration-500 space-y-8">
      {/* Finance Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatsCard 
          title="Total Revenue (MTD)" 
          value={`$${totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} 
          subtext="Processed via Stripe & PayPal"
          icon={<CreditCard className="w-6 h-6 text-emerald-400" />}
          trend="up"
          trendValue="+8.4%"
        />
        <StatsCard 
          title="Pending Invoices" 
          value={`$${pendingAmount.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} 
          subtext="3 invoices awaiting payment"
          icon={<FileText className="w-6 h-6 text-amber-400" />}
          trend="neutral"
          trendValue="Avg"
        />
        <StatsCard 
          title="Failed Transactions" 
          value="1" 
          subtext="Action required"
          icon={<Activity className="w-6 h-6 text-red-400" />}
          trend="down"
          trendValue="Low"
        />
      </div>

      {/* Invoice List */}
      <div className="bg-dark-900 rounded-xl border border-dark-800 shadow-lg overflow-hidden">
        <div className="p-6 border-b border-dark-800 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary" />
            Recent Invoices
          </h3>
          <div className="flex gap-2">
             <select className="bg-dark-950 border border-dark-800 text-slate-300 text-sm rounded-lg px-3 py-1.5 outline-none">
               <option>All Statuses</option>
               <option>Paid</option>
               <option>Pending</option>
             </select>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-dark-950/50 text-slate-400 font-medium">
              <tr>
                <th className="px-6 py-4">Invoice ID</th>
                <th className="px-6 py-4">Customer</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Amount</th>
                <th className="px-6 py-4">Gateway</th>
                <th className="px-6 py-4 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-800">
              {invoices.map((inv) => (
                <tr key={inv.id} className="hover:bg-dark-800/50 transition-colors">
                  <td className="px-6 py-4 font-mono text-slate-300 text-xs">
                    {inv.id}
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-medium text-white">{inv.userName}</div>
                    <div className="text-xs text-slate-500">{inv.userId}</div>
                  </td>
                  <td className="px-6 py-4 text-slate-400">
                    {new Date(inv.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 font-mono text-white font-medium">
                    ${inv.amount.toFixed(2)} <span className="text-slate-600 text-xs">{inv.currency}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-slate-300 text-xs bg-dark-800 px-2 py-1 rounded border border-dark-700">
                      {inv.gateway}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-bold border
                      ${inv.status === 'Paid' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                        inv.status === 'Pending' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 
                        'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                      {inv.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FinancePage;
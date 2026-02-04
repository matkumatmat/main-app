import React from 'react';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
}

const StatsCard: React.FC<StatsCardProps> = ({ title, value, subtext, icon, trend, trendValue }) => {
  return (
    <div className="bg-dark-900 rounded-xl p-6 border border-dark-800 shadow-lg flex items-start justify-between hover:border-primary/30 transition-all duration-300 group">
      <div>
        <p className="text-sm font-medium text-slate-400 mb-1 group-hover:text-slate-300 transition-colors">{title}</p>
        <h3 className="text-2xl font-bold text-white tracking-tight">{value}</h3>
        {(subtext || trendValue) && (
          <div className="flex items-center mt-2 gap-2">
            {trendValue && (
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                trend === 'down' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
                trend === 'up' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-slate-700 text-slate-300 border border-slate-600'
              }`}>
                {trendValue}
              </span>
            )}
            {subtext && <span className="text-xs text-slate-500">{subtext}</span>}
          </div>
        )}
      </div>
      <div className="p-3 bg-dark-800 rounded-lg text-primary shadow-inner border border-dark-800 group-hover:scale-105 transition-transform duration-300">
        {icon}
      </div>
    </div>
  );
};

export default StatsCard;
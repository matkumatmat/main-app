import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TimeSeriesPoint } from '../../types';

interface MetricsChartProps {
  data: TimeSeriesPoint[];
}

const MetricsChart: React.FC<MetricsChartProps> = ({ data }) => {
  return (
    <div className="h-[350px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8ACE00" stopOpacity={0.2}/>
              <stop offset="95%" stopColor="#8ACE00" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorError" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.2}/>
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={(str) => {
              const date = new Date(str);
              return `${date.getHours()}:00`;
            }}
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            dy={10}
          />
          <YAxis 
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => value >= 1000 ? `${value/1000}k` : value}
            dx={-10}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#0f172a', 
              borderRadius: '8px', 
              border: '1px solid #1e293b', 
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)', 
              color: '#f8fafc',
              padding: '12px'
            }}
            itemStyle={{ color: '#e2e8f0', fontSize: '13px', fontWeight: 500, padding: '2px 0' }}
            labelStyle={{ color: '#94a3b8', fontSize: '11px', marginBottom: '8px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}
            labelFormatter={(label) => new Date(label).toLocaleString()}
            cursor={{ fill: '#1e293b', opacity: 0.4 }}
          />
          <Area 
            type="monotone" 
            dataKey="totalRequests" 
            name="Total Requests"
            stroke="#8ACE00" 
            strokeWidth={2}
            fillOpacity={1} 
            fill="url(#colorTotal)" 
            activeDot={{ r: 6, strokeWidth: 0, fill: '#8ACE00' }}
          />
          <Area 
            type="monotone" 
            dataKey="errorCount" 
            name="Errors"
            stroke="#ef4444" 
            strokeWidth={2}
            fillOpacity={1} 
            fill="url(#colorError)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MetricsChart;
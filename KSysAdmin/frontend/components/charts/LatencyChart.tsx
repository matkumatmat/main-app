import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TimeSeriesPoint } from '../../types';

interface LatencyChartProps {
  data: TimeSeriesPoint[];
}

const LatencyChart: React.FC<LatencyChartProps> = ({ data }) => {
  return (
    <div className="h-[250px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={(str) => new Date(str).getHours() + 'h'}
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            interval={23} 
            dy={10}
          />
          <YAxis 
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            unit="ms"
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
             labelFormatter={(l) => new Date(l).toLocaleTimeString()}
             cursor={{ fill: '#1e293b', opacity: 0.4 }}
          />
          <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px', color: '#94a3b8' }} />
          <Line 
            type="monotone" 
            dataKey="avgLatency" 
            name="Avg Latency (ms)"
            stroke="#8ACE00" 
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#8ACE00', strokeWidth: 0 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LatencyChart;
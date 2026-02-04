import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { EndpointMetric } from '../types';

interface TopEndpointsProps {
  data: EndpointMetric[];
}

const TopEndpoints: React.FC<TopEndpointsProps> = ({ data }) => {
  return (
    <div className="bg-dark-900 rounded-xl border border-dark-800 shadow-lg p-5 h-full">
      <h3 className="font-semibold text-white mb-4">Top Endpoints</h3>
      <div className="h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20 }}>
            <XAxis type="number" hide />
            <YAxis 
              dataKey="url" 
              type="category" 
              width={100} 
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              tickFormatter={(val) => val.length > 20 ? val.substring(0, 18) + '...' : val}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip 
              cursor={{ fill: '#1e293b', opacity: 0.4 }}
              contentStyle={{ 
                backgroundColor: '#0f172a', 
                borderRadius: '8px', 
                border: '1px solid #1e293b', 
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)', 
                color: '#f8fafc',
                padding: '12px'
              }}
              itemStyle={{ color: '#8ACE00', fontSize: '13px', fontWeight: 500 }}
              labelStyle={{ color: '#94a3b8', fontSize: '11px', marginBottom: '8px', fontWeight: 600, letterSpacing: '0.05em' }}
            />
            <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={20}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={index === 0 ? '#8ACE00' : '#334155'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TopEndpoints;
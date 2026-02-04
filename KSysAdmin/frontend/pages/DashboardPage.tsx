import React from 'react';
import { Activity, Clock, ShieldAlert, AlertTriangle } from '../components/Icons';
import StatsCard from '../components/StatsCard';
import MetricsChart from '../components/charts/MetricsChart';
import LatencyChart from '../components/charts/LatencyChart';
import SecurityPanel from '../components/SecurityPanel';
import TopEndpoints from '../components/TopEndpoints';
import { TimeSeriesPoint, DashboardSummary, EndpointMetric, SecurityEvent } from '../types';

interface DashboardPageProps {
  metricsData: TimeSeriesPoint[];
  summary: DashboardSummary;
  topEndpoints: EndpointMetric[];
  securityEvents: SecurityEvent[];
}

const DashboardPage: React.FC<DashboardPageProps> = ({ metricsData, summary, topEndpoints, securityEvents }) => {
  return (
    <div className="animate-in fade-in duration-500">
      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard 
          title="Total Requests" 
          value={summary.totalRequests.toLocaleString()} 
          subtext="vs previous period"
          trend="up"
          trendValue="+12.5%"
          icon={<Activity className="w-6 h-6" />}
        />
        <StatsCard 
          title="Avg Latency" 
          value={`${summary.avgLatency}ms`} 
          subtext="Global average"
          trend="down"
          trendValue="-4.2%"
          icon={<Clock className="w-6 h-6" />}
        />
        <StatsCard 
          title="Error Rate" 
          value={`${summary.errorRate}%`} 
          subtext="Within operational limits"
          trend="neutral"
          trendValue="0.0%"
          icon={<AlertTriangle className="w-6 h-6 text-amber-500" />}
        />
        <StatsCard 
          title="Security Events" 
          value={summary.activeViolations} 
          subtext="Requires attention"
          trend="down"
          trendValue="High"
          icon={<ShieldAlert className="w-6 h-6 text-red-500" />}
        />
      </div>

      {/* Main Chart Section */}
      <div className="bg-dark-900 rounded-xl border border-dark-800 shadow-lg p-6 mb-8">
        <div className="flex items-center justify-between mb-8">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary" />
            Traffic & Error Trends
          </h3>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-2 text-xs font-medium text-slate-400 bg-dark-950 px-3 py-1.5 rounded-full border border-dark-800">
              <span className="w-2 h-2 rounded-full bg-primary shadow-[0_0_8px_rgba(138,206,0,0.5)]"></span> Requests
            </span>
            <span className="flex items-center gap-2 text-xs font-medium text-slate-400 bg-dark-950 px-3 py-1.5 rounded-full border border-dark-800">
              <span className="w-2 h-2 rounded-full bg-red-500"></span> Errors
            </span>
          </div>
        </div>
        <MetricsChart data={metricsData} />
      </div>

      {/* Lower Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Latency Chart */}
        <div className="lg:col-span-2 bg-dark-900 rounded-xl border border-dark-800 shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Clock className="w-5 h-5 text-primary" />
                System Latency
              </h3>
            </div>
            <LatencyChart data={metricsData} />
        </div>

        {/* Top Endpoints */}
        <div className="lg:col-span-1">
          <TopEndpoints data={topEndpoints} />
        </div>
      </div>
      
      {/* Bottom Security Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-1 gap-8 mt-8 pb-8">
          <SecurityPanel events={securityEvents} />
      </div>
    </div>
  );
};

export default DashboardPage;
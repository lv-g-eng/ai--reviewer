/**
 * Performance Monitoring Dashboard
 * 
 * Provides real-time performance monitoring and optimization insights:
 * - API response times and cache hit rates
 * - Database query performance
 * - Frontend bundle analysis
 * - Real-time system metrics
 * - Performance recommendations
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer
} from 'recharts';
import { 
  Activity, 
  Database, 
  Globe, 
  Zap, 
  TrendingUp, 
  AlertTriangle, 
  BarChart3,
  Cpu
} from 'lucide-react';

interface PerformanceMetrics {
  api: {
    responseTime: number;
    cacheHitRate: number;
    errorRate: number;
    requestsPerSecond: number;
  };
  database: {
    connectionCount: number;
    queryTime: number;
    cacheHitRate: number;
  };
  frontend: {
    bundleSize: number;
    loadTime: number;
    cacheHitRate: number;
    renderTime: number;
  };
  system: {
    cpuUsage: number;
    memoryUsage: number;
    diskUsage: number;
    networkLatency: number;
  };
}

const COLORS = {
  primary: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#6366f1'
};

const PerformanceDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Mock data for demonstration
  const mockMetrics: PerformanceMetrics = {
    api: {
      responseTime: 150,
      cacheHitRate: 0.75,
      errorRate: 2.1,
      requestsPerSecond: 45.2
    },
    database: {
      connectionCount: 25,
      queryTime: 85,
      cacheHitRate: 0.68
    },
    frontend: {
      bundleSize: 1.2,
      loadTime: 2800,
      cacheHitRate: 0.82,
      renderTime: 16.7
    },
    system: {
      cpuUsage: 45.3,
      memoryUsage: 62.1,
      diskUsage: 78.5,
      networkLatency: 150
    }
  };

  // Mock performance data for charts
  const performanceData = Array.from({ length: 20 }, (_, i) => ({
    timestamp: Date.now() - (19 - i) * 60000,
    duration: 120 + Math.random() * 100,
    requests: 40 + Math.random() * 20
  }));

  // Fetch performance metrics
  const fetchMetrics = async () => {
    try {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setMetrics(mockMetrics);
    } catch (error) {
      console.error('Failed to fetch performance metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh effect
  useEffect(() => {
    fetchMetrics();
    
    if (autoRefresh) {
      const interval = setInterval(fetchMetrics, 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  // Performance score calculation
  const performanceScore = React.useMemo(() => {
    if (!metrics) return 0;
    
    let score = 100;
    
    if (metrics.api.responseTime > 200) score -= 15;
    if (metrics.api.cacheHitRate < 0.5) score -= 10;
    if (metrics.api.errorRate > 5) score -= 20;
    if (metrics.database.queryTime > 100) score -= 15;
    if (metrics.system.cpuUsage > 80) score -= 20;
    if (metrics.system.memoryUsage > 85) score -= 15;
    
    return Math.max(0, score);
  }, [metrics]);

  const getScoreColor = (score: number) => {
    if (score >= 80) return COLORS.success;
    if (score >= 60) return COLORS.warning;
    return COLORS.error;
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  if (loading && !metrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Performance Dashboard</h1>
          <p className="text-gray-600 mt-1">Monitor and optimize system performance</p>
        </div>
        <div className="flex items-center space-x-4">
          <Button
            variant={autoRefresh ? "default" : "outline"}
            onClick={() => setAutoRefresh(!autoRefresh)}
            size="sm"
          >
            <Activity className="w-4 h-4 mr-2" />
            Auto Refresh
          </Button>
          <Button onClick={fetchMetrics} size="sm" disabled={loading}>
            <TrendingUp className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Performance Score */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            Overall Performance Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-6">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Performance Score</span>
                <span className="text-sm text-gray-600">{performanceScore}/100</span>
              </div>
              <Progress value={performanceScore} className="h-3" />
            </div>
            <div className="text-center">
              <div 
                className="text-3xl font-bold"
                style={{ color: getScoreColor(performanceScore) }}
              >
                {performanceScore}
              </div>
              <div className="text-sm text-gray-600">
                {getScoreLabel(performanceScore)}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="api">API</TabsTrigger>
          <TabsTrigger value="database">Database</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">API Response Time</CardTitle>
                <Globe className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.api.responseTime.toFixed(0)}ms
                </div>
                <p className="text-xs text-muted-foreground">
                  Target: &lt;200ms
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Cache Hit Rate</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {((metrics?.api.cacheHitRate || 0) * 100).toFixed(1)}%
                </div>
                <p className="text-xs text-muted-foreground">
                  Target: &gt;50%
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Database Queries</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.database.queryTime.toFixed(0)}ms
                </div>
                <p className="text-xs text-muted-foreground">
                  Avg query time
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">System Load</CardTitle>
                <Cpu className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.system.cpuUsage.toFixed(1)}%
                </div>
                <p className="text-xs text-muted-foreground">
                  CPU usage
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Performance Trends Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Performance Trends</CardTitle>
              <CardDescription>Response time over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="duration" 
                    stroke={COLORS.primary} 
                    strokeWidth={2}
                    name="Response Time (ms)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Tab */}
        <TabsContent value="api" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Request Volume</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {metrics?.api.requestsPerSecond.toFixed(1)}
                </div>
                <p className="text-sm text-gray-600">requests/second</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Error Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-600">
                  {metrics?.api.errorRate.toFixed(1)}%
                </div>
                <p className="text-sm text-gray-600">4xx/5xx errors</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Cache Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {((metrics?.api.cacheHitRate || 0) * 100).toFixed(1)}%
                </div>
                <p className="text-sm text-gray-600">hit rate</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Database Tab */}
        <TabsContent value="database" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Connection Pool</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {metrics?.database.connectionCount}
                </div>
                <p className="text-sm text-gray-600">active connections</p>
                <Progress 
                  value={(metrics?.database.connectionCount || 0)} 
                  className="mt-2"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Query Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {metrics?.database.queryTime.toFixed(0)}ms
                </div>
                <p className="text-sm text-gray-600">avg query time</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Cache Hit Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {((metrics?.database.cacheHitRate || 0) * 100).toFixed(1)}%
                </div>
                <p className="text-sm text-gray-600">query cache hits</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* System Tab */}
        <TabsContent value="system" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">CPU Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.system.cpuUsage.toFixed(1)}%
                </div>
                <Progress value={metrics?.system.cpuUsage} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Memory Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.system.memoryUsage.toFixed(1)}%
                </div>
                <Progress value={metrics?.system.memoryUsage} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Disk Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.system.diskUsage.toFixed(1)}%
                </div>
                <Progress value={metrics?.system.diskUsage} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Network Latency</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.system.networkLatency.toFixed(0)}ms
                </div>
                <p className="text-xs text-gray-600">avg latency</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PerformanceDashboard;
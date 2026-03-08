/**
 * Metrics数据导出属性测试
 * 
 * Feature: frontend-production-optimization
 * Property 21: 指标数据导出
 * 
 * **Validates: Requirements 6.2**
 * 
 * 测试覆盖:
 * - 对于任何指标数据，应该能够导出为CSV或JSON格式，且导出的数据与显示的数据一致
 * 
 * 注意: 此属性测试验证指标数据导出功能的正确性，确保导出的数据与显示的数据完全一致。
 * 测试覆盖CSV和JSON两种导出格式，以及各种指标配置和数据集。
 */

import fc from 'fast-check';
import { render, screen, waitFor, fireEvent, cleanup } from '@testing-library/react';
import Metrics from '../Metrics';
import { DashboardService } from '../../services/DashboardService';

// Mock DashboardService
jest.mock('../../services/DashboardService', () => ({
  DashboardService: {
    getDashboards: jest.fn(() => []),
    saveDashboard: jest.fn(),
    updateDashboard: jest.fn(),
    deleteDashboard: jest.fn(),
    updateLayout: jest.fn(),
  },
}));

describe('Property 21: 指标数据导出', () => {
  let mockCreateObjectURL: jest.Mock;
  let mockRevokeObjectURL: jest.Mock;
  let lastExportedBlob: Blob | null = null;
  let lastExportedFilename: string | null = null;

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    lastExportedBlob = null;
    lastExportedFilename = null;

    // Mock URL.createObjectURL and URL.revokeObjectURL
    mockCreateObjectURL = jest.fn((blob: Blob) => {
      lastExportedBlob = blob;
      return `mock-url-${Date.now()}`;
    });
    mockRevokeObjectURL = jest.fn();

    global.URL.createObjectURL = mockCreateObjectURL;
    global.URL.revokeObjectURL = mockRevokeObjectURL;

    // Mock document.createElement to capture download operations
    const originalCreateElement = document.createElement.bind(document);
    jest.spyOn(document, 'createElement').mockImplementation((tagName: string) => {
      const element = originalCreateElement(tagName);
      if (tagName === 'a') {
        const originalClick = element.click.bind(element);
        element.click = jest.fn(() => {
          const download = element.getAttribute('download');
          if (download) {
            lastExportedFilename = download;
          }
          originalClick();
        });
      }
      return element;
    });
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  // 自定义生成器：生成时间范围
  const timeRangeArbitrary = () =>
    fc.constantFrom('day', 'week', 'month');

  // 自定义生成器：生成指标ID
  const metricIdArbitrary = () =>
    fc.constantFrom('performance', 'errorRate', 'responseTime');

  /**
   * 辅助函数：读取Blob内容
   */
  const readBlobAsText = async (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsText(blob);
    });
  };

  /**
   * 辅助函数：解析CSV内容
   */
  const parseCSV = (content: string): Array<Record<string, string>> => {
    const lines = content.trim().split('\n');
    if (lines.length < 2) return [];

    const headers = lines[0].split(',');
    const rows: Array<Record<string, string>> = [];

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',');
      const row: Record<string, string> = {};
      headers.forEach((header, index) => {
        row[header] = values[index] || '';
      });
      rows.push(row);
    }

    return rows;
  };

  it('应该在任何时间范围下导出CSV格式的数据', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // 点击CSV导出按钮
          const csvButton = screen.getByRole('button', { name: /csv/i });
          fireEvent.click(csvButton);

          // 等待导出完成
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 验证Blob被创建
          expect(lastExportedBlob).not.toBeNull();
          expect(lastExportedFilename).not.toBeNull();

          // 验证文件类型
          expect(lastExportedBlob!.type).toBe('text/csv;charset=utf-8;');

          // 验证文件名包含时间范围
          expect(lastExportedFilename).toContain(timeRange);
          expect(lastExportedFilename).toMatch(/\.csv$/);

          // 读取并验证CSV内容
          const content = await readBlobAsText(lastExportedBlob!);
          expect(content).toContain('Timestamp');
          expect(content).toContain('Label');

          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 120000);

  it('应该在任何时间范围下导出JSON格式的数据', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // 点击JSON导出按钮
          const jsonButton = screen.getByRole('button', { name: /json/i });
          fireEvent.click(jsonButton);

          // 等待导出完成
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 验证Blob被创建
          expect(lastExportedBlob).not.toBeNull();
          expect(lastExportedFilename).not.toBeNull();

          // 验证文件类型
          expect(lastExportedBlob!.type).toBe('application/json;charset=utf-8;');

          // 验证文件名包含时间范围
          expect(lastExportedFilename).toContain(timeRange);
          expect(lastExportedFilename).toMatch(/\.json$/);

          // 读取并验证JSON内容
          const content = await readBlobAsText(lastExportedBlob!);
          const jsonData = JSON.parse(content);
          expect(jsonData).toHaveProperty('exportDate');
          expect(jsonData).toHaveProperty('timeRange');
          expect(jsonData).toHaveProperty('metrics');
          expect(jsonData).toHaveProperty('data');
          expect(jsonData.timeRange).toBe(timeRange);

          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 120000);

  it('应该导出与显示数据一致的CSV内容', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // 导出CSV
          const csvButton = screen.getByRole('button', { name: /csv/i });
          fireEvent.click(csvButton);

          // 等待导出完成
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 读取并验证CSV内容
          const content = await readBlobAsText(lastExportedBlob!);
          const csvRows = parseCSV(content);

          // 验证数据行数大于0
          expect(csvRows.length).toBeGreaterThan(0);

          // 验证每行都有timestamp和label
          csvRows.forEach(row => {
            expect(row['Timestamp']).toBeDefined();
            expect(row['Label']).toBeDefined();
          });

          // 验证至少包含一个指标列
          const firstRow = csvRows[0];
          const metricColumns = Object.keys(firstRow).filter(
            key => key !== 'Timestamp' && key !== 'Label'
          );
          expect(metricColumns.length).toBeGreaterThan(0);

          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 120000);

  it('应该导出与显示数据一致的JSON内容', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // 导出JSON
          const jsonButton = screen.getByRole('button', { name: /json/i });
          fireEvent.click(jsonButton);

          // 等待导出完成
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 读取并验证JSON内容
          const content = await readBlobAsText(lastExportedBlob!);
          const jsonData = JSON.parse(content);

          // 验证时间范围匹配
          expect(jsonData.timeRange).toBe(timeRange);

          // 验证数据数组
          expect(Array.isArray(jsonData.data)).toBe(true);
          expect(jsonData.data.length).toBeGreaterThan(0);

          // 验证每个数据点都有timestamp
          jsonData.data.forEach((dataPoint: any) => {
            expect(dataPoint.timestamp).toBeDefined();
            expect(dataPoint.label).toBeDefined();
          });

          // 验证指标定义
          expect(Array.isArray(jsonData.metrics)).toBe(true);
          expect(jsonData.metrics.length).toBeGreaterThan(0);

          jsonData.metrics.forEach((metric: any) => {
            expect(metric.id).toBeDefined();
            expect(metric.name).toBeDefined();
            expect(metric.unit).toBeDefined();
          });

          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 120000);

  it('应该在自定义仪表板中导出选定的指标', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(metricIdArbitrary(), { minLength: 1, maxLength: 3 }).map(arr => [...new Set(arr)]),
        timeRangeArbitrary(),
        async (selectedMetrics, timeRange) => {
          // 创建自定义仪表板
          const mockUser = {
            id: 'user_1',
            name: 'Test User',
            email: 'test@example.com'
          };

          const mockDashboard = {
            id: 'dashboard_1',
            name: 'Test Dashboard',
            description: 'Test',
            owner: mockUser,
            metrics: selectedMetrics,
            layout: {
              columns: 3,
              widgets: selectedMetrics.map((metricId, index) => ({
                id: `widget_${index}`,
                metricId,
                position: { x: index, y: 0, w: 1, h: 1 },
                chartType: 'line' as const,
                options: {}
              }))
            },
            timeRange: { type: 'relative' as const, value: 7, unit: 'day' as const },
            refreshInterval: 30,
            shared: false,
            createdAt: new Date(),
            updatedAt: new Date()
          };

          (DashboardService.getDashboards as jest.Mock).mockReturnValue([mockDashboard]);

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getAllByText('Test Dashboard').length).toBeGreaterThan(0);
          });

          // 切换到自定义仪表板
          const dashboardTabs = screen.getAllByRole('button', { name: 'Test Dashboard' });
          fireEvent.click(dashboardTabs[0]);

          await waitFor(() => {
            expect(screen.getByText(/refresh: 30s/i)).toBeInTheDocument();
          });

          // 导出JSON
          const jsonButton = screen.getByRole('button', { name: /json/i });
          fireEvent.click(jsonButton);

          // 等待导出完成
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 读取并验证导出的指标与选定的指标一致
          const content = await readBlobAsText(lastExportedBlob!);
          const jsonData = JSON.parse(content);

          // 验证仪表板信息
          expect(jsonData.dashboard).toBeDefined();
          expect(jsonData.dashboard.name).toBe('Test Dashboard');

          // 验证导出的指标ID与选定的指标一致
          const exportedMetricIds = jsonData.metrics.map((m: any) => m.id);
          expect(exportedMetricIds.sort()).toEqual(selectedMetrics.sort());

          // 验证数据点包含选定的指标
          jsonData.data.forEach((dataPoint: any) => {
            selectedMetrics.forEach(metricId => {
              expect(dataPoint).toHaveProperty(metricId);
            });
          });

          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 120000);

  it('应该在CSV导出中包含所有指标的正确单位', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // 导出CSV
          const csvButton = screen.getByRole('button', { name: /csv/i });
          fireEvent.click(csvButton);

          // 等待导出完成
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 读取并验证CSV头部包含指标名称和单位
          const content = await readBlobAsText(lastExportedBlob!);
          const lines = content.split('\n');
          const header = lines[0];

          // 验证头部包含指标名称和单位
          expect(header).toContain('Performance Score (score)');
          expect(header).toContain('Error Rate (%)');
          expect(header).toContain('Response Time (ms)');

          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 120000);

  it('应该在JSON导出中包含完整的指标定义', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // 导出JSON
          const jsonButton = screen.getByRole('button', { name: /json/i });
          fireEvent.click(jsonButton);

          // 等待导出完成
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 读取并验证JSON包含完整的指标定义
          const content = await readBlobAsText(lastExportedBlob!);
          const jsonData = JSON.parse(content);

          // 验证每个指标定义包含所有必需字段
          jsonData.metrics.forEach((metric: any) => {
            expect(metric).toHaveProperty('id');
            expect(metric).toHaveProperty('name');
            expect(metric).toHaveProperty('unit');
            expect(typeof metric.id).toBe('string');
            expect(typeof metric.name).toBe('string');
            expect(typeof metric.unit).toBe('string');
          });

          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 120000);

  it('应该在CSV导出中正确格式化数值', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // 导出CSV
          const csvButton = screen.getByRole('button', { name: /csv/i });
          fireEvent.click(csvButton);

          // 等待导出完成
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 读取并验证CSV数值格式
          const content = await readBlobAsText(lastExportedBlob!);
          const csvRows = parseCSV(content);

          csvRows.forEach(row => {
            // 验证每个指标值都是有效的数字格式（保留2位小数）
            Object.keys(row).forEach(key => {
              if (key !== 'Timestamp' && key !== 'Label') {
                const value = row[key];
                // 应该是数字格式的字符串
                expect(value).toMatch(/^\d+\.\d{2}$/);
              }
            });
          });

          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 120000);

  it('应该在JSON导出中包含导出时间戳', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          const beforeExport = new Date();

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // 导出JSON
          const jsonButton = screen.getByRole('button', { name: /json/i });
          fireEvent.click(jsonButton);

          // 等待导出完成
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          const afterExport = new Date();

          // 读取并验证JSON包含导出时间戳
          const content = await readBlobAsText(lastExportedBlob!);
          const jsonData = JSON.parse(content);

          expect(jsonData.exportDate).toBeDefined();
          const exportDate = new Date(jsonData.exportDate);

          // 验证导出时间在合理范围内
          expect(exportDate.getTime()).toBeGreaterThanOrEqual(beforeExport.getTime());
          expect(exportDate.getTime()).toBeLessThanOrEqual(afterExport.getTime());

          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 120000);

  it('应该确保CSV和JSON导出的数据点数量一致', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          // 导出CSV
          render(<Metrics initialTimeRange={timeRange} />);

          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          const csvButton = screen.getByRole('button', { name: /csv/i });
          fireEvent.click(csvButton);

          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          const csvContent = await readBlobAsText(lastExportedBlob!);
          const csvRows = parseCSV(csvContent);
          const csvDataCount = csvRows.length;

          // 清理并重新渲染
          cleanup();
          lastExportedBlob = null;
          mockCreateObjectURL.mockClear();

          render(<Metrics initialTimeRange={timeRange} />);

          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // 导出JSON
          const jsonButton = screen.getByRole('button', { name: /json/i });
          fireEvent.click(jsonButton);

          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          const jsonContent = await readBlobAsText(lastExportedBlob!);
          const jsonData = JSON.parse(jsonContent);
          const jsonDataCount = jsonData.data.length;

          // 验证数据点数量一致
          expect(csvDataCount).toBe(jsonDataCount);

          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 120000);
});

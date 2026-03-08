/**
 * Metricsdataexportpropertytest
 * 
 * Feature: frontend-production-optimization
 * Property 21: 指标dataexport
 * 
 * **Validates: Requirements 6.2**
 * 
 * testCoverage:
 * - 对于任何指标data，should能够export为CSV或JSONformat，且export的data与show的data一致
 * 
 * note: 此propertytestverify指标dataexportfeature的正确性，确保export的data与show的data完全一致。
 * testCoverageCSVandJSON两种exportformat，以及各种指标configanddata集。
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

describe('Property 21: 指标dataexport', () => {
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

  // customGenerator：generate时间范围
  const timeRangeArbitrary = () =>
    fc.constantFrom('day', 'week', 'month');

  // customGenerator：generate指标ID
  const metricIdArbitrary = () =>
    fc.constantFrom('performance', 'errorRate', 'responseTime');

  /**
   * 辅助function：读取Blobcontent
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
   * 辅助function：解析CSVcontent
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

  it('shouldBeAt任何时间范围下exportCSVformat的data', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // waitDataLoaded
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // 点击CSVexportbutton
          const csvButton = screen.getByRole('button', { name: /csv/i });
          fireEvent.click(csvButton);

          // waitExportDone
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // verifyBlob被create
          expect(lastExportedBlob).not.toBeNull();
          expect(lastExportedFilename).not.toBeNull();

          // verifyfiletype
          expect(lastExportedBlob!.type).toBe('text/csv;charset=utf-8;');

          // verifyfile名contain时间范围
          expect(lastExportedFilename).toContain(timeRange);
          expect(lastExportedFilename).toMatch(/\.csv$/);

          // 读取并verifyCSVcontent
          const content = await readBlobAsText(lastExportedBlob!);
          expect(content).toContain('Timestamp');
          expect(content).toContain('Label');

          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 120000);

  it('shouldBeAt任何时间范围下exportJSONformat的data', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // waitDataLoaded
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // 点击JSONexportbutton
          const jsonButton = screen.getByRole('button', { name: /json/i });
          fireEvent.click(jsonButton);

          // waitExportDone
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // verifyBlob被create
          expect(lastExportedBlob).not.toBeNull();
          expect(lastExportedFilename).not.toBeNull();

          // verifyfiletype
          expect(lastExportedBlob!.type).toBe('application/json;charset=utf-8;');

          // verifyfile名contain时间范围
          expect(lastExportedFilename).toContain(timeRange);
          expect(lastExportedFilename).toMatch(/\.json$/);

          // 读取并verifyJSONcontent
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

  it('shouldexport与showdata一致的CSVcontent', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // waitDataLoaded
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // exportCSV
          const csvButton = screen.getByRole('button', { name: /csv/i });
          fireEvent.click(csvButton);

          // waitExportDone
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 读取并verifyCSVcontent
          const content = await readBlobAsText(lastExportedBlob!);
          const csvRows = parseCSV(content);

          // verifydata行数大于0
          expect(csvRows.length).toBeGreaterThan(0);

          // verify每行都有timestampandlabel
          csvRows.forEach(row => {
            expect(row['Timestamp']).toBeDefined();
            expect(row['Label']).toBeDefined();
          });

          // verify至少contain一item指标列
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

  it('shouldexport与showdata一致的JSONcontent', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // waitDataLoaded
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // exportJSON
          const jsonButton = screen.getByRole('button', { name: /json/i });
          fireEvent.click(jsonButton);

          // waitExportDone
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 读取并verifyJSONcontent
          const content = await readBlobAsText(lastExportedBlob!);
          const jsonData = JSON.parse(content);

          // verify时间范围匹配
          expect(jsonData.timeRange).toBe(timeRange);

          // verifydata数组
          expect(Array.isArray(jsonData.data)).toBe(true);
          expect(jsonData.data.length).toBeGreaterThan(0);

          // verify每itemdata点都有timestamp
          jsonData.data.forEach((dataPoint: any) => {
            expect(dataPoint.timestamp).toBeDefined();
            expect(dataPoint.label).toBeDefined();
          });

          // verify指标定义
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

  it('shouldBeAt自定义仪表板中export选定的指标', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(metricIdArbitrary(), { minLength: 1, maxLength: 3 }).map(arr => [...new Set(arr)]),
        timeRangeArbitrary(),
        async (selectedMetrics, timeRange) => {
          // create自定义仪表板
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

          // waitDataLoaded
          await waitFor(() => {
            expect(screen.getAllByText('Test Dashboard').length).toBeGreaterThan(0);
          });

          // 切换到自定义仪表板
          const dashboardTabs = screen.getAllByRole('button', { name: 'Test Dashboard' });
          fireEvent.click(dashboardTabs[0]);

          await waitFor(() => {
            expect(screen.getByText(/refresh: 30s/i)).toBeInTheDocument();
          });

          // exportJSON
          const jsonButton = screen.getByRole('button', { name: /json/i });
          fireEvent.click(jsonButton);

          // waitExportDone
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 读取并verifyexport的指标与选定的指标一致
          const content = await readBlobAsText(lastExportedBlob!);
          const jsonData = JSON.parse(content);

          // verify仪表板info
          expect(jsonData.dashboard).toBeDefined();
          expect(jsonData.dashboard.name).toBe('Test Dashboard');

          // verifyexport的指标ID与选定的指标一致
          const exportedMetricIds = jsonData.metrics.map((m: any) => m.id);
          expect(exportedMetricIds.sort()).toEqual(selectedMetrics.sort());

          // verifydata点contain选定的指标
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

  it('shouldBeAtCSVexport中contain所有指标的正确单位', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // waitDataLoaded
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // exportCSV
          const csvButton = screen.getByRole('button', { name: /csv/i });
          fireEvent.click(csvButton);

          // waitExportDone
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 读取并verifyCSV头部contain指标名称and单位
          const content = await readBlobAsText(lastExportedBlob!);
          const lines = content.split('\n');
          const header = lines[0];

          // verify头部contain指标名称and单位
          expect(header).toContain('Performance Score (score)');
          expect(header).toContain('Error Rate (%)');
          expect(header).toContain('Response Time (ms)');

          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 120000);

  it('shouldBeAtJSONexport中contain完整的指标定义', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // waitDataLoaded
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // exportJSON
          const jsonButton = screen.getByRole('button', { name: /json/i });
          fireEvent.click(jsonButton);

          // waitExportDone
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 读取并verifyJSONcontain完整的指标定义
          const content = await readBlobAsText(lastExportedBlob!);
          const jsonData = JSON.parse(content);

          // verify每item指标定义contain所有必需field
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

  it('shouldBeAtCSVexport中正确format化数value', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // waitDataLoaded
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // exportCSV
          const csvButton = screen.getByRole('button', { name: /csv/i });
          fireEvent.click(csvButton);

          // waitExportDone
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          // 读取并verifyCSV数valueformat
          const content = await readBlobAsText(lastExportedBlob!);
          const csvRows = parseCSV(content);

          csvRows.forEach(row => {
            // verify每item指标value都是有效的数字format（保留2位小数）
            Object.keys(row).forEach(key => {
              if (key !== 'Timestamp' && key !== 'Label') {
                const value = row[key];
                // should是数字format的字符串
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

  it('shouldBeAtJSONexport中containexport时间戳', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          const beforeExport = new Date();

          render(<Metrics initialTimeRange={timeRange} />);

          // waitDataLoaded
          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // exportJSON
          const jsonButton = screen.getByRole('button', { name: /json/i });
          fireEvent.click(jsonButton);

          // waitExportDone
          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          const afterExport = new Date();

          // 读取并verifyJSONcontainexport时间戳
          const content = await readBlobAsText(lastExportedBlob!);
          const jsonData = JSON.parse(content);

          expect(jsonData.exportDate).toBeDefined();
          const exportDate = new Date(jsonData.exportDate);

          // verifyexport时间在合理范围内
          expect(exportDate.getTime()).toBeGreaterThanOrEqual(beforeExport.getTime());
          expect(exportDate.getTime()).toBeLessThanOrEqual(afterExport.getTime());

          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 120000);

  it('should确保CSVandJSONexport的data点数量一致', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          // exportCSV
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

          // cleanup并重新render
          cleanup();
          lastExportedBlob = null;
          mockCreateObjectURL.mockClear();

          render(<Metrics initialTimeRange={timeRange} />);

          await waitFor(() => {
            expect(screen.getAllByText(/metrics dashboard/i).length).toBeGreaterThan(0);
          });

          // exportJSON
          const jsonButton = screen.getByRole('button', { name: /json/i });
          fireEvent.click(jsonButton);

          await waitFor(() => {
            expect(mockCreateObjectURL).toHaveBeenCalled();
          });

          const jsonContent = await readBlobAsText(lastExportedBlob!);
          const jsonData = JSON.parse(jsonContent);
          const jsonDataCount = jsonData.data.length;

          // verifydata点数量一致
          expect(csvDataCount).toBe(jsonDataCount);

          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 120000);
});

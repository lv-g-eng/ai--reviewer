/**
 * Metrics多指标对比属性测试
 * 
 * Feature: frontend-production-optimization
 * Property 22: 多指标对比显示
 * 
 * **Validates: Requirements 6.4**
 * 
 * 测试覆盖:
 * - 对于任何选中的多个指标，应该能够在同一图表中对比显示
 * 
 * 注意: 此属性测试验证多指标对比功能的正确性，确保选中的所有指标都能在同一图表中正确显示。
 * 测试覆盖各种指标组合和选择场景。
 */

import fc from 'fast-check';
import { render, screen, waitFor, fireEvent, cleanup } from '@testing-library/react';
import Metrics from '../Metrics';

describe('Property 22: 多指标对比显示', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  // 可用的指标ID
  const availableMetrics = ['performance', 'errorRate', 'responseTime'];

  // 自定义生成器：生成指标ID数组（至少2个，确保是对比场景）
  const multipleMetricsArbitrary = () =>
    fc.array(
      fc.constantFrom(...availableMetrics),
      { minLength: 2, maxLength: 3 }
    ).map(arr => [...new Set(arr)]) // 去重
    .filter(arr => arr.length >= 2); // 确保至少有2个不同的指标

  // 自定义生成器：生成时间范围
  const timeRangeArbitrary = () =>
    fc.constantFrom('day', 'week', 'month');

  /**
   * 辅助函数：选择指定的指标
   */
  const selectMetrics = async (selectedMetrics: string[]) => {
    // 首先选择所有指标
    const selectAllButton = screen.getByRole('button', { name: /select all/i });
    fireEvent.click(selectAllButton);

    await waitFor(() => {
      expect(screen.getByText(/3 metrics selected/i)).toBeInTheDocument();
    });

    // 取消选择不需要的指标
    const allMetricIds = ['performance', 'errorRate', 'responseTime'];
    for (const metricId of allMetricIds) {
      if (!selectedMetrics.includes(metricId)) {
        let buttonText: string;
        if (metricId === 'performance') buttonText = 'Performance Score';
        else if (metricId === 'errorRate') buttonText = 'Error Rate';
        else buttonText = 'Response Time';

        const metricButton = screen.getByRole('button', { name: new RegExp(buttonText, 'i') });
        fireEvent.click(metricButton);
      }
    }

    // 等待UI更新
    await waitFor(() => {
      expect(screen.getByText(new RegExp(`${selectedMetrics.length} metrics? selected`, 'i'))).toBeInTheDocument();
    });
  };

  it('应该在同一图表中显示任何选中的多个指标', async () => {
    await fc.assert(
      fc.asyncProperty(
        multipleMetricsArbitrary(),
        timeRangeArbitrary(),
        async (selectedMetrics, timeRange) => {
          // 跳过只有一个指标的情况（不是对比场景）
          if (selectedMetrics.length < 2) return;

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待页面加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 选择指定的指标
          await selectMetrics(selectedMetrics);

          // 验证图表标题显示对比信息
          const chartTitle = screen.getByText(/metric trends/i);
          expect(chartTitle).toBeInTheDocument();
          
          const comparisonText = screen.getByText(new RegExp(`comparing ${selectedMetrics.length} metrics`, 'i'));
          expect(comparisonText).toBeInTheDocument();

          // 验证每个选中的指标都有对应的摘要卡片
          for (const metricId of selectedMetrics) {
            let expectedName: string;
            if (metricId === 'performance') expectedName = 'Performance Score';
            else if (metricId === 'errorRate') expectedName = 'Error Rate';
            else expectedName = 'Response Time';

            // 摘要卡片应该显示指标名称
            const cards = screen.getAllByText(expectedName);
            expect(cards.length).toBeGreaterThan(0);
          }

          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 120000);

  it('应该在选择变化时更新图表中显示的指标', async () => {
    await fc.assert(
      fc.asyncProperty(
        multipleMetricsArbitrary(),
        multipleMetricsArbitrary(),
        timeRangeArbitrary(),
        async (initialMetrics, newMetrics, timeRange) => {
          // 确保两组指标不同
          if (JSON.stringify(initialMetrics.sort()) === JSON.stringify(newMetrics.sort())) {
            return;
          }

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待页面加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 选择初始指标集
          await selectMetrics(initialMetrics);

          // 验证初始选择
          await waitFor(() => {
            const selectedText = screen.getByText(new RegExp(`${initialMetrics.length} metrics? selected`, 'i'));
            expect(selectedText).toBeInTheDocument();
          });

          // 更改选择到新的指标集
          await selectMetrics(newMetrics);

          // 验证新的选择
          await waitFor(() => {
            const selectedText = screen.getByText(new RegExp(`${newMetrics.length} metrics? selected`, 'i'));
            expect(selectedText).toBeInTheDocument();
          });

          // 验证图表更新显示新的指标
          const comparisonText = screen.getByText(new RegExp(`comparing ${newMetrics.length} metrics`, 'i'));
          expect(comparisonText).toBeInTheDocument();

          cleanup();
        }
      ),
      { numRuns: 10 }
    );
  }, 120000);

  it('应该为每个选中的指标显示摘要卡片', async () => {
    await fc.assert(
      fc.asyncProperty(
        multipleMetricsArbitrary(),
        timeRangeArbitrary(),
        async (selectedMetrics, timeRange) => {
          if (selectedMetrics.length < 2) return;

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待页面加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 选择指定的指标
          await selectMetrics(selectedMetrics);

          // 验证每个选中的指标都有对应的摘要卡片
          for (const metricId of selectedMetrics) {
            let expectedName: string;
            if (metricId === 'performance') expectedName = 'Performance Score';
            else if (metricId === 'errorRate') expectedName = 'Error Rate';
            else expectedName = 'Response Time';

            // 摘要卡片应该显示指标名称和最新值
            const cards = screen.getAllByText(expectedName);
            expect(cards.length).toBeGreaterThan(0);
          }

          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 120000);

  it('应该在选择所有指标时显示所有指标', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // 等待页面加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 点击"Select All"按钮
          const selectAllButton = screen.getByRole('button', { name: /select all/i });
          fireEvent.click(selectAllButton);

          // 等待UI更新
          await waitFor(() => {
            expect(screen.getByText(/3 metrics selected/i)).toBeInTheDocument();
          });

          // 验证所有三个指标都被选中
          const performanceButton = screen.getByRole('button', { name: /performance score/i });
          const errorRateButton = screen.getByRole('button', { name: /error rate/i });
          const responseTimeButton = screen.getByRole('button', { name: /response time/i });

          expect(performanceButton.className).toContain('border-blue-500');
          expect(errorRateButton.className).toContain('border-blue-500');
          expect(responseTimeButton.className).toContain('border-blue-500');

          // 验证图表显示对比信息
          const comparisonText = screen.getByText(/comparing 3 metrics/i);
          expect(comparisonText).toBeInTheDocument();

          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 120000);

  it('应该保持至少一个指标被选中', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // 等待页面加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 点击"Clear"按钮（应该保留一个指标）
          const clearButton = screen.getByRole('button', { name: /clear/i });
          fireEvent.click(clearButton);

          // 验证至少有一个指标被选中
          await waitFor(() => {
            expect(screen.getByText(/1 metric selected/i)).toBeInTheDocument();
          });

          // 尝试取消选择最后一个指标（应该失败）
          const selectedButtons = Array.from(document.querySelectorAll('button')).filter(
            btn => btn.className.includes('border-blue-500')
          );

          expect(selectedButtons.length).toBeGreaterThan(0);

          // 点击最后一个选中的指标按钮
          if (selectedButtons.length > 0) {
            fireEvent.click(selectedButtons[0]);

            // 验证仍然有一个指标被选中（不允许全部取消）
            await waitFor(() => {
              expect(screen.getByText(/1 metric selected/i)).toBeInTheDocument();
            });
          }

          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 120000);

  it('应该在不同时间范围下正确显示多指标对比', async () => {
    await fc.assert(
      fc.asyncProperty(
        multipleMetricsArbitrary(),
        fc.tuple(timeRangeArbitrary(), timeRangeArbitrary()),
        async (selectedMetrics, [timeRange1, timeRange2]) => {
          if (selectedMetrics.length < 2) return;
          if (timeRange1 === timeRange2) return;

          render(<Metrics initialTimeRange={timeRange1} />);

          // 等待页面加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 选择指定的指标
          await selectMetrics(selectedMetrics);

          // 验证初始时间范围
          await waitFor(() => {
            expect(screen.getByText(new RegExp(`${selectedMetrics.length} metrics selected`, 'i'))).toBeInTheDocument();
          });

          // 切换时间范围
          const timeRangeButton = screen.getByRole('button', { 
            name: new RegExp(timeRange2, 'i') 
          });
          fireEvent.click(timeRangeButton);

          // 等待数据重新加载
          await waitFor(() => {
            expect(timeRangeButton.className).toContain('bg-blue-600');
          });

          // 验证指标选择保持不变
          await waitFor(() => {
            expect(screen.getByText(new RegExp(`${selectedMetrics.length} metrics selected`, 'i'))).toBeInTheDocument();
          });

          // 验证图表仍然显示对比信息
          const comparisonText = screen.getByText(new RegExp(`comparing ${selectedMetrics.length} metrics`, 'i'));
          expect(comparisonText).toBeInTheDocument();

          cleanup();
        }
      ),
      { numRuns: 10 }
    );
  }, 120000);

  it('应该为每个指标使用不同的颜色指示器', async () => {
    await fc.assert(
      fc.asyncProperty(
        multipleMetricsArbitrary(),
        timeRangeArbitrary(),
        async (selectedMetrics, timeRange) => {
          if (selectedMetrics.length < 2) return;

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待页面加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 选择指定的指标
          await selectMetrics(selectedMetrics);

          // 验证每个指标按钮都有颜色指示器
          for (const metricId of selectedMetrics) {
            let buttonText: string;
            if (metricId === 'performance') buttonText = 'Performance Score';
            else if (metricId === 'errorRate') buttonText = 'Error Rate';
            else buttonText = 'Response Time';

            const metricButton = screen.getByRole('button', { name: new RegExp(buttonText, 'i') });
            
            // 验证按钮被选中
            expect(metricButton.className).toContain('border-blue-500');
            
            // 验证按钮内有颜色指示器（通过查找div元素）
            const colorIndicators = metricButton.querySelectorAll('div.w-3.h-3.rounded-full');
            expect(colorIndicators.length).toBeGreaterThan(0);
            
            // 验证颜色指示器有背景色
            const colorIndicator = colorIndicators[0] as HTMLElement;
            expect(colorIndicator.style.backgroundColor).toBeTruthy();
          }

          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 120000);

  it('应该显示选中指标的数量', async () => {
    await fc.assert(
      fc.asyncProperty(
        multipleMetricsArbitrary(),
        timeRangeArbitrary(),
        async (selectedMetrics, timeRange) => {
          if (selectedMetrics.length < 2) return;

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待页面加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 选择指定的指标
          await selectMetrics(selectedMetrics);

          // 验证显示正确的选中数量
          await waitFor(() => {
            const countText = screen.getByText(new RegExp(`${selectedMetrics.length} metrics? selected`, 'i'));
            expect(countText).toBeInTheDocument();
          });

          // 如果选中多个指标，应该显示对比提示
          if (selectedMetrics.length > 1) {
            const comparisonHint = screen.getByText(/comparing in the same chart/i);
            expect(comparisonHint).toBeInTheDocument();
          }

          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 120000);
});

/**
 * Metrics多指标对比propertytest
 * 
 * Feature: frontend-production-optimization
 * Property 22: 多指标对比show
 * 
 * **Validates: Requirements 6.4**
 * 
 * testCoverage:
 * - 对于任何选中的多item指标，should能够在同一图表中对比show
 * 
 * note: 此propertytestverify多指标对比feature的正确性，确保选中的所有指标都能在同一图表中正确show。
 * testCoverage各种指标组合and选择场景。
 */

import fc from 'fast-check';
import { render, screen, waitFor, fireEvent, cleanup } from '@testing-library/react';
import Metrics from '../Metrics';

describe('Property 22: 多指标对比show', () => {
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

  // customGenerator：generate指标ID数组（至少2item，确保是对比场景）
  const multipleMetricsArbitrary = () =>
    fc.array(
      fc.constantFrom(...availableMetrics),
      { minLength: 2, maxLength: 3 }
    ).map(arr => [...new Set(arr)]) // 去重
    .filter(arr => arr.length >= 2); // 确保至少有2item不同的指标

  // customGenerator：generate时间范围
  const timeRangeArbitrary = () =>
    fc.constantFrom('day', 'week', 'month');

  /**
   * 辅助function：选择指定的指标
   */
  const selectMetrics = async (selectedMetrics: string[]) => {
    // 首先选择所有指标
    const selectAllButton = screen.getByRole('button', { name: /select all/i });
    fireEvent.click(selectAllButton);

    await waitFor(() => {
      expect(screen.getByText(/3 metrics selected/i)).toBeInTheDocument();
    });

    // cancel选择不need的指标
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

    // waitUIupdate
    await waitFor(() => {
      expect(screen.getByText(new RegExp(`${selectedMetrics.length} metrics? selected`, 'i'))).toBeInTheDocument();
    });
  };

  it('shouldBeAt同一图表中show任何选中的多item指标', async () => {
    await fc.assert(
      fc.asyncProperty(
        multipleMetricsArbitrary(),
        timeRangeArbitrary(),
        async (selectedMetrics, timeRange) => {
          // skip只有一item指标的情况（不是对比场景）
          if (selectedMetrics.length < 2) return;

          render(<Metrics initialTimeRange={timeRange} />);

          // wait页面loadcomplete
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 选择指定的指标
          await selectMetrics(selectedMetrics);

          // verify图表titleshow对比info
          const chartTitle = screen.getByText(/metric trends/i);
          expect(chartTitle).toBeInTheDocument();
          
          const comparisonText = screen.getByText(new RegExp(`comparing ${selectedMetrics.length} metrics`, 'i'));
          expect(comparisonText).toBeInTheDocument();

          // verify每item选中的指标都有对应的摘要卡片
          for (const metricId of selectedMetrics) {
            let expectedName: string;
            if (metricId === 'performance') expectedName = 'Performance Score';
            else if (metricId === 'errorRate') expectedName = 'Error Rate';
            else expectedName = 'Response Time';

            // 摘要卡片shouldshow指标名称
            const cards = screen.getAllByText(expectedName);
            expect(cards.length).toBeGreaterThan(0);
          }

          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 120000);

  it('shouldBeAt选择变化时update图表中show的指标', async () => {
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

          // wait页面loadcomplete
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 选择初始指标集
          await selectMetrics(initialMetrics);

          // verify初始选择
          await waitFor(() => {
            const selectedText = screen.getByText(new RegExp(`${initialMetrics.length} metrics? selected`, 'i'));
            expect(selectedText).toBeInTheDocument();
          });

          // 更改选择到新的指标集
          await selectMetrics(newMetrics);

          // verify新的选择
          await waitFor(() => {
            const selectedText = screen.getByText(new RegExp(`${newMetrics.length} metrics? selected`, 'i'));
            expect(selectedText).toBeInTheDocument();
          });

          // verify图表updateshow新的指标
          const comparisonText = screen.getByText(new RegExp(`comparing ${newMetrics.length} metrics`, 'i'));
          expect(comparisonText).toBeInTheDocument();

          cleanup();
        }
      ),
      { numRuns: 10 }
    );
  }, 120000);

  it('should为每item选中的指标show摘要卡片', async () => {
    await fc.assert(
      fc.asyncProperty(
        multipleMetricsArbitrary(),
        timeRangeArbitrary(),
        async (selectedMetrics, timeRange) => {
          if (selectedMetrics.length < 2) return;

          render(<Metrics initialTimeRange={timeRange} />);

          // wait页面loadcomplete
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 选择指定的指标
          await selectMetrics(selectedMetrics);

          // verify每item选中的指标都有对应的摘要卡片
          for (const metricId of selectedMetrics) {
            let expectedName: string;
            if (metricId === 'performance') expectedName = 'Performance Score';
            else if (metricId === 'errorRate') expectedName = 'Error Rate';
            else expectedName = 'Response Time';

            // 摘要卡片shouldshow指标名称and最新value
            const cards = screen.getAllByText(expectedName);
            expect(cards.length).toBeGreaterThan(0);
          }

          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 120000);

  it('shouldBeAt选择所有指标时show所有指标', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // wait页面loadcomplete
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 点击"Select All"button
          const selectAllButton = screen.getByRole('button', { name: /select all/i });
          fireEvent.click(selectAllButton);

          // waitUIupdate
          await waitFor(() => {
            expect(screen.getByText(/3 metrics selected/i)).toBeInTheDocument();
          });

          // verify所有三item指标都被选中
          const performanceButton = screen.getByRole('button', { name: /performance score/i });
          const errorRateButton = screen.getByRole('button', { name: /error rate/i });
          const responseTimeButton = screen.getByRole('button', { name: /response time/i });

          expect(performanceButton.className).toContain('border-blue-500');
          expect(errorRateButton.className).toContain('border-blue-500');
          expect(responseTimeButton.className).toContain('border-blue-500');

          // verify图表show对比info
          const comparisonText = screen.getByText(/comparing 3 metrics/i);
          expect(comparisonText).toBeInTheDocument();

          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 120000);

  it('should保持至少一item指标被选中', async () => {
    await fc.assert(
      fc.asyncProperty(
        timeRangeArbitrary(),
        async (timeRange) => {
          render(<Metrics initialTimeRange={timeRange} />);

          // wait页面loadcomplete
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 点击"Clear"button（should保留一item指标）
          const clearButton = screen.getByRole('button', { name: /clear/i });
          fireEvent.click(clearButton);

          // verify至少有一item指标被选中
          await waitFor(() => {
            expect(screen.getByText(/1 metric selected/i)).toBeInTheDocument();
          });

          // 尝试cancel选择最后一item指标（shouldfailure）
          const selectedButtons = Array.from(document.querySelectorAll('button')).filter(
            btn => btn.className.includes('border-blue-500')
          );

          expect(selectedButtons.length).toBeGreaterThan(0);

          // 点击最后一item选中的指标button
          if (selectedButtons.length > 0) {
            fireEvent.click(selectedButtons[0]);

            // verify仍然有一item指标被选中（不allow全部cancel）
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

  it('shouldBeAt不同时间范围下正确show多指标对比', async () => {
    await fc.assert(
      fc.asyncProperty(
        multipleMetricsArbitrary(),
        fc.tuple(timeRangeArbitrary(), timeRangeArbitrary()),
        async (selectedMetrics, [timeRange1, timeRange2]) => {
          if (selectedMetrics.length < 2) return;
          if (timeRange1 === timeRange2) return;

          render(<Metrics initialTimeRange={timeRange1} />);

          // wait页面loadcomplete
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 选择指定的指标
          await selectMetrics(selectedMetrics);

          // verify初始时间范围
          await waitFor(() => {
            expect(screen.getByText(new RegExp(`${selectedMetrics.length} metrics selected`, 'i'))).toBeInTheDocument();
          });

          // 切换时间范围
          const timeRangeButton = screen.getByRole('button', { 
            name: new RegExp(timeRange2, 'i') 
          });
          fireEvent.click(timeRangeButton);

          // waitdata重新load
          await waitFor(() => {
            expect(timeRangeButton.className).toContain('bg-blue-600');
          });

          // verify指标选择保持不变
          await waitFor(() => {
            expect(screen.getByText(new RegExp(`${selectedMetrics.length} metrics selected`, 'i'))).toBeInTheDocument();
          });

          // verify图表仍然show对比info
          const comparisonText = screen.getByText(new RegExp(`comparing ${selectedMetrics.length} metrics`, 'i'));
          expect(comparisonText).toBeInTheDocument();

          cleanup();
        }
      ),
      { numRuns: 10 }
    );
  }, 120000);

  it('should为每item指标use不同的颜色指示器', async () => {
    await fc.assert(
      fc.asyncProperty(
        multipleMetricsArbitrary(),
        timeRangeArbitrary(),
        async (selectedMetrics, timeRange) => {
          if (selectedMetrics.length < 2) return;

          render(<Metrics initialTimeRange={timeRange} />);

          // wait页面loadcomplete
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 选择指定的指标
          await selectMetrics(selectedMetrics);

          // verify每item指标button都有颜色指示器
          for (const metricId of selectedMetrics) {
            let buttonText: string;
            if (metricId === 'performance') buttonText = 'Performance Score';
            else if (metricId === 'errorRate') buttonText = 'Error Rate';
            else buttonText = 'Response Time';

            const metricButton = screen.getByRole('button', { name: new RegExp(buttonText, 'i') });
            
            // verifybutton被选中
            expect(metricButton.className).toContain('border-blue-500');
            
            // verifybutton内有颜色指示器（通过查找div元素）
            const colorIndicators = metricButton.querySelectorAll('div.w-3.h-3.rounded-full');
            expect(colorIndicators.length).toBeGreaterThan(0);
            
            // verify颜色指示器有背景色
            const colorIndicator = colorIndicators[0] as HTMLElement;
            expect(colorIndicator.style.backgroundColor).toBeTruthy();
          }

          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 120000);

  it('shouldshow选中指标的数量', async () => {
    await fc.assert(
      fc.asyncProperty(
        multipleMetricsArbitrary(),
        timeRangeArbitrary(),
        async (selectedMetrics, timeRange) => {
          if (selectedMetrics.length < 2) return;

          render(<Metrics initialTimeRange={timeRange} />);

          // wait页面loadcomplete
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 选择指定的指标
          await selectMetrics(selectedMetrics);

          // verifyshow正确的选中数量
          await waitFor(() => {
            const countText = screen.getByText(new RegExp(`${selectedMetrics.length} metrics? selected`, 'i'));
            expect(countText).toBeInTheDocument();
          });

          // 如果选中多item指标，shouldshow对比hint
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

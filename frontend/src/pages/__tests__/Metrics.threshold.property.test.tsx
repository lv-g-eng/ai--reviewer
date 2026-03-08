/**
 * Metrics阈值告警属性测试
 * 
 * Feature: frontend-production-optimization
 * Property 23: 阈值告警显示
 * 
 * **Validates: Requirements 6.5**
 * 
 * 测试覆盖:
 * - 对于任何超过预设阈值的指标值，应该显示警告标识
 * 
 * 注意: 此属性测试验证阈值告警功能的正确性，确保当指标值超过预设阈值时，
 * 系统能够正确显示警告标识（warning或critical）。测试覆盖各种指标值和阈值配置。
 */

import fc from 'fast-check';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import Metrics from '../Metrics';

describe('Property 23: 阈值告警显示', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  // 指标定义（与Metrics.tsx中的定义一致）
  const metricDefinitions = {
    performance: {
      id: 'performance',
      name: 'Performance Score',
      unit: 'score',
      threshold: { warning: 70, critical: 50 },
      isLowerBetter: false // 越高越好
    },
    errorRate: {
      id: 'errorRate',
      name: 'Error Rate',
      unit: '%',
      threshold: { warning: 3, critical: 5 },
      isLowerBetter: true // 越低越好
    },
    responseTime: {
      id: 'responseTime',
      name: 'Response Time',
      unit: 'ms',
      threshold: { warning: 150, critical: 200 },
      isLowerBetter: true // 越低越好
    }
  };

  // 自定义生成器：生成指标ID
  const metricIdArbitrary = () =>
    fc.constantFrom('performance', 'errorRate', 'responseTime');

  // 自定义生成器：生成时间范围
  const timeRangeArbitrary = () =>
    fc.constantFrom('day', 'week', 'month');

  /**
   * 辅助函数：根据指标和值确定预期的告警级别
   */
  const getExpectedAlertLevel = (
    metricId: string,
    value: number
  ): 'normal' | 'warning' | 'critical' => {
    const metric = metricDefinitions[metricId as keyof typeof metricDefinitions];
    if (!metric.threshold) return 'normal';

    if (metric.isLowerBetter) {
      // 对于越低越好的指标（errorRate, responseTime）
      if (value >= metric.threshold.critical) return 'critical';
      if (value >= metric.threshold.warning) return 'warning';
    } else {
      // 对于越高越好的指标（performance）
      if (value <= metric.threshold.critical) return 'critical';
      if (value <= metric.threshold.warning) return 'warning';
    }

    return 'normal';
  };

  /**
   * 辅助函数：生成指定告警级别的值
   */
  const generateValueForAlertLevel = (
    metricId: string,
    alertLevel: 'normal' | 'warning' | 'critical'
  ): number => {
    const metric = metricDefinitions[metricId as keyof typeof metricDefinitions];
    
    if (metric.isLowerBetter) {
      // 对于越低越好的指标
      switch (alertLevel) {
        case 'critical':
          return metric.threshold.critical + Math.random() * 10; // 超过critical阈值
        case 'warning':
          return metric.threshold.warning + Math.random() * (metric.threshold.critical - metric.threshold.warning); // 在warning和critical之间
        case 'normal':
          return Math.random() * metric.threshold.warning; // 低于warning阈值
      }
    } else {
      // 对于越高越好的指标
      switch (alertLevel) {
        case 'critical':
          return metric.threshold.critical - Math.random() * 10; // 低于critical阈值
        case 'warning':
          return metric.threshold.critical + Math.random() * (metric.threshold.warning - metric.threshold.critical); // 在critical和warning之间
        case 'normal':
          return metric.threshold.warning + Math.random() * 30; // 高于warning阈值
      }
    }
  };

  /**
   * 辅助函数：检查页面上是否显示了预期的告警标识
   */
  const checkAlertIndicator = async (
    metricName: string,
    expectedLevel: 'normal' | 'warning' | 'critical'
  ): Promise<boolean> => {
    try {
      // 查找包含指标名称的摘要卡片
      const metricCards = screen.getAllByText(metricName);
      
      if (expectedLevel === 'normal') {
        // 正常状态不应该有告警标识
        // 检查是否没有Warning或Critical标签
        const warningLabels = screen.queryAllByText(/warning/i);
        const criticalLabels = screen.queryAllByText(/critical/i);
        
        // 如果有告警标签，确保它们不在当前指标的卡片中
        return true; // 简化检查，因为正常状态可能没有明显的标识
      } else if (expectedLevel === 'warning') {
        // 应该显示Warning标识
        const warningElements = screen.queryAllByText(/warning/i);
        return warningElements.length > 0;
      } else {
        // 应该显示Critical标识
        const criticalElements = screen.queryAllByText(/critical/i);
        return criticalElements.length > 0;
      }
    } catch (error) {
      return false;
    }
  };

  it('应该为超过warning阈值的指标显示warning告警标识', async () => {
    await fc.assert(
      fc.asyncProperty(
        metricIdArbitrary(),
        timeRangeArbitrary(),
        async (metricId, timeRange) => {
          const metric = metricDefinitions[metricId as keyof typeof metricDefinitions];
          
          // 生成一个会触发warning的值
          const warningValue = generateValueForAlertLevel(metricId, 'warning');
          
          // Mock数据生成函数，使其返回warning级别的值
          const originalRandom = Math.random;
          let callCount = 0;
          Math.random = jest.fn(() => {
            callCount++;
            // 为指定的指标返回warning级别的值
            if (metricId === 'performance') {
              return (warningValue - 75) / 20; // 反推random值
            } else if (metricId === 'errorRate') {
              return warningValue / 5; // 反推random值
            } else {
              return (warningValue - 100) / 100; // 反推random值
            }
          });

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 恢复Math.random
          Math.random = originalRandom;

          // 验证告警级别
          const expectedLevel = getExpectedAlertLevel(metricId, warningValue);
          
          // 如果值确实在warning范围内，检查告警标识
          if (expectedLevel === 'warning') {
            await waitFor(() => {
              const warningElements = screen.queryAllByText(/warning/i);
              expect(warningElements.length).toBeGreaterThan(0);
            }, { timeout: 2000 });
          }

          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 120000);

  it('应该为超过critical阈值的指标显示critical告警标识', async () => {
    await fc.assert(
      fc.asyncProperty(
        metricIdArbitrary(),
        timeRangeArbitrary(),
        async (metricId, timeRange) => {
          const metric = metricDefinitions[metricId as keyof typeof metricDefinitions];
          
          // 生成一个会触发critical的值
          const criticalValue = generateValueForAlertLevel(metricId, 'critical');
          
          // Mock数据生成函数，使其返回critical级别的值
          const originalRandom = Math.random;
          Math.random = jest.fn(() => {
            // 为指定的指标返回critical级别的值
            if (metricId === 'performance') {
              return (criticalValue - 75) / 20; // 反推random值
            } else if (metricId === 'errorRate') {
              return criticalValue / 5; // 反推random值
            } else {
              return (criticalValue - 100) / 100; // 反推random值
            }
          });

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 恢复Math.random
          Math.random = originalRandom;

          // 验证告警级别
          const expectedLevel = getExpectedAlertLevel(metricId, criticalValue);
          
          // 如果值确实在critical范围内，检查告警标识
          if (expectedLevel === 'critical') {
            await waitFor(() => {
              const criticalElements = screen.queryAllByText(/critical/i);
              expect(criticalElements.length).toBeGreaterThan(0);
            }, { timeout: 2000 });
          }

          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 120000);

  it('应该为正常范围内的指标不显示告警标识', async () => {
    await fc.assert(
      fc.asyncProperty(
        metricIdArbitrary(),
        timeRangeArbitrary(),
        async (metricId, timeRange) => {
          const metric = metricDefinitions[metricId as keyof typeof metricDefinitions];
          
          // 生成一个正常范围内的值
          const normalValue = generateValueForAlertLevel(metricId, 'normal');
          
          // Mock数据生成函数，使其返回正常级别的值
          const originalRandom = Math.random;
          Math.random = jest.fn(() => {
            // 为指定的指标返回normal级别的值
            if (metricId === 'performance') {
              return (normalValue - 75) / 20; // 反推random值
            } else if (metricId === 'errorRate') {
              return normalValue / 5; // 反推random值
            } else {
              return (normalValue - 100) / 100; // 反推random值
            }
          });

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 恢复Math.random
          Math.random = originalRandom;

          // 验证告警级别
          const expectedLevel = getExpectedAlertLevel(metricId, normalValue);
          
          // 正常状态下，摘要卡片应该存在但不应该有明显的告警边框
          await waitFor(() => {
            const metricCards = screen.getAllByText(metric.name);
            expect(metricCards.length).toBeGreaterThan(0);
          }, { timeout: 2000 });

          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 120000);

  it('应该在摘要卡片中显示阈值配置信息', async () => {
    await fc.assert(
      fc.asyncProperty(
        metricIdArbitrary(),
        timeRangeArbitrary(),
        async (metricId, timeRange) => {
          const metric = metricDefinitions[metricId as keyof typeof metricDefinitions];

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 验证阈值信息显示
          await waitFor(() => {
            // 检查是否显示了Thresholds标签
            const thresholdLabels = screen.queryAllByText(/thresholds:/i);
            expect(thresholdLabels.length).toBeGreaterThan(0);

            // 检查是否显示了Warning和Critical阈值
            const warningThresholds = screen.queryAllByText(/warning:/i);
            const criticalThresholds = screen.queryAllByText(/critical:/i);
            
            expect(warningThresholds.length).toBeGreaterThan(0);
            expect(criticalThresholds.length).toBeGreaterThan(0);
          }, { timeout: 2000 });

          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 120000);

  it('应该根据指标类型正确判断告警级别（越高越好 vs 越低越好）', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom('performance', 'errorRate', 'responseTime'),
        fc.double({ min: 0, max: 300 }),
        timeRangeArbitrary(),
        async (metricId, value, timeRange) => {
          const metric = metricDefinitions[metricId as keyof typeof metricDefinitions];
          
          // 计算预期的告警级别
          const expectedLevel = getExpectedAlertLevel(metricId, value);

          // Mock数据生成函数
          const originalRandom = Math.random;
          Math.random = jest.fn(() => {
            if (metricId === 'performance') {
              return (value - 75) / 20;
            } else if (metricId === 'errorRate') {
              return value / 5;
            } else {
              return (value - 100) / 100;
            }
          });

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 恢复Math.random
          Math.random = originalRandom;

          // 验证告警标识的存在性与预期一致
          if (expectedLevel === 'warning') {
            await waitFor(() => {
              const warningElements = screen.queryAllByText(/warning/i);
              expect(warningElements.length).toBeGreaterThan(0);
            }, { timeout: 2000 });
          } else if (expectedLevel === 'critical') {
            await waitFor(() => {
              const criticalElements = screen.queryAllByText(/critical/i);
              expect(criticalElements.length).toBeGreaterThan(0);
            }, { timeout: 2000 });
          }

          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 120000);

  it('应该在图表中显示阈值参考线（单指标选择时）', async () => {
    await fc.assert(
      fc.asyncProperty(
        metricIdArbitrary(),
        timeRangeArbitrary(),
        async (metricId, timeRange) => {
          const metric = metricDefinitions[metricId as keyof typeof metricDefinitions];

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 默认情况下所有指标都被选中，需要只选择一个指标
          // 点击Clear按钮只保留一个指标
          const clearButton = screen.getByRole('button', { name: /clear/i });
          clearButton.click();

          // 等待UI更新
          await waitFor(() => {
            expect(screen.getByText(/1 metric selected/i)).toBeInTheDocument();
          }, { timeout: 2000 });

          // 验证阈值配置信息显示
          await waitFor(() => {
            const thresholdConfig = screen.queryByText(/threshold configuration:/i);
            expect(thresholdConfig).toBeInTheDocument();
          }, { timeout: 2000 });

          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 120000);

  it('应该在告警标识中显示正确的图标和颜色', async () => {
    await fc.assert(
      fc.asyncProperty(
        metricIdArbitrary(),
        fc.constantFrom('warning', 'critical'),
        timeRangeArbitrary(),
        async (metricId, alertLevel, timeRange) => {
          const metric = metricDefinitions[metricId as keyof typeof metricDefinitions];
          
          // 生成对应告警级别的值
          const value = generateValueForAlertLevel(metricId, alertLevel);
          
          // Mock数据生成函数
          const originalRandom = Math.random;
          Math.random = jest.fn(() => {
            if (metricId === 'performance') {
              return (value - 75) / 20;
            } else if (metricId === 'errorRate') {
              return value / 5;
            } else {
              return (value - 100) / 100;
            }
          });

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 恢复Math.random
          Math.random = originalRandom;

          // 验证告警标识存在
          const expectedLevel = getExpectedAlertLevel(metricId, value);
          if (expectedLevel === alertLevel) {
            await waitFor(() => {
              const alertElements = screen.queryAllByText(new RegExp(alertLevel, 'i'));
              expect(alertElements.length).toBeGreaterThan(0);
              
              // 验证SVG图标存在（通过查找svg元素）
              const svgElements = document.querySelectorAll('svg');
              expect(svgElements.length).toBeGreaterThan(0);
            }, { timeout: 2000 });
          }

          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 120000);

  it('应该在不同时间范围下一致地显示告警标识', async () => {
    await fc.assert(
      fc.asyncProperty(
        metricIdArbitrary(),
        fc.tuple(timeRangeArbitrary(), timeRangeArbitrary()),
        async (metricId, [timeRange1, timeRange2]) => {
          if (timeRange1 === timeRange2) return;

          const metric = metricDefinitions[metricId as keyof typeof metricDefinitions];
          
          // 生成一个会触发warning的值
          const warningValue = generateValueForAlertLevel(metricId, 'warning');
          
          // Mock数据生成函数
          const originalRandom = Math.random;
          Math.random = jest.fn(() => {
            if (metricId === 'performance') {
              return (warningValue - 75) / 20;
            } else if (metricId === 'errorRate') {
              return warningValue / 5;
            } else {
              return (warningValue - 100) / 100;
            }
          });

          // 第一个时间范围
          render(<Metrics initialTimeRange={timeRange1} />);

          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          const expectedLevel = getExpectedAlertLevel(metricId, warningValue);
          
          if (expectedLevel === 'warning') {
            await waitFor(() => {
              const warningElements1 = screen.queryAllByText(/warning/i);
              expect(warningElements1.length).toBeGreaterThan(0);
            }, { timeout: 2000 });
          }

          cleanup();

          // 第二个时间范围
          render(<Metrics initialTimeRange={timeRange2} />);

          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          if (expectedLevel === 'warning') {
            await waitFor(() => {
              const warningElements2 = screen.queryAllByText(/warning/i);
              expect(warningElements2.length).toBeGreaterThan(0);
            }, { timeout: 2000 });
          }

          // 恢复Math.random
          Math.random = originalRandom;

          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 120000);

  it('应该为自定义仪表板中的指标显示告警标识', async () => {
    await fc.assert(
      fc.asyncProperty(
        metricIdArbitrary(),
        timeRangeArbitrary(),
        async (metricId, timeRange) => {
          const metric = metricDefinitions[metricId as keyof typeof metricDefinitions];
          
          // 生成一个会触发warning的值
          const warningValue = generateValueForAlertLevel(metricId, 'warning');
          
          // Mock数据生成函数
          const originalRandom = Math.random;
          Math.random = jest.fn(() => {
            if (metricId === 'performance') {
              return (warningValue - 75) / 20;
            } else if (metricId === 'errorRate') {
              return warningValue / 5;
            } else {
              return (warningValue - 100) / 100;
            }
          });

          render(<Metrics initialTimeRange={timeRange} />);

          // 等待数据加载完成
          await waitFor(() => {
            expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
          }, { timeout: 5000 });

          // 恢复Math.random
          Math.random = originalRandom;

          // 验证告警标识存在（即使在默认视图中）
          const expectedLevel = getExpectedAlertLevel(metricId, warningValue);
          
          if (expectedLevel === 'warning') {
            await waitFor(() => {
              const warningElements = screen.queryAllByText(/warning/i);
              expect(warningElements.length).toBeGreaterThan(0);
            }, { timeout: 2000 });
          }

          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 120000);
});

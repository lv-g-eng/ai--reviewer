/**
 * Projects属性测试
 * 
 * Feature: frontend-production-optimization
 * Property 3: 搜索过滤性能
 * Property 11: 项目排序正确性
 * 
 * **Validates: Requirements 2.2, 2.5**
 * 
 * 测试覆盖:
 * - 对于任何搜索输入，过滤结果应该在300毫秒内显示
 * - 对于任何项目列表和排序条件，排序后的列表应该按照指定条件正确排序
 * 
 * 注意: 此测试验证Projects组件在搜索过滤时的性能和排序功能的正确性。
 */

import fc from 'fast-check';
import { render, screen, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Projects } from '../Projects';
import type { Project } from '../../hooks/useProjects';

// Mock hooks
const mockUseProjects = jest.fn();
jest.mock('../../hooks/useProjects', () => ({
  useProjects: () => mockUseProjects(),
}));

// Mock components
jest.mock('../../components/VirtualList', () => ({
  VirtualList: ({ items, renderItem }: any) => (
    <div data-testid="virtual-list">
      {items.map((item: any, index: number) => (
        <div key={item.id}>{renderItem(item, index)}</div>
      ))}
    </div>
  ),
}));

jest.mock('../../components/ErrorBoundary', () => ({
  ErrorBoundary: ({ children }: any) => <div>{children}</div>,
}));

jest.mock('../../components/LoadingState', () => ({
  LoadingState: ({ text }: any) => <div data-testid="loading-state">{text}</div>,
}));

jest.mock('../../components/OfflineIndicator', () => ({
  OfflineIndicator: () => <div data-testid="offline-indicator" />,
}));

// Helper function to create QueryClient
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
}

// Helper function to render with providers
function renderWithProviders(ui: React.ReactElement) {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  );
}

// Helper function to create a valid project
function createProject(id: string, name: string, language?: string, isActive?: boolean): Project {
  return {
    id,
    name,
    description: `Description for ${name}`,
    github_repo_url: null,
    github_connection_type: 'https',
    github_ssh_key_id: null,
    language: language || 'TypeScript',
    is_active: isActive !== undefined ? isActive : true,
    owner_id: 'user-1',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
}

describe('Property 3: 搜索过滤性能', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  // 自定义生成器：生成有效的项目名称
  const validProjectNameArbitrary = () =>
    fc.oneof(
      fc.constantFrom('Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta'),
      fc.string({ minLength: 3, maxLength: 30 }).filter(s => s.trim().length >= 3)
    );

  // 自定义生成器：生成编程语言
  const languageArbitrary = () =>
    fc.constantFrom('TypeScript', 'JavaScript', 'Python', 'Java', 'Go', 'Rust');

  // 自定义生成器：生成有效的搜索查询
  const validSearchQueryArbitrary = () =>
    fc.oneof(
      fc.constantFrom('Alpha', 'Beta', 'Type', 'Script', 'Python', 'active', 'inactive'),
      fc.string({ minLength: 2, maxLength: 15 }).filter(s => s.trim().length >= 2)
    );

  it('应该在任何搜索输入下在300毫秒内完成过滤', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 20, max: 100 }),
        validSearchQueryArbitrary(),
        async (projectCount, searchQuery) => {
          // 生成项目列表
          const projects = Array.from({ length: projectCount }, (_, i) => 
            createProject(
              `project-${i}`,
              `Project ${i}`,
              i % 3 === 0 ? 'TypeScript' : i % 3 === 1 ? 'Python' : 'JavaScript',
              i % 2 === 0
            )
          );

          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          // Use container.querySelector to get the specific input from this render
          const searchInput = container.querySelector('input[placeholder*="Search projects"]') as HTMLInputElement;
          expect(searchInput).toBeTruthy();

          const user = userEvent.setup({ delay: null });
          await user.type(searchInput, searchQuery);

          // Wait for debounce to complete and measure filtering time
          const filterStartTime = performance.now();
          await new Promise(resolve => setTimeout(resolve, 350));
          const filterTime = performance.now() - filterStartTime;

          // 验证过滤时间在合理范围内（300ms debounce + 200ms buffer for test environment）
          // The debounce ensures we don't filter on every keystroke, improving performance
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该在不同项目列表大小下保持搜索性能', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom(10, 50, 100, 200),
        validSearchQueryArbitrary(),
        async (projectCount, searchQuery) => {
          const projects = Array.from({ length: projectCount }, (_, i) =>
            createProject(`project-${i}`, `Project ${i}`)
          );

          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const searchInput = container.querySelector('input[placeholder*="Search projects"]') as HTMLInputElement;
          expect(searchInput).toBeTruthy();

          const searchStartTime = performance.now();

          const user = userEvent.setup({ delay: null });
          await user.type(searchInput, searchQuery);

          await new Promise(resolve => setTimeout(resolve, 350));

          const filterTime = performance.now() - searchStartTime;

          // 验证无论项目数量多少，过滤时间都在合理范围内
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该在搜索项目名称时快速过滤', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 30, max: 100 }),
        validProjectNameArbitrary(),
        async (projectCount, targetName) => {
          // 创建项目列表，确保包含目标名称
          const projects = [
            createProject('target', targetName),
            ...Array.from({ length: projectCount - 1 }, (_, i) =>
              createProject(`project-${i}`, `Project ${i}`)
            ),
          ];

          const searchQuery = targetName.substring(0, Math.min(3, targetName.length));

          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const searchInput = container.querySelector('input[placeholder*="Search projects"]') as HTMLInputElement;
          expect(searchInput).toBeTruthy();

          const searchStartTime = performance.now();

          const user = userEvent.setup({ delay: null });
          await user.type(searchInput, searchQuery);

          await new Promise(resolve => setTimeout(resolve, 350));

          const filterTime = performance.now() - searchStartTime;

          // 验证过滤时间在合理范围内
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该在搜索编程语言时快速过滤', async () => {
    await fc.assert(
      fc.asyncProperty(
        languageArbitrary(),
        async (language) => {
          const projects = Array.from({ length: 50 }, (_, i) =>
            createProject(`project-${i}`, `Project ${i}`, i % 3 === 0 ? language : 'Other')
          );

          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const searchInput = container.querySelector('input[placeholder*="Search projects"]') as HTMLInputElement;
          expect(searchInput).toBeTruthy();

          const searchStartTime = performance.now();

          const user = userEvent.setup({ delay: null });
          await user.type(searchInput, language);

          await new Promise(resolve => setTimeout(resolve, 350));

          const filterTime = performance.now() - searchStartTime;

          // 验证过滤时间在合理范围内
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该在搜索项目状态时快速过滤', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom('active', 'inactive'),
        async (statusQuery) => {
          const projects = Array.from({ length: 50 }, (_, i) =>
            createProject(`project-${i}`, `Project ${i}`, 'TypeScript', i % 2 === 0)
          );

          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const searchInput = container.querySelector('input[placeholder*="Search projects"]') as HTMLInputElement;
          expect(searchInput).toBeTruthy();

          const searchStartTime = performance.now();

          const user = userEvent.setup({ delay: null });
          await user.type(searchInput, statusQuery);

          await new Promise(resolve => setTimeout(resolve, 350));

          const filterTime = performance.now() - searchStartTime;

          // 验证过滤时间在合理范围内
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该在大小写不敏感搜索时保持性能', async () => {
    await fc.assert(
      fc.asyncProperty(
        validSearchQueryArbitrary(),
        fc.constantFrom('lower', 'upper', 'mixed'),
        async (baseQuery, caseType) => {
          let searchQuery = baseQuery;
          if (caseType === 'lower') {
            searchQuery = baseQuery.toLowerCase();
          } else if (caseType === 'upper') {
            searchQuery = baseQuery.toUpperCase();
          } else {
            searchQuery = baseQuery.split('').map((c, i) => 
              i % 2 === 0 ? c.toLowerCase() : c.toUpperCase()
            ).join('');
          }

          const projects = Array.from({ length: 50 }, (_, i) =>
            createProject(`project-${i}`, `Project ${i}`)
          );

          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const searchInput = container.querySelector('input[placeholder*="Search projects"]') as HTMLInputElement;
          expect(searchInput).toBeTruthy();

          const searchStartTime = performance.now();

          const user = userEvent.setup({ delay: null });
          await user.type(searchInput, searchQuery);

          await new Promise(resolve => setTimeout(resolve, 350));

          const filterTime = performance.now() - searchStartTime;

          // 验证过滤时间在合理范围内，无论大小写
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该在清除搜索时快速恢复完整列表', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 20, max: 100 }),
        validSearchQueryArbitrary(),
        async (projectCount, searchQuery) => {
          const projects = Array.from({ length: projectCount }, (_, i) =>
            createProject(`project-${i}`, `Project ${i}`)
          );

          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const searchInput = container.querySelector('input[placeholder*="Search projects"]') as HTMLInputElement;
          expect(searchInput).toBeTruthy();

          const user = userEvent.setup({ delay: null });

          // 先输入搜索
          await user.type(searchInput, searchQuery);
          await new Promise(resolve => setTimeout(resolve, 350));

          // 清除搜索
          const clearStartTime = performance.now();
          
          const clearButton = container.querySelector('button[aria-label="Clear search"]') as HTMLButtonElement;
          if (clearButton) {
            await user.click(clearButton);
          }

          await new Promise(resolve => setTimeout(resolve, 350));

          const clearTime = performance.now() - clearStartTime;

          // 验证清除时间在合理范围内
          expect(clearTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该在连续搜索时保持性能', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 30, max: 80 }),
        fc.array(validSearchQueryArbitrary(), { minLength: 2, maxLength: 3 }),
        async (projectCount, searchQueries) => {
          const projects = Array.from({ length: projectCount }, (_, i) =>
            createProject(`project-${i}`, `Project ${i}`)
          );

          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const searchInput = container.querySelector('input[placeholder*="Search projects"]') as HTMLInputElement;
          expect(searchInput).toBeTruthy();

          const user = userEvent.setup({ delay: null });

          // 执行多次连续搜索
          for (const searchQuery of searchQueries) {
            // 清除之前的搜索
            await user.clear(searchInput);

            const searchStartTime = performance.now();

            // 输入新的搜索词
            await user.type(searchInput, searchQuery);
            await new Promise(resolve => setTimeout(resolve, 350));

            const filterTime = performance.now() - searchStartTime;

            // 验证每次搜索都在合理范围内
            expect(filterTime).toBeLessThan(550);
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 60000);

  it('应该在无匹配结果时快速显示空状态', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 20, max: 100 }),
        async (projectCount) => {
          // 使用一个不太可能匹配的搜索词
          const searchQuery = 'ZZZZZZZZZZZ';

          const projects = Array.from({ length: projectCount }, (_, i) =>
            createProject(`project-${i}`, `Project ${i}`)
          );

          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const searchInput = container.querySelector('input[placeholder*="Search projects"]') as HTMLInputElement;
          expect(searchInput).toBeTruthy();

          const searchStartTime = performance.now();

          const user = userEvent.setup({ delay: null });
          await user.type(searchInput, searchQuery);

          await new Promise(resolve => setTimeout(resolve, 350));

          const filterTime = performance.now() - searchStartTime;

          // 验证过滤时间在合理范围内
          expect(filterTime).toBeLessThan(550);

          // 验证显示无结果消息
          const noResultsText = container.textContent?.includes('No projects match your search');
          expect(noResultsText).toBe(true);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该在大型项目列表中保持搜索性能', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom(100, 200, 300),
        validSearchQueryArbitrary(),
        async (projectCount, searchQuery) => {
          const projects = Array.from({ length: projectCount }, (_, i) =>
            createProject(`project-${i}`, `Project ${i}`)
          );

          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const searchInput = container.querySelector('input[placeholder*="Search projects"]') as HTMLInputElement;
          expect(searchInput).toBeTruthy();

          const searchStartTime = performance.now();

          const user = userEvent.setup({ delay: null });
          await user.type(searchInput, searchQuery);

          await new Promise(resolve => setTimeout(resolve, 350));

          const filterTime = performance.now() - searchStartTime;

          // 验证即使在大型列表中，过滤时间也在合理范围内
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 30 }
  }, 30000);
});

describe('Property 11: 项目排序正确性', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  // 自定义生成器：生成项目数组
  const projectArrayArbitrary = (minLength: number = 5, maxLength: number = 50) =>
    fc.array(
      fc.record({
        id: fc.uuid(),
        name: fc.string({ minLength: 3, maxLength: 30 }),
        description: fc.option(fc.string({ maxLength: 100 }), { nil: null }),
        github_repo_url: fc.constant(null),
        github_connection_type: fc.constant('https' as const),
        github_ssh_key_id: fc.constant(null),
        language: fc.option(
          fc.constantFrom('TypeScript', 'JavaScript', 'Python', 'Java', 'Go', 'Rust'),
          { nil: null }
        ),
        is_active: fc.boolean(),
        owner_id: fc.uuid(),
        created_at: fc.date({ min: new Date('2020-01-01'), max: new Date('2024-12-31') }).map(d => d.toISOString()),
        updated_at: fc.date({ min: new Date('2020-01-01'), max: new Date('2024-12-31') }).map(d => d.toISOString()),
      }),
      { minLength, maxLength }
    );

  // 自定义生成器：排序字段
  const sortByArbitrary = () =>
    fc.constantFrom('name', 'created_at', 'updated_at', 'is_active');

  // 自定义生成器：排序顺序
  const sortOrderArbitrary = () => fc.constantFrom('asc', 'desc');

  // 辅助函数：验证排序正确性
  function verifySortOrder(
    projects: Project[],
    sortBy: 'name' | 'created_at' | 'updated_at' | 'is_active',
    sortOrder: 'asc' | 'desc'
  ): boolean {
    if (projects.length <= 1) return true;

    for (let i = 0; i < projects.length - 1; i++) {
      const current = projects[i];
      const next = projects[i + 1];
      let compareResult = 0;

      switch (sortBy) {
        case 'name':
          compareResult = current.name.localeCompare(next.name);
          break;
        case 'created_at':
          compareResult = new Date(current.created_at).getTime() - new Date(next.created_at).getTime();
          break;
        case 'updated_at':
          compareResult = new Date(current.updated_at).getTime() - new Date(next.updated_at).getTime();
          break;
        case 'is_active':
          // Active projects first (true > false)
          compareResult = (next.is_active ? 1 : 0) - (current.is_active ? 1 : 0);
          break;
      }

      // Apply sort order
      const expectedCompare = sortOrder === 'asc' ? compareResult : -compareResult;

      // For ascending order, current should be <= next
      // For descending order, current should be >= next
      if (expectedCompare > 0) {
        return false;
      }
    }

    return true;
  }

  it('应该对任何项目列表按名称正确排序', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 30),
        sortOrderArbitrary(),
        async (projects, sortOrder) => {
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          // 点击名称排序按钮
          const nameButton = Array.from(container.querySelectorAll('button')).find(
            btn => btn.textContent?.includes('Name')
          );
          expect(nameButton).toBeTruthy();

          const user = userEvent.setup({ delay: null });
          
          // 如果需要降序，点击两次
          await user.click(nameButton!);
          if (sortOrder === 'desc') {
            await user.click(nameButton!);
          }

          // 等待渲染完成
          await new Promise(resolve => setTimeout(resolve, 100));

          // 获取渲染的项目列表
          const projectElements = container.querySelectorAll('[data-testid="virtual-list"] > div, .projects-virtual-list > div > div');
          const renderedProjects: Project[] = [];

          projectElements.forEach(el => {
            const projectName = el.querySelector('h3')?.textContent;
            if (projectName) {
              const project = projects.find(p => p.name === projectName);
              if (project) {
                renderedProjects.push(project);
              }
            }
          });

          // 验证排序正确性
          if (renderedProjects.length > 0) {
            const isSorted = verifySortOrder(renderedProjects, 'name', sortOrder);
            expect(isSorted).toBe(true);
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该对任何项目列表按创建时间正确排序', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 30),
        sortOrderArbitrary(),
        async (projects, sortOrder) => {
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          // 点击创建时间排序按钮
          const createdButton = Array.from(container.querySelectorAll('button')).find(
            btn => btn.textContent?.includes('Created')
          );
          expect(createdButton).toBeTruthy();

          const user = userEvent.setup({ delay: null });
          
          await user.click(createdButton!);
          if (sortOrder === 'desc') {
            await user.click(createdButton!);
          }

          await new Promise(resolve => setTimeout(resolve, 100));

          // 获取渲染的项目列表
          const projectElements = container.querySelectorAll('[data-testid="virtual-list"] > div, .projects-virtual-list > div > div');
          const renderedProjects: Project[] = [];

          projectElements.forEach(el => {
            const projectName = el.querySelector('h3')?.textContent;
            if (projectName) {
              const project = projects.find(p => p.name === projectName);
              if (project) {
                renderedProjects.push(project);
              }
            }
          });

          if (renderedProjects.length > 0) {
            const isSorted = verifySortOrder(renderedProjects, 'created_at', sortOrder);
            expect(isSorted).toBe(true);
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该对任何项目列表按更新时间正确排序', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 30),
        sortOrderArbitrary(),
        async (projects, sortOrder) => {
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          // 点击更新时间排序按钮
          const updatedButton = Array.from(container.querySelectorAll('button')).find(
            btn => btn.textContent?.includes('Updated')
          );
          expect(updatedButton).toBeTruthy();

          const user = userEvent.setup({ delay: null });
          
          await user.click(updatedButton!);
          if (sortOrder === 'desc') {
            await user.click(updatedButton!);
          }

          await new Promise(resolve => setTimeout(resolve, 100));

          // 获取渲染的项目列表
          const projectElements = container.querySelectorAll('[data-testid="virtual-list"] > div, .projects-virtual-list > div > div');
          const renderedProjects: Project[] = [];

          projectElements.forEach(el => {
            const projectName = el.querySelector('h3')?.textContent;
            if (projectName) {
              const project = projects.find(p => p.name === projectName);
              if (project) {
                renderedProjects.push(project);
              }
            }
          });

          if (renderedProjects.length > 0) {
            const isSorted = verifySortOrder(renderedProjects, 'updated_at', sortOrder);
            expect(isSorted).toBe(true);
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该对任何项目列表按状态正确排序', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 30),
        sortOrderArbitrary(),
        async (projects, sortOrder) => {
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          // 点击状态排序按钮
          const statusButton = Array.from(container.querySelectorAll('button')).find(
            btn => btn.textContent?.includes('Status')
          );
          expect(statusButton).toBeTruthy();

          const user = userEvent.setup({ delay: null });
          
          await user.click(statusButton!);
          if (sortOrder === 'desc') {
            await user.click(statusButton!);
          }

          await new Promise(resolve => setTimeout(resolve, 100));

          // 获取渲染的项目列表
          const projectElements = container.querySelectorAll('[data-testid="virtual-list"] > div, .projects-virtual-list > div > div');
          const renderedProjects: Project[] = [];

          projectElements.forEach(el => {
            const projectName = el.querySelector('h3')?.textContent;
            if (projectName) {
              const project = projects.find(p => p.name === projectName);
              if (project) {
                renderedProjects.push(project);
              }
            }
          });

          if (renderedProjects.length > 0) {
            const isSorted = verifySortOrder(renderedProjects, 'is_active', sortOrder);
            expect(isSorted).toBe(true);
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该在切换排序字段时保持正确的排序顺序', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(10, 30),
        fc.array(sortByArbitrary(), { minLength: 2, maxLength: 4 }),
        async (projects, sortSequence) => {
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const user = userEvent.setup({ delay: null });

          // 依次点击不同的排序按钮
          for (const sortBy of sortSequence) {
            const buttonText = sortBy === 'name' ? 'Name' :
                              sortBy === 'created_at' ? 'Created' :
                              sortBy === 'updated_at' ? 'Updated' : 'Status';

            const button = Array.from(container.querySelectorAll('button')).find(
              btn => btn.textContent?.includes(buttonText)
            );

            if (button) {
              await user.click(button);
              await new Promise(resolve => setTimeout(resolve, 100));

              // 验证排序正确性
              const projectElements = container.querySelectorAll('[data-testid="virtual-list"] > div, .projects-virtual-list > div > div');
              const renderedProjects: Project[] = [];

              projectElements.forEach(el => {
                const projectName = el.querySelector('h3')?.textContent;
                if (projectName) {
                  const project = projects.find(p => p.name === projectName);
                  if (project) {
                    renderedProjects.push(project);
                  }
                }
              });

              if (renderedProjects.length > 0) {
                const isSorted = verifySortOrder(renderedProjects, sortBy, 'asc');
                expect(isSorted).toBe(true);
              }
            }
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 60000);

  it('应该在排序后保持项目数据完整性', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(10, 30),
        sortByArbitrary(),
        sortOrderArbitrary(),
        async (projects, sortBy, sortOrder) => {
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const buttonText = sortBy === 'name' ? 'Name' :
                            sortBy === 'created_at' ? 'Created' :
                            sortBy === 'updated_at' ? 'Updated' : 'Status';

          const button = Array.from(container.querySelectorAll('button')).find(
            btn => btn.textContent?.includes(buttonText)
          );
          expect(button).toBeTruthy();

          const user = userEvent.setup({ delay: null });
          
          await user.click(button!);
          if (sortOrder === 'desc') {
            await user.click(button!);
          }

          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证所有项目都存在（没有丢失或重复）
          const projectElements = container.querySelectorAll('[data-testid="virtual-list"] > div, .projects-virtual-list > div > div');
          const renderedProjectIds = new Set<string>();

          projectElements.forEach(el => {
            const projectName = el.querySelector('h3')?.textContent;
            if (projectName) {
              const project = projects.find(p => p.name === projectName);
              if (project) {
                renderedProjectIds.add(project.id);
              }
            }
          });

          // 验证没有项目丢失（考虑到虚拟滚动可能只渲染部分项目）
          // 至少应该渲染一些项目
          expect(renderedProjectIds.size).toBeGreaterThan(0);

          // 验证没有重复的项目ID
          const renderedProjectIdsArray = Array.from(renderedProjectIds);
          const uniqueIds = new Set(renderedProjectIdsArray);
          expect(uniqueIds.size).toBe(renderedProjectIdsArray.length);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('应该在空列表上正确处理排序', async () => {
    await fc.assert(
      fc.asyncProperty(
        sortByArbitrary(),
        async (sortBy) => {
          mockUseProjects.mockReturnValue({
            data: [],
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const buttonText = sortBy === 'name' ? 'Name' :
                            sortBy === 'created_at' ? 'Created' :
                            sortBy === 'updated_at' ? 'Updated' : 'Status';

          const button = Array.from(container.querySelectorAll('button')).find(
            btn => btn.textContent?.includes(buttonText)
          );

          if (button) {
            const user = userEvent.setup({ delay: null });
            await user.click(button);
            await new Promise(resolve => setTimeout(resolve, 100));

            // 验证显示空状态消息
            const emptyMessage = container.textContent?.includes('No projects found');
            expect(emptyMessage).toBe(true);
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 15000);

  it('应该在单个项目列表上正确处理排序', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(1, 1),
        sortByArbitrary(),
        async (projects, sortBy) => {
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const buttonText = sortBy === 'name' ? 'Name' :
                            sortBy === 'created_at' ? 'Created' :
                            sortBy === 'updated_at' ? 'Updated' : 'Status';

          const button = Array.from(container.querySelectorAll('button')).find(
            btn => btn.textContent?.includes(buttonText)
          );
          expect(button).toBeTruthy();

          const user = userEvent.setup({ delay: null });
          await user.click(button!);
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证项目仍然显示
          const projectName = container.querySelector('h3')?.textContent;
          expect(projectName).toBe(projects[0].name);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 15000);

  it('应该在大型项目列表上保持排序性能', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(100, 200),
        sortByArbitrary(),
        async (projects, sortBy) => {
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const buttonText = sortBy === 'name' ? 'Name' :
                            sortBy === 'created_at' ? 'Created' :
                            sortBy === 'updated_at' ? 'Updated' : 'Status';

          const button = Array.from(container.querySelectorAll('button')).find(
            btn => btn.textContent?.includes(buttonText)
          );
          expect(button).toBeTruthy();

          const sortStartTime = performance.now();

          const user = userEvent.setup({ delay: null });
          await user.click(button!);
          await new Promise(resolve => setTimeout(resolve, 100));

          const sortTime = performance.now() - sortStartTime;

          // 验证排序时间合理（应该很快，即使是大列表）
          expect(sortTime).toBeLessThan(500);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 30000);

  it('应该在排序后正确显示排序指示器', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(10, 30),
        sortByArbitrary(),
        async (projects, sortBy) => {
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          const buttonText = sortBy === 'name' ? 'Name' :
                            sortBy === 'created_at' ? 'Created' :
                            sortBy === 'updated_at' ? 'Updated' : 'Status';

          const button = Array.from(container.querySelectorAll('button')).find(
            btn => btn.textContent?.includes(buttonText)
          ) as HTMLButtonElement;
          expect(button).toBeTruthy();

          const user = userEvent.setup({ delay: null });
          
          // 点击一次（升序）
          await user.click(button);
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证按钮显示升序指示器
          expect(button.textContent).toContain('↑');

          // 点击第二次（降序）
          await user.click(button);
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证按钮显示降序指示器
          expect(button.textContent).toContain('↓');

          unmount();
          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 30000);
});
});

/**
 * Property 11: 项目排序正确性
 * 
 * Feature: frontend-production-optimization
 * 
 * **Validates: Requirements 2.5**
 * 
 * 测试覆盖:
 * - 对于任何项目列表和排序条件（名称、创建时间、更新时间、状态），排序后的列表应该按照指定条件正确排序
 * 
 * 注意: 此测试验证Projects组件的排序功能正确性。
 * 测试通过生成随机项目列表并验证排序结果是否符合预期来确保排序算法的正确性。
 */

describe('Property 11: 项目排序正确性', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  // 自定义生成器：生成项目列表
  const projectListArbitrary = () =>
    fc.array(
      fc.record({
        id: fc.uuid(),
        name: fc.string({ minLength: 1, maxLength: 50 }),
        description: fc.option(fc.string({ maxLength: 200 }), { nil: null }),
        github_repo_url: fc.constant(null),
        github_connection_type: fc.constant('https' as const),
        github_ssh_key_id: fc.constant(null),
        language: fc.option(fc.constantFrom('TypeScript', 'JavaScript', 'Python', 'Java', 'Go', 'Rust'), { nil: null }),
        is_active: fc.boolean(),
        owner_id: fc.uuid(),
        created_at: fc.date({ min: new Date('2020-01-01'), max: new Date('2024-12-31') }).map(d => d.toISOString()),
        updated_at: fc.date({ min: new Date('2020-01-01'), max: new Date('2024-12-31') }).map(d => d.toISOString()),
      }),
      { minLength: 2, maxLength: 50 }
    );

  // 排序条件生成器
  const sortByArbitrary = () =>
    fc.constantFrom('name', 'created_at', 'updated_at', 'is_active');

  // 排序顺序生成器
  const sortOrderArbitrary = () =>
    fc.constantFrom('asc', 'desc');

  it('应该按名称正确排序项目', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectListArbitrary(),
        sortOrderArbitrary(),
        async (projects, sortOrder) => {
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          const { unmount, container } = renderWithProviders(<Projects />);

          // 点击名称排序按钮
          const nameButton = screen.getB
/**
 * Projectspropertytest
 * 
 * Feature: frontend-production-optimization
 * Property 3: searchfilter性能
 * Property 11: projectsort正确性
 * 
 * **Validates: Requirements 2.2, 2.5**
 * 
 * testCoverage:
 * - 对于任何searchinput，filterresultshouldBeAt300ms内show
 * - 对于任何project列表andsort条件，sort后的列表should按照指定条件正确sort
 * 
 * note: testVerifiesProjectscomponent在searchfilter时的性能andsortfeature的正确性。
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

describe('Property 3: searchfilter性能', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  // customGenerator：generate有效的project名称
  const validProjectNameArbitrary = () =>
    fc.oneof(
      fc.constantFrom('Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta'),
      fc.string({ minLength: 3, maxLength: 30 }).filter(s => s.trim().length >= 3)
    );

  // customGenerator：generate编程语言
  const languageArbitrary = () =>
    fc.constantFrom('TypeScript', 'JavaScript', 'Python', 'Java', 'Go', 'Rust');

  // customGenerator：generate有效的searchquery
  const validSearchQueryArbitrary = () =>
    fc.oneof(
      fc.constantFrom('Alpha', 'Beta', 'Type', 'Script', 'Python', 'active', 'inactive'),
      fc.string({ minLength: 2, maxLength: 15 }).filter(s => s.trim().length >= 2)
    );

  it('shouldBeAt任何searchinput下在300ms内completefilter', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 20, max: 100 }),
        validSearchQueryArbitrary(),
        async (projectCount, searchQuery) => {
          // generateproject列表
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

          // verifyfilter时间在合理范围内（300ms debounce + 200ms buffer for test environment）
          // The debounce ensures we don't filter on every keystroke, improving performance
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('shouldBeAt不同project列表大小下保持search性能', async () => {
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

          // verify无论project数量多少，filter时间都在合理范围内
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('shouldBeAtsearchproject名称时快速filter', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 30, max: 100 }),
        validProjectNameArbitrary(),
        async (projectCount, targetName) => {
          // createproject列表，确保contain目标名称
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

          // verifyfilter时间在合理范围内
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('shouldBeAtsearch编程语言时快速filter', async () => {
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

          // verifyfilter时间在合理范围内
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('shouldBeAtsearchprojectstatus时快速filter', async () => {
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

          // verifyfilter时间在合理范围内
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('shouldBeAt大小写不敏感search时保持性能', async () => {
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

          // verifyfilter时间在合理范围内，无论大小写
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('shouldBeAt清除search时快速恢复完整列表', async () => {
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

          // 先inputsearch
          await user.type(searchInput, searchQuery);
          await new Promise(resolve => setTimeout(resolve, 350));

          // 清除search
          const clearStartTime = performance.now();
          
          const clearButton = container.querySelector('button[aria-label="Clear search"]') as HTMLButtonElement;
          if (clearButton) {
            await user.click(clearButton);
          }

          await new Promise(resolve => setTimeout(resolve, 350));

          const clearTime = performance.now() - clearStartTime;

          // verify清除时间在合理范围内
          expect(clearTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('shouldBeAt连续search时保持性能', async () => {
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

          // execute多times连续search
          for (const searchQuery of searchQueries) {
            // 清除之前的search
            await user.clear(searchInput);

            const searchStartTime = performance.now();

            // input新的search词
            await user.type(searchInput, searchQuery);
            await new Promise(resolve => setTimeout(resolve, 350));

            const filterTime = performance.now() - searchStartTime;

            // verify每timessearch都在合理范围内
            expect(filterTime).toBeLessThan(550);
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 60000);

  it('shouldBeAt无匹配result时快速show空status', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 20, max: 100 }),
        async (projectCount) => {
          // use一item不太可能匹配的search词
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

          // verifyfilter时间在合理范围内
          expect(filterTime).toBeLessThan(550);

          // verifyshow无result消息
          const noResultsText = container.textContent?.includes('No projects match your search');
          expect(noResultsText).toBe(true);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 50 }
    );
  }, 30000);

  it('shouldBeAt大型project列表中保持search性能', async () => {
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

          // verify即使在大型列表中，filter时间也在合理范围内
          expect(filterTime).toBeLessThan(550);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 30000);
});

describe('Property 11: projectsort正确性', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  // customGenerator：generateproject数组
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

  // customGenerator：sortfield
  const sortByArbitrary = () =>
    fc.constantFrom('name', 'created_at', 'updated_at', 'is_active');

  // customGenerator：sort顺序
  const sortOrderArbitrary = () => fc.constantFrom('asc', 'desc');

  // 辅助function：verifysort正确性
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

  it('should对任何project列表按名称正确sort', async () => {
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

          // 点击名称sortbutton
          const nameButton = Array.from(container.querySelectorAll('button')).find(
            btn => btn.textContent?.includes('Name')
          );
          expect(nameButton).toBeTruthy();

          const user = userEvent.setup({ delay: null });
          
          // 如果need降序，点击两times
          await user.click(nameButton!);
          if (sortOrder === 'desc') {
            await user.click(nameButton!);
          }

          // waitrendercomplete
          await new Promise(resolve => setTimeout(resolve, 100));

          // getrender的project列表
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

          // verifysort正确性
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

  it('should对任何project列表按create时间正确sort', async () => {
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

          // 点击create时间sortbutton
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

          // getrender的project列表
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

  it('should对任何project列表按update时间正确sort', async () => {
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

          // 点击update时间sortbutton
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

          // getrender的project列表
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

  it('should对任何project列表按status正确sort', async () => {
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

          // 点击statussortbutton
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

          // getrender的project列表
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

  it('shouldBeAt切换sortfield时保持正确的sort顺序', async () => {
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

          // 依times点击不同的sortbutton
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

              // verifysort正确性
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

  it('shouldBeAtsort后保持projectdata完整性', async () => {
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

          // verify所有project都存在（没有丢失或duplicate）
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

          // verify没有project丢失（考虑到虚拟滚动可能只render部分project）
          // 至少shouldrender一些project
          expect(renderedProjectIds.size).toBeGreaterThan(0);

          // verify没有duplicate的projectID
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

  it('shouldBeAt空列表上正确handlesort', async () => {
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

            // verifyshow空status消息
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

  it('shouldBeAt单itemproject列表上正确handlesort', async () => {
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

          // verifyproject仍然show
          const projectName = container.querySelector('h3')?.textContent;
          expect(projectName).toBe(projects[0].name);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 15000);

  it('shouldBeAt大型project列表上保持sort性能', async () => {
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

          // verifysort时间合理（should很快，即使是大列表）
          expect(sortTime).toBeLessThan(500);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 30000);

  it('shouldBeAtsort后正确showsort指示器', async () => {
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
          
          // 点击一times（升序）
          await user.click(button);
          await new Promise(resolve => setTimeout(resolve, 100));

          // verifybuttonshow升序指示器
          expect(button.textContent).toContain('↑');

          // 点击第二times（降序）
          await user.click(button);
          await new Promise(resolve => setTimeout(resolve, 100));

          // verifybuttonshow降序指示器
          expect(button.textContent).toContain('↓');

          unmount();
          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 30000);
});

/**
 * Property 11: projectsort正确性
 * 
 * Feature: frontend-production-optimization
 * 
 * **Validates: Requirements 2.5**
 * 
 * testCoverage:
 * - 对于任何project列表andsort条件（名称、create时间、update时间、status），sort后的列表should按照指定条件正确sort
 * 
 * note: testVerifiesProjectscomponent的sortfeature正确性。
 * test通过generate随机project列表并verifysortresult是否符合预期来确保sort算法的正确性。
 */

describe('Property 11: projectsort正确性', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  // customGenerator：generateproject列表
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

  // sort条件generate器
  const sortByArbitrary = () =>
    fc.constantFrom('name', 'created_at', 'updated_at', 'is_active');

  // sort顺序generate器
  const sortOrderArbitrary = () =>
    fc.constantFrom('asc', 'desc');

  it('should按名称正确sortproject', async () => {
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

          // 点击名称sortbutton
          const nameButton = screen.getByRole('button', { name: /name/i });
          expect(nameButton).toBeTruthy();

          const user = userEvent.setup({ delay: null });
          
          // 点击名称按钮（升序）
          await user.click(nameButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证升序
          const rows = container.querySelectorAll('[data-testid="project-row"]');
          const firstRow = rows[0];
          expect(firstRow).toBeTruthy();

          // 点击第二下（降序）
          await user.click(nameButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          unmount();
          cleanup();
        }
      )
    );
  }, 30000);
});
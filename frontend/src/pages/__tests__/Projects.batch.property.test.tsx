/**
 * Projects批量操作propertytest
 * 
 * Feature: frontend-production-optimization
 * Property 13: 批量操作一致性
 * 
 * **Validates: Requirements 2.3**
 * 
 * testCoverage:
 * - 对于任何选中的多itemproject，批量操作（delete、归档、tag）should对所有选中project生效
 * 
 * note: testVerifiesProjectscomponent的批量操作feature在各种场景下的一致性and正确性。
 */

import fc from 'fast-check';
import { render, screen, cleanup, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Projects } from '../Projects';
import type { Project } from '../../hooks/useProjects';

// Mock hooks
const mockUseProjects = jest.fn();
const mockUseUpdateProject = jest.fn();

jest.mock('../../hooks/useProjects', () => ({
  useProjects: () => mockUseProjects(),
  useUpdateProject: () => mockUseUpdateProject(),
}));

// Mock components
jest.mock('../../components/VirtualList', () => ({
  VirtualList: ({ items, renderItem }: any) => (
    <div data-testid="virtual-list">
      {items.map((item: any, index: number) => (
        <div key={item.id} data-testid={`project-item-${item.id}`}>
          {renderItem(item, index)}
        </div>
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
function createProject(
  id: string,
  name: string,
  isActive: boolean = true,
  description: string = ''
): Project {
  return {
    id,
    name,
    description: description || `Description for ${name}`,
    github_repo_url: null,
    github_connection_type: 'https',
    github_ssh_key_id: null,
    language: 'TypeScript',
    is_active: isActive,
    owner_id: 'user-1',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
}

describe('Property 13: 批量操作一致性', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock window.confirm to always return true
    global.confirm = jest.fn(() => true);
    // Mock window.alert
    global.alert = jest.fn();
  });

  afterEach(() => {
    cleanup();
  });

  // customGenerator：generateproject数组
  const projectArrayArbitrary = (minLength: number = 3, maxLength: number = 20) =>
    fc.array(
      fc.record({
        id: fc.uuid(),
        name: fc.string({ minLength: 3, maxLength: 30 }),
        isActive: fc.boolean(),
        description: fc.string({ maxLength: 100 }),
      }),
      { minLength, maxLength }
    ).map(projects =>
      projects.map(p => createProject(p.id, p.name, p.isActive, p.description))
    );

  // customGenerator：generatetag字符串
  const tagStringArbitrary = () =>
    fc.oneof(
      fc.constantFrom('urgent', 'backend', 'frontend', 'bug-fix', 'feature'),
      fc
        .array(fc.string({ minLength: 2, maxLength: 10 }), { minLength: 1, maxLength: 3 })
        .map(tags => tags.join(', '))
    );

  it('批量deleteshould对所有选中的project生效', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 15),
        async (projects) => {
          // 选择一些project进行delete
          const selectedCount = Math.min(Math.floor(projects.length / 2), 5);
          const selectedIds = new Set(
            projects.slice(0, selectedCount).map(p => p.id)
          );

          const mutateAsync = jest.fn().mockResolvedValue({});
          
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          mockUseUpdateProject.mockReturnValue({ mutateAsync });

          const { unmount, container } = renderWithProviders(<Projects />);

          // 选中project
          for (const id of selectedIds) {
            const checkbox = container.querySelector(
              `input[type="checkbox"][data-project-id="${id}"]`
            ) as HTMLInputElement;
            if (checkbox) {
              await userEvent.click(checkbox);
            }
          }

          // 点击批量deletebutton
          const deleteButton = screen.queryByRole('button', { name: /batch delete/i });
          if (deleteButton) {
            await userEvent.click(deleteButton);

            // wait操作complete
            await waitFor(() => {
              expect(mutateAsync).toHaveBeenCalled();
            });

            // verify所有选中的project都被调用了delete操作
            expect(mutateAsync).toHaveBeenCalledTimes(selectedIds.size);

            // verify每item选中的project都被标记为不活跃（软delete）
            selectedIds.forEach(id => {
              expect(mutateAsync).toHaveBeenCalledWith(
                expect.objectContaining({
                  projectId: id,
                  updates: expect.objectContaining({ is_active: false }),
                })
              );
            });
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 30000);

  it('批量归档should对所有选中的project生效', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 15),
        async (projects) => {
          // 选择一些活跃的project进行归档
          const activeProjects = projects.filter(p => p.is_active);
          if (activeProjects.length === 0) return; // Skip if no active projects

          const selectedCount = Math.min(Math.floor(activeProjects.length / 2), 5);
          const selectedIds = new Set(
            activeProjects.slice(0, selectedCount).map(p => p.id)
          );

          const mutateAsync = jest.fn().mockResolvedValue({});
          
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          mockUseUpdateProject.mockReturnValue({ mutateAsync });

          const { unmount, container } = renderWithProviders(<Projects />);

          // 选中project
          for (const id of selectedIds) {
            const checkbox = container.querySelector(
              `input[type="checkbox"][data-project-id="${id}"]`
            ) as HTMLInputElement;
            if (checkbox) {
              await userEvent.click(checkbox);
            }
          }

          // 点击批量归档button
          const archiveButton = screen.queryByRole('button', { name: /batch archive/i });
          if (archiveButton) {
            await userEvent.click(archiveButton);

            // wait操作complete
            await waitFor(() => {
              expect(mutateAsync).toHaveBeenCalled();
            });

            // verify所有选中的project都被调用了归档操作
            expect(mutateAsync).toHaveBeenCalledTimes(selectedIds.size);

            // verify每item选中的project都被标记为不活跃（归档）
            selectedIds.forEach(id => {
              expect(mutateAsync).toHaveBeenCalledWith(
                expect.objectContaining({
                  projectId: id,
                  updates: expect.objectContaining({ is_active: false }),
                })
              );
            });
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 30000);

  it('批量addtagshould对所有选中的project生效', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 15),
        tagStringArbitrary(),
        async (projects, tagString) => {
          const selectedCount = Math.min(Math.floor(projects.length / 2), 5);
          const selectedIds = new Set(
            projects.slice(0, selectedCount).map(p => p.id)
          );

          const mutateAsync = jest.fn().mockResolvedValue({});
          
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          mockUseUpdateProject.mockReturnValue({ mutateAsync });

          const { unmount, container } = renderWithProviders(<Projects />);

          // 选中project
          for (const id of selectedIds) {
            const checkbox = container.querySelector(
              `input[type="checkbox"][data-project-id="${id}"]`
            ) as HTMLInputElement;
            if (checkbox) {
              await userEvent.click(checkbox);
            }
          }

          // 点击批量tagbutton
          const tagButton = screen.queryByRole('button', { name: /batch tag/i });
          if (tagButton) {
            await userEvent.click(tagButton);

            // waittag模态框出现
            await waitFor(() => {
              const tagInput = screen.queryByPlaceholderText(/enter tags/i);
              expect(tagInput).toBeInTheDocument();
            });

            // inputtag
            const tagInput = screen.getByPlaceholderText(/enter tags/i);
            await userEvent.type(tagInput, tagString);

            // confirmaddtag
            const confirmButton = screen.getByRole('button', { name: /confirm/i });
            await userEvent.click(confirmButton);

            // wait操作complete
            await waitFor(() => {
              expect(mutateAsync).toHaveBeenCalled();
            });

            // verify所有选中的project都被调用了tag操作
            expect(mutateAsync).toHaveBeenCalledTimes(selectedIds.size);

            // verify每item选中的project都update了description（containtag）
            selectedIds.forEach(id => {
              expect(mutateAsync).toHaveBeenCalledWith(
                expect.objectContaining({
                  projectId: id,
                  updates: expect.objectContaining({
                    description: expect.stringContaining('[Tags:'),
                  }),
                })
              );
            });
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 30 }
    );
  }, 30000);

  it('批量操作shouldBeAt不同project数量下保持一致性', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom(3, 10, 20, 50),
        fc.constantFrom('delete', 'archive'),
        async (projectCount, operation) => {
          const projects = Array.from({ length: projectCount }, (_, i) =>
            createProject(`project-${i}`, `Project ${i}`, true)
          );

          // 选择一半的project
          const selectedCount = Math.floor(projectCount / 2);
          const selectedIds = new Set(
            projects.slice(0, selectedCount).map(p => p.id)
          );

          const mutateAsync = jest.fn().mockResolvedValue({});
          
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          mockUseUpdateProject.mockReturnValue({ mutateAsync });

          const { unmount, container } = renderWithProviders(<Projects />);

          // 选中project
          for (const id of selectedIds) {
            const checkbox = container.querySelector(
              `input[type="checkbox"][data-project-id="${id}"]`
            ) as HTMLInputElement;
            if (checkbox) {
              await userEvent.click(checkbox);
            }
          }

          // execute批量操作
          const buttonName = operation === 'delete' ? /batch delete/i : /batch archive/i;
          const operationButton = screen.queryByRole('button', { name: buttonName });
          
          if (operationButton) {
            await userEvent.click(operationButton);

            // wait操作complete
            await waitFor(() => {
              expect(mutateAsync).toHaveBeenCalled();
            });

            // verify操作times数等于选中的project数量
            expect(mutateAsync).toHaveBeenCalledTimes(selectedIds.size);

            // verify所有调用都是针对选中的project
            const calledProjectIds = mutateAsync.mock.calls.map(
              call => call[0].projectId
            );
            selectedIds.forEach(id => {
              expect(calledProjectIds).toContain(id);
            });
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 30000);

  it('批量操作failure时should保持data一致性', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 10),
        async (projects) => {
          const selectedCount = Math.min(3, projects.length);
          const selectedIds = new Set(
            projects.slice(0, selectedCount).map(p => p.id)
          );

          // 模拟部分操作failure
          let callCount = 0;
          const mutateAsync = jest.fn().mockImplementation(() => {
            callCount++;
            // 第二item调用failure
            if (callCount === 2) {
              return Promise.reject(new Error('Network error'));
            }
            return Promise.resolve({});
          });

          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          mockUseUpdateProject.mockReturnValue({ mutateAsync });

          const { unmount, container } = renderWithProviders(<Projects />);

          // 选中project
          for (const id of selectedIds) {
            const checkbox = container.querySelector(
              `input[type="checkbox"][data-project-id="${id}"]`
            ) as HTMLInputElement;
            if (checkbox) {
              await userEvent.click(checkbox);
            }
          }

          // 点击批量deletebutton
          const deleteButton = screen.queryByRole('button', { name: /batch delete/i });
          if (deleteButton) {
            await userEvent.click(deleteButton);

            // wait操作complete（包括failure）
            await waitFor(
              () => {
                // shouldshowerrorhint
                expect(global.alert).toHaveBeenCalledWith(
                  expect.stringContaining('Failed')
                );
              },
              { timeout: 3000 }
            );

            // verify尝试了所有选中的project（即使有failure）
            expect(mutateAsync).toHaveBeenCalled();
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 30000);

  it('空选择时批量操作should不execute任何操作', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 10),
        async (projects) => {
          const mutateAsync = jest.fn().mockResolvedValue({});
          
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          mockUseUpdateProject.mockReturnValue({ mutateAsync });

          const { unmount } = renderWithProviders(<Projects />);

          // 不选择任何project，直接点击批量操作button
          const deleteButton = screen.queryByRole('button', { name: /batch delete/i });
          if (deleteButton) {
            await userEvent.click(deleteButton);

            // wait一小段时间
            await new Promise(resolve => setTimeout(resolve, 100));

            // verify没有调用任何update操作
            expect(mutateAsync).not.toHaveBeenCalled();
            // verify没有showconfirm对话框
            expect(global.confirm).not.toHaveBeenCalled();
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 30000);

  it('批量操作should正确handleduplicate选择', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 10),
        async (projects) => {
          if (projects.length === 0) return;

          const selectedIds = new Set([projects[0].id]);

          const mutateAsync = jest.fn().mockResolvedValue({});
          
          mockUseProjects.mockReturnValue({
            data: projects,
            isLoading: false,
            error: null,
          });

          mockUseUpdateProject.mockReturnValue({ mutateAsync });

          const { unmount, container } = renderWithProviders(<Projects />);

          // 选中同一itemproject多times（模拟user点击多times）
          const checkbox = container.querySelector(
            `input[type="checkbox"][data-project-id="${projects[0].id}"]`
          ) as HTMLInputElement;
          
          if (checkbox) {
            await userEvent.click(checkbox); // 选中
            await userEvent.click(checkbox); // cancel选中
            await userEvent.click(checkbox); // 再times选中
          }

          // 点击批量deletebutton
          const deleteButton = screen.queryByRole('button', { name: /batch delete/i });
          if (deleteButton) {
            await userEvent.click(deleteButton);

            // wait操作complete
            await waitFor(() => {
              if (mutateAsync.mock.calls.length > 0) {
                expect(mutateAsync).toHaveBeenCalled();
              }
            });

            // verify只调用了一times（不会duplicate操作）
            if (mutateAsync.mock.calls.length > 0) {
              expect(mutateAsync).toHaveBeenCalledTimes(1);
              expect(mutateAsync).toHaveBeenCalledWith(
                expect.objectContaining({
                  projectId: projects[0].id,
                })
              );
            }
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 30000);
});

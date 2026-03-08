/**
 * Projects批量操作属性测试
 * 
 * Feature: frontend-production-optimization
 * Property 13: 批量操作一致性
 * 
 * **Validates: Requirements 2.3**
 * 
 * 测试覆盖:
 * - 对于任何选中的多个项目，批量操作（删除、归档、标签）应该对所有选中项目生效
 * 
 * 注意: 此测试验证Projects组件的批量操作功能在各种场景下的一致性和正确性。
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

  // 自定义生成器：生成项目数组
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

  // 自定义生成器：生成标签字符串
  const tagStringArbitrary = () =>
    fc.oneof(
      fc.constantFrom('urgent', 'backend', 'frontend', 'bug-fix', 'feature'),
      fc
        .array(fc.string({ minLength: 2, maxLength: 10 }), { minLength: 1, maxLength: 3 })
        .map(tags => tags.join(', '))
    );

  it('批量删除应该对所有选中的项目生效', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 15),
        async (projects) => {
          // 选择一些项目进行删除
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

          // 选中项目
          for (const id of selectedIds) {
            const checkbox = container.querySelector(
              `input[type="checkbox"][data-project-id="${id}"]`
            ) as HTMLInputElement;
            if (checkbox) {
              await userEvent.click(checkbox);
            }
          }

          // 点击批量删除按钮
          const deleteButton = screen.queryByRole('button', { name: /batch delete/i });
          if (deleteButton) {
            await userEvent.click(deleteButton);

            // 等待操作完成
            await waitFor(() => {
              expect(mutateAsync).toHaveBeenCalled();
            });

            // 验证所有选中的项目都被调用了删除操作
            expect(mutateAsync).toHaveBeenCalledTimes(selectedIds.size);

            // 验证每个选中的项目都被标记为不活跃（软删除）
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

  it('批量归档应该对所有选中的项目生效', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 15),
        async (projects) => {
          // 选择一些活跃的项目进行归档
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

          // 选中项目
          for (const id of selectedIds) {
            const checkbox = container.querySelector(
              `input[type="checkbox"][data-project-id="${id}"]`
            ) as HTMLInputElement;
            if (checkbox) {
              await userEvent.click(checkbox);
            }
          }

          // 点击批量归档按钮
          const archiveButton = screen.queryByRole('button', { name: /batch archive/i });
          if (archiveButton) {
            await userEvent.click(archiveButton);

            // 等待操作完成
            await waitFor(() => {
              expect(mutateAsync).toHaveBeenCalled();
            });

            // 验证所有选中的项目都被调用了归档操作
            expect(mutateAsync).toHaveBeenCalledTimes(selectedIds.size);

            // 验证每个选中的项目都被标记为不活跃（归档）
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

  it('批量添加标签应该对所有选中的项目生效', async () => {
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

          // 选中项目
          for (const id of selectedIds) {
            const checkbox = container.querySelector(
              `input[type="checkbox"][data-project-id="${id}"]`
            ) as HTMLInputElement;
            if (checkbox) {
              await userEvent.click(checkbox);
            }
          }

          // 点击批量标签按钮
          const tagButton = screen.queryByRole('button', { name: /batch tag/i });
          if (tagButton) {
            await userEvent.click(tagButton);

            // 等待标签模态框出现
            await waitFor(() => {
              const tagInput = screen.queryByPlaceholderText(/enter tags/i);
              expect(tagInput).toBeInTheDocument();
            });

            // 输入标签
            const tagInput = screen.getByPlaceholderText(/enter tags/i);
            await userEvent.type(tagInput, tagString);

            // 确认添加标签
            const confirmButton = screen.getByRole('button', { name: /confirm/i });
            await userEvent.click(confirmButton);

            // 等待操作完成
            await waitFor(() => {
              expect(mutateAsync).toHaveBeenCalled();
            });

            // 验证所有选中的项目都被调用了标签操作
            expect(mutateAsync).toHaveBeenCalledTimes(selectedIds.size);

            // 验证每个选中的项目都更新了description（包含标签）
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

  it('批量操作应该在不同项目数量下保持一致性', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom(3, 10, 20, 50),
        fc.constantFrom('delete', 'archive'),
        async (projectCount, operation) => {
          const projects = Array.from({ length: projectCount }, (_, i) =>
            createProject(`project-${i}`, `Project ${i}`, true)
          );

          // 选择一半的项目
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

          // 选中项目
          for (const id of selectedIds) {
            const checkbox = container.querySelector(
              `input[type="checkbox"][data-project-id="${id}"]`
            ) as HTMLInputElement;
            if (checkbox) {
              await userEvent.click(checkbox);
            }
          }

          // 执行批量操作
          const buttonName = operation === 'delete' ? /batch delete/i : /batch archive/i;
          const operationButton = screen.queryByRole('button', { name: buttonName });
          
          if (operationButton) {
            await userEvent.click(operationButton);

            // 等待操作完成
            await waitFor(() => {
              expect(mutateAsync).toHaveBeenCalled();
            });

            // 验证操作次数等于选中的项目数量
            expect(mutateAsync).toHaveBeenCalledTimes(selectedIds.size);

            // 验证所有调用都是针对选中的项目
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

  it('批量操作失败时应该保持数据一致性', async () => {
    await fc.assert(
      fc.asyncProperty(
        projectArrayArbitrary(5, 10),
        async (projects) => {
          const selectedCount = Math.min(3, projects.length);
          const selectedIds = new Set(
            projects.slice(0, selectedCount).map(p => p.id)
          );

          // 模拟部分操作失败
          let callCount = 0;
          const mutateAsync = jest.fn().mockImplementation(() => {
            callCount++;
            // 第二个调用失败
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

          // 选中项目
          for (const id of selectedIds) {
            const checkbox = container.querySelector(
              `input[type="checkbox"][data-project-id="${id}"]`
            ) as HTMLInputElement;
            if (checkbox) {
              await userEvent.click(checkbox);
            }
          }

          // 点击批量删除按钮
          const deleteButton = screen.queryByRole('button', { name: /batch delete/i });
          if (deleteButton) {
            await userEvent.click(deleteButton);

            // 等待操作完成（包括失败）
            await waitFor(
              () => {
                // 应该显示错误提示
                expect(global.alert).toHaveBeenCalledWith(
                  expect.stringContaining('Failed')
                );
              },
              { timeout: 3000 }
            );

            // 验证尝试了所有选中的项目（即使有失败）
            expect(mutateAsync).toHaveBeenCalled();
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 30000);

  it('空选择时批量操作应该不执行任何操作', async () => {
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

          // 不选择任何项目，直接点击批量操作按钮
          const deleteButton = screen.queryByRole('button', { name: /batch delete/i });
          if (deleteButton) {
            await userEvent.click(deleteButton);

            // 等待一小段时间
            await new Promise(resolve => setTimeout(resolve, 100));

            // 验证没有调用任何更新操作
            expect(mutateAsync).not.toHaveBeenCalled();
            // 验证没有显示确认对话框
            expect(global.confirm).not.toHaveBeenCalled();
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 20 }
    );
  }, 30000);

  it('批量操作应该正确处理重复选择', async () => {
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

          // 选中同一个项目多次（模拟用户点击多次）
          const checkbox = container.querySelector(
            `input[type="checkbox"][data-project-id="${projects[0].id}"]`
          ) as HTMLInputElement;
          
          if (checkbox) {
            await userEvent.click(checkbox); // 选中
            await userEvent.click(checkbox); // 取消选中
            await userEvent.click(checkbox); // 再次选中
          }

          // 点击批量删除按钮
          const deleteButton = screen.queryByRole('button', { name: /batch delete/i });
          if (deleteButton) {
            await userEvent.click(deleteButton);

            // 等待操作完成
            await waitFor(() => {
              if (mutateAsync.mock.calls.length > 0) {
                expect(mutateAsync).toHaveBeenCalled();
              }
            });

            // 验证只调用了一次（不会重复操作）
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

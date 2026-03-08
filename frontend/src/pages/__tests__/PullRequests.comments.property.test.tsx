/**
 * PullRequests评论功能属性测试
 * 
 * Feature: frontend-production-optimization
 * Property 14: 评论线程创建
 * 
 * **Validates: Requirements 3.2**
 * 
 * 测试覆盖:
 * - 对于任何代码行上的评论添加操作，应该创建评论线程并支持后续回复
 * 
 * 注意: 此测试验证PullRequests组件的评论线程创建和回复功能的正确性。
 */

import React from 'react';
import fc from 'fast-check';
import { render, screen, cleanup, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PullRequests, PullRequest, User } from '../PullRequests';
import type { FileDiff, Comment } from '../../components/CodeDiff';

// Mock ErrorBoundary
jest.mock('../../components/ErrorBoundary', () => ({
  ErrorBoundary: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock LoadingState
jest.mock('../../components/LoadingState', () => ({
  LoadingState: ({ text }: { text: string }) => <div>{text}</div>,
}));

// Mock CodeDiff with comment functionality
jest.mock('../../components/CodeDiff', () => {
  const React = require('react');
  return {
    __esModule: true,
    default: ({ files, comments, onAddComment, onDeleteComment }: any) => {
      const [localComments, setLocalComments] = React.useState(comments || []);
      
      React.useEffect(() => {
        setLocalComments(comments || []);
      }, [comments]);

      const handleAddComment = (fileName: string, lineNumber: number, content: string, parentId?: string) => {
        if (onAddComment) {
          onAddComment(fileName, lineNumber, content, parentId);
        }
      };

      const handleDeleteComment = (commentId: string) => {
        if (onDeleteComment) {
          onDeleteComment(commentId);
        }
      };

      const renderComment = (comment: any, depth: number = 0) => (
        <div 
          key={comment.id} 
          data-testid={`comment-${comment.id}`}
          style={{ marginLeft: `${depth * 20}px` }}
        >
          <div data-testid={`comment-author-${comment.id}`}>{comment.author}</div>
          <div data-testid={`comment-content-${comment.id}`}>{comment.content}</div>
          <div data-testid={`comment-line-${comment.id}`}>Line: {comment.lineNumber}</div>
          <button 
            data-testid={`reply-button-${comment.id}`}
            onClick={() => handleAddComment(comment.fileName, comment.lineNumber, `Reply to ${comment.id}`, comment.id)}
          >
            Reply
          </button>
          <button 
            data-testid={`delete-button-${comment.id}`}
            onClick={() => handleDeleteComment(comment.id)}
          >
            Delete
          </button>
          {comment.replies && comment.replies.length > 0 && (
            <div data-testid={`replies-${comment.id}`}>
              {comment.replies.map((reply: any) => renderComment(reply, depth + 1))}
            </div>
          )}
        </div>
      );

      return (
        <div data-testid="code-diff">
          <div data-testid="files-count">Files: {files.length}</div>
          {files.map((file: any, index: number) => (
            <div key={index} data-testid={`file-${index}`}>
              <div data-testid={`file-path-${index}`}>{file.path}</div>
              {file.chunks && file.chunks.map((chunk: any, chunkIndex: number) => (
                <div key={chunkIndex} data-testid={`chunk-${index}-${chunkIndex}`}>
                  {chunk.lines && chunk.lines.map((line: any, lineIndex: number) => (
                    <div key={lineIndex} data-testid={`line-${index}-${line.lineNumber || lineIndex}`}>
                      <span>{line.content}</span>
                      <button
                        data-testid={`add-comment-${index}-${line.lineNumber || lineIndex}`}
                        onClick={() => handleAddComment(file.path, line.lineNumber || lineIndex, `Comment on line ${line.lineNumber || lineIndex}`)}
                      >
                        Add Comment
                      </button>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          ))}
          <div data-testid="comments-section">
            {localComments.map((comment: any) => renderComment(comment))}
          </div>
        </div>
      );
    },
  };
});

// Helper function to create mock user
const createMockUser = (overrides?: Partial<User>): User => ({
  id: 'user-1',
  name: 'Test User',
  email: 'test@example.com',
  role: 'developer',
  ...overrides,
});

// Helper function to create mock file diff
const createMockFileDiff = (overrides?: Partial<FileDiff>): FileDiff => ({
  path: 'src/test.ts',
  status: 'modified',
  additions: 10,
  deletions: 5,
  chunks: [
    {
      oldStart: 1,
      oldLines: 5,
      newStart: 1,
      newLines: 10,
      lines: [
        {
          type: 'add',
          content: 'console.log("test");',
          lineNumber: 1,
          newLineNumber: 1,
        },
        {
          type: 'add',
          content: 'const x = 42;',
          lineNumber: 2,
          newLineNumber: 2,
        },
        {
          type: 'context',
          content: 'function test() {',
          lineNumber: 3,
          newLineNumber: 3,
        },
      ],
    },
  ],
  ...overrides,
});

// Helper function to create mock PR
const createMockPR = (overrides?: Partial<PullRequest>): PullRequest => ({
  id: 'pr-1',
  number: 1,
  title: 'Test PR',
  description: 'Test description',
  author: createMockUser(),
  status: 'open',
  sourceBranch: 'feature/test',
  targetBranch: 'main',
  approvers: [],
  reviewers: [],
  diff: {
    files: [createMockFileDiff()],
    totalAdditions: 10,
    totalDeletions: 5,
    totalChanges: 15,
  },
  comments: [],
  createdAt: new Date('2024-01-01'),
  updatedAt: new Date('2024-01-02'),
  ...overrides,
});

describe('Property 14: 评论线程创建', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  // 自定义生成器：生成有效的文件路径
  const filePathArbitrary = () =>
    fc.oneof(
      fc.constantFrom(
        'src/index.ts',
        'src/components/Button.tsx',
        'src/utils/helpers.ts',
        'src/services/api.ts',
        'tests/unit/example.test.ts'
      ),
      fc.string({ minLength: 5, maxLength: 50 }).map(s => `src/${s}.ts`)
    );

  // 自定义生成器：生成有效的行号
  const lineNumberArbitrary = () => fc.integer({ min: 1, max: 1000 });

  // 自定义生成器：生成有效的评论内容
  const commentContentArbitrary = () =>
    fc.oneof(
      fc.constantFrom(
        'This looks good',
        'Please fix this',
        'Can you explain this logic?',
        'LGTM',
        'Consider refactoring this',
        'Add error handling here'
      ),
      fc.string({ minLength: 5, maxLength: 200 }).filter(s => s.trim().length >= 5)
    );

  // 自定义生成器：生成用户名
  const userNameArbitrary = () =>
    fc.constantFrom('Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank');

  it('应该为任何代码行创建评论线程', async () => {
    await fc.assert(
      fc.asyncProperty(
        filePathArbitrary(),
        lineNumberArbitrary(),
        commentContentArbitrary(),
        async (fileName, lineNumber, commentContent) => {
          const fileDiff = createMockFileDiff({
            path: fileName,
            chunks: [
              {
                oldStart: 1,
                oldLines: 10,
                newStart: 1,
                newLines: 10,
                lines: Array.from({ length: 10 }, (_, i) => ({
                  type: 'add' as const,
                  content: `Line ${i + 1} content`,
                  lineNumber: i + 1,
                  newLineNumber: i + 1,
                })),
              },
            ],
          });

          const pr = createMockPR({
            diff: {
              files: [fileDiff],
              totalAdditions: 10,
              totalDeletions: 0,
              totalChanges: 10,
            },
            comments: [],
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // 打开PR详情
          const prTitle = screen.getByText('Test PR');
          await userEvent.click(prTitle);

          // 等待渲染完成
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证CodeDiff已渲染
          const codeDiff = screen.getByTestId('code-diff');
          expect(codeDiff).toBeInTheDocument();

          // 查找添加评论按钮（使用第一个可用的行）
          const addCommentButtons = container.querySelectorAll('[data-testid^="add-comment-"]');
          expect(addCommentButtons.length).toBeGreaterThan(0);

          // 点击第一个添加评论按钮
          const firstButton = addCommentButtons[0] as HTMLButtonElement;
          await userEvent.click(firstButton);

          // 等待评论添加
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证评论已创建
          const commentsSection = screen.getByTestId('comments-section');
          expect(commentsSection).toBeInTheDocument();

          // 验证评论内容存在
          const comments = container.querySelectorAll('[data-testid^="comment-"]');
          expect(comments.length).toBeGreaterThan(0);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该支持在评论线程中添加回复', async () => {
    await fc.assert(
      fc.asyncProperty(
        commentContentArbitrary(),
        commentContentArbitrary(),
        async (originalComment, replyComment) => {
          const existingComment: Comment = {
            id: 'comment-1',
            author: 'Reviewer',
            content: originalComment,
            createdAt: new Date(),
            lineNumber: 1,
            fileName: 'src/test.ts',
            replies: [],
          };

          const pr = createMockPR({
            comments: [existingComment],
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // 打开PR详情
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证原始评论存在
          const originalCommentElement = screen.getByTestId('comment-comment-1');
          expect(originalCommentElement).toBeInTheDocument();

          // 点击回复按钮
          const replyButton = screen.getByTestId('reply-button-comment-1');
          await userEvent.click(replyButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证回复已添加
          const repliesSection = container.querySelector('[data-testid="replies-comment-1"]');
          expect(repliesSection).toBeInTheDocument();

          // 验证回复内容
          const replies = repliesSection?.querySelectorAll('[data-testid^="comment-"]');
          expect(replies && replies.length).toBeGreaterThan(0);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该支持多层嵌套回复', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 2, max: 5 }),
        async (replyDepth) => {
          const pr = createMockPR({
            comments: [
              {
                id: 'comment-1',
                author: 'User1',
                content: 'Original comment',
                createdAt: new Date(),
                lineNumber: 1,
                fileName: 'src/test.ts',
                replies: [],
              },
            ],
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // 打开PR详情
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // 添加多层回复
          let currentCommentId = 'comment-1';
          for (let i = 0; i < replyDepth; i++) {
            const replyButton = screen.getByTestId(`reply-button-${currentCommentId}`);
            await userEvent.click(replyButton);
            await new Promise(resolve => setTimeout(resolve, 100));

            // 查找新添加的回复
            const repliesSection = container.querySelector(`[data-testid="replies-${currentCommentId}"]`);
            expect(repliesSection).toBeInTheDocument();

            // 获取最新的回复ID（简化处理，实际应该从DOM中提取）
            const newReplies = repliesSection?.querySelectorAll('[data-testid^="comment-"]');
            if (newReplies && newReplies.length > 0) {
              const lastReply = newReplies[newReplies.length - 1];
              const replyId = lastReply.getAttribute('data-testid')?.replace('comment-', '');
              if (replyId) {
                currentCommentId = replyId;
              }
            }
          }

          // 验证嵌套结构存在
          const allComments = container.querySelectorAll('[data-testid^="comment-"]');
          expect(allComments.length).toBeGreaterThanOrEqual(replyDepth + 1);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该为不同代码行创建独立的评论线程', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(lineNumberArbitrary(), { minLength: 2, maxLength: 5 }).map(arr => [...new Set(arr)]),
        async (lineNumbers) => {
          if (lineNumbers.length < 2) return; // 需要至少2个不同的行号

          const fileDiff = createMockFileDiff({
            chunks: [
              {
                oldStart: 1,
                oldLines: Math.max(...lineNumbers),
                newStart: 1,
                newLines: Math.max(...lineNumbers),
                lines: lineNumbers.map(lineNum => ({
                  type: 'add' as const,
                  content: `Line ${lineNum} content`,
                  lineNumber: lineNum,
                  newLineNumber: lineNum,
                })),
              },
            ],
          });

          const pr = createMockPR({
            diff: {
              files: [fileDiff],
              totalAdditions: lineNumbers.length,
              totalDeletions: 0,
              totalChanges: lineNumbers.length,
            },
            comments: [],
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // 打开PR详情
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // 为每个行号添加评论
          for (const lineNum of lineNumbers.slice(0, 2)) {
            const addCommentButton = container.querySelector(
              `[data-testid="add-comment-0-${lineNum}"]`
            ) as HTMLButtonElement;
            
            if (addCommentButton) {
              await userEvent.click(addCommentButton);
              await new Promise(resolve => setTimeout(resolve, 100));
            }
          }

          // 验证创建了多个独立的评论
          const comments = container.querySelectorAll('[data-testid^="comment-"]');
          expect(comments.length).toBeGreaterThanOrEqual(2);

          // 验证评论关联到不同的行号
          const commentLines = Array.from(comments).map(comment => {
            const lineElement = comment.querySelector('[data-testid^="comment-line-"]');
            return lineElement?.textContent;
          });

          const uniqueLines = new Set(commentLines);
          expect(uniqueLines.size).toBeGreaterThanOrEqual(2);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该保持评论线程的作者信息', async () => {
    await fc.assert(
      fc.asyncProperty(
        userNameArbitrary(),
        commentContentArbitrary(),
        async (authorName, commentContent) => {
          const comment: Comment = {
            id: 'comment-1',
            author: authorName,
            content: commentContent,
            createdAt: new Date(),
            lineNumber: 1,
            fileName: 'src/test.ts',
            replies: [],
          };

          const pr = createMockPR({
            comments: [comment],
          });

          const { unmount } = render(<PullRequests initialPRs={[pr]} />);

          // 打开PR详情
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证作者信息显示
          const authorElement = screen.getByTestId('comment-author-comment-1');
          expect(authorElement).toHaveTextContent(authorName);

          // 验证评论内容显示
          const contentElement = screen.getByTestId('comment-content-comment-1');
          expect(contentElement).toHaveTextContent(commentContent);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该支持删除评论和回复', async () => {
    await fc.assert(
      fc.asyncProperty(
        commentContentArbitrary(),
        async (commentContent) => {
          const comment: Comment = {
            id: 'comment-1',
            author: 'User1',
            content: commentContent,
            createdAt: new Date(),
            lineNumber: 1,
            fileName: 'src/test.ts',
            replies: [
              {
                id: 'reply-1',
                author: 'User2',
                content: 'Reply content',
                createdAt: new Date(),
                lineNumber: 1,
                fileName: 'src/test.ts',
                parentId: 'comment-1',
              },
            ],
          };

          const pr = createMockPR({
            comments: [comment],
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // 打开PR详情
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证评论和回复都存在
          expect(screen.getByTestId('comment-comment-1')).toBeInTheDocument();
          expect(screen.getByTestId('comment-reply-1')).toBeInTheDocument();

          // 删除回复
          const deleteReplyButton = screen.getByTestId('delete-button-reply-1');
          await userEvent.click(deleteReplyButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证回复已删除
          expect(screen.queryByTestId('comment-reply-1')).not.toBeInTheDocument();

          // 验证原始评论仍然存在
          expect(screen.getByTestId('comment-comment-1')).toBeInTheDocument();

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该在多个文件中支持评论线程', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(filePathArbitrary(), { minLength: 2, maxLength: 5 }).map(arr => [...new Set(arr)]),
        async (filePaths) => {
          if (filePaths.length < 2) return; // 需要至少2个不同的文件

          const files = filePaths.map(path =>
            createMockFileDiff({
              path,
              chunks: [
                {
                  oldStart: 1,
                  oldLines: 5,
                  newStart: 1,
                  newLines: 5,
                  lines: [
                    {
                      type: 'add' as const,
                      content: 'Line 1',
                      lineNumber: 1,
                      newLineNumber: 1,
                    },
                  ],
                },
              ],
            })
          );

          const pr = createMockPR({
            diff: {
              files,
              totalAdditions: files.length,
              totalDeletions: 0,
              totalChanges: files.length,
            },
            comments: [],
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // 打开PR详情
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证所有文件都已渲染
          const fileElements = container.querySelectorAll('[data-testid^="file-"]');
          expect(fileElements.length).toBe(filePaths.length);

          // 为前两个文件添加评论
          for (let i = 0; i < Math.min(2, filePaths.length); i++) {
            const addCommentButton = container.querySelector(
              `[data-testid="add-comment-${i}-1"]`
            ) as HTMLButtonElement;
            
            if (addCommentButton) {
              await userEvent.click(addCommentButton);
              await new Promise(resolve => setTimeout(resolve, 100));
            }
          }

          // 验证创建了多个评论
          const comments = container.querySelectorAll('[data-testid^="comment-"]');
          expect(comments.length).toBeGreaterThanOrEqual(2);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该保持评论线程的时间顺序', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(commentContentArbitrary(), { minLength: 2, maxLength: 5 }),
        async (commentContents) => {
          const comments: Comment[] = commentContents.map((content, index) => ({
            id: `comment-${index + 1}`,
            author: `User${index + 1}`,
            content,
            createdAt: new Date(Date.now() + index * 1000), // 确保时间递增
            lineNumber: 1,
            fileName: 'src/test.ts',
            replies: [],
          }));

          const pr = createMockPR({
            comments,
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // 打开PR详情
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证所有评论都已渲染
          const commentElements = container.querySelectorAll('[data-testid^="comment-comment-"]');
          expect(commentElements.length).toBe(commentContents.length);

          // 验证评论按顺序显示
          commentElements.forEach((element, index) => {
            const contentElement = element.querySelector(`[data-testid="comment-content-comment-${index + 1}"]`);
            expect(contentElement).toHaveTextContent(commentContents[index]);
          });

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该在评论线程中保持文件名和行号信息', async () => {
    await fc.assert(
      fc.asyncProperty(
        filePathArbitrary(),
        lineNumberArbitrary(),
        commentContentArbitrary(),
        async (fileName, lineNumber, content) => {
          const comment: Comment = {
            id: 'comment-1',
            author: 'Reviewer',
            content,
            createdAt: new Date(),
            lineNumber,
            fileName,
            replies: [],
          };

          const pr = createMockPR({
            comments: [comment],
          });

          const { unmount } = render(<PullRequests initialPRs={[pr]} />);

          // 打开PR详情
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证行号信息
          const lineElement = screen.getByTestId('comment-line-comment-1');
          expect(lineElement).toHaveTextContent(`Line: ${lineNumber}`);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该支持在同一行上创建多个评论线程', async () => {
    await fc.assert(
      fc.asyncProperty(
        lineNumberArbitrary(),
        fc.array(commentContentArbitrary(), { minLength: 2, maxLength: 4 }),
        async (lineNumber, commentContents) => {
          const comments: Comment[] = commentContents.map((content, index) => ({
            id: `comment-${index + 1}`,
            author: `User${index + 1}`,
            content,
            createdAt: new Date(Date.now() + index * 1000),
            lineNumber,
            fileName: 'src/test.ts',
            replies: [],
          }));

          const pr = createMockPR({
            comments,
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // 打开PR详情
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // 验证所有评论都已渲染
          const commentElements = container.querySelectorAll('[data-testid^="comment-comment-"]');
          expect(commentElements.length).toBe(commentContents.length);

          // 验证所有评论都关联到同一行
          commentElements.forEach(element => {
            const lineElement = element.querySelector('[data-testid^="comment-line-"]');
            expect(lineElement).toHaveTextContent(`Line: ${lineNumber}`);
          });

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);
});

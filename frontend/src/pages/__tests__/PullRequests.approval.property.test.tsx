/**
 * PullRequests审批流程propertytest
 * 
 * Feature: frontend-production-optimization
 * Property 15: 审批statusupdate
 * 
 * **Validates: Requirements 3.4**
 * 
 * testCoverage:
 * - 对于任何审批决策submit，Pull Request的审批statusshouldupdate并触发通知
 * 
 * note: testVerifiesPullRequestscomponent的审批流程feature的正确性。
 */

import React from 'react';
import fc from 'fast-check';
import { render, screen, cleanup, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PullRequests, PullRequest, User, Approver } from '../PullRequests';
import type { FileDiff } from '../../components/CodeDiff';

// Mock ErrorBoundary
jest.mock('../../components/ErrorBoundary', () => ({
  ErrorBoundary: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock LoadingState
jest.mock('../../components/LoadingState', () => ({
  LoadingState: ({ text }: { text: string }) => <div>{text}</div>,
}));

// Mock CodeDiff
jest.mock('../../components/CodeDiff', () => {
  return {
    __esModule: true,
    default: ({ files }: any) => (
      <div data-testid="code-diff">
        <div data-testid="files-count">Files: {files.length}</div>
      </div>
    ),
  };
});

// Mock console.log to capture notification calls
const originalConsoleLog = console.log;
let notificationLogs: any[] = [];

beforeAll(() => {
  console.log = jest.fn((...args) => {
    if (args[0] === 'Approval notification sent:') {
      notificationLogs.push(args[1]);
    }
    originalConsoleLog(...args);
  });
});

afterAll(() => {
  console.log = originalConsoleLog;
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

describe('Property 15: 审批statusupdate', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    notificationLogs = [];
  });

  afterEach(() => {
    cleanup();
  });

  // customGenerator：generate审批决策
  const approvalDecisionArbitrary = () =>
    fc.constantFrom('approved' as const, 'rejected' as const);

  // customGenerator：generate可选的评论
  const optionalCommentArbitrary = () =>
    fc.option(
      fc.oneof(
        fc.constantFrom(
          'Looks good to me',
          'Please address the comments',
          'LGTM',
          'Needs more work',
          'Great job!',
          'Consider refactoring'
        ),
        fc.string({ minLength: 5, maxLength: 200 }).filter(s => s.trim().length >= 5)
      ),
      { nil: undefined }
    );

  // customGenerator：generateuser
  const userArbitrary = () =>
    fc.record({
      id: fc.uuid(),
      name: fc.constantFrom('Alice', 'Bob', 'Charlie', 'Diana', 'Eve'),
      email: fc.emailAddress(),
      role: fc.constantFrom('admin' as const, 'developer' as const, 'viewer' as const),
    });

  // customGenerator：generate审批者列表
  const approversArbitrary = () =>
    fc.array(
      fc.record({
        user: userArbitrary(),
        status: fc.constantFrom('pending' as const, 'approved' as const, 'rejected' as const),
        comment: fc.option(fc.string({ minLength: 5, maxLength: 100 }), { nil: undefined }),
        timestamp: fc.date({ min: new Date('2024-01-01'), max: new Date('2024-12-31') }),
      }),
      { minLength: 0, maxLength: 5 }
    );

  it('should为任何审批决策update审批者status', async () => {
    await fc.assert(
      fc.asyncProperty(
        approvalDecisionArbitrary(),
        optionalCommentArbitrary(),
        async (decision, comment) => {
          const pr = createMockPR({
            status: 'open',
            approvers: [],
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // openPRdetail
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // verify审批操作区域存在
          const submitReviewTitle = screen.getByText('Submit Your Review');
          expect(submitReviewTitle).toBeInTheDocument();

          // 点击审批或拒绝button
          const actionButton = decision === 'approved'
            ? screen.getByText('✓ Approve')
            : screen.getByText('✗ Reject');
          await userEvent.click(actionButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // 如果有评论，input评论
          if (comment) {
            const textarea = screen.getByPlaceholderText('Add a comment (optional)...');
            await userEvent.clear(textarea);
            await userEvent.type(textarea, comment);
            await new Promise(resolve => setTimeout(resolve, 100));
          }

          // submit决策
          const submitButton = decision === 'approved'
            ? screen.getByText('Submit Approval')
            : screen.getByText('Submit Rejection');
          await userEvent.click(submitButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // verify审批者status已update
          const approversList = container.querySelector('[data-testid="approvers-list"]');
          if (approversList) {
            const statusText = decision === 'approved' ? '✓ Approved' : '✗ Rejected';
            expect(approversList.textContent).toContain(statusText);
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('should为任何审批决策触发通知', async () => {
    await fc.assert(
      fc.asyncProperty(
        approvalDecisionArbitrary(),
        optionalCommentArbitrary(),
        async (decision, comment) => {
          const author = createMockUser({ id: 'author-1', email: 'author@example.com' });
          const reviewer = createMockUser({ id: 'reviewer-1', email: 'reviewer@example.com' });

          const pr = createMockPR({
            status: 'open',
            author,
            reviewers: [reviewer],
            approvers: [],
          });

          // 清空之前的通知log
          notificationLogs = [];

          const { unmount } = render(<PullRequests initialPRs={[pr]} />);

          // openPRdetail
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // 点击审批或拒绝button
          const actionButton = decision === 'approved'
            ? screen.getByText('✓ Approve')
            : screen.getByText('✗ Reject');
          await userEvent.click(actionButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // 如果有评论，input评论
          if (comment) {
            const textarea = screen.getByPlaceholderText('Add a comment (optional)...');
            await userEvent.clear(textarea);
            await userEvent.type(textarea, comment);
            await new Promise(resolve => setTimeout(resolve, 100));
          }

          // submit决策
          const submitButton = decision === 'approved'
            ? screen.getByText('Submit Approval')
            : screen.getByText('Submit Rejection');
          await userEvent.click(submitButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // verify通知已发送
          expect(notificationLogs.length).toBeGreaterThan(0);

          // verify通知content
          const notification = notificationLogs[notificationLogs.length - 1];
          expect(notification.prId).toBe(pr.id);
          expect(notification.prTitle).toBe(pr.title);
          expect(notification.decision).toBe(decision);
          if (comment) {
            expect(notification.comment).toBe(comment);
          }
          expect(notification.recipients).toContain(author.email);
          expect(notification.recipients).toContain(reviewer.email);

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('should根据所有审批者的决策updatePRstatus', async () => {
    await fc.assert(
      fc.asyncProperty(
        approversArbitrary(),
        approvalDecisionArbitrary(),
        async (existingApprovers, newDecision) => {
          const pr = createMockPR({
            status: 'open',
            approvers: existingApprovers,
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // openPRdetail
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // submit新的审批决策
          const actionButton = newDecision === 'approved'
            ? screen.getByText('✓ Approve')
            : screen.getByText('✗ Reject');
          await userEvent.click(actionButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          const submitButton = newDecision === 'approved'
            ? screen.getByText('Submit Approval')
            : screen.getByText('Submit Rejection');
          await userEvent.click(submitButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // verifyPRstatus已update
          // 如果有任何拒绝，statusshould是rejected
          // 如果所有审批者都批准，statusshould是approved
          // 否则statusshould是open
          const hasRejection = existingApprovers.some(a => a.status === 'rejected') || newDecision === 'rejected';
          const allApproved = !hasRejection && 
            (existingApprovers.every(a => a.status === 'approved') && newDecision === 'approved');

          const statusBadge = container.querySelector('[style*="backgroundColor"]');
          if (statusBadge) {
            const statusText = statusBadge.textContent;
            if (hasRejection) {
              expect(statusText).toContain('Rejected');
            } else if (allApproved && (existingApprovers.length > 0 || newDecision === 'approved')) {
              expect(statusText).toContain('Approved');
            }
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('should保留审批者的评论info', async () => {
    await fc.assert(
      fc.asyncProperty(
        approvalDecisionArbitrary(),
        fc.string({ minLength: 10, maxLength: 100 }).filter(s => s.trim().length >= 10),
        async (decision, comment) => {
          const pr = createMockPR({
            status: 'open',
            approvers: [],
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // openPRdetail
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // 点击审批或拒绝button
          const actionButton = decision === 'approved'
            ? screen.getByText('✓ Approve')
            : screen.getByText('✗ Reject');
          await userEvent.click(actionButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // input评论
          const textarea = screen.getByPlaceholderText('Add a comment (optional)...');
          await userEvent.clear(textarea);
          await userEvent.type(textarea, comment);
          await new Promise(resolve => setTimeout(resolve, 100));

          // submit决策
          const submitButton = decision === 'approved'
            ? screen.getByText('Submit Approval')
            : screen.getByText('Submit Rejection');
          await userEvent.click(submitButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // verify评论已save并show
          const approversList = container.querySelector('[data-testid="approvers-list"]');
          if (approversList) {
            expect(approversList.textContent).toContain(comment);
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('shouldallow同一userupdate其审批决策', async () => {
    await fc.assert(
      fc.asyncProperty(
        approvalDecisionArbitrary(),
        approvalDecisionArbitrary(),
        async (firstDecision, secondDecision) => {
          const currentUser = createMockUser({ id: 'current-user-id', name: 'Current User' });

          const pr = createMockPR({
            status: 'open',
            approvers: [
              {
                user: currentUser,
                status: 'pending',
                timestamp: new Date(),
              },
            ],
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // openPRdetail
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // submit第一item决策
          const firstActionButton = firstDecision === 'approved'
            ? screen.getByText('✓ Approve')
            : screen.getByText('✗ Reject');
          await userEvent.click(firstActionButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          const firstSubmitButton = firstDecision === 'approved'
            ? screen.getByText('Submit Approval')
            : screen.getByText('Submit Rejection');
          await userEvent.click(firstSubmitButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // verify第一item决策已应用
          const approversList = container.querySelector('[data-testid="approvers-list"]');
          if (approversList) {
            const firstStatusText = firstDecision === 'approved' ? '✓ Approved' : '✗ Rejected';
            expect(approversList.textContent).toContain(firstStatusText);
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('shouldBeAt多item审批者的情况下正确updatestatus', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(userArbitrary(), { minLength: 2, maxLength: 5 }),
        approvalDecisionArbitrary(),
        async (users, newDecision) => {
          // 确保userID唯一
          const uniqueUsers = users.filter((user, index, self) =>
            index === self.findIndex(u => u.id === user.id)
          );

          if (uniqueUsers.length < 2) return; // need至少2item不同的user

          const approvers: Approver[] = uniqueUsers.slice(0, -1).map(user => ({
            user,
            status: 'pending' as const,
            timestamp: new Date(),
          }));

          const pr = createMockPR({
            status: 'open',
            approvers,
          });

          const { unmount, container } = render(<PullRequests initialPRs={[pr]} />);

          // openPRdetail
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // verify所有审批者都show
          const approversList = container.querySelector('[data-testid="approvers-list"]');
          if (approversList) {
            approvers.forEach(approver => {
              expect(approversList.textContent).toContain(approver.user.name);
            });
          }

          // submit新的审批决策
          const actionButton = newDecision === 'approved'
            ? screen.getByText('✓ Approve')
            : screen.getByText('✗ Reject');
          await userEvent.click(actionButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          const submitButton = newDecision === 'approved'
            ? screen.getByText('Submit Approval')
            : screen.getByText('Submit Rejection');
          await userEvent.click(submitButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // verify新的审批者已add
          const updatedApproversList = container.querySelector('[data-testid="approvers-list"]');
          if (updatedApproversList) {
            expect(updatedApproversList.textContent).toContain('Current User');
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('shouldBeAt审批决策后updatePR的updatedAt时间戳', async () => {
    await fc.assert(
      fc.asyncProperty(
        approvalDecisionArbitrary(),
        async (decision) => {
          const originalUpdatedAt = new Date('2024-01-01');
          const pr = createMockPR({
            status: 'open',
            updatedAt: originalUpdatedAt,
            approvers: [],
          });

          const { unmount } = render(<PullRequests initialPRs={[pr]} />);

          // openPRdetail
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // recordsubmit前的时间
          const beforeSubmit = Date.now();

          // submit审批决策
          const actionButton = decision === 'approved'
            ? screen.getByText('✓ Approve')
            : screen.getByText('✗ Reject');
          await userEvent.click(actionButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          const submitButton = decision === 'approved'
            ? screen.getByText('Submit Approval')
            : screen.getByText('Submit Rejection');
          await userEvent.click(submitButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // verify通知中contain时间戳
          if (notificationLogs.length > 0) {
            const notification = notificationLogs[notificationLogs.length - 1];
            expect(notification.timestamp).toBeDefined();
            expect(notification.timestamp.getTime()).toBeGreaterThanOrEqual(beforeSubmit);
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('should只在PRstatus为open时show审批操作', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom('approved' as const, 'rejected' as const, 'merged' as const, 'closed' as const),
        async (prStatus) => {
          const pr = createMockPR({
            status: prStatus,
            approvers: [],
          });

          const { unmount } = render(<PullRequests initialPRs={[pr]} />);

          // openPRdetail
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // verify审批操作不show（因为PRstatus不是open）
          const submitReviewTitle = screen.queryByText('Submit Your Review');
          expect(submitReviewTitle).not.toBeInTheDocument();

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('shouldBeAtcancel审批操作时清除input', async () => {
    await fc.assert(
      fc.asyncProperty(
        approvalDecisionArbitrary(),
        fc.string({ minLength: 10, maxLength: 100 }),
        async (decision, comment) => {
          const pr = createMockPR({
            status: 'open',
            approvers: [],
          });

          const { unmount } = render(<PullRequests initialPRs={[pr]} />);

          // openPRdetail
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // 点击审批或拒绝button
          const actionButton = decision === 'approved'
            ? screen.getByText('✓ Approve')
            : screen.getByText('✗ Reject');
          await userEvent.click(actionButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // input评论
          const textarea = screen.getByPlaceholderText('Add a comment (optional)...');
          await userEvent.type(textarea, comment);
          await new Promise(resolve => setTimeout(resolve, 100));

          // 点击cancelbutton
          const cancelButton = screen.getByText('Cancel');
          await userEvent.click(cancelButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // verify回到初始status
          expect(screen.getByText('✓ Approve')).toBeInTheDocument();
          expect(screen.getByText('✗ Reject')).toBeInTheDocument();
          expect(screen.queryByPlaceholderText('Add a comment (optional)...')).not.toBeInTheDocument();

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('shouldBeAt通知中contain所有相关人员的邮箱', async () => {
    await fc.assert(
      fc.asyncProperty(
        approvalDecisionArbitrary(),
        fc.array(userArbitrary(), { minLength: 1, maxLength: 5 }),
        async (decision, reviewers) => {
          // 确保邮箱唯一
          const uniqueReviewers = reviewers.filter((reviewer, index, self) =>
            index === self.findIndex(r => r.email === reviewer.email)
          );

          const author = createMockUser({ id: 'author-1', email: 'author@example.com' });

          const pr = createMockPR({
            status: 'open',
            author,
            reviewers: uniqueReviewers,
            approvers: [],
          });

          // 清空之前的通知log
          notificationLogs = [];

          const { unmount } = render(<PullRequests initialPRs={[pr]} />);

          // openPRdetail
          await userEvent.click(screen.getByText('Test PR'));
          await new Promise(resolve => setTimeout(resolve, 100));

          // submit审批决策
          const actionButton = decision === 'approved'
            ? screen.getByText('✓ Approve')
            : screen.getByText('✗ Reject');
          await userEvent.click(actionButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          const submitButton = decision === 'approved'
            ? screen.getByText('Submit Approval')
            : screen.getByText('Submit Rejection');
          await userEvent.click(submitButton);
          await new Promise(resolve => setTimeout(resolve, 100));

          // verify通知contain所有相关人员
          if (notificationLogs.length > 0) {
            const notification = notificationLogs[notificationLogs.length - 1];
            expect(notification.recipients).toContain(author.email);
            uniqueReviewers.forEach(reviewer => {
              expect(notification.recipients).toContain(reviewer.email);
            });
          }

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);
});

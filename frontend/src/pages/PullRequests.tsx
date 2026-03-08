/**
 * PullRequests页面组件
 * 
 * 功能:
 * - 展示Pull Request列表
 * - 集成CodeDiff组件显示代码差异
 * - 支持查看PR详情和代码变更
 * - 使用ErrorBoundary包裹
 * 
 * 验证需求: 3.1
 */

'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { LoadingState } from '../components/LoadingState';
import CodeDiff, { FileDiff, Comment } from '../components/CodeDiff';
import '../styles/responsive.css';

// Types based on design.md
export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'admin' | 'developer' | 'viewer';
}

export interface Approver {
  user: User;
  status: 'pending' | 'approved' | 'rejected';
  comment?: string;
  timestamp: Date;
}

export interface PullRequest {
  id: string;
  number: number;
  title: string;
  description: string;
  author: User;
  status: 'open' | 'approved' | 'rejected' | 'merged' | 'closed';
  sourceBranch: string;
  targetBranch: string;
  approvers: Approver[];
  reviewers: User[];
  diff: {
    files: FileDiff[];
    totalAdditions: number;
    totalDeletions: number;
    totalChanges: number;
  };
  comments: Comment[];
  createdAt: Date;
  updatedAt: Date;
}

export interface PullRequestsProps {
  /** Optional initial PR list */
  initialPRs?: PullRequest[];
}

/**
 * ApprovalActions component for submitting approval decisions
 */
interface ApprovalActionsProps {
  onSubmit: (decision: 'approved' | 'rejected', comment?: string) => void;
}

const ApprovalActions: React.FC<ApprovalActionsProps> = ({ onSubmit }) => {
  const [comment, setComment] = useState('');
  const [showCommentBox, setShowCommentBox] = useState(false);
  const [pendingDecision, setPendingDecision] = useState<'approved' | 'rejected' | null>(null);

  const handleApprove = () => {
    setPendingDecision('approved');
    setShowCommentBox(true);
  };

  const handleReject = () => {
    setPendingDecision('rejected');
    setShowCommentBox(true);
  };

  const handleSubmit = () => {
    if (pendingDecision) {
      onSubmit(pendingDecision, comment.trim() || undefined);
      setComment('');
      setShowCommentBox(false);
      setPendingDecision(null);
    }
  };

  const handleCancel = () => {
    setComment('');
    setShowCommentBox(false);
    setPendingDecision(null);
  };

  return (
    <div style={approvalStyles.container}>
      <h3 style={approvalStyles.title}>Submit Your Review</h3>
      
      {!showCommentBox ? (
        <div style={approvalStyles.buttonGroup}>
          <button
            onClick={handleApprove}
            style={{
              ...approvalStyles.button,
              ...approvalStyles.approveButton,
            }}
          >
            ✓ Approve
          </button>
          <button
            onClick={handleReject}
            style={{
              ...approvalStyles.button,
              ...approvalStyles.rejectButton,
            }}
          >
            ✗ Reject
          </button>
        </div>
      ) : (
        <div style={approvalStyles.commentSection}>
          <div style={approvalStyles.decisionLabel}>
            Decision: {pendingDecision === 'approved' ? '✓ Approve' : '✗ Reject'}
          </div>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add a comment (optional)..."
            style={approvalStyles.textarea}
            rows={4}
          />
          <div style={approvalStyles.actionButtons}>
            <button
              onClick={handleSubmit}
              style={{
                ...approvalStyles.button,
                ...(pendingDecision === 'approved'
                  ? approvalStyles.approveButton
                  : approvalStyles.rejectButton),
              }}
            >
              Submit {pendingDecision === 'approved' ? 'Approval' : 'Rejection'}
            </button>
            <button
              onClick={handleCancel}
              style={{
                ...approvalStyles.button,
                ...approvalStyles.cancelButton,
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * PullRequests页面主组件
 */
export const PullRequestsComponent: React.FC<PullRequestsProps> = ({ initialPRs = [] }) => {
  const [pullRequests, setPullRequests] = useState<PullRequest[]>(initialPRs);
  const [selectedPR, setSelectedPR] = useState<PullRequest | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [filterStatus, setFilterStatus] = useState<PullRequest['status'] | 'all'>('all');

  // Filter PRs by status
  const filteredPRs = useMemo(() => {
    if (filterStatus === 'all') {
      return pullRequests;
    }
    return pullRequests.filter((pr) => pr.status === filterStatus);
  }, [pullRequests, filterStatus]);

  // Handle PR selection
  const handleSelectPR = useCallback((pr: PullRequest) => {
    setSelectedPR(pr);
  }, []);

  // Handle back to list
  const handleBackToList = useCallback(() => {
    setSelectedPR(null);
  }, []);

  // Handle add comment or reply
  const handleAddComment = useCallback(
    (fileName: string, lineNumber: number, content: string, parentId?: string) => {
      if (!selectedPR) return;

      const newComment: Comment = {
        id: `comment-${Date.now()}`,
        author: 'Current User', // In real app, get from auth context
        content,
        createdAt: new Date(),
        lineNumber,
        fileName,
        parentId,
        replies: [],
      };

      let updatedComments: Comment[];

      if (parentId) {
        // This is a reply - add it to the parent comment's replies array
        updatedComments = selectedPR.comments.map((comment) => {
          if (comment.id === parentId) {
            return {
              ...comment,
              replies: [...(comment.replies || []), newComment],
            };
          }
          return comment;
        });
      } else {
        // This is a new top-level comment
        updatedComments = [...selectedPR.comments, newComment];
      }

      // Update selected PR with new comment
      const updatedPR = {
        ...selectedPR,
        comments: updatedComments,
      };

      setSelectedPR(updatedPR);

      // Update PR in list
      setPullRequests((prev) =>
        prev.map((pr) => (pr.id === selectedPR.id ? updatedPR : pr))
      );
    },
    [selectedPR]
  );

  // Handle delete comment or reply
  const handleDeleteComment = useCallback(
    (commentId: string) => {
      if (!selectedPR) return;

      // Helper function to recursively remove comment or reply
      const removeComment = (comments: Comment[]): Comment[] => {
        return comments
          .filter((c) => c.id !== commentId)
          .map((c) => ({
            ...c,
            replies: c.replies ? removeComment(c.replies) : [],
          }));
      };

      const updatedPR = {
        ...selectedPR,
        comments: removeComment(selectedPR.comments),
      };

      setSelectedPR(updatedPR);

      // Update PR in list
      setPullRequests((prev) =>
        prev.map((pr) => (pr.id === selectedPR.id ? updatedPR : pr))
      );
    },
    [selectedPR]
  );

  // Handle approval decision submission
  const handleApprovalDecision = useCallback(
    (decision: 'approved' | 'rejected', comment?: string) => {
      if (!selectedPR) return;

      // Get current user (in real app, get from auth context)
      const currentUser: User = {
        id: 'current-user-id',
        name: 'Current User',
        email: 'current@example.com',
        role: 'developer',
      };

      // Update approver status
      const updatedApprovers = selectedPR.approvers.map((approver) => {
        if (approver.user.id === currentUser.id) {
          return {
            ...approver,
            status: decision,
            comment,
            timestamp: new Date(),
          };
        }
        return approver;
      });

      // If current user is not in approvers list, add them
      const isApprover = selectedPR.approvers.some(
        (a) => a.user.id === currentUser.id
      );
      if (!isApprover) {
        updatedApprovers.push({
          user: currentUser,
          status: decision,
          comment,
          timestamp: new Date(),
        });
      }

      // Determine new PR status based on approvals
      let newStatus = selectedPR.status;
      const allApproved = updatedApprovers.every(
        (a) => a.status === 'approved'
      );
      const anyRejected = updatedApprovers.some(
        (a) => a.status === 'rejected'
      );

      if (anyRejected) {
        newStatus = 'rejected';
      } else if (allApproved && updatedApprovers.length > 0) {
        newStatus = 'approved';
      } else if (selectedPR.status === 'rejected' || selectedPR.status === 'approved') {
        // If status was rejected/approved but now has pending approvers, set to open
        newStatus = 'open';
      }

      const updatedPR = {
        ...selectedPR,
        approvers: updatedApprovers,
        status: newStatus,
        updatedAt: new Date(),
      };

      setSelectedPR(updatedPR);

      // Update PR in list
      setPullRequests((prev) =>
        prev.map((pr) => (pr.id === selectedPR.id ? updatedPR : pr))
      );

      // Send notification (in real app, this would be an API call)
      sendApprovalNotification(selectedPR, decision, comment);
    },
    [selectedPR]
  );

  // Send approval notification
  const sendApprovalNotification = useCallback(
    (pr: PullRequest, decision: 'approved' | 'rejected', comment?: string) => {
      // In a real application, this would send a notification via API
      // For now, we'll just log it
      console.log('Approval notification sent:', {
        prId: pr.id,
        prTitle: pr.title,
        decision,
        comment,
        timestamp: new Date(),
        recipients: [pr.author.email, ...pr.reviewers.map((r) => r.email)],
      });

      // Show a simple notification to the user
      if (typeof window !== 'undefined' && 'Notification' in window) {
        if (Notification.permission === 'granted') {
          new Notification(`PR #${pr.number} ${decision}`, {
            body: comment || `Pull request has been ${decision}`,
            icon: '/notification-icon.png',
          });
        }
      }
    },
    []
  );

  // Get status badge color
  const getStatusColor = (status: PullRequest['status']): string => {
    switch (status) {
      case 'open':
        return '#2563eb'; // blue
      case 'approved':
        return '#16a34a'; // green
      case 'rejected':
        return '#dc2626'; // red
      case 'merged':
        return '#7c3aed'; // purple
      case 'closed':
        return '#6b7280'; // gray
      default:
        return '#6b7280';
    }
  };

  // Get status badge text
  const getStatusText = (status: PullRequest['status']): string => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  // Loading state
  if (loading) {
    return <LoadingState text="Loading pull requests..." />;
  }

  // Error state
  if (error) {
    return (
      <div style={styles.errorContainer}>
        <div style={styles.errorIcon}>⚠️</div>
        <h2 style={styles.errorTitle}>Failed to Load Pull Requests</h2>
        <p style={styles.errorMessage}>{error.message}</p>
      </div>
    );
  }

  // Detail view - show selected PR with CodeDiff
  if (selectedPR) {
    return (
      <div style={styles.container}>
        {/* Header */}
        <div style={styles.detailHeader}>
          <button onClick={handleBackToList} style={styles.backButton}>
            ← Back to List
          </button>
          <div style={styles.prTitleSection}>
            <h1 style={styles.prTitle}>
              #{selectedPR.number} {selectedPR.title}
            </h1>
            <span
              style={{
                ...styles.statusBadge,
                backgroundColor: getStatusColor(selectedPR.status),
              }}
            >
              {getStatusText(selectedPR.status)}
            </span>
          </div>
        </div>

        {/* PR Info */}
        <div style={styles.prInfo}>
          <div style={styles.prInfoRow}>
            <span style={styles.prInfoLabel}>Author:</span>
            <span style={styles.prInfoValue}>{selectedPR.author.name}</span>
          </div>
          <div style={styles.prInfoRow}>
            <span style={styles.prInfoLabel}>Branch:</span>
            <span style={styles.prInfoValue}>
              {selectedPR.sourceBranch} → {selectedPR.targetBranch}
            </span>
          </div>
          <div style={styles.prInfoRow}>
            <span style={styles.prInfoLabel}>Created:</span>
            <span style={styles.prInfoValue}>
              {selectedPR.createdAt.toLocaleString()}
            </span>
          </div>
          <div style={styles.prInfoRow}>
            <span style={styles.prInfoLabel}>Changes:</span>
            <span style={styles.prInfoValue}>
              <span style={{ color: '#16a34a' }}>
                +{selectedPR.diff.totalAdditions}
              </span>
              {' / '}
              <span style={{ color: '#dc2626' }}>
                -{selectedPR.diff.totalDeletions}
              </span>
            </span>
          </div>
        </div>

        {/* Description */}
        {selectedPR.description && (
          <div style={styles.descriptionSection}>
            <h3 style={styles.sectionTitle}>Description</h3>
            <p style={styles.description}>{selectedPR.description}</p>
          </div>
        )}

        {/* Approvers */}
        {selectedPR.approvers.length > 0 && (
          <div style={styles.approversSection}>
            <h3 style={styles.sectionTitle}>Approvers</h3>
            <div style={styles.approversList} data-testid="approvers-list">
              {selectedPR.approvers.map((approver, index) => (
                <div key={index} style={styles.approverItem}>
                  <div style={styles.approverInfo}>
                    <span style={styles.approverName}>{approver.user.name}</span>
                    {approver.comment && (
                      <span style={styles.approverComment}>
                        "{approver.comment}"
                      </span>
                    )}
                    <span style={styles.approverTimestamp}>
                      {approver.timestamp.toLocaleString()}
                    </span>
                  </div>
                  <span
                    style={{
                      ...styles.approverStatus,
                      color:
                        approver.status === 'approved'
                          ? '#16a34a'
                          : approver.status === 'rejected'
                          ? '#dc2626'
                          : '#6b7280',
                    }}
                  >
                    {approver.status === 'approved'
                      ? '✓ Approved'
                      : approver.status === 'rejected'
                      ? '✗ Rejected'
                      : '⏳ Pending'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Approval Actions */}
        {selectedPR.status === 'open' && (
          <ApprovalActions onSubmit={handleApprovalDecision} />
        )}

        {/* Code Diff */}
        <div style={styles.diffSection}>
          <h3 style={styles.sectionTitle}>Code Changes</h3>
          <CodeDiff
            files={selectedPR.diff.files}
            comments={selectedPR.comments}
            onAddComment={handleAddComment}
            onDeleteComment={handleDeleteComment}
            enablePagination={true}
            linesPerPage={1000}
          />
        </div>
      </div>
    );
  }

  // List view - show all PRs
  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>Pull Requests</h1>
        <div style={styles.headerActions}>
          <span style={styles.prCount}>
            {filteredPRs.length} {filteredPRs.length === 1 ? 'PR' : 'PRs'}
          </span>
        </div>
      </div>

      {/* Filter Bar */}
      <div style={styles.filterBar}>
        <span style={styles.filterLabel}>Filter:</span>
        <button
          onClick={() => setFilterStatus('all')}
          style={{
            ...styles.filterButton,
            ...(filterStatus === 'all' ? styles.filterButtonActive : {}),
          }}
        >
          All
        </button>
        <button
          onClick={() => setFilterStatus('open')}
          style={{
            ...styles.filterButton,
            ...(filterStatus === 'open' ? styles.filterButtonActive : {}),
          }}
        >
          Open
        </button>
        <button
          onClick={() => setFilterStatus('approved')}
          style={{
            ...styles.filterButton,
            ...(filterStatus === 'approved' ? styles.filterButtonActive : {}),
          }}
        >
          Approved
        </button>
        <button
          onClick={() => setFilterStatus('merged')}
          style={{
            ...styles.filterButton,
            ...(filterStatus === 'merged' ? styles.filterButtonActive : {}),
          }}
        >
          Merged
        </button>
        <button
          onClick={() => setFilterStatus('closed')}
          style={{
            ...styles.filterButton,
            ...(filterStatus === 'closed' ? styles.filterButtonActive : {}),
          }}
        >
          Closed
        </button>
      </div>

      {/* PR List */}
      {filteredPRs.length === 0 ? (
        <div style={styles.emptyState}>
          <div style={styles.emptyIcon}>📋</div>
          <h2 style={styles.emptyTitle}>No Pull Requests</h2>
          <p style={styles.emptyMessage}>
            {filterStatus === 'all'
              ? 'There are no pull requests yet.'
              : `No ${filterStatus} pull requests found.`}
          </p>
        </div>
      ) : (
        <div style={styles.prList}>
          {filteredPRs.map((pr) => (
            <div
              key={pr.id}
              style={styles.prCard}
              onClick={() => handleSelectPR(pr)}
            >
              <div style={styles.prCardHeader}>
                <div style={styles.prCardTitle}>
                  <span style={styles.prNumber}>#{pr.number}</span>
                  <span style={styles.prTitleText}>{pr.title}</span>
                </div>
                <span
                  style={{
                    ...styles.statusBadge,
                    backgroundColor: getStatusColor(pr.status),
                  }}
                >
                  {getStatusText(pr.status)}
                </span>
              </div>
              <div style={styles.prCardMeta}>
                <span style={styles.prMetaItem}>
                  👤 {pr.author.name}
                </span>
                <span style={styles.prMetaItem}>
                  🔀 {pr.sourceBranch} → {pr.targetBranch}
                </span>
                <span style={styles.prMetaItem}>
                  📅 {pr.createdAt.toLocaleDateString()}
                </span>
                <span style={styles.prMetaItem}>
                  <span style={{ color: '#16a34a' }}>
                    +{pr.diff.totalAdditions}
                  </span>
                  {' / '}
                  <span style={{ color: '#dc2626' }}>
                    -{pr.diff.totalDeletions}
                  </span>
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * PullRequests组件 - 使用ErrorBoundary包裹
 */
export const PullRequests: React.FC<PullRequestsProps> = (props) => {
  return (
    <ErrorBoundary>
      <PullRequestsComponent {...props} />
    </ErrorBoundary>
  );
};

// Styles - Responsive design
const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: 'clamp(16px, 3vw, 24px)',
    maxWidth: '100%',
    width: '100%',
    margin: '0 auto',
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    overflowX: 'hidden',
  },
  header: {
    display: 'flex',
    flexDirection: window.innerWidth < 768 ? 'column' : 'row',
    justifyContent: 'space-between',
    alignItems: window.innerWidth < 768 ? 'flex-start' : 'center',
    marginBottom: 'clamp(16px, 3vw, 24px)',
    gap: '12px',
  },
  title: {
    fontSize: 'clamp(24px, 5vw, 32px)',
    fontWeight: 'bold',
    color: '#1f2937',
    margin: 0,
    wordWrap: 'break-word',
  },
  headerActions: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    flexWrap: 'wrap',
  },
  prCount: {
    fontSize: 'clamp(12px, 2.5vw, 14px)',
    color: '#6b7280',
    padding: '4px 12px',
    backgroundColor: '#f3f4f6',
    borderRadius: '12px',
    whiteSpace: 'nowrap',
  },
  filterBar: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: 'clamp(16px, 3vw, 24px)',
    padding: 'clamp(12px, 2vw, 16px)',
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    flexWrap: 'wrap',
    overflowX: 'auto',
  },
  filterLabel: {
    fontSize: 'clamp(12px, 2.5vw, 14px)',
    fontWeight: '500',
    color: '#6b7280',
    marginRight: '8px',
    whiteSpace: 'nowrap',
  },
  filterButton: {
    padding: '6px 12px',
    fontSize: 'clamp(12px, 2.5vw, 14px)',
    fontWeight: '500',
    color: '#6b7280',
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    whiteSpace: 'nowrap',
  },
  filterButtonActive: {
    color: '#fff',
    backgroundColor: '#2563eb',
    borderColor: '#2563eb',
  },
  prList: {
    display: 'flex',
    flexDirection: 'column',
    gap: 'clamp(12px, 2vw, 16px)',
  },
  prCard: {
    padding: 'clamp(16px, 3vw, 20px)',
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    maxWidth: '100%',
    overflowX: 'hidden',
  },
  prCardHeader: {
    display: 'flex',
    flexDirection: window.innerWidth < 480 ? 'column' : 'row',
    justifyContent: 'space-between',
    alignItems: window.innerWidth < 480 ? 'flex-start' : 'center',
    marginBottom: '12px',
    gap: '8px',
  },
  prCardTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    flex: 1,
    minWidth: 0,
  },
  prNumber: {
    fontSize: 'clamp(12px, 2.5vw, 14px)',
    fontWeight: '600',
    color: '#6b7280',
    flexShrink: 0,
  },
  prTitleText: {
    fontSize: 'clamp(14px, 3vw, 16px)',
    fontWeight: '600',
    color: '#1f2937',
    wordWrap: 'break-word',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  statusBadge: {
    padding: '4px 12px',
    fontSize: 'clamp(11px, 2vw, 12px)',
    fontWeight: '600',
    color: '#fff',
    borderRadius: '12px',
    whiteSpace: 'nowrap',
    flexShrink: 0,
  },
  prCardMeta: {
    display: 'flex',
    gap: 'clamp(8px, 2vw, 16px)',
    fontSize: 'clamp(12px, 2.5vw, 14px)',
    color: '#6b7280',
    flexWrap: 'wrap',
  },
  prMetaItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    whiteSpace: 'nowrap',
  },
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 'clamp(40px, 8vw, 60px) 20px',
    textAlign: 'center',
  },
  emptyIcon: {
    fontSize: 'clamp(48px, 10vw, 64px)',
    marginBottom: '16px',
  },
  emptyTitle: {
    fontSize: 'clamp(20px, 4vw, 24px)',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '8px',
    wordWrap: 'break-word',
  },
  emptyMessage: {
    fontSize: 'clamp(14px, 3vw, 16px)',
    color: '#6b7280',
    wordWrap: 'break-word',
  },
  errorContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 'clamp(40px, 8vw, 60px) 20px',
    textAlign: 'center',
  },
  errorIcon: {
    fontSize: 'clamp(48px, 10vw, 64px)',
    marginBottom: '16px',
  },
  errorTitle: {
    fontSize: 'clamp(20px, 4vw, 24px)',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '8px',
    wordWrap: 'break-word',
  },
  errorMessage: {
    fontSize: 'clamp(14px, 3vw, 16px)',
    color: '#6b7280',
    wordWrap: 'break-word',
  },
  detailHeader: {
    marginBottom: 'clamp(16px, 3vw, 24px)',
  },
  backButton: {
    padding: '8px 16px',
    fontSize: 'clamp(12px, 2.5vw, 14px)',
    fontWeight: '500',
    color: '#2563eb',
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '6px',
    cursor: 'pointer',
    marginBottom: '16px',
    transition: 'all 0.2s',
    whiteSpace: 'nowrap',
  },
  prTitleSection: {
    display: 'flex',
    flexDirection: window.innerWidth < 480 ? 'column' : 'row',
    alignItems: window.innerWidth < 480 ? 'flex-start' : 'center',
    gap: '12px',
  },
  prTitle: {
    fontSize: 'clamp(20px, 4vw, 28px)',
    fontWeight: 'bold',
    color: '#1f2937',
    margin: 0,
    wordWrap: 'break-word',
  },
  prInfo: {
    padding: 'clamp(16px, 3vw, 20px)',
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    marginBottom: 'clamp(16px, 3vw, 24px)',
    overflowX: 'hidden',
  },
  prInfoRow: {
    display: 'flex',
    flexDirection: window.innerWidth < 480 ? 'column' : 'row',
    alignItems: window.innerWidth < 480 ? 'flex-start' : 'center',
    gap: '8px',
    marginBottom: '8px',
  },
  prInfoLabel: {
    fontSize: 'clamp(12px, 2.5vw, 14px)',
    fontWeight: '600',
    color: '#6b7280',
    minWidth: window.innerWidth < 480 ? 'auto' : '80px',
  },
  prInfoValue: {
    fontSize: 'clamp(12px, 2.5vw, 14px)',
    color: '#1f2937',
    wordWrap: 'break-word',
  },
  descriptionSection: {
    padding: 'clamp(16px, 3vw, 20px)',
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    marginBottom: 'clamp(16px, 3vw, 24px)',
    overflowX: 'hidden',
  },
  sectionTitle: {
    fontSize: 'clamp(16px, 3.5vw, 18px)',
    fontWeight: '600',
    color: '#1f2937',
    marginTop: 0,
    marginBottom: '12px',
  },
  description: {
    fontSize: 'clamp(13px, 2.5vw, 14px)',
    color: '#4b5563',
    lineHeight: '1.6',
    margin: 0,
    wordWrap: 'break-word',
  },
  approversSection: {
    padding: 'clamp(16px, 3vw, 20px)',
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    marginBottom: 'clamp(16px, 3vw, 24px)',
    overflowX: 'hidden',
  },
  approversList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  approverItem: {
    display: 'flex',
    flexDirection: window.innerWidth < 480 ? 'column' : 'row',
    justifyContent: 'space-between',
    alignItems: window.innerWidth < 480 ? 'flex-start' : 'flex-start',
    padding: '12px',
    backgroundColor: '#f9fafb',
    borderRadius: '6px',
    gap: '8px',
  },
  approverInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    flex: 1,
    minWidth: 0,
  },
  approverName: {
    fontSize: 'clamp(13px, 2.5vw, 14px)',
    fontWeight: '600',
    color: '#1f2937',
  },
  approverComment: {
    fontSize: 'clamp(12px, 2.5vw, 13px)',
    color: '#4b5563',
    fontStyle: 'italic',
    marginTop: '4px',
    wordWrap: 'break-word',
  },
  approverTimestamp: {
    fontSize: 'clamp(11px, 2vw, 12px)',
    color: '#9ca3af',
  },
  approverStatus: {
    fontSize: 'clamp(13px, 2.5vw, 14px)',
    fontWeight: '600',
    whiteSpace: 'nowrap',
    flexShrink: 0,
  },
  diffSection: {
    marginBottom: 'clamp(16px, 3vw, 24px)',
    overflowX: 'hidden',
  },
};

// Approval Actions Styles
const approvalStyles: Record<string, React.CSSProperties> = {
  container: {
    padding: '20px',
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    marginBottom: '24px',
  },
  title: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1f2937',
    marginTop: 0,
    marginBottom: '16px',
  },
  buttonGroup: {
    display: 'flex',
    gap: '12px',
  },
  button: {
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: '600',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  approveButton: {
    color: '#fff',
    backgroundColor: '#16a34a',
  },
  rejectButton: {
    color: '#fff',
    backgroundColor: '#dc2626',
  },
  cancelButton: {
    color: '#374151',
    backgroundColor: '#f3f4f6',
  },
  commentSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  decisionLabel: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#1f2937',
  },
  textarea: {
    width: '100%',
    padding: '12px',
    fontSize: '14px',
    color: '#1f2937',
    backgroundColor: '#fff',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    resize: 'vertical',
    fontFamily: 'inherit',
  },
  actionButtons: {
    display: 'flex',
    gap: '12px',
  },
};

export default PullRequests;

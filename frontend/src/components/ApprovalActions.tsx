/**
 * ApprovalActions Component
 * 
 * Handles approval/rejection actions for pull requests
 */

import React, { useState } from 'react';

interface ApprovalActionsProps {
  onSubmit: (decision: 'approved' | 'rejected', comment?: string) => void;
}

export const ApprovalActions: React.FC<ApprovalActionsProps> = ({ onSubmit }) => {
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
    <div style={styles.container}>
      <h3 style={styles.title}>Submit Your Review</h3>
      
      {!showCommentBox ? (
        <div style={styles.buttonGroup}>
          <button
            onClick={handleApprove}
            style={{
              ...styles.button,
              ...styles.approveButton,
            }}
          >
            ✓ Approve
          </button>
          <button
            onClick={handleReject}
            style={{
              ...styles.button,
              ...styles.rejectButton,
            }}
          >
            ✗ Reject
          </button>
        </div>
      ) : (
        <div style={styles.commentSection}>
          <div style={styles.decisionLabel}>
            Decision: {pendingDecision === 'approved' ? '✓ Approve' : '✗ Reject'}
          </div>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add a comment (optional)..."
            style={styles.textarea}
            rows={4}
          />
          <div style={styles.actionButtons}>
            <button
              onClick={handleSubmit}
              style={{
                ...styles.button,
                ...(pendingDecision === 'approved'
                  ? styles.approveButton
                  : styles.rejectButton),
              }}
            >
              Submit {pendingDecision === 'approved' ? 'Approval' : 'Rejection'}
            </button>
            <button
              onClick={handleCancel}
              style={{
                ...styles.button,
                ...styles.cancelButton,
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

const styles = {
  container: {
    backgroundColor: '#f8f9fa',
    border: '1px solid #e9ecef',
    borderRadius: '8px',
    padding: '20px',
    margin: '20px 0',
  },
  title: {
    margin: '0 0 16px 0',
    fontSize: '18px',
    fontWeight: '600',
    color: '#333',
  },
  buttonGroup: {
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap' as const,
  },
  button: {
    padding: '10px 20px',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    minWidth: '100px',
  },
  approveButton: {
    backgroundColor: '#28a745',
    color: '#fff',
    ':hover': {
      backgroundColor: '#218838',
    },
  },
  rejectButton: {
    backgroundColor: '#dc3545',
    color: '#fff',
    ':hover': {
      backgroundColor: '#c82333',
    },
  },
  cancelButton: {
    backgroundColor: '#6c757d',
    color: '#fff',
    ':hover': {
      backgroundColor: '#5a6268',
    },
  },
  commentSection: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
  },
  decisionLabel: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#333',
  },
  textarea: {
    width: '100%',
    padding: '12px',
    border: '1px solid #ced4da',
    borderRadius: '4px',
    fontSize: '14px',
    fontFamily: 'inherit',
    resize: 'vertical' as const,
    minHeight: '80px',
  },
  actionButtons: {
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap' as const,
  },
};
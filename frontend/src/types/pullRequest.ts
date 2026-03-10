/**
 * Pull Request Types
 * 
 * Shared type definitions for pull request related components
 */

import type { FileDiff, Comment } from '../components/CodeDiff';

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
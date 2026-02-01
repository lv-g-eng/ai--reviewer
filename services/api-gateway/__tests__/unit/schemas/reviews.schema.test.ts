/**
 * Unit tests for reviews validation schemas
 */

import {
  createReviewBodySchema,
  updateReviewBodySchema,
  listReviewsQuerySchema,
  addCommentBodySchema,
  reviewStatusSchema,
  reviewTypeSchema,
  reviewPrioritySchema,
  severitySchema,
  issueCategorySchema,
} from '../../../src/schemas/reviews.schema';

describe('Reviews Schemas', () => {
  describe('reviewStatusSchema', () => {
    it('should validate all valid statuses', () => {
      const statuses = ['pending', 'in_progress', 'completed', 'failed', 'cancelled'];
      statuses.forEach((status) => {
        const result = reviewStatusSchema.safeParse(status);
        expect(result.success).toBe(true);
      });
    });

    it('should reject invalid status', () => {
      const result = reviewStatusSchema.safeParse('invalid');
      expect(result.success).toBe(false);
    });
  });

  describe('reviewTypeSchema', () => {
    it('should validate all valid types', () => {
      const types = ['manual', 'automatic', 'scheduled', 'webhook'];
      types.forEach((type) => {
        const result = reviewTypeSchema.safeParse(type);
        expect(result.success).toBe(true);
      });
    });

    it('should reject invalid type', () => {
      const result = reviewTypeSchema.safeParse('invalid');
      expect(result.success).toBe(false);
    });
  });

  describe('reviewPrioritySchema', () => {
    it('should validate all valid priorities', () => {
      const priorities = ['low', 'medium', 'high', 'critical'];
      priorities.forEach((priority) => {
        const result = reviewPrioritySchema.safeParse(priority);
        expect(result.success).toBe(true);
      });
    });

    it('should reject invalid priority', () => {
      const result = reviewPrioritySchema.safeParse('invalid');
      expect(result.success).toBe(false);
    });
  });

  describe('severitySchema', () => {
    it('should validate all valid severities', () => {
      const severities = ['info', 'low', 'medium', 'high', 'critical'];
      severities.forEach((severity) => {
        const result = severitySchema.safeParse(severity);
        expect(result.success).toBe(true);
      });
    });

    it('should reject invalid severity', () => {
      const result = severitySchema.safeParse('invalid');
      expect(result.success).toBe(false);
    });
  });

  describe('issueCategorySchema', () => {
    it('should validate all valid categories', () => {
      const categories = [
        'bug',
        'security',
        'performance',
        'maintainability',
        'style',
        'documentation',
        'best-practice',
        'other',
      ];
      categories.forEach((category) => {
        const result = issueCategorySchema.safeParse(category);
        expect(result.success).toBe(true);
      });
    });

    it('should reject invalid category', () => {
      const result = issueCategorySchema.safeParse('invalid');
      expect(result.success).toBe(false);
    });
  });

  describe('createReviewBodySchema', () => {
    const validReview = {
      projectId: '507f1f77bcf86cd799439011',
      commitHash: 'abc123def456',
      branch: 'feature/new-feature',
      pullRequestNumber: 42,
      type: 'manual',
      priority: 'medium',
      description: 'Review for new feature',
      files: ['src/index.ts', 'src/utils.ts'],
      options: {
        includeTests: true,
        includeDocs: true,
        checkSecurity: true,
        checkPerformance: true,
        checkStyle: true,
        checkComplexity: true,
      },
      tags: ['feature', 'backend'],
    };

    it('should validate valid review data', () => {
      const result = createReviewBodySchema.safeParse(validReview);
      expect(result.success).toBe(true);
    });

    it('should validate minimal review data', () => {
      const minimalReview = {
        projectId: '507f1f77bcf86cd799439011',
      };
      const result = createReviewBodySchema.safeParse(minimalReview);
      expect(result.success).toBe(true);
    });

    it('should apply default values', () => {
      const minimalReview = {
        projectId: '507f1f77bcf86cd799439011',
      };
      const result = createReviewBodySchema.safeParse(minimalReview);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.type).toBe('manual');
        expect(result.data.priority).toBe('medium');
      }
    });

    it('should reject invalid projectId', () => {
      const invalidReview = { ...validReview, projectId: 'invalid-id' };
      const result = createReviewBodySchema.safeParse(invalidReview);
      expect(result.success).toBe(false);
    });

    it('should reject commitHash over 40 chars', () => {
      const invalidReview = { ...validReview, commitHash: 'a'.repeat(41) };
      const result = createReviewBodySchema.safeParse(invalidReview);
      expect(result.success).toBe(false);
    });

    it('should reject branch over 100 chars', () => {
      const invalidReview = { ...validReview, branch: 'a'.repeat(101) };
      const result = createReviewBodySchema.safeParse(invalidReview);
      expect(result.success).toBe(false);
    });

    it('should reject negative pullRequestNumber', () => {
      const invalidReview = { ...validReview, pullRequestNumber: -1 };
      const result = createReviewBodySchema.safeParse(invalidReview);
      expect(result.success).toBe(false);
    });

    it('should reject description over 1000 chars', () => {
      const invalidReview = { ...validReview, description: 'a'.repeat(1001) };
      const result = createReviewBodySchema.safeParse(invalidReview);
      expect(result.success).toBe(false);
    });

    it('should reject over 1000 files', () => {
      const invalidReview = {
        ...validReview,
        files: Array(1001).fill('file.ts'),
      };
      const result = createReviewBodySchema.safeParse(invalidReview);
      expect(result.success).toBe(false);
    });

    it('should reject invalid type', () => {
      const invalidReview = { ...validReview, type: 'invalid' };
      const result = createReviewBodySchema.safeParse(invalidReview);
      expect(result.success).toBe(false);
    });

    it('should reject invalid priority', () => {
      const invalidReview = { ...validReview, priority: 'invalid' };
      const result = createReviewBodySchema.safeParse(invalidReview);
      expect(result.success).toBe(false);
    });
  });

  describe('updateReviewBodySchema', () => {
    it('should validate partial update', () => {
      const update = {
        status: 'completed',
        priority: 'high',
        description: 'Updated description',
      };
      const result = updateReviewBodySchema.safeParse(update);
      expect(result.success).toBe(true);
    });

    it('should validate empty update', () => {
      const result = updateReviewBodySchema.safeParse({});
      expect(result.success).toBe(true);
    });

    it('should reject invalid status', () => {
      const update = { status: 'invalid' };
      const result = updateReviewBodySchema.safeParse(update);
      expect(result.success).toBe(false);
    });

    it('should reject description over 1000 chars', () => {
      const update = { description: 'a'.repeat(1001) };
      const result = updateReviewBodySchema.safeParse(update);
      expect(result.success).toBe(false);
    });
  });

  describe('listReviewsQuerySchema', () => {
    it('should validate empty query', () => {
      const result = listReviewsQuerySchema.safeParse({});
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.page).toBe(1);
        expect(result.data.limit).toBe(10);
        expect(result.data.sortBy).toBe('createdAt');
        expect(result.data.sortOrder).toBe('desc');
      }
    });

    it('should validate with filters', () => {
      const query = {
        projectId: '507f1f77bcf86cd799439011',
        status: 'completed',
        type: 'automatic',
        priority: 'high',
        branch: 'main',
        search: 'test',
        page: '2',
        limit: '20',
        sortBy: 'priority',
        sortOrder: 'asc',
        startDate: '2024-01-01T00:00:00Z',
        endDate: '2024-12-31T23:59:59Z',
        tags: 'feature,backend',
      };
      const result = listReviewsQuerySchema.safeParse(query);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.page).toBe(2);
        expect(result.data.limit).toBe(20);
        expect(result.data.sortBy).toBe('priority');
        expect(result.data.sortOrder).toBe('asc');
      }
    });

    it('should reject invalid projectId', () => {
      const query = { projectId: 'invalid-id' };
      const result = listReviewsQuerySchema.safeParse(query);
      expect(result.success).toBe(false);
    });

    it('should reject invalid status', () => {
      const query = { status: 'invalid' };
      const result = listReviewsQuerySchema.safeParse(query);
      expect(result.success).toBe(false);
    });

    it('should reject invalid sortBy', () => {
      const query = { sortBy: 'invalid' };
      const result = listReviewsQuerySchema.safeParse(query);
      expect(result.success).toBe(false);
    });
  });

  describe('addCommentBodySchema', () => {
    const validComment = {
      content: 'This is a code review comment',
      fileId: '507f1f77bcf86cd799439011',
      lineNumber: 42,
      severity: 'medium',
      category: 'bug',
      suggestion: 'Consider using a more efficient algorithm',
      codeSnippet: 'const result = array.map(x => x * 2);',
    };

    it('should validate valid comment', () => {
      const result = addCommentBodySchema.safeParse(validComment);
      expect(result.success).toBe(true);
    });

    it('should validate minimal comment', () => {
      const minimalComment = {
        content: 'This is a comment',
      };
      const result = addCommentBodySchema.safeParse(minimalComment);
      expect(result.success).toBe(true);
    });

    it('should reject empty content', () => {
      const invalidComment = { ...validComment, content: '' };
      const result = addCommentBodySchema.safeParse(invalidComment);
      expect(result.success).toBe(false);
    });

    it('should reject content over 5000 chars', () => {
      const invalidComment = { ...validComment, content: 'a'.repeat(5001) };
      const result = addCommentBodySchema.safeParse(invalidComment);
      expect(result.success).toBe(false);
    });

    it('should reject invalid fileId', () => {
      const invalidComment = { ...validComment, fileId: 'invalid-id' };
      const result = addCommentBodySchema.safeParse(invalidComment);
      expect(result.success).toBe(false);
    });

    it('should reject negative lineNumber', () => {
      const invalidComment = { ...validComment, lineNumber: -1 };
      const result = addCommentBodySchema.safeParse(invalidComment);
      expect(result.success).toBe(false);
    });

    it('should reject invalid severity', () => {
      const invalidComment = { ...validComment, severity: 'invalid' };
      const result = addCommentBodySchema.safeParse(invalidComment);
      expect(result.success).toBe(false);
    });

    it('should reject invalid category', () => {
      const invalidComment = { ...validComment, category: 'invalid' };
      const result = addCommentBodySchema.safeParse(invalidComment);
      expect(result.success).toBe(false);
    });

    it('should reject suggestion over 2000 chars', () => {
      const invalidComment = { ...validComment, suggestion: 'a'.repeat(2001) };
      const result = addCommentBodySchema.safeParse(invalidComment);
      expect(result.success).toBe(false);
    });

    it('should reject codeSnippet over 1000 chars', () => {
      const invalidComment = { ...validComment, codeSnippet: 'a'.repeat(1001) };
      const result = addCommentBodySchema.safeParse(invalidComment);
      expect(result.success).toBe(false);
    });
  });
});

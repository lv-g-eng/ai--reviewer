/**
 * Unit tests for common validation schemas
 */

import {
  objectIdSchema,
  uuidSchema,
  isoDateSchema,
  paginationSchema,
  cursorPaginationSchema,
  sortOrderSchema,
  emailSchema,
  urlSchema,
  nonEmptyStringSchema,
  positiveIntSchema,
  percentageSchema,
  tagsSchema,
} from '../../../src/schemas/common.schema';

describe('Common Schemas', () => {
  describe('objectIdSchema', () => {
    it('should validate valid ObjectId', () => {
      const result = objectIdSchema.safeParse('507f1f77bcf86cd799439011');
      expect(result.success).toBe(true);
    });

    it('should reject invalid ObjectId', () => {
      const result = objectIdSchema.safeParse('invalid-id');
      expect(result.success).toBe(false);
    });

    it('should reject ObjectId with wrong length', () => {
      const result = objectIdSchema.safeParse('507f1f77bcf86cd7994390');
      expect(result.success).toBe(false);
    });
  });

  describe('uuidSchema', () => {
    it('should validate valid UUID', () => {
      const result = uuidSchema.safeParse('550e8400-e29b-41d4-a716-446655440000');
      expect(result.success).toBe(true);
    });

    it('should reject invalid UUID', () => {
      const result = uuidSchema.safeParse('not-a-uuid');
      expect(result.success).toBe(false);
    });
  });

  describe('isoDateSchema', () => {
    it('should validate valid ISO date', () => {
      const result = isoDateSchema.safeParse('2024-01-20T10:00:00Z');
      expect(result.success).toBe(true);
    });

    it('should validate ISO date with milliseconds', () => {
      const result = isoDateSchema.safeParse('2024-01-20T10:00:00.000Z');
      expect(result.success).toBe(true);
    });

    it('should reject invalid date format', () => {
      const result = isoDateSchema.safeParse('2024-01-20');
      expect(result.success).toBe(false);
    });
  });

  describe('paginationSchema', () => {
    it('should validate and transform valid pagination', () => {
      const result = paginationSchema.safeParse({ page: '2', limit: '20' });
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.page).toBe(2);
        expect(result.data.limit).toBe(20);
      }
    });

    it('should use default values', () => {
      const result = paginationSchema.safeParse({});
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.page).toBe(1);
        expect(result.data.limit).toBe(10);
      }
    });

    it('should reject negative page', () => {
      const result = paginationSchema.safeParse({ page: '-1', limit: '10' });
      expect(result.success).toBe(false);
    });

    it('should reject limit over 100', () => {
      const result = paginationSchema.safeParse({ page: '1', limit: '101' });
      expect(result.success).toBe(false);
    });

    it('should reject page over 1000', () => {
      const result = paginationSchema.safeParse({ page: '1001', limit: '10' });
      expect(result.success).toBe(false);
    });
  });

  describe('cursorPaginationSchema', () => {
    it('should validate cursor pagination', () => {
      const result = cursorPaginationSchema.safeParse({
        cursor: 'abc123',
        limit: '20',
      });
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.cursor).toBe('abc123');
        expect(result.data.limit).toBe(20);
      }
    });

    it('should work without cursor', () => {
      const result = cursorPaginationSchema.safeParse({ limit: '10' });
      expect(result.success).toBe(true);
    });
  });

  describe('sortOrderSchema', () => {
    it('should validate asc', () => {
      const result = sortOrderSchema.safeParse('asc');
      expect(result.success).toBe(true);
    });

    it('should validate desc', () => {
      const result = sortOrderSchema.safeParse('desc');
      expect(result.success).toBe(true);
    });

    it('should use default value', () => {
      const result = sortOrderSchema.safeParse(undefined);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('desc');
      }
    });

    it('should reject invalid sort order', () => {
      const result = sortOrderSchema.safeParse('invalid');
      expect(result.success).toBe(false);
    });
  });

  describe('emailSchema', () => {
    it('should validate valid email', () => {
      const result = emailSchema.safeParse('user@example.com');
      expect(result.success).toBe(true);
    });

    it('should reject invalid email', () => {
      const result = emailSchema.safeParse('not-an-email');
      expect(result.success).toBe(false);
    });

    it('should reject email over 255 chars', () => {
      const longEmail = 'a'.repeat(250) + '@example.com';
      const result = emailSchema.safeParse(longEmail);
      expect(result.success).toBe(false);
    });
  });

  describe('urlSchema', () => {
    it('should validate valid URL', () => {
      const result = urlSchema.safeParse('https://example.com');
      expect(result.success).toBe(true);
    });

    it('should validate URL with path', () => {
      const result = urlSchema.safeParse('https://example.com/path/to/resource');
      expect(result.success).toBe(true);
    });

    it('should reject invalid URL', () => {
      const result = urlSchema.safeParse('not-a-url');
      expect(result.success).toBe(false);
    });
  });

  describe('nonEmptyStringSchema', () => {
    it('should validate non-empty string', () => {
      const result = nonEmptyStringSchema.safeParse('hello');
      expect(result.success).toBe(true);
    });

    it('should trim whitespace', () => {
      const result = nonEmptyStringSchema.safeParse('  hello  ');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('hello');
      }
    });

    it('should reject empty string', () => {
      const result = nonEmptyStringSchema.safeParse('');
      expect(result.success).toBe(false);
    });

    it('should reject whitespace-only string', () => {
      const result = nonEmptyStringSchema.safeParse('   ');
      expect(result.success).toBe(false);
    });
  });

  describe('positiveIntSchema', () => {
    it('should validate positive integer', () => {
      const result = positiveIntSchema.safeParse(42);
      expect(result.success).toBe(true);
    });

    it('should reject zero', () => {
      const result = positiveIntSchema.safeParse(0);
      expect(result.success).toBe(false);
    });

    it('should reject negative number', () => {
      const result = positiveIntSchema.safeParse(-5);
      expect(result.success).toBe(false);
    });

    it('should reject decimal', () => {
      const result = positiveIntSchema.safeParse(3.14);
      expect(result.success).toBe(false);
    });
  });

  describe('percentageSchema', () => {
    it('should validate 0', () => {
      const result = percentageSchema.safeParse(0);
      expect(result.success).toBe(true);
    });

    it('should validate 100', () => {
      const result = percentageSchema.safeParse(100);
      expect(result.success).toBe(true);
    });

    it('should validate 50.5', () => {
      const result = percentageSchema.safeParse(50.5);
      expect(result.success).toBe(true);
    });

    it('should reject negative percentage', () => {
      const result = percentageSchema.safeParse(-1);
      expect(result.success).toBe(false);
    });

    it('should reject percentage over 100', () => {
      const result = percentageSchema.safeParse(101);
      expect(result.success).toBe(false);
    });
  });

  describe('tagsSchema', () => {
    it('should validate valid tags array', () => {
      const result = tagsSchema.safeParse(['tag1', 'tag2', 'tag3']);
      expect(result.success).toBe(true);
    });

    it('should accept empty array', () => {
      const result = tagsSchema.safeParse([]);
      expect(result.success).toBe(true);
    });

    it('should accept undefined', () => {
      const result = tagsSchema.safeParse(undefined);
      expect(result.success).toBe(true);
    });

    it('should reject array with over 20 tags', () => {
      const tags = Array(21).fill('tag');
      const result = tagsSchema.safeParse(tags);
      expect(result.success).toBe(false);
    });

    it('should reject tag over 50 chars', () => {
      const result = tagsSchema.safeParse(['a'.repeat(51)]);
      expect(result.success).toBe(false);
    });

    it('should reject empty tag', () => {
      const result = tagsSchema.safeParse(['tag1', '', 'tag3']);
      expect(result.success).toBe(false);
    });
  });
});

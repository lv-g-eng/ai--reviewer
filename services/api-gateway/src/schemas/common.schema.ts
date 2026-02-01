/**
 * Common validation schemas used across multiple endpoints
 * These schemas provide reusable validation patterns for common data types
 */

import { z } from 'zod';

/**
 * MongoDB ObjectId validation
 * Validates 24-character hexadecimal strings
 */
export const objectIdSchema = z
  .string()
  .regex(/^[0-9a-fA-F]{24}$/, 'Invalid ObjectId format')
  .describe('MongoDB ObjectId (24-character hex string)');

/**
 * UUID validation
 * Validates standard UUID format
 */
export const uuidSchema = z
  .string()
  .uuid('Invalid UUID format')
  .describe('UUID v4 format');

/**
 * ISO 8601 date validation
 * Validates date strings in ISO format
 */
export const isoDateSchema = z
  .string()
  .datetime({ message: 'Invalid ISO 8601 date format' })
  .describe('ISO 8601 date string');

/**
 * Pagination query parameters
 * Standard pagination with page and limit
 */
export const paginationSchema = z.object({
  page: z
    .string()
    .optional()
    .default('1')
    .transform((val) => parseInt(val, 10))
    .pipe(z.number().int().positive().max(1000))
    .describe('Page number (1-indexed)'),
  limit: z
    .string()
    .optional()
    .default('10')
    .transform((val) => parseInt(val, 10))
    .pipe(z.number().int().positive().max(100))
    .describe('Items per page (max 100)'),
});

/**
 * Cursor-based pagination query parameters
 * For efficient pagination of large datasets
 */
export const cursorPaginationSchema = z.object({
  cursor: z.string().optional().describe('Cursor for next page'),
  limit: z
    .string()
    .optional()
    .default('10')
    .transform((val) => parseInt(val, 10))
    .pipe(z.number().int().positive().max(100))
    .describe('Items per page (max 100)'),
});

/**
 * Sort order validation
 */
export const sortOrderSchema = z
  .enum(['asc', 'desc'])
  .default('desc')
  .describe('Sort order (ascending or descending)');

/**
 * Date range filter
 * For filtering by date ranges
 */
export const dateRangeSchema = z.object({
  startDate: isoDateSchema.optional().describe('Start date (inclusive)'),
  endDate: isoDateSchema.optional().describe('End date (inclusive)'),
});

/**
 * Search query parameter
 * For text search functionality
 */
export const searchSchema = z.object({
  q: z.string().min(1).max(200).optional().describe('Search query string'),
});

/**
 * Status filter
 * Common status values across entities
 */
export const statusSchema = z
  .enum(['active', 'inactive', 'pending', 'completed', 'failed', 'cancelled'])
  .optional()
  .describe('Status filter');

/**
 * ID parameter validation
 * For route parameters that expect an ID
 */
export const idParamSchema = z.object({
  id: objectIdSchema.describe('Resource ID'),
});

/**
 * Email validation
 */
export const emailSchema = z
  .string()
  .email('Invalid email format')
  .max(255)
  .describe('Email address');

/**
 * URL validation
 */
export const urlSchema = z
  .string()
  .url('Invalid URL format')
  .max(2048)
  .describe('URL');

/**
 * Non-empty string validation
 * For required text fields
 */
export const nonEmptyStringSchema = z
  .string()
  .trim()
  .min(1, 'Field cannot be empty');

/**
 * Optional non-empty string
 * For optional text fields that shouldn't be empty if provided
 */
export const optionalNonEmptyStringSchema = z
  .string()
  .min(1, 'Field cannot be empty if provided')
  .trim()
  .optional();

/**
 * Positive integer validation
 */
export const positiveIntSchema = z
  .number()
  .int('Must be an integer')
  .positive('Must be positive');

/**
 * Non-negative integer validation
 */
export const nonNegativeIntSchema = z
  .number()
  .int('Must be an integer')
  .nonnegative('Must be non-negative');

/**
 * Percentage validation (0-100)
 */
export const percentageSchema = z
  .number()
  .min(0, 'Percentage must be at least 0')
  .max(100, 'Percentage must be at most 100');

/**
 * Tags array validation
 * For tag/label arrays
 */
export const tagsSchema = z
  .array(z.string().min(1).max(50))
  .max(20)
  .optional()
  .describe('Array of tags (max 20 tags, each max 50 chars)');

/**
 * Metadata object validation
 * For flexible key-value metadata
 */
export const metadataSchema = z
  .record(z.string(), z.any())
  .optional()
  .describe('Flexible metadata object');

// Type exports for TypeScript
export type Pagination = z.infer<typeof paginationSchema>;
export type CursorPagination = z.infer<typeof cursorPaginationSchema>;
export type DateRange = z.infer<typeof dateRangeSchema>;
export type IdParam = z.infer<typeof idParamSchema>;

import {
  generateCorrelationId,
  getOrCreateCorrelationId,
  correlationIdMiddleware,
  extractCorrelationId,
  CORRELATION_ID_HEADER,
} from '../../../src/utils/correlationId';
import { Request, Response, NextFunction } from 'express';

describe('Correlation ID Utilities', () => {
  describe('generateCorrelationId', () => {
    it('should generate a valid UUID v4', () => {
      const id = generateCorrelationId();

      expect(id).toBeDefined();
      expect(typeof id).toBe('string');
      expect(id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });

    it('should generate unique IDs', () => {
      const id1 = generateCorrelationId();
      const id2 = generateCorrelationId();

      expect(id1).not.toBe(id2);
    });

    it('should generate multiple unique IDs', () => {
      const ids = new Set<string>();
      for (let i = 0; i < 100; i++) {
        ids.add(generateCorrelationId());
      }

      expect(ids.size).toBe(100);
    });
  });

  describe('getOrCreateCorrelationId', () => {
    it('should return existing correlation ID from request', () => {
      const existingId = 'existing-correlation-id';
      const mockReq = {
        headers: {
          [CORRELATION_ID_HEADER]: existingId,
        },
      } as Partial<Request> as Request;

      const id = getOrCreateCorrelationId(mockReq);

      expect(id).toBe(existingId);
    });

    it('should generate new correlation ID if not present', () => {
      const mockReq = {
        headers: {},
      } as Request;

      const id = getOrCreateCorrelationId(mockReq);

      expect(id).toBeDefined();
      expect(typeof id).toBe('string');
      expect(id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });

    it('should generate new correlation ID if header is not a string', () => {
      const mockReq = {
        headers: {
          [CORRELATION_ID_HEADER]: ['array', 'value'],
        },
      } as any;

      const id = getOrCreateCorrelationId(mockReq);

      expect(id).toBeDefined();
      expect(typeof id).toBe('string');
      expect(id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });
  });

  describe('correlationIdMiddleware', () => {
    let mockReq: Partial<Request>;
    let mockRes: Partial<Response>;
    let mockNext: jest.Mock;

    beforeEach(() => {
      mockReq = {
        headers: {},
      };
      mockRes = {
        setHeader: jest.fn(),
      };
      mockNext = jest.fn();
    });

    it('should add correlation ID to request headers', () => {
      correlationIdMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      expect(mockReq.headers![CORRELATION_ID_HEADER]).toBeDefined();
      expect(typeof mockReq.headers![CORRELATION_ID_HEADER]).toBe('string');
    });

    it('should add correlation ID to response headers', () => {
      correlationIdMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      expect(mockRes.setHeader).toHaveBeenCalledWith(
        CORRELATION_ID_HEADER,
        expect.any(String)
      );
    });

    it('should preserve existing correlation ID', () => {
      const existingId = 'existing-correlation-id';
      mockReq.headers![CORRELATION_ID_HEADER] = existingId;

      correlationIdMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      expect(mockReq.headers![CORRELATION_ID_HEADER]).toBe(existingId);
      expect(mockRes.setHeader).toHaveBeenCalledWith(
        CORRELATION_ID_HEADER,
        existingId
      );
    });

    it('should call next middleware', () => {
      correlationIdMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      expect(mockNext).toHaveBeenCalledTimes(1);
      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should use same ID for request and response headers', () => {
      correlationIdMiddleware(
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      const requestId = mockReq.headers![CORRELATION_ID_HEADER];
      const responseId = (mockRes.setHeader as jest.Mock).mock.calls[0][1];

      expect(requestId).toBe(responseId);
    });
  });

  describe('extractCorrelationId', () => {
    it('should extract correlation ID from request', () => {
      const correlationId = 'test-correlation-id';
      const mockReq = {
        headers: {
          [CORRELATION_ID_HEADER]: correlationId,
        },
      } as Partial<Request> as Request;

      const extracted = extractCorrelationId(mockReq);

      expect(extracted).toBe(correlationId);
    });

    it('should return undefined if correlation ID is not present', () => {
      const mockReq = {
        headers: {},
      } as Request;

      const extracted = extractCorrelationId(mockReq);

      expect(extracted).toBeUndefined();
    });

    it('should return undefined if correlation ID is not a string', () => {
      const mockReq = {
        headers: {
          [CORRELATION_ID_HEADER]: ['array', 'value'],
        },
      } as any;

      const extracted = extractCorrelationId(mockReq);

      expect(extracted).toBeUndefined();
    });
  });

  describe('CORRELATION_ID_HEADER constant', () => {
    it('should be defined', () => {
      expect(CORRELATION_ID_HEADER).toBeDefined();
      expect(typeof CORRELATION_ID_HEADER).toBe('string');
    });

    it('should be lowercase', () => {
      expect(CORRELATION_ID_HEADER).toBe(CORRELATION_ID_HEADER.toLowerCase());
    });

    it('should be x-correlation-id', () => {
      expect(CORRELATION_ID_HEADER).toBe('x-correlation-id');
    });
  });
});

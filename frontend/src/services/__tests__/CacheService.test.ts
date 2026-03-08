/**
 * CacheService 单元测试
 * 
 * 测试场景:
 * - 基本的设置和获取功能
 * - TTL过期检查
 * - 缓存清理功能
 * - 统计功能
 * - 边缘情况
 */

import { CacheService } from '../CacheService';

describe('CacheService', () => {
  let cacheService: CacheService;

  beforeEach(() => {
    // 每个测试使用新的CacheService实例
    cacheService = new CacheService(5 * 60 * 1000); // 5分钟TTL
  });

  describe('set and get', () => {
    it('should store and retrieve data', () => {
      const key = 'test-key';
      const data = { value: 'test-data' };

      cacheService.set(key, data);
      const result = cacheService.get(key);

      expect(result).toEqual(data);
    });

    it('should return null for non-existent key', () => {
      const result = cacheService.get('non-existent');
      expect(result).toBeNull();
    });

    it('should support different data types', () => {
      cacheService.set('string', 'hello');
      cacheService.set('number', 42);
      cacheService.set('boolean', true);
      cacheService.set('array', [1, 2, 3]);
      cacheService.set('object', { a: 1, b: 2 });

      expect(cacheService.get('string')).toBe('hello');
      expect(cacheService.get('number')).toBe(42);
      expect(cacheService.get('boolean')).toBe(true);
      expect(cacheService.get('array')).toEqual([1, 2, 3]);
      expect(cacheService.get('object')).toEqual({ a: 1, b: 2 });
    });

    it('should overwrite existing key', () => {
      const key = 'test-key';

      cacheService.set(key, 'first');
      expect(cacheService.get(key)).toBe('first');

      cacheService.set(key, 'second');
      expect(cacheService.get(key)).toBe('second');
    });
  });

  describe('TTL and expiration', () => {
    it('should use default TTL when not specified', () => {
      const key = 'test-key';
      cacheService.set(key, 'data');

      const ttl = cacheService.getTTL(key);
      expect(ttl).toBeGreaterThan(0);
      expect(ttl).toBeLessThanOrEqual(5 * 60 * 1000);
    });

    it('should use custom TTL when specified', () => {
      const key = 'test-key';
      const customTTL = 1000; // 1秒

      cacheService.set(key, 'data', customTTL);

      const ttl = cacheService.getTTL(key);
      expect(ttl).toBeGreaterThan(0);
      expect(ttl).toBeLessThanOrEqual(customTTL);
    });

    it('should return null for expired data', async () => {
      const key = 'test-key';
      const shortTTL = 100; // 100ms

      cacheService.set(key, 'data', shortTTL);

      // 等待过期
      await new Promise((resolve) => setTimeout(resolve, 150));

      const result = cacheService.get(key);
      expect(result).toBeNull();
    });

    it('should detect expired entries', async () => {
      const key = 'test-key';
      const shortTTL = 100; // 100ms

      cacheService.set(key, 'data', shortTTL);

      expect(cacheService.isExpired(key)).toBe(false);

      // 等待过期
      await new Promise((resolve) => setTimeout(resolve, 150));

      expect(cacheService.isExpired(key)).toBe(true);
    });

    it('should return 0 TTL for expired entries', async () => {
      const key = 'test-key';
      const shortTTL = 100; // 100ms

      cacheService.set(key, 'data', shortTTL);

      // 等待过期
      await new Promise((resolve) => setTimeout(resolve, 150));

      expect(cacheService.getTTL(key)).toBe(0);
    });

    it('should update TTL for existing entry', () => {
      const key = 'test-key';
      cacheService.set(key, 'data', 1000);

      const updated = cacheService.updateTTL(key, 5000);
      expect(updated).toBe(true);

      const newTTL = cacheService.getTTL(key);
      expect(newTTL).toBeGreaterThan(1000);
      expect(newTTL).toBeLessThanOrEqual(5000);
    });

    it('should not update TTL for non-existent entry', () => {
      const updated = cacheService.updateTTL('non-existent', 5000);
      expect(updated).toBe(false);
    });
  });

  describe('clear', () => {
    it('should clear all cache when no pattern provided', () => {
      cacheService.set('key1', 'data1');
      cacheService.set('key2', 'data2');
      cacheService.set('key3', 'data3');

      cacheService.clear();

      expect(cacheService.get('key1')).toBeNull();
      expect(cacheService.get('key2')).toBeNull();
      expect(cacheService.get('key3')).toBeNull();
      expect(cacheService.getStats().size).toBe(0);
    });

    it('should clear only matching keys when pattern provided', () => {
      cacheService.set('user:1', 'data1');
      cacheService.set('user:2', 'data2');
      cacheService.set('post:1', 'data3');

      cacheService.clear('user');

      expect(cacheService.get('user:1')).toBeNull();
      expect(cacheService.get('user:2')).toBeNull();
      expect(cacheService.get('post:1')).toBe('data3');
    });

    it('should not affect cache when pattern matches nothing', () => {
      cacheService.set('key1', 'data1');
      cacheService.set('key2', 'data2');

      cacheService.clear('non-matching-pattern');

      expect(cacheService.get('key1')).toBe('data1');
      expect(cacheService.get('key2')).toBe('data2');
    });
  });

  describe('clearExpired', () => {
    it('should remove only expired entries', async () => {
      cacheService.set('key1', 'data1', 100); // 100ms TTL
      cacheService.set('key2', 'data2', 5000); // 5s TTL
      cacheService.set('key3', 'data3', 100); // 100ms TTL

      // 等待部分过期
      await new Promise((resolve) => setTimeout(resolve, 150));

      const clearedCount = cacheService.clearExpired();

      expect(clearedCount).toBe(2);
      expect(cacheService.get('key1')).toBeNull();
      expect(cacheService.get('key2')).toBe('data2');
      expect(cacheService.get('key3')).toBeNull();
    });

    it('should return 0 when no entries are expired', () => {
      cacheService.set('key1', 'data1', 5000);
      cacheService.set('key2', 'data2', 5000);

      const clearedCount = cacheService.clearExpired();

      expect(clearedCount).toBe(0);
      expect(cacheService.getStats().size).toBe(2);
    });
  });

  describe('has', () => {
    it('should return true for existing non-expired entry', () => {
      cacheService.set('key', 'data');
      expect(cacheService.has('key')).toBe(true);
    });

    it('should return false for non-existent entry', () => {
      expect(cacheService.has('non-existent')).toBe(false);
    });

    it('should return false for expired entry', async () => {
      cacheService.set('key', 'data', 100);

      // 等待过期
      await new Promise((resolve) => setTimeout(resolve, 150));

      expect(cacheService.has('key')).toBe(false);
    });
  });

  describe('statistics', () => {
    it('should track cache hits', () => {
      cacheService.set('key', 'data');

      cacheService.get('key'); // hit
      cacheService.get('key'); // hit

      const stats = cacheService.getStats();
      expect(stats.hits).toBe(2);
      expect(stats.misses).toBe(0);
    });

    it('should track cache misses', () => {
      cacheService.get('non-existent'); // miss
      cacheService.get('another-miss'); // miss

      const stats = cacheService.getStats();
      expect(stats.hits).toBe(0);
      expect(stats.misses).toBe(2);
    });

    it('should calculate hit rate correctly', () => {
      cacheService.set('key1', 'data1');
      cacheService.set('key2', 'data2');

      cacheService.get('key1'); // hit
      cacheService.get('key2'); // hit
      cacheService.get('key3'); // miss
      cacheService.get('key4'); // miss

      const stats = cacheService.getStats();
      expect(stats.hits).toBe(2);
      expect(stats.misses).toBe(2);
      expect(stats.hitRate).toBe(50); // 50%
    });

    it('should return 0 hit rate when no requests', () => {
      const stats = cacheService.getStats();
      expect(stats.hitRate).toBe(0);
    });

    it('should include cache size in stats', () => {
      cacheService.set('key1', 'data1');
      cacheService.set('key2', 'data2');
      cacheService.set('key3', 'data3');

      const stats = cacheService.getStats();
      expect(stats.size).toBe(3);
    });

    it('should include all keys in stats', () => {
      cacheService.set('key1', 'data1');
      cacheService.set('key2', 'data2');

      const stats = cacheService.getStats();
      expect(stats.keys).toContain('key1');
      expect(stats.keys).toContain('key2');
      expect(stats.keys.length).toBe(2);
    });

    it('should reset statistics', () => {
      cacheService.set('key', 'data');
      cacheService.get('key'); // hit
      cacheService.get('non-existent'); // miss

      cacheService.resetStats();

      const stats = cacheService.getStats();
      expect(stats.hits).toBe(0);
      expect(stats.misses).toBe(0);
      expect(stats.hitRate).toBe(0);
      // Cache data should still exist
      expect(stats.size).toBe(1);
    });
  });

  describe('edge cases', () => {
    it('should handle empty string as key', () => {
      cacheService.set('', 'data');
      expect(cacheService.get('')).toBe('data');
    });

    it('should handle null as data', () => {
      cacheService.set('key', null);
      expect(cacheService.get('key')).toBeNull();
    });

    it('should handle undefined as data', () => {
      cacheService.set('key', undefined);
      expect(cacheService.get('key')).toBeUndefined();
    });

    it('should handle very large TTL', () => {
      const largeTTL = Number.MAX_SAFE_INTEGER;
      cacheService.set('key', 'data', largeTTL);

      expect(cacheService.has('key')).toBe(true);
      expect(cacheService.isExpired('key')).toBe(false);
    });

    it('should handle zero TTL (immediate expiration)', () => {
      cacheService.set('key', 'data', 0);

      // Should be immediately expired
      expect(cacheService.isExpired('key')).toBe(true);
      expect(cacheService.get('key')).toBeNull();
    });

    it('should handle negative TTL (immediate expiration)', () => {
      cacheService.set('key', 'data', -1000);

      // Should be immediately expired
      expect(cacheService.isExpired('key')).toBe(true);
      expect(cacheService.get('key')).toBeNull();
    });
  });

  describe('concurrent operations', () => {
    it('should handle multiple rapid sets and gets', () => {
      const operations = 100;

      for (let i = 0; i < operations; i++) {
        cacheService.set(`key${i}`, `data${i}`);
      }

      for (let i = 0; i < operations; i++) {
        expect(cacheService.get(`key${i}`)).toBe(`data${i}`);
      }

      expect(cacheService.getStats().size).toBe(operations);
    });

    it('should maintain consistency during mixed operations', () => {
      cacheService.set('key1', 'data1');
      cacheService.set('key2', 'data2');

      expect(cacheService.get('key1')).toBe('data1');

      cacheService.clear('key1');

      expect(cacheService.get('key1')).toBeNull();
      expect(cacheService.get('key2')).toBe('data2');

      cacheService.set('key1', 'new-data1');

      expect(cacheService.get('key1')).toBe('new-data1');
    });
  });
});

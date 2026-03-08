/**
 * CacheService - 请求缓存管理服务
 * 
 * 功能:
 * - 设置和获取缓存数据
 * - 支持自定义TTL (Time To Live)
 * - 自动过期检查和清理
 * - 缓存统计功能 (命中率、大小等)
 * - 支持模式匹配的缓存清除
 * 
 * 默认TTL: 5分钟 (300000ms)
 */

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

export interface CacheStats {
  size: number;
  hits: number;
  misses: number;
  hitRate: number;
  keys: string[];
}

export class CacheService {
  private cache: Map<string, CacheEntry<any>>;
  private hits: number;
  private misses: number;
  private defaultTTL: number;

  constructor(defaultTTL: number = 5 * 60 * 1000) {
    this.cache = new Map();
    this.hits = 0;
    this.misses = 0;
    this.defaultTTL = defaultTTL;
  }

  /**
   * 设置缓存
   * @param key 缓存键
   * @param data 缓存数据
   * @param ttl 过期时间（毫秒），默认使用构造函数中的defaultTTL
   */
  set<T>(key: string, data: T, ttl?: number): void {
    const now = Date.now();
    const expirationTime = ttl !== undefined ? ttl : this.defaultTTL;

    const entry: CacheEntry<T> = {
      data,
      timestamp: now,
      expiresAt: now + expirationTime,
    };

    this.cache.set(key, entry);
  }

  /**
   * 获取缓存
   * @param key 缓存键
   * @returns 缓存数据，如果不存在或已过期则返回null
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) {
      this.misses++;
      return null;
    }

    // 检查是否过期
    if (this.isExpired(key)) {
      this.cache.delete(key);
      this.misses++;
      return null;
    }

    this.hits++;
    return entry.data;
  }

  /**
   * 检查缓存是否过期
   * @param key 缓存键
   * @returns 如果过期或不存在返回true，否则返回false
   */
  isExpired(key: string): boolean {
    const entry = this.cache.get(key);

    if (!entry) {
      return true;
    }

    const now = Date.now();
    return now >= entry.expiresAt;
  }

  /**
   * 清除缓存
   * @param pattern 可选的模式字符串，如果提供则只清除匹配的键
   */
  clear(pattern?: string): void {
    if (!pattern) {
      this.cache.clear();
      return;
    }

    // 清除匹配模式的缓存
    const keys = Array.from(this.cache.keys());
    keys.forEach((key) => {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    });
  }

  /**
   * 清理所有过期的缓存条目
   * @returns 清理的条目数量
   */
  clearExpired(): number {
    const keys = Array.from(this.cache.keys());
    let clearedCount = 0;

    keys.forEach((key) => {
      if (this.isExpired(key)) {
        this.cache.delete(key);
        clearedCount++;
      }
    });

    return clearedCount;
  }

  /**
   * 获取缓存统计信息
   * @returns 缓存统计对象
   */
  getStats(): CacheStats {
    const totalRequests = this.hits + this.misses;
    const hitRate = totalRequests > 0 ? this.hits / totalRequests : 0;

    return {
      size: this.cache.size,
      hits: this.hits,
      misses: this.misses,
      hitRate: Math.round(hitRate * 10000) / 100, // 保留两位小数的百分比
      keys: Array.from(this.cache.keys()),
    };
  }

  /**
   * 检查缓存中是否存在指定的键
   * @param key 缓存键
   * @returns 如果存在且未过期返回true，否则返回false
   */
  has(key: string): boolean {
    if (!this.cache.has(key)) {
      return false;
    }

    if (this.isExpired(key)) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  /**
   * 重置统计信息
   */
  resetStats(): void {
    this.hits = 0;
    this.misses = 0;
  }

  /**
   * 获取缓存条目的剩余生存时间
   * @param key 缓存键
   * @returns 剩余时间（毫秒），如果不存在或已过期返回0
   */
  getTTL(key: string): number {
    const entry = this.cache.get(key);

    if (!entry) {
      return 0;
    }

    const now = Date.now();
    const remaining = entry.expiresAt - now;

    return remaining > 0 ? remaining : 0;
  }

  /**
   * 更新缓存条目的过期时间
   * @param key 缓存键
   * @param ttl 新的过期时间（毫秒）
   * @returns 如果更新成功返回true，否则返回false
   */
  updateTTL(key: string, ttl: number): boolean {
    const entry = this.cache.get(key);

    if (!entry || this.isExpired(key)) {
      return false;
    }

    const now = Date.now();
    entry.expiresAt = now + ttl;
    this.cache.set(key, entry);

    return true;
  }
}

// 创建默认实例的工厂函数
export function createDefaultCacheService(): CacheService {
  return new CacheService(5 * 60 * 1000); // 5分钟默认TTL
}

// 默认实例 - 延迟初始化
let defaultInstance: CacheService | null = null;

export function getCacheService(): CacheService {
  if (!defaultInstance) {
    defaultInstance = createDefaultCacheService();
  }
  return defaultInstance;
}

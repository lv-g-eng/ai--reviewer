/**
 * A/B Testing Feature Flags Tests
 * 
 * Tests for A/B testing functionality in the feature flags service
 * Requirements: 10.5, 10.7
 */

import { featureFlagsService } from '../feature-flags';

describe('FeatureFlagsService - A/B Testing', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Reset the service to defaults
    featureFlagsService.resetToDefaults();
  });

  describe('User ID-based hash grouping', () => {
    it('should consistently assign the same user to the same group', () => {
      const flagKey = 'test-ab-flag';
      const userId = 'user-123';
      
      // Set up a flag with 50% rollout
      featureFlagsService.setFlag(flagKey, true);
      featureFlagsService.setRolloutPercentage(flagKey, 50);
      
      // Check multiple times - should always return the same result
      const result1 = featureFlagsService.isEnabledForUser(flagKey, userId);
      const result2 = featureFlagsService.isEnabledForUser(flagKey, userId);
      const result3 = featureFlagsService.isEnabledForUser(flagKey, userId);
      
      expect(result1).toBe(result2);
      expect(result2).toBe(result3);
    });

    it('should distribute users across rollout percentage', () => {
      const flagKey = 'test-ab-flag';
      featureFlagsService.setFlag(flagKey, true);
      featureFlagsService.setRolloutPercentage(flagKey, 50);
      
      // Test with 100 different users
      let enabledCount = 0;
      for (let i = 0; i < 100; i++) {
        if (featureFlagsService.isEnabledForUser(flagKey, `user-${i}`)) {
          enabledCount++;
        }
      }
      
      // Should be approximately 50% (allow 20% margin for hash distribution)
      expect(enabledCount).toBeGreaterThan(30);
      expect(enabledCount).toBeLessThan(70);
    });
  });

  describe('A/B test variant assignment', () => {
    it('should assign users to variants consistently', () => {
      const flagKey = 'test-ab-flag';
      const userId = 'user-123';
      
      // Set up A/B test with 2 variants
      featureFlagsService.setFlag(flagKey, true);
      featureFlagsService.setRolloutPercentage(flagKey, 100);
      featureFlagsService.setABTestVariants(flagKey, ['control', 'variant-a']);
      
      // Get variant multiple times - should always be the same
      const variant1 = featureFlagsService.getABTestVariant(flagKey, userId);
      const variant2 = featureFlagsService.getABTestVariant(flagKey, userId);
      const variant3 = featureFlagsService.getABTestVariant(flagKey, userId);
      
      expect(variant1).toBe(variant2);
      expect(variant2).toBe(variant3);
      expect(['control', 'variant-a']).toContain(variant1);
    });

    it('should distribute users across variants', () => {
      const flagKey = 'test-ab-flag';
      
      // Set up A/B test with 2 variants
      featureFlagsService.setFlag(flagKey, true);
      featureFlagsService.setRolloutPercentage(flagKey, 100);
      featureFlagsService.setABTestVariants(flagKey, ['control', 'variant-a']);
      
      // Test with 100 different users
      const variantCounts: Record<string, number> = { control: 0, 'variant-a': 0 };
      for (let i = 0; i < 100; i++) {
        const variant = featureFlagsService.getABTestVariant(flagKey, `user-${i}`);
        if (variant) {
          variantCounts[variant]++;
        }
      }
      
      // Should be approximately 50/50 (allow 20% margin)
      expect(variantCounts.control).toBeGreaterThan(30);
      expect(variantCounts.control).toBeLessThan(70);
      expect(variantCounts['variant-a']).toBeGreaterThan(30);
      expect(variantCounts['variant-a']).toBeLessThan(70);
    });

    it('should return null for users not in rollout', () => {
      const flagKey = 'test-ab-flag';
      
      // Set up A/B test with 0% rollout
      featureFlagsService.setFlag(flagKey, true);
      featureFlagsService.setRolloutPercentage(flagKey, 0);
      featureFlagsService.setABTestVariants(flagKey, ['control', 'variant-a']);
      
      const variant = featureFlagsService.getABTestVariant(flagKey, 'user-123');
      expect(variant).toBeNull();
    });

    it('should return null for disabled flags', () => {
      const flagKey = 'test-ab-flag';
      
      // Set up A/B test but disable the flag
      featureFlagsService.setFlag(flagKey, false);
      featureFlagsService.setRolloutPercentage(flagKey, 100);
      featureFlagsService.setABTestVariants(flagKey, ['control', 'variant-a']);
      
      const variant = featureFlagsService.getABTestVariant(flagKey, 'user-123');
      expect(variant).toBeNull();
    });
  });

  describe('A/B test metrics collection', () => {
    it('should track impression metrics', () => {
      const flagKey = 'test-ab-flag';
      const userId = 'user-123';
      
      // Set up A/B test
      featureFlagsService.setFlag(flagKey, true);
      featureFlagsService.setRolloutPercentage(flagKey, 100);
      featureFlagsService.setABTestVariants(flagKey, ['control', 'variant-a']);
      
      // Get variant (should automatically track impression)
      const variant = featureFlagsService.getABTestVariant(flagKey, userId);
      
      // Get stats
      const stats = featureFlagsService.getABTestStats(flagKey);
      
      expect(stats).not.toBeNull();
      expect(stats!.totalUsers).toBeGreaterThan(0);
      expect(stats!.variantStats[variant!].impressions).toBeGreaterThan(0);
    });

    it('should track interaction metrics', () => {
      const flagKey = 'test-ab-flag';
      const userId = 'user-123';
      
      // Set up A/B test
      featureFlagsService.setFlag(flagKey, true);
      featureFlagsService.setRolloutPercentage(flagKey, 100);
      featureFlagsService.setABTestVariants(flagKey, ['control', 'variant-a']);
      
      // Get variant
      const variant = featureFlagsService.getABTestVariant(flagKey, userId);
      
      // Track interaction
      featureFlagsService.trackABTestMetric(flagKey, userId, variant!, 'interaction');
      
      // Get stats
      const stats = featureFlagsService.getABTestStats(flagKey);
      
      expect(stats!.variantStats[variant!].interactions).toBeGreaterThan(0);
    });

    it('should track conversion metrics', () => {
      const flagKey = 'test-ab-flag';
      const userId = 'user-123';
      
      // Set up A/B test
      featureFlagsService.setFlag(flagKey, true);
      featureFlagsService.setRolloutPercentage(flagKey, 100);
      featureFlagsService.setABTestVariants(flagKey, ['control', 'variant-a']);
      
      // Get variant
      const variant = featureFlagsService.getABTestVariant(flagKey, userId);
      
      // Track conversion
      featureFlagsService.trackABTestMetric(flagKey, userId, variant!, 'conversion');
      
      // Get stats
      const stats = featureFlagsService.getABTestStats(flagKey);
      
      expect(stats!.variantStats[variant!].conversions).toBeGreaterThan(0);
    });

    it('should aggregate metrics across multiple users', () => {
      const flagKey = 'test-ab-flag';
      
      // Set up A/B test
      featureFlagsService.setFlag(flagKey, true);
      featureFlagsService.setRolloutPercentage(flagKey, 100);
      featureFlagsService.setABTestVariants(flagKey, ['control', 'variant-a']);
      
      // Simulate multiple users
      for (let i = 0; i < 10; i++) {
        const userId = `user-${i}`;
        const variant = featureFlagsService.getABTestVariant(flagKey, userId);
        
        // Some users interact
        if (i % 2 === 0) {
          featureFlagsService.trackABTestMetric(flagKey, userId, variant!, 'interaction');
        }
        
        // Some users convert
        if (i % 3 === 0) {
          featureFlagsService.trackABTestMetric(flagKey, userId, variant!, 'conversion');
        }
      }
      
      // Get stats
      const stats = featureFlagsService.getABTestStats(flagKey);
      
      expect(stats!.totalUsers).toBe(10);
      
      // Check that both variants have some users
      const totalUsers = stats!.variantStats.control.userCount + stats!.variantStats['variant-a'].userCount;
      expect(totalUsers).toBe(10);
    });

    it('should clear metrics when requested', () => {
      const flagKey = 'test-ab-flag';
      const userId = 'user-123';
      
      // Set up A/B test and track some metrics
      featureFlagsService.setFlag(flagKey, true);
      featureFlagsService.setRolloutPercentage(flagKey, 100);
      featureFlagsService.setABTestVariants(flagKey, ['control', 'variant-a']);
      
      const variant = featureFlagsService.getABTestVariant(flagKey, userId);
      featureFlagsService.trackABTestMetric(flagKey, userId, variant!, 'interaction');
      
      // Clear metrics
      featureFlagsService.clearABTestMetrics();
      
      // Get stats - should be empty
      const stats = featureFlagsService.getABTestStats(flagKey);
      
      expect(stats!.totalUsers).toBe(0);
      expect(stats!.variantStats.control.impressions).toBe(0);
      expect(stats!.variantStats['variant-a'].impressions).toBe(0);
    });
  });

  describe('Rollout percentage logic', () => {
    it('should respect 0% rollout', () => {
      const flagKey = 'test-ab-flag';
      featureFlagsService.setFlag(flagKey, true);
      featureFlagsService.setRolloutPercentage(flagKey, 0);
      
      // Test with multiple users - none should be enabled
      let enabledCount = 0;
      for (let i = 0; i < 100; i++) {
        if (featureFlagsService.isEnabledForUser(flagKey, `user-${i}`)) {
          enabledCount++;
        }
      }
      
      expect(enabledCount).toBe(0);
    });

    it('should respect 100% rollout', () => {
      const flagKey = 'test-ab-flag';
      featureFlagsService.setFlag(flagKey, true);
      featureFlagsService.setRolloutPercentage(flagKey, 100);
      
      // Test with multiple users - all should be enabled
      let enabledCount = 0;
      for (let i = 0; i < 100; i++) {
        if (featureFlagsService.isEnabledForUser(flagKey, `user-${i}`)) {
          enabledCount++;
        }
      }
      
      expect(enabledCount).toBe(100);
    });

    it('should reject invalid rollout percentages', () => {
      const flagKey = 'test-ab-flag';
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      featureFlagsService.setFlag(flagKey, true);
      
      // Try to set invalid percentages
      featureFlagsService.setRolloutPercentage(flagKey, -10);
      expect(consoleSpy).toHaveBeenCalled();
      
      consoleSpy.mockClear();
      featureFlagsService.setRolloutPercentage(flagKey, 150);
      expect(consoleSpy).toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });
  });
});

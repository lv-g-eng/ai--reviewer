/**
 * Unit tests for projects validation schemas
 */

import {
  createProjectBodySchema,
  updateProjectBodySchema,
  listProjectsQuerySchema,
  projectStatusSchema,
  repositoryProviderSchema,
} from '../../../src/schemas/projects.schema';

describe('Projects Schemas', () => {
  describe('projectStatusSchema', () => {
    it('should validate active status', () => {
      const result = projectStatusSchema.safeParse('active');
      expect(result.success).toBe(true);
    });

    it('should validate all valid statuses', () => {
      const statuses = ['active', 'inactive', 'archived', 'pending'];
      statuses.forEach((status) => {
        const result = projectStatusSchema.safeParse(status);
        expect(result.success).toBe(true);
      });
    });

    it('should reject invalid status', () => {
      const result = projectStatusSchema.safeParse('invalid');
      expect(result.success).toBe(false);
    });
  });

  describe('repositoryProviderSchema', () => {
    it('should validate all providers', () => {
      const providers = ['github', 'gitlab', 'bitbucket', 'other'];
      providers.forEach((provider) => {
        const result = repositoryProviderSchema.safeParse(provider);
        expect(result.success).toBe(true);
      });
    });

    it('should reject invalid provider', () => {
      const result = repositoryProviderSchema.safeParse('invalid');
      expect(result.success).toBe(false);
    });
  });

  describe('createProjectBodySchema', () => {
    const validProject = {
      name: 'Test Project',
      description: 'A test project',
      repositoryUrl: 'https://github.com/user/repo',
      repositoryProvider: 'github',
      branch: 'main',
      language: 'TypeScript',
      framework: 'Express',
      tags: ['backend', 'api'],
      settings: {
        autoReview: true,
        reviewOnPush: true,
        reviewOnPR: true,
        minCoverageThreshold: 80,
        enableArchitectureAnalysis: true,
        enableSecurityScan: true,
      },
    };

    it('should validate valid project data', () => {
      const result = createProjectBodySchema.safeParse(validProject);
      expect(result.success).toBe(true);
    });

    it('should validate minimal project data', () => {
      const minimalProject = {
        name: 'Test Project',
        repositoryUrl: 'https://github.com/user/repo',
      };
      const result = createProjectBodySchema.safeParse(minimalProject);
      expect(result.success).toBe(true);
    });

    it('should apply default values', () => {
      const minimalProject = {
        name: 'Test Project',
        repositoryUrl: 'https://github.com/user/repo',
      };
      const result = createProjectBodySchema.safeParse(minimalProject);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.repositoryProvider).toBe('github');
        expect(result.data.branch).toBe('main');
      }
    });

    it('should reject empty name', () => {
      const invalidProject = { ...validProject, name: '' };
      const result = createProjectBodySchema.safeParse(invalidProject);
      expect(result.success).toBe(false);
    });

    it('should reject name over 100 chars', () => {
      const invalidProject = { ...validProject, name: 'a'.repeat(101) };
      const result = createProjectBodySchema.safeParse(invalidProject);
      expect(result.success).toBe(false);
    });

    it('should reject invalid repository URL', () => {
      const invalidProject = { ...validProject, repositoryUrl: 'not-a-url' };
      const result = createProjectBodySchema.safeParse(invalidProject);
      expect(result.success).toBe(false);
    });

    it('should reject description over 500 chars', () => {
      const invalidProject = { ...validProject, description: 'a'.repeat(501) };
      const result = createProjectBodySchema.safeParse(invalidProject);
      expect(result.success).toBe(false);
    });

    it('should reject branch over 100 chars', () => {
      const invalidProject = { ...validProject, branch: 'a'.repeat(101) };
      const result = createProjectBodySchema.safeParse(invalidProject);
      expect(result.success).toBe(false);
    });

    it('should reject language over 50 chars', () => {
      const invalidProject = { ...validProject, language: 'a'.repeat(51) };
      const result = createProjectBodySchema.safeParse(invalidProject);
      expect(result.success).toBe(false);
    });

    it('should reject framework over 50 chars', () => {
      const invalidProject = { ...validProject, framework: 'a'.repeat(51) };
      const result = createProjectBodySchema.safeParse(invalidProject);
      expect(result.success).toBe(false);
    });

    it('should reject over 20 tags', () => {
      const invalidProject = { ...validProject, tags: Array(21).fill('tag') };
      const result = createProjectBodySchema.safeParse(invalidProject);
      expect(result.success).toBe(false);
    });

    it('should reject invalid coverage threshold', () => {
      const invalidProject = {
        ...validProject,
        settings: { ...validProject.settings, minCoverageThreshold: 101 },
      };
      const result = createProjectBodySchema.safeParse(invalidProject);
      expect(result.success).toBe(false);
    });

    it('should trim whitespace from strings', () => {
      const projectWithWhitespace = {
        ...validProject,
        name: '  Test Project  ',
        description: '  A test project  ',
      };
      const result = createProjectBodySchema.safeParse(projectWithWhitespace);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.name).toBe('Test Project');
        expect(result.data.description).toBe('A test project');
      }
    });
  });

  describe('updateProjectBodySchema', () => {
    it('should validate partial update', () => {
      const update = {
        name: 'Updated Name',
        description: 'Updated description',
      };
      const result = updateProjectBodySchema.safeParse(update);
      expect(result.success).toBe(true);
    });

    it('should validate empty update', () => {
      const result = updateProjectBodySchema.safeParse({});
      expect(result.success).toBe(true);
    });

    it('should validate status update', () => {
      const update = { status: 'archived' };
      const result = updateProjectBodySchema.safeParse(update);
      expect(result.success).toBe(true);
    });

    it('should validate settings update', () => {
      const update = {
        settings: {
          autoReview: false,
          minCoverageThreshold: 90,
        },
      };
      const result = updateProjectBodySchema.safeParse(update);
      expect(result.success).toBe(true);
    });

    it('should reject invalid status', () => {
      const update = { status: 'invalid' };
      const result = updateProjectBodySchema.safeParse(update);
      expect(result.success).toBe(false);
    });

    it('should reject name over 100 chars', () => {
      const update = { name: 'a'.repeat(101) };
      const result = updateProjectBodySchema.safeParse(update);
      expect(result.success).toBe(false);
    });
  });

  describe('listProjectsQuerySchema', () => {
    it('should validate empty query', () => {
      const result = listProjectsQuerySchema.safeParse({});
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.page).toBe(1);
        expect(result.data.limit).toBe(10);
        expect(result.data.sortBy).toBe('updatedAt');
        expect(result.data.sortOrder).toBe('desc');
      }
    });

    it('should validate with filters', () => {
      const query = {
        status: 'active',
        language: 'TypeScript',
        framework: 'Express',
        search: 'test',
        page: '2',
        limit: '20',
        sortBy: 'name',
        sortOrder: 'asc',
        tags: 'backend,api',
      };
      const result = listProjectsQuerySchema.safeParse(query);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.page).toBe(2);
        expect(result.data.limit).toBe(20);
        expect(result.data.sortBy).toBe('name');
        expect(result.data.sortOrder).toBe('asc');
      }
    });

    it('should reject invalid status', () => {
      const query = { status: 'invalid' };
      const result = listProjectsQuerySchema.safeParse(query);
      expect(result.success).toBe(false);
    });

    it('should reject invalid sortBy', () => {
      const query = { sortBy: 'invalid' };
      const result = listProjectsQuerySchema.safeParse(query);
      expect(result.success).toBe(false);
    });

    it('should reject search over 200 chars', () => {
      const query = { search: 'a'.repeat(201) };
      const result = listProjectsQuerySchema.safeParse(query);
      expect(result.success).toBe(false);
    });
  });
});

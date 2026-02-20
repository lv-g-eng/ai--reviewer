/**
 * RBAC Type Definitions
 */

export enum Role {
  ADMIN = 'ADMIN',
  PROGRAMMER = 'PROGRAMMER',
  VISITOR = 'VISITOR',
}

export enum Permission {
  VIEW_PROJECTS = 'VIEW_PROJECTS',
  CREATE_PROJECT = 'CREATE_PROJECT',
  MODIFY_PROJECT = 'MODIFY_PROJECT',
  DELETE_PROJECT = 'DELETE_PROJECT',
  VIEW_USERS = 'VIEW_USERS',
  CREATE_USER = 'CREATE_USER',
  MODIFY_USER = 'MODIFY_USER',
  DELETE_USER = 'DELETE_USER',
  VIEW_REVIEWS = 'VIEW_REVIEWS',
  CREATE_REVIEW = 'CREATE_REVIEW',
  MODIFY_REVIEW = 'MODIFY_REVIEW',
  MODIFY_CONFIG = 'MODIFY_CONFIG',
}

export interface RBACUser {
  id: string;
  username: string;
  role: Role;
  permissions?: Permission[];
}

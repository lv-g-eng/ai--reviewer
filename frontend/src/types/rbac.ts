/**
 * RBAC Type Definitions
 */

export enum Role {
  ADMIN = 'ADMIN',           // Full system control
  MANAGER = 'MANAGER',       // Project oversight & ROI
  REVIEWER = 'REVIEWER',     // Read/Write analysis
  PROGRAMMER = 'PROGRAMMER', // CRUD own branch
  VISITOR = 'VISITOR',       // Read-only grants
}

export enum Permission {
  // User Management
  CREATE_USER = 'CREATE_USER',
  DELETE_USER = 'DELETE_USER',
  UPDATE_USER = 'UPDATE_USER',
  VIEW_USER = 'VIEW_USER',
  
  // Project Management
  CREATE_PROJECT = 'CREATE_PROJECT',
  DELETE_PROJECT = 'DELETE_PROJECT',
  UPDATE_PROJECT = 'UPDATE_PROJECT',
  VIEW_PROJECT = 'VIEW_PROJECT',
  
  // Configuration
  MODIFY_CONFIG = 'MODIFY_CONFIG',
  VIEW_CONFIG = 'VIEW_CONFIG',
  
  // Reports
  EXPORT_REPORT = 'EXPORT_REPORT',
}

export interface RBACUser {
  id: string;
  username: string;
  role: Role;
  permissions?: Permission[];
}


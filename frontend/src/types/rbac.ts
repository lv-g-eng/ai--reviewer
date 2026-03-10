/**
 * RBAC Type Definitions
 */

// Import consolidated enums from common library
export { Role, Permission } from '../../common/shared/enums';

export interface RBACUser {
  id: string;
  username: string;
  role: Role;
  permissions?: Permission[];
}


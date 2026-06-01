export type UsersSortField = 'id' | 'firstName' | 'lastName' | 'email' | 'createdAt';
export type SortDirection = 'asc' | 'desc';

export interface UsersTableUser {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  /** ISO date string */
  createdAt: string;
}

export interface UsersTableFilters {
  /** Full-text search across firstName/lastName/email (case-insensitive) */
  q?: string;
  firstName?: string;
  lastName?: string;
  email?: string;
  /**
   * createdAt >= createdAfter (ISO date string). If invalid, server ignores.
   * Example: 2026-01-01T00:00:00.000Z
   */
  createdAfter?: string;
  /**
   * createdAt <= createdBefore (ISO date string). If invalid, server ignores.
   * Example: 2026-12-31T23:59:59.999Z
   */
  createdBefore?: string;
}

export interface ListUsersQuery {
  /**
   * 1-based page index.
   * Default: 1
   */
  page?: number;
  /**
   * Page size.
   * Default: 10
   */
  pageSize?: number;
  /**
   * Sort field.
   * Default: createdAt
   */
  sortBy?: UsersSortField;
  /**
   * Sort direction.
   * Default: desc
   */
  sortDir?: SortDirection;
  filters?: UsersTableFilters;
}

export interface PaginatedResult<T> {
  items: T[];
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
}

export interface ListUsersResponse {
  status: 'ok';
  data: PaginatedResult<UsersTableUser>;
}

export interface ErrorResponse {
  status: 'error';
  message: string;
}

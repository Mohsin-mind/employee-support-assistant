// Categorical constants mirroring backend enums for full-stack consistency

export const LeaveStatus = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  CANCELLED: 'cancelled',
} as const;
export type LeaveStatus = typeof LeaveStatus[keyof typeof LeaveStatus];

export const LeaveType = {
  ANNUAL: 'annual',
  SICK: 'sick',
  CASUAL: 'casual',
  MATERNITY: 'maternity',
  PATERNITY: 'paternity',
  UNPAID: 'unpaid',
} as const;
export type LeaveType = typeof LeaveType[keyof typeof LeaveType];

export const MessageRole = {
  SYSTEM: 'system',
  USER: 'user',
  ASSISTANT: 'assistant',
  TOOL: 'tool',
} as const;
export type MessageRole = typeof MessageRole[keyof typeof MessageRole];

export const DocumentStatus = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  INDEXED: 'indexed',
  FAILED: 'failed',
} as const;
export type DocumentStatus = typeof DocumentStatus[keyof typeof DocumentStatus];

export const ErrorCode = {
  NOT_FOUND: 'NOT_FOUND',
  BAD_REQUEST: 'BAD_REQUEST',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  CONFLICT: 'CONFLICT',
  DATABASE_ERROR: 'DATABASE_ERROR',
  DATABASE_UNAVAILABLE: 'DATABASE_UNAVAILABLE',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  AI_SERVICE_ERROR: 'AI_SERVICE_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
} as const;
export type ErrorCode = typeof ErrorCode[keyof typeof ErrorCode];

// Client Route Paths
export const ROUTES = {
  HOME: '/',
  CHAT: '/chat',
  DOCUMENTS: '/documents',
  LEAVE: '/leave',
} as const;

// Pagination Defaults
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
} as const;

// Standard User-Facing Notices
export const UI_MESSAGES = {
  GENERIC_ERROR: 'An unexpected error occurred. Please try again.',
  NETWORK_ERROR: 'Unable to connect to the server. Please check your connection.',
  SAVED_SUCCESS: 'Saved successfully.',
  DELETED_SUCCESS: 'Deleted successfully.',
} as const;

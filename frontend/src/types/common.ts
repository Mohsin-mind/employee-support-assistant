// Generic response envelopes matching backend schemas/common.py

export interface BaseResponse {
  success: boolean;
  message?: string;
}

export interface APIResponse<T> extends BaseResponse {
  data: T;
}

export interface PageMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface PaginatedData<T> {
  items: T[];
  pagination: PageMeta;
}

export interface PaginatedResponse<T> extends BaseResponse {
  data: PaginatedData<T>;
}

export interface ErrorDetail {
  code: string;
  message: string;
  details?: unknown;
}

export interface ErrorResponse {
  success: false;
  error: ErrorDetail;
}

export interface AppError {
  message: string;
  code: string;
  status: number;
  details?: unknown;
}

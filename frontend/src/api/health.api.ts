import { apiClient } from './client';
import type { HealthResponse } from '../types/health';

export const fetchHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
};

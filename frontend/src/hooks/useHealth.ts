import { useQuery } from '@tanstack/react-query';
import { fetchHealth } from '../api/health.api';

export const useHealth = () => {
  return useQuery({
    queryKey: ['system-health'],
    queryFn: fetchHealth,
    refetchInterval: 10000, // Polling health every 10s
    retry: 2,
  });
};

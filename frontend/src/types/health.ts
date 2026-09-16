export interface HealthData {
  status: 'healthy' | 'degraded' | 'error';
  app_name: string;
  environment: string;
  database: string;
  db_name: string;
  db_host: string;
  db_latency_ms?: number;
}

export interface HealthResponse {
  success: boolean;
  data: HealthData;
}

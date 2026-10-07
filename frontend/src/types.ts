export interface Detection {
  id: number;
  code: string;
  timestamp: string;
  lat: number;
  lon: number;
  confidence: number;
  severity: 'Low' | 'Medium' | 'High';
  status: 'Reported' | 'Dispatched' | 'In progress' | 'Repaired';
  snapshot_path?: string;
  repair_proof_path?: string;
  street_name?: string;
  priority?: string;
  is_simulated_gps: boolean;
}

export interface WorkOrder {
  id: number;
  detection_id: number;
  title: string;
  assignee: string;
  priority: 'Low' | 'Medium' | 'High' | 'Urgent';
  status: 'Reported' | 'Dispatched' | 'In progress' | 'Repaired';
  notes: string;
  repair_proof_path?: string;
  cost_estimate?: number;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  open_issues: number;
  high_severity: number;
  dispatched: number;
  repaired_this_week: number;
  total_budget_allocated?: number;
}

export interface Settings {
  model_path: string;
  model_loaded: boolean;
  input_size: number;
  default_conf: number;
  gps_mode: string;
  custom_gps_path?: string;
}

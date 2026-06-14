export interface Customer {
  id: string;
  name: string;
  email: string;
  phone?: string;
  city?: string;
  total_spend: number;
  order_count: number;
  last_order_at?: string;
  last_order_days?: number;
  created_at?: string;
  twin?: CustomerTwin;
}

export interface CustomerTwin {
  customer_id: string;
  version: number;
  channel_affinity: Record<string, number>;
  category_affinity: Record<string, number>;
  churn_probability: number;
  purchase_intent_score: number;
  predicted_ltv_90d: number;
  predicted_next_purchase_days?: number;
  price_sensitivity: number;
  urgency_responsiveness: number;
  social_proof_affinity: number;
  communication_style: string;
  narrative_summary?: string;
  confidence_score: number;
  updated_at?: string;
}

export interface Campaign {
  id: string;
  name: string;
  intent: string;
  status: string;
  segment_id?: string;
  strategy?: {
    channel_allocation: Record<string, number>;
    send_time: string;
    campaign_structure: string;
    estimated_cost_inr?: number;
    rationale?: string;
    risk_factors?: string[];
    key_actions?: string[];
  };
  simulation_result?: SimulationResult;
  personas?: Persona[];
  copies?: MessageCopy[];
  agent_trace?: AgentStep[];
  explanation?: ExplanationBlock;
  actual_stats?: CampaignStats;
  created_at?: string;
  executed_at?: string;
  completed_at?: string;
}

export interface SimulationResult {
  open_rate: { p10: number; p50: number; p90: number };
  click_rate: { p10: number; p50: number; p90: number };
  conversion_rate: { p10: number; p50: number; p90: number };
  revenue_inr: { p10: number; p50: number; p90: number };
  roi: number;
  confidence: number;
  confidence_reason: string;
  alternatives: Alternative[];
  segment_size?: number;
  channel_mix?: Record<string, number>;
}

export interface Alternative {
  strategy: string;
  predicted_uplift_pct: number;
  tradeoff: string;
}

export interface Persona {
  name: string;
  traits: string[];
  preferred_channel: string;
  preferred_timing: string;
  message_tone: string;
  communication_style: string;
  pct_of_segment: number;
  price_sensitive: boolean;
  urgency_responsive: boolean;
  key_motivation?: string;
  customer_count?: number;
}

export interface MessageCopy {
  persona_name: string;
  channel: string;
  variant: number;
  subject?: string;
  body: string;
  cta: string;
  personalisation_tokens: string[];
  why_it_works: string;
}

export interface AgentStep {
  agent_id: string;
  agent_name: string;
  status: string;
  input_summary: string;
  output_summary: string;
  reasoning: string;
  confidence: number;
  started_at: string;
  completed_at?: string;
  error?: string;
}

export interface ExplanationBlock {
  recommendation: string;
  reasoning: string;
  evidence: string[];
  confidence: number;
  confidence_label: string;
  expected_impact: string;
  alternative: Record<string, any>;
  risk_factors: string[];
  agent_id: string;
}

export interface CampaignStats {
  total_sent: number;
  delivered: number;
  opened: number;
  clicked: number;
  converted: number;
  failed: number;
  open_rate: number;
  click_rate: number;
  conversion_rate: number;
  by_channel?: Record<string, any>;
}

export interface LiveEvent {
  type: string;
  campaign_id?: string;
  message_id?: string;
  customer_id?: string;
  event_type?: string;
  channel?: string;
  timestamp: string;
  agent?: string;
  agent_name?: string;
  status?: string;
  message?: string;
  confidence?: number;
  reasoning?: string;
}

export interface Insight {
  id: string;
  campaign_id: string;
  campaign_name?: string;
  campaign_intent?: string;
  content: {
    key_insights?: string[];
    prediction_accuracy?: Record<string, string>;
    next_campaign_recommendations?: string[];
    anomalies?: string[];
    executive_summary?: string;
    winning_element?: string;
    improvement_area?: string;
    actual_stats?: Record<string, number>;
    predicted_stats?: Record<string, number>;
    [key: string]: any;
  };
  generated_at?: string;
}

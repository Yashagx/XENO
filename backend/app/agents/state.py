from typing import TypedDict, Optional, List, Literal, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ParsedIntent:
    goal: str
    churn_window_days: Optional[int] = None
    value_tier: Optional[str] = None  # high, medium, low
    occasion: Optional[str] = None
    channel_preference: Optional[str] = None
    min_ltv: Optional[float] = None
    max_recency_days: Optional[int] = None
    keywords: List[str] = field(default_factory=list)


@dataclass
class CustomerSummary:
    id: str
    name: str
    email: str
    total_spend: float
    order_count: int
    last_order_days: int
    churn_probability: float
    channel_affinity: dict
    category_affinity: dict
    narrative: str
    communication_style: str
    price_sensitivity: float
    urgency_responsiveness: float


@dataclass
class Segment:
    name: str
    description: str
    inclusion_criteria: dict
    exclusion_criteria: dict
    customer_ids: List[str]
    customer_count: int
    performance_baseline: dict
    confidence: float
    reasoning: str


@dataclass
class Persona:
    name: str
    traits: List[str]
    preferred_channel: str
    preferred_timing: str
    message_tone: str
    communication_style: str
    pct_of_segment: float
    customer_ids: List[str]
    price_sensitive: bool
    urgency_responsive: bool


@dataclass
class Strategy:
    channel_allocation: dict  # {"email": 0.6, "sms": 0.4}
    send_time: str
    campaign_structure: str  # single | drip | ab_test
    estimated_cost: float
    rationale: str
    risk_factors: List[str]
    key_actions: List[str]


@dataclass
class MessageCopy:
    persona_name: str
    channel: str
    subject: Optional[str]
    body: str
    cta: str
    personalisation_tokens: List[str]
    variant: int  # 1 or 2
    why_it_works: str


@dataclass
class SimulationResult:
    open_rate_p10: float
    open_rate_p50: float
    open_rate_p90: float
    click_rate_p10: float
    click_rate_p50: float
    click_rate_p90: float
    conversion_rate_p10: float
    conversion_rate_p50: float
    conversion_rate_p90: float
    revenue_p10: float
    revenue_p50: float
    revenue_p90: float
    roi: float
    confidence: float
    confidence_reason: str
    alternatives: List[dict]


@dataclass
class ExplanationBlock:
    recommendation: str
    reasoning: str
    evidence: List[str]
    confidence: float
    confidence_label: str  # low | medium | high
    expected_impact: str
    alternative: dict
    risk_factors: List[str]
    agent_id: str


@dataclass
class AgentStep:
    agent_id: str
    agent_name: str
    status: str  # running | completed | failed
    input_summary: str
    output_summary: str
    reasoning: str
    confidence: float
    started_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None


class CampaignState(TypedDict):
    campaign_id: str
    intent: str
    parsed_intent: Optional[dict]
    customers: Optional[List[dict]]
    segment: Optional[dict]
    personas: Optional[List[dict]]
    strategy: Optional[dict]
    copies: Optional[List[dict]]
    channel_assignments: Optional[List[dict]]
    simulation: Optional[dict]
    explanation: Optional[dict]
    agent_trace: List[dict]
    status: str
    errors: List[str]
    confidence: float

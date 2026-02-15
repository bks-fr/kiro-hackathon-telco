"""
Pydantic data models for AI-Powered Customer Support System MVP.

All data structures use Pydantic BaseModel for type safety, validation, and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class PriorityLevel(str, Enum):
    """Priority level enumeration for ticket routing."""
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class Team(str, Enum):
    """Support team enumeration."""
    NETWORK_OPS = "Network Operations"
    BILLING = "Billing Support"
    TECHNICAL = "Technical Support"
    ACCOUNT_MGMT = "Account Management"


class AccountType(str, Enum):
    """Customer account type enumeration."""
    ENTERPRISE = "Enterprise"
    CONSUMER = "Consumer"
    BUSINESS = "Business"


class ServiceHealth(str, Enum):
    """Service health status enumeration."""
    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    OUTAGE = "Outage"


class Ticket(BaseModel):
    """Incoming support ticket model."""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    customer_id: str = Field(..., description="Customer identifier")
    subject: str = Field(..., min_length=1, description="Ticket subject")
    description: str = Field(..., min_length=1, description="Ticket description")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Ticket creation time")
    
    @validator('ticket_id', 'customer_id')
    def validate_ids(cls, v):
        """Validate that IDs are not empty."""
        if not v or not v.strip():
            raise ValueError("ID cannot be empty")
        return v.strip()


class Customer(BaseModel):
    """Customer information model."""
    customer_id: str = Field(..., description="Customer identifier")
    is_vip: bool = Field(default=False, description="VIP status")
    account_type: AccountType = Field(default=AccountType.CONSUMER, description="Account type")
    lifetime_value: float = Field(ge=0, description="Customer lifetime value")
    account_standing: str = Field(default="Good", description="Account standing")
    service_plan: str = Field(..., description="Service plan name")


class Outage(BaseModel):
    """Service outage information model."""
    service_id: str = Field(..., description="Service identifier")
    severity: str = Field(..., description="Outage severity")
    started_at: datetime = Field(..., description="Outage start time")
    description: Optional[str] = Field(None, description="Outage description")


class ServiceStatus(BaseModel):
    """Service status information model."""
    service_id: str = Field(..., description="Service identifier")
    service_health: ServiceHealth = Field(..., description="Current health status")
    active_outages: List[Outage] = Field(default_factory=list, description="Active outages")


class IssueClassification(BaseModel):
    """Issue classification result model."""
    primary_category: str = Field(..., description="Primary issue category")
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence")
    keywords: List[str] = Field(default_factory=list, description="Matched keywords")
    secondary_categories: List[str] = Field(default_factory=list, description="Alternative categories")


class ExtractedEntities(BaseModel):
    """Extracted entities from ticket model."""
    account_numbers: List[str] = Field(default_factory=list, description="Account numbers")
    service_ids: List[str] = Field(default_factory=list, description="Service IDs")
    error_codes: List[str] = Field(default_factory=list, description="Error codes")
    phone_numbers: List[str] = Field(default_factory=list, description="Phone numbers")
    monetary_amounts: List[float] = Field(default_factory=list, description="Monetary amounts")


class PriorityCalculation(BaseModel):
    """Priority calculation result model."""
    priority_level: PriorityLevel = Field(..., description="Calculated priority")
    priority_score: float = Field(ge=0, le=100, description="Numeric priority score")
    factors: Dict[str, Any] = Field(default_factory=dict, description="Contributing factors")
    reasoning: str = Field(..., description="Priority reasoning")


class RoutingDecision(BaseModel):
    """Team routing decision model."""
    assigned_team: Team = Field(..., description="Assigned team")
    confidence: float = Field(ge=0.0, le=1.0, description="Routing confidence")
    alternative_teams: List[Team] = Field(default_factory=list, description="Alternative teams")
    reasoning: str = Field(..., description="Routing reasoning")
    requires_manual_review: bool = Field(default=False, description="Manual review flag")


class HistoricalTicket(BaseModel):
    """Historical ticket information model."""
    ticket_id: str = Field(..., description="Ticket identifier")
    issue_type: str = Field(..., description="Issue type")
    resolution_time_hours: float = Field(ge=0, description="Resolution time")
    escalated: bool = Field(default=False, description="Escalation flag")
    resolved_at: datetime = Field(..., description="Resolution timestamp")


class HistoricalContext(BaseModel):
    """Customer historical context model."""
    recent_tickets: List[HistoricalTicket] = Field(default_factory=list, description="Recent tickets")
    common_issues: List[str] = Field(default_factory=list, description="Common issue types")
    escalation_history: bool = Field(default=False, description="Has escalation history")


class FinalDecision(BaseModel):
    """Final routing decision with all context model."""
    ticket_id: str = Field(..., description="Ticket identifier")
    customer_id: str = Field(..., description="Customer identifier")
    assigned_team: Team = Field(..., description="Assigned team")
    priority_level: PriorityLevel = Field(..., description="Priority level")
    confidence_score: float = Field(ge=0, le=100, description="Overall confidence")
    reasoning: str = Field(..., description="Decision reasoning")
    processing_time_ms: float = Field(ge=0, description="Processing time in milliseconds")
    requires_manual_review: bool = Field(default=False, description="Manual review flag")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Decision timestamp")

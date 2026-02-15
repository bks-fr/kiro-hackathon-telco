# API Documentation

This document describes the data models and tool interfaces for the AI-Powered Customer Support System MVP.

## Data Models

All data models are implemented using Pydantic BaseModel for type safety and validation.

### Enumerations

#### PriorityLevel

```python
class PriorityLevel(str, Enum):
    P0 = "P0"  # Critical
    P1 = "P1"  # High
    P2 = "P2"  # Medium
    P3 = "P3"  # Low
```

#### Team

```python
class Team(str, Enum):
    NETWORK_OPS = "Network Operations"
    BILLING = "Billing Support"
    TECHNICAL = "Technical Support"
    ACCOUNT_MGMT = "Account Management"
```

#### AccountType

```python
class AccountType(str, Enum):
    ENTERPRISE = "Enterprise"
    CONSUMER = "Consumer"
    BUSINESS = "Business"
```

#### ServiceHealth

```python
class ServiceHealth(str, Enum):
    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    OUTAGE = "Outage"
```

### Core Models

#### Ticket

Represents an incoming support ticket.

```python
class Ticket(BaseModel):
    ticket_id: str          # Unique identifier (required, non-empty)
    customer_id: str        # Customer identifier (required, non-empty)
    subject: str            # Ticket subject (required, min_length=1)
    description: str        # Ticket description (required, min_length=1)
    timestamp: datetime     # Creation time (default: current UTC time)
```

**Example:**
```python
ticket = Ticket(
    ticket_id="TKT-001",
    customer_id="CUST001",
    subject="Internet connection down",
    description="My internet has been down for 2 hours. Error code: NET-500.",
    timestamp=datetime.utcnow()
)
```

#### Customer

Represents customer information.

```python
class Customer(BaseModel):
    customer_id: str        # Customer identifier (required)
    is_vip: bool           # VIP status (default: False)
    account_type: AccountType  # Account type (default: CONSUMER)
    lifetime_value: float  # Customer lifetime value (>= 0)
    account_standing: str  # Account standing (default: "Good")
    service_plan: str      # Service plan name (required)
```

**Example:**
```python
customer = Customer(
    customer_id="CUST001",
    is_vip=True,
    account_type=AccountType.ENTERPRISE,
    lifetime_value=50000.0,
    account_standing="Good",
    service_plan="Premium"
)
```

#### ServiceStatus

Represents service health status.

```python
class ServiceStatus(BaseModel):
    service_id: str              # Service identifier (required)
    service_health: ServiceHealth  # Current health status (required)
    active_outages: List[Outage]  # List of active outages (default: [])
```

#### IssueClassification

Result of ticket classification.

```python
class IssueClassification(BaseModel):
    primary_category: str           # Primary issue category (required)
    confidence: float               # Confidence score (0.0-1.0)
    keywords: List[str]             # Matched keywords (default: [])
    secondary_categories: List[str] # Alternative categories (default: [])
```

**Categories:**
- Network Outage
- Billing Dispute
- Technical Problem
- Account Access

#### ExtractedEntities

Entities extracted from ticket text.

```python
class ExtractedEntities(BaseModel):
    account_numbers: List[str]    # Account numbers (e.g., ACC-12345)
    service_ids: List[str]        # Service IDs (e.g., SVC001)
    error_codes: List[str]        # Error codes (e.g., NET-500)
    phone_numbers: List[str]      # Phone numbers
    monetary_amounts: List[float] # Dollar amounts
```

#### PriorityCalculation

Result of priority calculation.

```python
class PriorityCalculation(BaseModel):
    priority_level: PriorityLevel  # Calculated priority (P0-P3)
    priority_score: float          # Numeric score (0-100)
    factors: Dict[str, Any]        # Contributing factors
    reasoning: str                 # Explanation of priority
```

**Scoring:**
- P0 (Critical): Score >= 80
- P1 (High): Score >= 60
- P2 (Medium): Score >= 40
- P3 (Low): Score < 40

**Factors:**
- VIP status: 30% weight
- Issue severity: 40% weight
- Ticket age: 20% weight
- Service outage: 10% weight

#### RoutingDecision

Team routing decision.

```python
class RoutingDecision(BaseModel):
    assigned_team: Team              # Assigned team (required)
    confidence: float                # Routing confidence (0.0-1.0)
    alternative_teams: List[Team]    # Alternative teams (default: [])
    reasoning: str                   # Routing explanation (required)
    requires_manual_review: bool     # Manual review flag (default: False)
```

#### FinalDecision

Complete routing decision with all context.

```python
class FinalDecision(BaseModel):
    ticket_id: str                   # Ticket identifier (required)
    customer_id: str                 # Customer identifier (required)
    assigned_team: Team              # Assigned team (required)
    priority_level: PriorityLevel    # Priority level (required)
    confidence_score: float          # Overall confidence (0-100)
    reasoning: str                   # Decision explanation (required)
    processing_time_ms: float        # Processing time in ms (>= 0)
    requires_manual_review: bool     # Manual review flag (default: False)
    timestamp: datetime              # Decision timestamp (default: now)
```

## Agent Tools

### 1. classify_issue()

Classifies a ticket into an issue category.

```python
def classify_issue(ticket_text: str) -> IssueClassification:
    """
    Classify ticket using keyword matching.
    
    Args:
        ticket_text: Combined subject and description text
        
    Returns:
        IssueClassification with category, confidence, and keywords
    """
```

**Example:**
```python
result = classify_issue("My internet is down and offline")
# Returns: IssueClassification(
#     primary_category="Network Outage",
#     confidence=0.85,
#     keywords=["down", "offline"],
#     secondary_categories=[]
# )
```

### 2. extract_entities()

Extracts structured entities from ticket text.

```python
def extract_entities(ticket_text: str) -> ExtractedEntities:
    """
    Extract entities using regex patterns.
    
    Args:
        ticket_text: Ticket subject and description
        
    Returns:
        ExtractedEntities with all found entities
    """
```

**Patterns:**
- Account numbers: `ACC-\d+`
- Service IDs: `SVC\d+`
- Error codes: `[A-Z]+-\d+`
- Phone numbers: `\d{3}-\d{3}-\d{4}`
- Money: `\$(\d+(?:\.\d{2})?)`

### 3. check_vip_status()

Retrieves customer information.

```python
def check_vip_status(customer_id: str) -> Customer:
    """
    Check VIP status from mock database.
    
    Args:
        customer_id: Customer identifier
        
    Returns:
        Customer model with VIP status and account info
    """
```

### 4. check_service_status()

Checks service health and outages.

```python
def check_service_status(service_ids: List[str]) -> ServiceStatus:
    """
    Check service status from mock data.
    
    Args:
        service_ids: List of service identifiers
        
    Returns:
        ServiceStatus with health and active outages
    """
```

### 5. calculate_priority()

Calculates ticket priority level.

```python
def calculate_priority(
    vip_status: Customer,
    issue_classification: IssueClassification,
    service_status: ServiceStatus,
    ticket_age_hours: float
) -> PriorityCalculation:
    """
    Calculate priority using weighted scoring.
    
    Args:
        vip_status: Customer information
        issue_classification: Issue classification result
        service_status: Service health status
        ticket_age_hours: Hours since ticket creation
        
    Returns:
        PriorityCalculation with level, score, and reasoning
    """
```

### 6. route_to_team()

Determines the best support team.

```python
def route_to_team(
    issue_classification: IssueClassification,
    entities: ExtractedEntities,
    service_status: ServiceStatus
) -> RoutingDecision:
    """
    Route to team based on issue classification.
    
    Args:
        issue_classification: Issue classification result
        entities: Extracted entities
        service_status: Service health status
        
    Returns:
        RoutingDecision with team, confidence, and reasoning
    """
```

**Routing Map:**
- Network Outage → Network Operations
- Billing Dispute → Billing Support
- Technical Problem → Technical Support
- Account Access → Account Management

### 7. get_historical_context()

Retrieves customer ticket history.

```python
def get_historical_context(
    customer_id: str,
    limit: int = 5
) -> HistoricalContext:
    """
    Get historical tickets from mock data.
    
    Args:
        customer_id: Customer identifier
        limit: Maximum number of recent tickets (default: 5)
        
    Returns:
        HistoricalContext with recent tickets and patterns
    """
```

## Agent Interface

### TicketRoutingAgent

Main agent class for processing tickets.

```python
class TicketRoutingAgent:
    def __init__(self, use_agent_tools: bool = False):
        """
        Initialize the ticket routing agent.
        
        Args:
            use_agent_tools: Use AI-powered tools instead of mock tools
        """
        
    def process_ticket(self, ticket: Ticket) -> FinalDecision:
        """
        Process a ticket and return routing decision.
        
        Args:
            ticket: Ticket model to process
            
        Returns:
            FinalDecision with team, priority, and reasoning
            
        Raises:
            Exception: If agent fails (returns fallback decision)
        """
```

## Pydantic Usage

### Creating Models

```python
# From keyword arguments
ticket = Ticket(
    ticket_id="TKT-001",
    customer_id="CUST001",
    subject="Issue",
    description="Description"
)

# From dictionary
data = {"ticket_id": "TKT-001", ...}
ticket = Ticket(**data)
```

### Validation

```python
from pydantic import ValidationError

try:
    ticket = Ticket(ticket_id="", customer_id="CUST001")
except ValidationError as e:
    print(e.errors())
    # [{'loc': ('ticket_id',), 'msg': 'ID cannot be empty', ...}]
```

### Serialization

```python
# To dictionary
data = ticket.model_dump()

# To JSON string
json_str = ticket.model_dump_json(indent=2)

# To JSON file
with open('ticket.json', 'w') as f:
    f.write(ticket.model_dump_json(indent=2))
```

### Deserialization

```python
# From dictionary
ticket = Ticket(**data)

# From JSON string
import json
ticket = Ticket(**json.loads(json_str))
```

## Configuration

### config.py

```python
# Bedrock Configuration
BEDROCK_REGION = 'us-east-1'
BEDROCK_MODEL_ID = 'anthropic.claude-sonnet-4-5-v2'

# Agent Configuration
AGENT_CONFIG = {
    'temperature': 0.1,
    'max_tokens': 4096,
    'max_iterations': 10,
    'timeout_seconds': 30
}

# Confidence Threshold
CONFIDENCE_THRESHOLD = 0.7

# Priority Thresholds
PRIORITY_THRESHOLDS = {
    'P0': 80,
    'P1': 60,
    'P2': 40,
    'P3': 0
}
```

## Error Handling

All tools and agent methods handle errors gracefully:

```python
try:
    decision = agent.process_ticket(ticket)
except Exception as e:
    # Agent provides fallback decision
    # decision.requires_manual_review = True
    # decision.confidence_score = 50.0
```

## Type Hints

All functions use Python type hints:

```python
from typing import List, Dict, Any, Optional

def my_function(
    param1: str,
    param2: List[str],
    param3: Optional[int] = None
) -> Dict[str, Any]:
    ...
```

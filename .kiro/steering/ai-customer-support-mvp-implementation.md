---
inclusion: always
---

# AI Customer Support System MVP - Implementation Guide

## Project Structure Requirements

```
ticket-routing-mvp/
├── src/                    # Source code
│   ├── config.py
│   ├── models.py
│   ├── tools.py
│   ├── agent.py
│   └── main.py
├── tests/                  # All tests go here
│   ├── test_tools.py
│   ├── test_agent.py
│   └── test_integration.py
├── docs/                   # All documentation
│   ├── README.md
│   ├── setup.md
│   └── api.md
├── mock_data.py
├── requirements.txt
├── .env.example
├── .gitignore
└── CHANGELOG.md           # Track all changes
```

## Core Principles

1. **Pydantic First**: All data structures MUST use Pydantic BaseModel classes
2. **Type Safety**: Use Python type hints everywhere
3. **Minimal Code**: Write only what's necessary
4. **Tests in tests/**: All test files go in the tests/ folder
5. **Docs in docs/**: All documentation goes in the docs/ folder
6. **Update CHANGELOG.md**: Document every significant change

## Pydantic Standards


```python
# Always use Field() with validation
class Ticket(BaseModel):
    ticket_id: str = Field(..., description="Unique ticket identifier")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")

# Use Enums for constrained values
class Team(str, Enum):
    NETWORK_OPS = "Network Operations"
    BILLING = "Billing Support"

# Add validators when needed
@validator('ticket_id')
def validate_id(cls, v):
    if not v or not v.strip():
        raise ValueError("ID cannot be empty")
    return v.strip()
```


## Tool Implementation Pattern

```python
def classify_issue(ticket_text: str) -> IssueClassification:
    """Classify ticket using keyword matching"""
    text_lower = ticket_text.lower()
    patterns = {
        'Network Outage': ['outage', 'down', 'offline'],
        'Billing Dispute': ['bill', 'charge', 'invoice'],
        'Technical Problem': ['error', 'not working', 'broken'],
        'Account Access': ['password', 'login', 'access']
    }
    
    scores = {cat: sum(1 for kw in kws if kw in text_lower) / len(kws) 
              for cat, kws in patterns.items()}
    
    best_category = max(scores, key=scores.get) if scores else 'Technical Problem'
    
    return IssueClassification(
        primary_category=best_category,
        confidence=scores.get(best_category, 0.5),
        keywords=[kw for kw in patterns[best_category] if kw in text_lower]
    )
```


## Error Handling

Always provide graceful fallbacks:

```python
def _fallback_decision(self, ticket: Ticket, error: str) -> FinalDecision:
    """Provide fallback decision when agent fails"""
    return FinalDecision(
        ticket_id=ticket.ticket_id,
        customer_id=ticket.customer_id,
        assigned_team=Team.TECHNICAL,
        priority_level=PriorityLevel.P2,
        confidence_score=50.0,
        reasoning=f"Fallback routing due to error: {error}",
        processing_time_ms=0,
        requires_manual_review=True
    )

try:
    result = self.agent.run(ticket_prompt)
    decision = self._parse_decision(result, ticket)
except Exception as e:
    decision = self._fallback_decision(ticket, str(e))
```


## Testing Requirements

All tests MUST be in the `tests/` folder:

```python
# tests/test_tools.py
def test_classify_issue():
    result = classify_issue("My internet is down and offline")
    assert result.primary_category == "Network Outage"
    assert result.confidence > 0.5

def test_extract_entities():
    text = "Account ACC-12345 has error NET-500 on service SVC001"
    result = extract_entities(text)
    assert "ACC-12345" in result.account_numbers
    assert "SVC001" in result.service_ids

# tests/test_integration.py
def test_end_to_end():
    agent = TicketRoutingAgent()
    ticket = Ticket(
        ticket_id="TKT-TEST",
        customer_id="CUST001",
        subject="Internet down",
        description="My internet has been down for 2 hours",
        timestamp=datetime.utcnow()
    )
    decision = agent.process_ticket(ticket)
    assert decision.assigned_team in Team
    assert 0 <= decision.confidence_score <= 100
```


## Documentation Requirements

All documentation MUST be in the `docs/` folder:

- `docs/README.md` - Main documentation with setup instructions
- `docs/setup.md` - Detailed setup and configuration guide
- `docs/api.md` - API documentation for tools and models

## CHANGELOG.md Requirements

MUST maintain a CHANGELOG.md in the root directory:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.1.0] - 2024-02-14

### Added
- Initial MVP implementation
- 7 agent tools with Pydantic models
- Strands agent integration with Bedrock
- Mock data for testing
- CLI interface with formatted output
- JSON results export

### Changed
- N/A

### Fixed
- N/A
```

Update CHANGELOG.md whenever you:
- Add new features
- Fix bugs
- Change behavior
- Update dependencies
- Modify configuration


## Common Pitfalls

1. **Don't over-engineer** - Keep tools simple with keyword matching
2. **Don't skip validation** - Always use Pydantic models
3. **Don't ignore errors** - Provide fallback decisions
4. **Don't hardcode values** - Use config and enums
5. **Don't forget to update CHANGELOG.md** - Document all changes
6. **Don't put tests in src/** - Tests go in tests/ folder
7. **Don't put docs in root** - Documentation goes in docs/ folder

## Quick Reference

### Regex Patterns
```python
r'ACC-\d+'              # Account numbers: ACC-12345
r'SVC\d+'               # Service IDs: SVC001
r'[A-Z]+-\d+'           # Error codes: NET-500
r'\d{3}-\d{3}-\d{4}'    # Phone: 555-123-4567
r'\$(\d+(?:\.\d{2})?)'  # Money: $15.99
```

### Pydantic Serialization
```python
obj.model_dump()              # To dict
obj.model_dump_json(indent=2) # To JSON string
[d.model_dump() for d in list] # List to dicts
```

### Agent Configuration
```python
agent = Agent(
    name="TicketRoutingAgent",
    model="bedrock/anthropic.claude-sonnet-4-5-v2",
    system_prompt="You are...",
    tools=[tool1, tool2],
    temperature=0.1,
    max_tokens=4096
)
```

## Success Checklist

- [ ] All models use Pydantic BaseModel
- [ ] All tests in tests/ folder
- [ ] All docs in docs/ folder
- [ ] CHANGELOG.md exists and is updated
- [ ] Tools return Pydantic models
- [ ] Error handling with fallbacks
- [ ] Processing time < 5 seconds per ticket
- [ ] Results saved to JSON
- [ ] Console output is formatted
- [ ] Mock data covers all scenarios












## Testing Guidelines





## Common Pitfalls to Avoid

### 1. Don't Over-Engineer

```python
# BAD - Too complex for MVP
class AdvancedMLClassifier:
    def __init__(self):
        self.model = self.load_pretrained_model()
        self.vectorizer = TfidfVectorizer()
    
    def classify(self, text):
        # 100 lines of ML code...

# GOOD - Simple and effective for MVP
def classify_issue(ticket_text: str) -> IssueClassification:
    # Simple keyword matching
    patterns = {...}
    # 20 lines of straightforward logic
```

### 2. Don't Skip Pydantic Validation

```python
# BAD - No validation
def process_ticket(ticket_dict: dict):
    ticket_id = ticket_dict['ticket_id']  # KeyError if missing!
    
# GOOD - Pydantic validates automatically
def process_ticket(ticket: Ticket):
    ticket_id = ticket.ticket_id  # Guaranteed to exist
```

### 3. Don't Ignore Error Cases

```python
# BAD - Crashes on error
result = self.agent.run(prompt)
decision = parse_decision(result)

# GOOD - Handles errors gracefully
try:
    result = self.agent.run(prompt)
    decision = parse_decision(result)
except Exception as e:
    decision = self._fallback_decision(ticket, str(e))
```

### 4. Don't Hardcode Values

```python
# BAD - Magic numbers everywhere
if score >= 80:
    priority = "P0"

# GOOD - Use configuration and enums
if score >= PRIORITY_THRESHOLDS['P0']:
    priority = PriorityLevel.P0
```












## Quick Reference

### Pydantic Model Cheat Sheet

```python
# Define model
class MyModel(BaseModel):
    field: str = Field(..., description="Required field")
    optional: Optional[int] = Field(None, description="Optional field")
    validated: float = Field(ge=0, le=100, description="0-100 range")

# Create instance
obj = MyModel(field="value", validated=50.0)

# Access fields
print(obj.field)

# Convert to dict
data = obj.model_dump()

# Convert to JSON
json_str = obj.model_dump_json(indent=2)

# Parse from dict
obj = MyModel(**data)

# Validate
try:
    obj = MyModel(**data)
except ValidationError as e:
    print(e.errors())
```

### Strands Agent Cheat Sheet

```python
# Initialize agent
agent = Agent(
    name="MyAgent",
    model="bedrock/anthropic.claude-sonnet-4-5-v2",
    system_prompt="You are...",
    tools=[tool1, tool2],
    temperature=0.1,
    max_tokens=4096
)

# Run agent
result = agent.run("User prompt here")

# Access result
print(result)
```

### Common Regex Patterns

```python
# Account numbers: ACC-12345
r'ACC-\d+'

# Service IDs: SVC001
r'SVC\d+'

# Error codes: NET-500, AUTH-403
r'[A-Z]+-\d+'

# Phone numbers: 555-123-4567
r'\d{3}-\d{3}-\d{4}'

# Money: $15.99
r'\$(\d+(?:\.\d{2})?)'
```





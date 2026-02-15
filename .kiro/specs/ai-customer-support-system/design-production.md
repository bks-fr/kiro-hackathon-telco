# Design Document: AI-Powered Customer Support System - Production

## Overview

This document specifies the production design for an AI-powered ticket routing system deployed on AWS infrastructure. The system processes 1,000+ tickets per day with 99.9% uptime, achieving 90%+ routing accuracy while maintaining costs under $0.10 per ticket.

**Production Goal**: Deploy a scalable, reliable, and secure ticket routing system on AWS.

**Key Characteristics**:
- Event-driven architecture with AWS Lambda
- Real-time integration with external systems
- DynamoDB for persistent storage
- CloudWatch for comprehensive monitoring
- Auto-scaling for variable load
- 99.9% availability SLA

## Design Principles

1. **Event-Driven**: Asynchronous processing via EventBridge
2. **Serverless**: Lambda functions for compute, DynamoDB for storage
3. **Scalable**: Auto-scaling based on load
4. **Observable**: Comprehensive logging and metrics
5. **Resilient**: Retry logic, DLQ, and graceful degradation
6. **Secure**: Encryption, IAM roles, audit logging

## Production Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SYSTEMS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  Ticketing System API  │  Customer DB  │  Service Status API  │  VIP DB │
└────────┬────────────────┴───────┬───────┴──────────┬──────────┴─────┬───┘
         │                        │                  │                │
         │ Webhook/Poll           │ Query            │ Query          │ Query
         │                        │                  │                │
┌────────▼────────────────────────▼──────────────────▼────────────────▼───┐
│                          AWS CLOUD INFRASTRUCTURE                        │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────┐         ┌──────────────────────────────────┐       │
│  │  API Gateway   │────────▶│  Lambda: Ticket Ingestion        │       │
│  │  (REST API)    │         │  - Validate incoming tickets     │       │
│  └────────────────┘         │  - Enrich with customer data     │       │
│                             │  - Publish to EventBridge        │       │
│                             └──────────────┬───────────────────┘       │
│                                            │                            │
│                                            │ Event                      │
│                                            ▼                            │
│                             ┌──────────────────────────────────┐       │
│                             │  EventBridge Event Bus           │       │
│                             │  - Ticket routing events         │       │
│                             └──────────────┬───────────────────┘       │
│                                            │                            │
│                                            │ Trigger                    │
│                                            ▼                            │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │         Lambda: Strands Agent Orchestrator                      │  │
│  │  ┌───────────────────────────────────────────────────────────┐ │  │
│  │  │  STRANDS AGENT (Ticket Routing Agent)                     │ │  │
│  │  │                                                            │ │  │
│  │  │  ┌──────────────────────────────────────────────────┐    │ │  │
│  │  │  │  Amazon Bedrock (Claude Sonnet 4.5)              │    │ │  │
│  │  │  │  - Reasoning engine                              │    │ │  │
│  │  │  │  - Tool calling orchestration                    │    │ │  │
│  │  │  │  - Decision making                               │    │ │  │
│  │  │  └──────────────────────────────────────────────────┘    │ │  │
│  │  │                                                            │ │  │
│  │  │  Agent Tools:                                             │ │  │
│  │  │  ┌─────────────────────────────────────────────────┐    │ │  │
│  │  │  │ 1. classify_issue()                             │    │ │  │
│  │  │  │ 2. extract_entities()                           │    │ │  │
│  │  │  │ 3. check_vip_status()                           │    │ │  │
│  │  │  │ 4. check_service_status()                       │    │ │  │
│  │  │  │ 5. calculate_priority()                         │    │ │  │
│  │  │  │ 6. route_to_team()                              │    │ │  │
│  │  │  │ 7. get_historical_context()                     │    │ │  │
│  │  │  └─────────────────────────────────────────────────┘    │ │  │
│  │  └───────────────────────────────────────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                            │                            │
│                                            │ Store results              │
│                                            ▼                            │
│                             ┌──────────────────────────────────┐       │
│                             │  DynamoDB Tables                 │       │
│                             │  - Routing decisions             │       │
│                             │  - Ticket metadata               │       │
│                             │  - Performance metrics           │       │
│                             └──────────────────────────────────┘       │
│                                            │                            │
│                                            │ Update                     │
│                                            ▼                            │
│                             ┌──────────────────────────────────┐       │
│                             │  Lambda: Ticketing System Update │       │
│                             │  - Update ticket assignment      │       │
│                             │  - Add routing metadata          │       │
│                             │  - Retry logic with backoff      │       │
│                             └──────────────────────────────────┘       │
│                                            │                            │
└────────────────────────────────────────────┼────────────────────────────┘
                                             │ API Call
                                             ▼
                              ┌──────────────────────────────┐
                              │  Ticketing System            │
                              │  - Updated with routing      │
                              │  - Updated with priority     │
                              └──────────────────────────────┘
```

## Production Sequence Diagram

See the complete sequence diagram in the [main design document](./design.md#production-sequence-diagram) showing the full flow from ticket ingestion through Bedrock processing to ticketing system updates.

## AWS Components

### 1. API Gateway

**Purpose**: REST API endpoint for ticketing system integration

**Configuration**:
- Type: REST API
- Authentication: API Key
- Rate Limiting: 100 requests/second
- Request Validation: JSON schema
- Timeout: 29 seconds

**Endpoints**:
- `POST /tickets` - Submit new ticket for routing
- `GET /tickets/{id}` - Retrieve routing decision
- `GET /health` - Health check endpoint

**Integration**: Lambda proxy integration with Ticket Ingestion function

### 2. Lambda: Ticket Ingestion

**Purpose**: Validate, enrich, and publish tickets to event bus

**Configuration**:
- Runtime: Python 3.11
- Memory: 512 MB
- Timeout: 10 seconds
- Concurrency: 100
- Reserved Concurrency: 10 (prevent throttling)

**Environment Variables**:
- `CUSTOMER_DB_ENDPOINT` - Customer database API endpoint
- `EVENTBRIDGE_BUS_NAME` - EventBridge bus name
- `LOG_LEVEL` - Logging level (INFO, DEBUG)

**IAM Permissions**:
- `events:PutEvents` - Publish to EventBridge
- `dynamodb:GetItem` - Query customer data (if using DynamoDB)
- `secretsmanager:GetSecretValue` - Retrieve API credentials

**Logic**:
1. Validate ticket schema (required fields)
2. Query customer database for VIP status
3. Generate correlation ID
4. Publish enriched ticket to EventBridge
5. Return 202 Accepted

### 3. EventBridge Event Bus

**Purpose**: Decouple ingestion from processing

**Configuration**:
- Bus Name: `ticket-routing-bus`
- Event Pattern: Match `TicketReceived` events
- Archive: 7-day retention for replay
- Dead Letter Queue: SQS for failed deliveries

**Event Schema**:
```json
{
  "detail-type": "TicketReceived",
  "source": "support.ticketing",
  "detail": {
    "ticket_id": "string",
    "customer_id": "string",
    "subject": "string",
    "description": "string",
    "timestamp": "ISO8601",
    "correlation_id": "string",
    "customer_context": {
      "is_vip": "boolean",
      "account_type": "string"
    }
  }
}
```

### 4. Lambda: Agent Orchestrator

**Purpose**: Execute Strands agent for ticket routing

**Configuration**:
- Runtime: Python 3.11
- Memory: 2048 MB (for Strands framework)
- Timeout: 30 seconds
- Concurrency: 50 (Bedrock rate limits)
- Reserved Concurrency: 20

**Environment Variables**:
- `BEDROCK_MODEL_ID` - anthropic.claude-sonnet-4-5-v2
- `BEDROCK_REGION` - us-east-1
- `ROUTING_DECISIONS_TABLE` - DynamoDB table name
- `CUSTOMER_DB_ENDPOINT` - Customer database endpoint
- `SERVICE_STATUS_ENDPOINT` - Service status API endpoint

**IAM Permissions**:
- `bedrock:InvokeModel` - Call Bedrock API
- `dynamodb:PutItem` - Store routing decisions
- `dynamodb:Query` - Retrieve historical tickets
- `secretsmanager:GetSecretValue` - API credentials
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` - CloudWatch logging

**Dependencies**:
- strands-agents
- boto3
- Custom tool implementations

**Logic**:
1. Initialize Strands agent with Bedrock client
2. Load ticket data from EventBridge event
3. Execute agent with 7 tools
4. Parse agent's routing decision
5. Store decision in DynamoDB
6. Log metrics to CloudWatch

### 5. DynamoDB: Routing Decisions Table

**Purpose**: Store routing decisions for audit and analytics

**Table Schema**:
```python
{
  "ticket_id": "string (partition key)",
  "timestamp": "number (sort key, Unix timestamp)",
  "customer_id": "string (GSI partition key)",
  "assigned_team": "string",
  "priority_level": "string",
  "confidence_score": "number",
  "issue_classification": "map",
  "reasoning": "string",
  "requires_manual_review": "boolean",
  "processing_time_ms": "number",
  "tool_calls": "list",
  "correlation_id": "string",
  "sync_status": "string",  // pending, success, failed
  "created_at": "string (ISO8601)",
  "ttl": "number (Unix timestamp)"
}
```

**Configuration**:
- Billing Mode: On-demand
- Point-in-time Recovery: Enabled
- TTL: 90 days (compliance requirement)
- Stream: Enabled (for triggering update Lambda)

**Global Secondary Indexes**:
- `customer_id-timestamp-index` - Query tickets by customer
- `assigned_team-timestamp-index` - Query tickets by team
- `sync_status-timestamp-index` - Query failed syncs

### 6. Lambda: Ticketing System Update

**Purpose**: Update external ticketing system with routing decisions

**Configuration**:
- Runtime: Python 3.11
- Memory: 512 MB
- Timeout: 30 seconds
- Concurrency: 20
- Retry: 3 attempts with exponential backoff
- Dead Letter Queue: SQS for failed updates

**Trigger**: DynamoDB Stream from Routing Decisions table

**Environment Variables**:
- `TICKETING_SYSTEM_ENDPOINT` - External API endpoint
- `TICKETING_SYSTEM_API_KEY_SECRET` - Secrets Manager ARN
- `MAX_RETRIES` - 3
- `RETRY_DELAY_BASE` - 1 second

**IAM Permissions**:
- `dynamodb:UpdateItem` - Update sync status
- `secretsmanager:GetSecretValue` - API credentials
- `sqs:SendMessage` - Send to DLQ on failure

**Logic**:
1. Receive routing decision from DynamoDB stream
2. Format update payload for ticketing system
3. Call ticketing system API with retry logic
4. Update DynamoDB sync status
5. Send to DLQ if all retries fail

**Retry Strategy**:
```python
def exponential_backoff(attempt):
    return min(2 ** attempt, 16)  # Max 16 seconds

# Retry delays: 1s, 2s, 4s, 8s, 16s
```

### 7. CloudWatch

**Purpose**: Monitoring, logging, and alerting

**Log Groups**:
- `/aws/lambda/ticket-ingestion`
- `/aws/lambda/agent-orchestrator`
- `/aws/lambda/ticketing-system-update`
- `/aws/apigateway/ticket-routing-api`

**Metrics**:
- `TicketsProcessed` - Count of tickets processed
- `ProcessingTime` - Duration of agent execution
- `ConfidenceScore` - Average confidence score
- `RoutingAccuracy` - Percentage of correct routings
- `ManualReviewRate` - Percentage requiring manual review
- `TicketingSystemSyncFailures` - Count of failed updates
- `BedrockAPIErrors` - Count of Bedrock failures

**Alarms**:
- `HighErrorRate` - Error rate > 5% for 5 minutes
- `LowConfidence` - Average confidence < 60% for 15 minutes
- `HighLatency` - Processing time > 5 seconds for 10 minutes
- `SyncFailures` - > 10 failed syncs in 5 minutes
- `BedrockThrottling` - Bedrock throttling errors

**Dashboard**:
- Real-time ticket processing rate
- Average processing time trend
- Confidence score distribution
- Team distribution pie chart
- Priority distribution bar chart
- Error rate timeline
- Cost per ticket estimate

## Agent Tool Implementations (Production)

### Tool 1: classify_issue()

**Implementation**: ML classification model or AI-powered

**Options**:
1. **SageMaker Endpoint**: Fine-tuned BERT model on historical tickets
2. **Bedrock Agent**: Specialized Claude Haiku agent
3. **Comprehend**: AWS Comprehend custom classifier

**Recommended**: Bedrock Agent (Claude Haiku) for flexibility

```python
def classify_issue(ticket_text: str) -> Dict[str, Any]:
    """Classify using specialized Bedrock agent"""
    response = bedrock.converse(
        modelId='anthropic.claude-3-haiku-20240307',
        messages=[{
            'role': 'user',
            'content': [{
                'text': f'Classify this telecom ticket: {ticket_text}'
            }]
        }],
        inferenceConfig={'temperature': 0.1, 'maxTokens': 500}
    )
    return parse_classification(response)
```

### Tool 2: extract_entities()

**Implementation**: NER + regex patterns

```python
def extract_entities(ticket_text: str) -> Dict[str, List[str]]:
    """Extract entities using Comprehend + regex"""
    # Use AWS Comprehend for NER
    comprehend = boto3.client('comprehend')
    entities = comprehend.detect_entities(
        Text=ticket_text,
        LanguageCode='en'
    )
    
    # Combine with regex for telecom-specific patterns
    return {
        'account_numbers': re.findall(r'ACC-\d+', ticket_text),
        'service_ids': re.findall(r'SVC\d+', ticket_text),
        'error_codes': re.findall(r'[A-Z]+-\d+', ticket_text),
        'phone_numbers': [e['Text'] for e in entities['Entities'] 
                         if e['Type'] == 'PHONE_NUMBER'],
        'monetary_amounts': [float(e['Text'].replace('$', '')) 
                            for e in entities['Entities'] 
                            if e['Type'] == 'QUANTITY']
    }
```

### Tool 3: check_vip_status()

**Implementation**: DynamoDB or external API

```python
def check_vip_status(customer_id: str) -> Dict[str, Any]:
    """Query customer database"""
    # Option 1: DynamoDB cache
    table = dynamodb.Table('customer-data')
    response = table.get_item(Key={'customer_id': customer_id})
    
    if 'Item' in response:
        return response['Item']
    
    # Option 2: External API with caching
    customer_data = requests.get(
        f'{CUSTOMER_DB_ENDPOINT}/customers/{customer_id}',
        headers={'Authorization': f'Bearer {api_key}'}
    ).json()
    
    # Cache in DynamoDB for future lookups
    table.put_item(Item=customer_data)
    
    return customer_data
```

### Tool 4: check_service_status()

**Implementation**: Real-time API integration

```python
def check_service_status(service_ids: List[str]) -> Dict[str, Any]:
    """Query service status API"""
    response = requests.post(
        f'{SERVICE_STATUS_ENDPOINT}/status/batch',
        json={'service_ids': service_ids},
        headers={'Authorization': f'Bearer {api_key}'}
    )
    
    status_data = response.json()
    
    return {
        'active_outages': status_data.get('outages', []),
        'known_issues': status_data.get('known_issues', []),
        'service_health': status_data.get('overall_health', 'Healthy')
    }
```

### Tool 5: calculate_priority()

**Implementation**: Same weighted scoring as MVP

(See MVP design for algorithm details)

### Tool 6: route_to_team()

**Implementation**: Enhanced with ML or rule-based

**Options**:
1. **Rule-based**: Enhanced version of MVP logic
2. **ML Model**: SageMaker endpoint trained on historical routings
3. **Hybrid**: Rules + ML confidence boosting

### Tool 7: get_historical_context()

**Implementation**: DynamoDB query

```python
def get_historical_context(customer_id: str, limit: int = 5) -> Dict[str, Any]:
    """Query DynamoDB for historical tickets"""
    table = dynamodb.Table('routing-decisions')
    
    response = table.query(
        IndexName='customer_id-timestamp-index',
        KeyConditionExpression='customer_id = :cid',
        ExpressionAttributeValues={':cid': customer_id},
        ScanIndexForward=False,  # Descending order
        Limit=limit
    )
    
    tickets = response['Items']
    
    return {
        'recent_tickets': tickets,
        'common_issues': list(set(t['issue_classification']['primary_category'] 
                                 for t in tickets)),
        'escalation_history': any(t.get('requires_manual_review') for t in tickets)
    }
```

## Deployment Strategy

### Infrastructure as Code

**Tool**: AWS CDK (Python)

**Stack Structure**:
```
ticket-routing-system/
├── infrastructure/
│   ├── app.py                    # CDK app entry point
│   ├── stacks/
│   │   ├── api_stack.py          # API Gateway
│   │   ├── ingestion_stack.py    # Ingestion Lambda
│   │   ├── eventbridge_stack.py  # Event bus
│   │   ├── agent_stack.py        # Agent Lambda
│   │   ├── storage_stack.py      # DynamoDB tables
│   │   ├── update_stack.py       # Update Lambda
│   │   └── monitoring_stack.py   # CloudWatch
│   └── requirements.txt
└── src/
    ├── ingestion/
    ├── agent/
    └── update/
```

### Deployment Pipeline

**Stages**:
1. **Build**: Package Lambda functions
2. **Test**: Run unit and integration tests
3. **Deploy Dev**: Deploy to dev environment
4. **Integration Test**: Run end-to-end tests
5. **Deploy Staging**: Deploy to staging
6. **Smoke Test**: Validate staging deployment
7. **Deploy Production**: Blue-green deployment
8. **Monitor**: Watch metrics for 1 hour

### Blue-Green Deployment

**Strategy**:
1. Deploy new version to "green" environment
2. Route 10% of traffic to green
3. Monitor metrics for 15 minutes
4. If successful, route 50% of traffic
5. Monitor for 15 minutes
6. Route 100% of traffic to green
7. Keep blue environment for 24 hours (rollback capability)

## Monitoring and Alerting

### Key Metrics

**Performance Metrics**:
- Processing time (p50, p95, p99)
- Throughput (tickets/minute)
- Error rate (%)
- Bedrock API latency

**Business Metrics**:
- Routing accuracy (%)
- Confidence score distribution
- Manual review rate (%)
- Team distribution

**Cost Metrics**:
- Cost per ticket
- Daily AWS spend
- Bedrock API costs

### Alerting Strategy

**Critical Alerts** (PagerDuty):
- Error rate > 10% for 5 minutes
- Processing time > 10 seconds for 5 minutes
- Bedrock API failures > 50% for 2 minutes
- Ticketing system sync failures > 20 in 5 minutes

**Warning Alerts** (Email):
- Error rate > 5% for 10 minutes
- Average confidence < 70% for 30 minutes
- Manual review rate > 30% for 1 hour
- Daily cost > $350

**Info Alerts** (Slack):
- New deployment completed
- Daily summary report
- Weekly accuracy report

## Security

### Data Encryption

**In Transit**:
- TLS 1.2+ for all API calls
- Certificate validation enabled
- No plaintext transmission

**At Rest**:
- DynamoDB encryption with AWS KMS
- S3 encryption (if used for logs)
- Secrets Manager for credentials

### Access Control

**IAM Roles**:
- `TicketIngestionRole` - Minimal permissions for ingestion
- `AgentOrchestratorRole` - Bedrock + DynamoDB access
- `TicketingSystemUpdateRole` - External API access only

**Principle of Least Privilege**: Each Lambda has only required permissions

### Audit Logging

**CloudTrail**: All API calls logged
**CloudWatch Logs**: All Lambda executions logged
**DynamoDB**: All routing decisions stored with correlation IDs

## Cost Optimization

### Cost Breakdown (1,000 tickets/day)

**Bedrock API**: $180/month
- 1,000 tickets × 30 days × $0.006/ticket

**Lambda**: $50/month
- Ingestion: 1M requests × $0.20/1M = $0.20
- Agent: 1M requests × $0.20/1M = $0.20
- Compute: 30K GB-seconds × $0.0000166667 = $0.50

**DynamoDB**: $25/month
- On-demand pricing for 30K writes, 100K reads

**API Gateway**: $10/month
- 30K requests × $3.50/1M = $0.11

**CloudWatch**: $15/month
- Logs and metrics

**Total**: ~$280/month = $0.09/ticket ✅ (under $0.10 target)

### Optimization Strategies

1. **Cache Customer Data**: Reduce DynamoDB reads
2. **Batch Processing**: Process multiple tickets in single Lambda invocation
3. **Reserved Concurrency**: Prevent over-provisioning
4. **Log Retention**: 7 days for debug logs, 90 days for audit
5. **Bedrock Model Selection**: Use Haiku for specialized tasks

## Testing Strategy

### Unit Tests
- Test each tool independently
- Mock external API calls
- Validate data transformations

### Integration Tests
- Test Lambda functions with test events
- Validate DynamoDB operations
- Test EventBridge event flow

### End-to-End Tests
- Submit test tickets via API Gateway
- Verify routing decisions in DynamoDB
- Validate ticketing system updates

### Load Tests
- Simulate 2,000 tickets/day
- Measure processing time under load
- Validate auto-scaling behavior

### Chaos Engineering
- Simulate Bedrock API failures
- Test DynamoDB throttling scenarios
- Validate retry and DLQ behavior

## Migration from MVP

**Step 1**: Package MVP code as Lambda functions
**Step 2**: Deploy infrastructure with CDK
**Step 3**: Replace mock tools with real implementations
**Step 4**: Deploy to dev environment
**Step 5**: Run integration tests
**Step 6**: Deploy to staging
**Step 7**: Run load tests
**Step 8**: Deploy to production with 10% traffic
**Step 9**: Monitor and gradually increase traffic
**Step 10**: Decommission MVP

## Related Documents

- [Production Requirements](./requirements-production.md)
- [MVP Design](../ai-customer-support-system-mvp/design.md)
- [Implementation Guide](../../steering/ai-customer-support-implementation.md)

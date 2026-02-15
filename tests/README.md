# Test Suite Documentation

This directory contains the test suite for the AI-Powered Customer Support System MVP.

## Test Files

### Unit Tests (No API Calls)

1. **test_tools.py** - Unit tests for all 7 agent tools
   - 60 tests covering classify_issue, extract_entities, check_vip_status, check_service_status, calculate_priority, route_to_team, get_historical_context
   - Tests use mock data and Pydantic validation
   - No external API calls

2. **test_agent.py** - Unit tests for TicketRoutingAgent
   - 18 tests covering agent initialization, process_ticket(), _parse_decision(), _fallback_decision()
   - Uses unittest.mock to avoid Bedrock API calls
   - Tests Pydantic validation and error handling

### Integration Tests (Real API Calls)

3. **test_agent_integration.py** - Integration tests with real Bedrock API
   - 10 tests using actual AWS Bedrock API calls
   - Tests end-to-end ticket routing with real AI reasoning
   - Marked with @pytest.mark.integration
   - **Requires AWS credentials configured**
   - **Incurs AWS Bedrock costs** (~$0.006 per ticket)

## Running Tests

### Run All Unit Tests (No API Calls)

```bash
# Run all unit tests (excludes integration tests by default)
pytest -m "not integration" -v

# Or simply
pytest -v
```

### Run Specific Test Files

```bash
# Run only tool tests
pytest tests/test_tools.py -v

# Run only agent unit tests
pytest tests/test_agent.py -v
```

### Run Integration Tests (Requires AWS Credentials)

```bash
# Run only integration tests
pytest -m integration -v

# Run integration tests with output
pytest -m integration -v -s
```

### Run All Tests (Unit + Integration)

```bash
# Run everything
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html -v
```

## AWS Credentials Setup for Integration Tests

Integration tests require AWS credentials with Bedrock access.

### Option 1: AWS CLI Configuration

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., eu-central-1)
- Default output format (json)

### Option 2: Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=eu-central-1
```

### Option 3: AWS Profile

```bash
export AWS_PROFILE=your_profile_name
```

### Verify Credentials

```bash
aws sts get-caller-identity
```

## Integration Test Behavior

- **Automatic Skip**: Integration tests automatically skip if AWS credentials are not configured
- **Real API Calls**: Tests make actual calls to AWS Bedrock (Claude Sonnet 4.5)
- **Cost**: Approximately $0.006 per ticket processed (~$0.06 for full suite)
- **Performance**: Each test verifies processing time < 5 seconds

## Test Coverage

### Unit Tests Coverage

- **test_tools.py**: 60 tests
  - TestClassifyIssue: 7 tests
  - TestExtractEntities: 8 tests
  - TestCheckVipStatus: 5 tests
  - TestCheckServiceStatus: 8 tests
  - TestCalculatePriority: 7 tests
  - TestRouteToTeam: 7 tests
  - TestGetHistoricalContext: 6 tests
  - TestPydanticValidation: 8 tests
  - TestToolIntegration: 4 tests

- **test_agent.py**: 18 tests
  - TestTicketRoutingAgentInit: 3 tests
  - TestProcessTicket: 3 tests
  - TestParseDecision: 6 tests
  - TestFallbackDecision: 2 tests
  - TestAgentPydanticValidation: 2 tests
  - TestAgentIntegration: 2 tests

### Integration Tests Coverage

- **test_agent_integration.py**: 10 tests
  - TestAgentIntegrationWithBedrock: 8 tests
    - VIP customer network outage routing
    - Standard customer billing dispute routing
    - Technical problem routing
    - Account access routing
    - Processing time performance
    - Confidence score variation
    - Reasoning quality
    - Sample tickets distribution
  - TestIntegrationConfiguration: 2 tests

**Total**: 88 tests (78 unit + 10 integration)

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.integration` - Integration tests that use real Bedrock API

### Using Markers

```bash
# Run only integration tests
pytest -m integration

# Run everything except integration tests
pytest -m "not integration"

# List all available markers
pytest --markers
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Run only unit tests (no AWS credentials needed)
pytest -m "not integration" -v --junitxml=test-results.xml

# Run integration tests only if AWS credentials are available
pytest -m integration -v --junitxml=integration-results.xml
```

## Troubleshooting

### Integration Tests Skip

If integration tests are skipped:

```
SKIPPED [1] tests/test_agent_integration.py: AWS credentials not configured
```

**Solution**: Configure AWS credentials using one of the methods above.

### Bedrock Access Denied

If you get access denied errors:

```
botocore.exceptions.ClientError: An error occurred (AccessDeniedException)
```

**Solution**: 
1. Ensure Bedrock is enabled in your AWS account
2. Verify your IAM user/role has `bedrock:InvokeModel` permission
3. Check that Claude Sonnet 4.5 is available in your region

### Model Not Found

If you get model not found errors:

```
botocore.exceptions.ClientError: An error occurred (ResourceNotFoundException)
```

**Solution**: 
1. Verify the model ID in `src/config.py` matches your region
2. Check model availability: `aws bedrock list-foundation-models --region eu-central-1`
3. Request model access in AWS Bedrock console if needed

## Best Practices

1. **Run unit tests frequently** during development (fast, no costs)
2. **Run integration tests before commits** to validate end-to-end behavior
3. **Monitor AWS costs** when running integration tests repeatedly
4. **Use mocking for development** to avoid API costs during rapid iteration
5. **Keep integration tests focused** on critical end-to-end scenarios

## Test Maintenance

When adding new features:

1. Add unit tests to `test_tools.py` or `test_agent.py`
2. Add integration tests to `test_agent_integration.py` only for critical paths
3. Update this README if adding new test files or markers
4. Update CHANGELOG.md with test additions

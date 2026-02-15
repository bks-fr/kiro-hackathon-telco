# Implementation Plan: AI-Powered Customer Support System - MVP

## Overview

This implementation plan creates a local Python application that demonstrates intelligent ticket routing using AWS Bedrock and the Strands Agent Framework. The MVP uses mock data for external systems and real AI reasoning via Amazon Bedrock (Claude Sonnet 4.5).

**Goal**: Complete a working MVP in 2-4 hours that processes sample tickets and demonstrates AI-powered routing decisions.

**Key Technologies**: Python 3.9+, AWS Bedrock, Strands Agent Framework, boto3

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create project directory structure (config.py, models.py, mock_data.py, tools.py, agent.py, main.py)
  - Create requirements.txt with dependencies (strands-agents, boto3, python-dotenv, pydantic)
  - Create .env.example with AWS configuration template
  - Create .gitignore for Python project
  - Create README.md with setup instructions
  - _Requirements: 1.1, 1.2_

- [x] 2. Implement configuration and data models
  - [x] 2.1 Create config.py with Bedrock settings
    - Define BEDROCK_REGION and BEDROCK_MODEL_ID constants
    - Define AGENT_CONFIG dictionary (temperature, max_tokens, max_iterations, timeout)
    - Define CONFIDENCE_THRESHOLD constant
    - Import enums from models.py for TEAMS and PRIORITY_LEVELS
    - _Requirements: 7.1, 7.2_
  
  - [x] 2.2 Create models.py with all Pydantic data models
    - Define enums: PriorityLevel, Team, AccountType, ServiceHealth
    - Create Ticket model with field validation
    - Create Customer model with VIP and account information
    - Create Outage and ServiceStatus models
    - Create IssueClassification and ExtractedEntities models
    - Create PriorityCalculation and RoutingDecision models
    - Create HistoricalTicket and HistoricalContext models
    - Create FinalDecision model for complete routing results
    - Add validators for required fields (ticket_id, customer_id validation)
    - _Requirements: 7.1, 7.2_

- [x] 3. Create mock data module with Pydantic models
  - [x] 3.1 Implement mock_data.py with sample data using Pydantic models
    - Import all models from models.py
    - Create MOCK_CUSTOMERS dictionary with Customer Pydantic models (5-10 customers, VIP and non-VIP examples)
    - Create MOCK_SERVICE_STATUS dictionary with ServiceStatus Pydantic models (healthy and outage scenarios)
    - Create MOCK_HISTORY dictionary with HistoricalTicket Pydantic models
    - Create SAMPLE_TICKETS list with Ticket Pydantic models (10-20 diverse tickets covering all issue types)
    - Ensure all datetime fields use proper datetime objects
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. Implement agent tools with Pydantic models
  - [x] 4.1 Create tools.py and implement classify_issue() tool
    - Import IssueClassification model from models.py
    - Implement keyword-based classification logic with pattern matching
    - Return IssueClassification Pydantic model with primary_category, confidence, keywords, secondary_categories
    - Support four categories: Network Outage, Billing Dispute, Technical Problem, Account Access
    - _Requirements: 4.1, 4.2, 6.1_
  
  - [x] 4.2 Implement extract_entities() tool
    - Import ExtractedEntities model from models.py
    - Use regex patterns to extract account numbers (ACC-\d+)
    - Extract service IDs (SVC\d+), error codes ([A-Z]+-\d+)
    - Extract phone numbers and monetary amounts
    - Return ExtractedEntities Pydantic model with all extracted entities
    - _Requirements: 6.1_
  
  - [x] 4.3 Implement check_vip_status() tool
    - Import Customer model from models.py
    - Look up customer in MOCK_CUSTOMERS dictionary
    - Return Customer Pydantic model including is_vip, account_type, lifetime_value
    - Provide default Customer model for unknown customers
    - _Requirements: 5.3, 6.1_
  
  - [x] 4.4 Implement check_service_status() tool
    - Import ServiceStatus, ServiceHealth, Outage models from models.py
    - Look up service IDs in MOCK_SERVICE_STATUS
    - Aggregate active outages across all service IDs
    - Determine worst service health status
    - Return ServiceStatus Pydantic model with active_outages and service_health
    - _Requirements: 5.4, 6.1_
  
  - [x] 4.5 Implement calculate_priority() tool
    - Import PriorityCalculation, PriorityLevel, Customer, IssueClassification, ServiceStatus models
    - Accept Pydantic models as parameters
    - Implement weighted scoring algorithm (VIP 30%, severity 40%, age 20%, outage 10%)
    - Map scores to PriorityLevel enum (P0: ≥80, P1: ≥60, P2: ≥40, P3: <40)
    - Return PriorityCalculation Pydantic model with priority_level, priority_score, factors, reasoning
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1_
  
  - [x] 4.6 Implement route_to_team() tool
    - Import RoutingDecision, Team, IssueClassification, ExtractedEntities, ServiceStatus models
    - Accept Pydantic models as parameters
    - Create routing_map for issue categories to Team enum values
    - Determine assigned team based on classification
    - Calculate confidence score and identify alternative teams
    - Flag for manual review if confidence < 0.7
    - Return RoutingDecision Pydantic model with assigned_team, confidence, alternative_teams, reasoning, requires_manual_review
    - _Requirements: 3.3, 3.5, 6.1_
  
  - [x] 4.7 Implement get_historical_context() tool
    - Import HistoricalContext, HistoricalTicket models from models.py
    - Look up customer history in MOCK_HISTORY
    - Return HistoricalContext Pydantic model with recent_tickets (limited by parameter)
    - Identify common issues and escalation history
    - _Requirements: 6.1_
  
  - [x] 4.8 Write unit tests for all tools with Pydantic validation
    - Test classify_issue returns IssueClassification model with various ticket texts
    - Test extract_entities returns ExtractedEntities model with different entity patterns
    - Test check_vip_status returns Customer model with known and unknown customers
    - Test check_service_status returns ServiceStatus model with healthy and outage scenarios
    - Test calculate_priority returns PriorityCalculation model with different factor combinations
    - Test route_to_team returns RoutingDecision model with all issue categories
    - Test get_historical_context returns HistoricalContext model with various customer IDs
    - Test Pydantic validation catches invalid data (empty IDs, invalid enums)
    - _Requirements: 6.2, 6.3_

- [x] 5. Checkpoint - Verify all tools work independently
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement agent module with Pydantic models
  - [x] 6.1 Create agent.py with TicketRoutingAgent class
    - Import Ticket, FinalDecision, Team, PriorityLevel models from models.py
    - Initialize boto3 Bedrock client with region configuration
    - Define comprehensive system prompt for ticket routing
    - Initialize Strands Agent with model, system prompt, tools, and config
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [x] 6.2 Implement process_ticket() method
    - Accept Ticket Pydantic model as parameter
    - Format ticket data into agent prompt using Pydantic model fields
    - Execute agent.run() with ticket prompt
    - Parse agent result into FinalDecision Pydantic model
    - Track processing time and add to FinalDecision model
    - Handle exceptions with fallback decision logic
    - Return FinalDecision model with assigned_team, priority_level, confidence_score, reasoning, processing_time_ms
    - _Requirements: 3.1, 3.2, 3.4, 3.5, 7.4, 7.5_
  
  - [x] 6.3 Implement _parse_decision() helper method
    - Extract routing decision from agent result
    - Create and return FinalDecision Pydantic model
    - Validate decision structure using Pydantic validation
    - Ensure all required fields are present and properly typed
    - _Requirements: 3.5_
  
  - [x] 6.4 Implement _fallback_decision() helper method
    - Accept Ticket Pydantic model and error string
    - Provide basic routing when agent fails
    - Log error information
    - Return FinalDecision Pydantic model with safe defaults and requires_manual_review=True
    - _Requirements: 7.4, 7.5_
  
  - [x] 6.5 Write and run unit tests for agent module with mocked Bedrock
    - Create tests/test_agent.py with comprehensive test suite
    - Test agent initialization with Bedrock client and Strands agent setup
    - Test process_ticket() method with mocked agent responses
    - Test _parse_decision() helper with various response formats
    - Test _fallback_decision() helper with error scenarios
    - Test Pydantic validation for FinalDecision model
    - Use unittest.mock to avoid actual Bedrock API calls
    - Run tests with: pytest tests/test_agent.py -v
    - Verify all tests pass (18+ tests)
    - _Requirements: 6.2, 6.3_
  
  - [x] 6.6 Write and run integration tests using actual Bedrock API
    - Create tests/test_agent_integration.py for real Bedrock API tests
    - Mark tests with @pytest.mark.integration decorator
    - Test end-to-end ticket processing with real Bedrock calls
    - Test VIP customer ticket routing (expect P0/P1 priority)
    - Test standard customer ticket routing (expect reasonable priority based on context)
    - Verify agent makes reasonable routing decisions (team assignments may vary by model)
    - Verify processing time < 60 seconds per ticket (reasonable for AI processing)
    - Verify confidence scores are meaningful (not all 100% or 0%)
    - Verify agent provides clear reasoning for decisions
    - Add pytest.skip if AWS credentials not configured
    - Create pytest.ini with integration marker configuration
    - Create tests/README.md and RUN_INTEGRATION_TESTS.md documentation
    - Run integration tests with: pytest -m integration -v
    - Note: Different models (Sonnet vs Haiku) may route tickets differently - both can be valid
    - Document how to run integration tests separately
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 7.1, 7.3, 7.4, 7.5_

- [x] 7. Implement CLI interface with Pydantic models
  - [x] 7.1 Create main.py with ticket loading functionality
    - Import Ticket, FinalDecision models from models.py
    - Load sample tickets from mock_data.SAMPLE_TICKETS (already Pydantic models)
    - Support loading from JSON file and parsing into Ticket models (optional)
    - Validate ticket data structure using Pydantic validation
    - _Requirements: 1.2_
  
  - [x] 7.2 Implement agent initialization in main.py
    - Initialize TicketRoutingAgent
    - Handle initialization errors gracefully
    - Display initialization status to console
    - _Requirements: 1.1_
  
  - [x] 7.3 Implement ticket processing loop
    - Process Ticket Pydantic models sequentially
    - Display progress for each ticket
    - Track processing time per ticket
    - Collect all FinalDecision models for summary
    - _Requirements: 1.3, 3.1_
  
  - [x] 7.4 Implement results display
    - Format and display each FinalDecision model in console
    - Show ticket_id, subject, assigned_team (enum value), priority_level (enum value), confidence_score, reasoning
    - Display processing_time_ms for each ticket
    - _Requirements: 1.5, 8.1, 8.2_
  
  - [x] 7.5 Implement results saving with Pydantic serialization
    - Create results/ directory if it doesn't exist
    - Save all FinalDecision models to routing_decisions.json using model_dump()
    - Format JSON with proper indentation
    - Handle datetime serialization properly
    - _Requirements: 1.4, 8.3_
  
  - [x] 7.6 Implement summary statistics
    - Calculate total tickets processed from FinalDecision list
    - Calculate average processing_time_ms and confidence_score
    - Count tickets with requires_manual_review=True
    - Show team distribution using Team enum values
    - Show priority distribution using PriorityLevel enum values
    - Display formatted summary to console
    - _Requirements: 8.4, 8.5_
  
  - [x] 7.7 Write unit tests for CLI interface
    - Create tests/test_main.py for CLI testing
    - Test ticket loading from mock_data.SAMPLE_TICKETS
    - Test agent initialization and error handling
    - Test ticket processing loop with mocked agent
    - Test results display formatting
    - Test results saving to JSON file
    - Test summary statistics calculation
    - Use unittest.mock to avoid actual Bedrock calls
    - Run tests with: pytest tests/test_main.py -v
    - Verify all tests pass
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 7.8 Write integration tests for CLI end-to-end flow
    - Create tests/test_main_integration.py for end-to-end CLI testing
    - Mark tests with @pytest.mark.integration decorator
    - Test complete CLI flow with real Bedrock API calls
    - Test processing multiple sample tickets
    - Test JSON output file creation and format
    - Test summary statistics accuracy
    - Verify all FinalDecision models are properly serialized
    - Add pytest.skip if AWS credentials not configured
    - Run integration tests with: pytest -m integration tests/test_main_integration.py -v
    - Document expected behavior and outputs
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 8. Checkpoint - Test end-to-end flow
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Add error handling and validation
  - [x] 9.1 Add ticket data validation using Pydantic
    - Validate required fields using Pydantic validators (ticket_id, customer_id, subject, description)
    - Handle Pydantic ValidationError for missing or malformed ticket data
    - Log validation errors with details from Pydantic error messages
    - _Requirements: 1.2_
  
  - [x] 9.2 Add Bedrock error handling
    - Catch boto3 client errors
    - Handle rate limiting and throttling
    - Provide informative error messages
    - Use fallback FinalDecision models when Bedrock unavailable
    - _Requirements: 7.4, 7.5_
  
  - [x] 9.3 Add configuration validation
    - Validate AWS credentials are configured
    - Check Bedrock region availability
    - Verify required environment variables
    - _Requirements: 7.2_

- [x] 10. Create documentation
  - [x] 10.1 Write comprehensive README.md
    - Document setup instructions (virtual environment, dependencies including pydantic, AWS credentials)
    - Provide usage examples for CLI
    - Document configuration options
    - Explain Pydantic model structure and benefits (type safety, validation)
    - Include troubleshooting section
    - Add cost estimates and performance expectations
    - _Requirements: 1.1_
  
  - [x] 10.2 Create .env.example file
    - Document all required environment variables
    - Provide example values
    - Include comments explaining each variable
    - _Requirements: 7.2_

- [-] 11. Final testing and validation
  - [ ]* 11.1 Run full test suite with Pydantic validation
    - Execute all unit tests
    - Verify all tools return correct Pydantic models
    - Test Pydantic validation catches invalid data
    - Check error handling paths
    - _Requirements: 6.2, 6.3_
  
  - [x] 11.2 Process all sample tickets
    - Run main.py with all sample Ticket models
    - Verify processing time < 5 seconds per ticket
    - Check that tickets are distributed across all Team enum values
    - Verify PriorityLevel enum values vary appropriately
    - Confirm confidence scores are meaningful
    - Validate all FinalDecision models have required fields
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 11.3 Validate output files
    - Create results/tickets/ subdirectory for individual ticket outputs
    - For each processed ticket, create a separate JSON file: results/tickets/{ticket_id}.json
    - Each file should contain: original Ticket model data and FinalDecision model data
    - Check routing_decisions.json (summary file) is properly formatted
    - Verify all FinalDecision models serialize correctly in individual files
    - Confirm datetime fields are properly serialized
    - Verify all decisions include required fields with correct types
    - Confirm summary statistics are accurate
    - _Requirements: 8.3, 8.4, 8.5_

- [ ] 12. Final checkpoint - MVP complete
  - Ensure all tests pass, ask the user if questions arise.

## Optional Enhancements

These tasks are optional and can be implemented after the core MVP is complete:

- [x] 13. Implement multi-agent tools (Optional)
  - [x] 13.1 Create agent_tools.py module with Pydantic models
    - Import all relevant Pydantic models from models.py
    - Implement AI-powered classify_issue returning IssueClassification model using Claude Haiku
    - Implement AI-powered extract_entities returning ExtractedEntities model
    - Implement AI-powered route_to_team returning RoutingDecision model
    - Maintain same tool interfaces as mock tools (accept and return Pydantic models)
    - _Requirements: Enhancement 1.1, 1.2, 1.4_
  
  - [x] 13.2 Add configuration toggle
    - Add USE_AGENT_TOOLS flag to config.py
    - Modify agent.py to switch between mock and agent tools
    - _Requirements: Enhancement 1.3_
  
  - [x] 13.3 Update project documentation
    - Update docs/README.md with AI-powered tools feature
    - Document USE_AGENT_TOOLS configuration option
    - Add section explaining mock vs AI-powered tools differences
    - Document cost implications of using AI-powered tools
    - Add usage examples for both modes
    - Update troubleshooting section with AI tool error handling
    - _Requirements: Enhancement 1.3_
  
  - [x] 13.3.1 Write unit tests for AI-powered tools
    - Create tests/test_agent_tools.py for AI tool unit tests
    - Test classify_issue with mocked Strands agents (7 tests)
    - Test extract_entities with mocked Strands agents (5 tests)
    - Test route_to_team with mocked Strands agents (8 tests)
    - Test agent initialization and caching (4 tests)
    - Use unittest.mock to avoid actual Bedrock calls
    - Verify all tools return correct Pydantic models
    - Test error handling with graceful fallbacks
    - Run tests with: pytest tests/test_agent_tools.py -v
    - _Requirements: Enhancement 1.1, 1.2, 1.4, 6.2, 6.3_
  
  - [x] 13.3.2 Write integration tests for AI-powered tools
    - Create tests/test_agent_tools_integration.py for real Bedrock API tests
    - Mark tests with @pytest.mark.integration decorator
    - Test classify_issue with real AI reasoning (5 tests)
    - Test extract_entities with real AI extraction (6 tests)
    - Test route_to_team with real AI routing (6 tests)
    - Test end-to-end AI tools workflow (3 tests)
    - Verify AI provides meaningful results (confidence varies, reasoning is clear)
    - Verify processing time < 10 seconds per tool call
    - Add pytest.skip if AWS credentials not configured
    - Run integration tests with: pytest -m integration tests/test_agent_tools_integration.py -v
    - _Requirements: Enhancement 1.1, 1.2, 1.4, 6.2, 6.3_
  
  - [x] 13.4 Compare mock vs agent tools performance
    - Process a subset of 5 sample tickets with mock tools mode
    - Process the same 5 tickets with AI-powered tools mode
    - Track cost differences between modes
    - Compare accuracy and confidence scores
    - Measure processing time differences
    - Document findings in comparison report
    - _Requirements: Enhancement 1.5_

- [ ] 14. Implement Streamlit GUI (Optional)
  - [ ] 14.1 Create streamlit_app.py
    - Set up Streamlit page configuration
    - Create sidebar with configuration options
    - _Requirements: Enhancement 2.1_
  
  - [ ] 14.2 Implement single ticket processing UI
    - Add text inputs for ticket fields
    - Add process button
    - Display routing decision with formatting
    - _Requirements: Enhancement 2.2_
  
  - [ ] 14.3 Implement batch processing UI
    - Add file uploader for JSON files
    - Process all tickets from uploaded file
    - Display results in table format
    - _Requirements: Enhancement 2.3_
  
  - [ ] 14.4 Add visual analytics
    - Create pie chart for team distribution
    - Create bar chart for priority distribution
    - Create histogram for confidence scores
    - _Requirements: Enhancement 2.4_
  
  - [ ] 14.5 Add export functionality
    - Add download button for results JSON
    - Support CSV export option
    - _Requirements: Enhancement 2.5_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP completion
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and provide opportunities to ask questions
- The core MVP (tasks 1-12) should be completable in 2-4 hours
- Optional enhancements (tasks 13-14) add 2-4 additional hours
- All data models use Pydantic BaseModel for type safety, validation, and serialization
- All tools accept and return Pydantic models instead of dictionaries
- Pydantic provides automatic validation, better IDE support, and cleaner serialization
- All tools use mock data initially; multi-agent tools are an optional enhancement
- Focus on getting the core flow working before adding optional features

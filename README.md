# AI-Powered Customer Support System - MVP

An intelligent ticket routing system that uses AWS Bedrock and the Strands Agent Framework to automatically classify, prioritize, and route customer support tickets.

## Summary

This project demonstrates **AI-powered ticket routing** built using **Kiro's spec-driven development methodology**. It's a fully functional MVP that validates the agentic approach with real AWS Bedrock integration, comprehensive testing (88 tests), and dual tool modes (mock and AI-powered).

**Quick Facts**:
- 🤖 **AI-Powered**: Uses Claude Haiku 4.5 via AWS Bedrock for intelligent routing
- 📋 **Spec-Driven**: Built from formal specifications (requirements → design → tasks)
- ✅ **Complete MVP**: 13 Pydantic models, 7 tools, comprehensive error handling
- 🧪 **Well-Tested**: 88 tests with 100% pass rate (78 unit + 10 integration)
- ⚡ **Fast**: 30-60 seconds per ticket with thorough AI analysis
- 💰 **Affordable**: $0.0005-0.0011 per ticket depending on tool mode
- 🔄 **Dual Modes**: Mock tools (keyword matching) or AI-powered tools (LLM reasoning)

**Navigation Guide**:
- **New to Kiro?** → Start with [About This Project](#about-this-project) to understand the development methodology
- **Want to run it?** → Jump to [Quick Start](#quick-start) for setup instructions
- **Exploring the code?** → See [Project Structure](#project-structure) and [Architecture](#architecture)
- **Understanding the specs?** → Review [Project Artifacts](#project-artifacts) and [Development Workflow](#development-workflow-from-idea-to-implementation)
- **Comparing tool modes?** → Check [Tool Modes Comparison](#tool-modes-mock-vs-ai-powered) and [Performance Comparison](#performance-comparison-script)
- **Running tests?** → See [Running Tests](#running-tests) for unit and integration tests

## About This Project

**This project was developed using Kiro's spec-driven development methodology**, which provides a structured approach to building software with AI assistance. The entire codebase, from requirements to implementation, was created through an iterative process of specification, design, and automated implementation.

### Multiple Specifications: MVP Focus

This repository contains **two related specifications** for the AI-powered customer support system:

1. **ai-customer-support-system** (`.kiro/specs/ai-customer-support-system/`)
   - **Full production system specification**
   - Includes AWS infrastructure (Lambda, DynamoDB, EventBridge, API Gateway)
   - Real integrations with ticketing systems and databases
   - Comprehensive monitoring, alerting, and analytics
   - Production-ready architecture with scalability and security
   - **Status**: Specification only (not implemented in this repository)

2. **ai-customer-support-system-mvp** (`.kiro/specs/ai-customer-support-system-mvp/`) ← **THIS PROJECT**
   - **Simplified MVP specification for rapid validation**
   - Local Python application (no AWS infrastructure except Bedrock)
   - Mock data interfaces for external systems
   - Focus on AI reasoning and agent workflow validation
   - 2-4 hour implementation timeline
   - **Status**: Fully implemented (this codebase)

**This codebase implements the MVP specification**, designed to validate the AI-powered routing approach before investing in full production infrastructure. The MVP demonstrates core functionality with real Bedrock integration while using mock data for rapid development.

**Development Strategy**: The MVP spec was created first to validate the agentic approach with minimal investment. Once validated, the production spec (ai-customer-support-system) can be implemented with confidence, building upon the proven MVP architecture.

### Spec-Driven Development with Kiro

Kiro is an AI-powered IDE that enables developers to build software through a formalized specification process. This project demonstrates the complete spec-driven workflow:

**1. Requirements Phase** → **2. Design Phase** → **3. Implementation Phase**

#### Project Artifacts

All development artifacts for the **MVP specification** are preserved in the `.kiro/specs/ai-customer-support-system-mvp/` directory:

```
.kiro/
├── specs/
│   ├── ai-customer-support-system/          # Production spec (not implemented)
│   │   ├── requirements.md
│   │   ├── requirements-production.md
│   │   ├── design.md
│   │   └── design-production.md
│   └── ai-customer-support-system-mvp/      # MVP spec (THIS PROJECT)
│       ├── requirements.md                   # Business requirements and acceptance criteria
│       ├── design.md                         # Original technical design and architecture
│       ├── post-implementation-design.md     # As-built documentation (1,224 lines)
│       └── tasks.md                          # Implementation task list (all completed)
└── steering/
    └── ai-customer-support-mvp-implementation.md  # Implementation guidelines and standards
```

**MVP Spec Artifacts** (ai-customer-support-system-mvp):

- **requirements.md**: Defines 8 core MVP requirements with acceptance criteria, including automated ticket routing, issue classification, priority calculation, and Bedrock integration. Explicitly scopes out production features (AWS infrastructure, real integrations, monitoring).

- **design.md**: Original technical design with architecture diagrams, data models (13 Pydantic models), component specifications, and development timeline. Designed for 2-4 hour implementation.

- **post-implementation-design.md**: Comprehensive as-built documentation (1,224 lines) reflecting actual implementation, including multi-agent architecture diagrams, sequence diagrams, performance metrics, lessons learned, and comparison of mock vs AI-powered tools.

- **tasks.md**: Detailed implementation plan with 14 major tasks and 50+ subtasks. All tasks tracked and completed, including core MVP (tasks 1-12) and optional enhancements (tasks 13-14 for AI-powered tools).

- **steering/ai-customer-support-mvp-implementation.md**: Implementation guidelines that guided development, including Pydantic standards, tool implementation patterns, error handling requirements, testing guidelines, and project structure rules.

#### Development Workflow: From Idea to Implementation

This project followed Kiro's structured spec-driven workflow. Here's the complete development flow:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KIRO SPEC-DRIVEN DEVELOPMENT FLOW                 │
│                    AI-Powered Customer Support MVP                   │
└─────────────────────────────────────────────────────────────────────┘

PHASE 1: REQUIREMENTS DEFINITION
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Initial Idea                                                      │
│    "Build an AI-powered ticket routing system"                      │
│    ↓                                                                 │
│ 2. Create Spec in Kiro                                              │
│    User: "Create spec for ai-customer-support-system-mvp"           │
│    ↓                                                                 │
│ 3. Requirements Gathering (Kiro AI + User Collaboration)            │
│    • Define business context and objectives                         │
│    • Identify 8 core requirements                                   │
│    • Write acceptance criteria for each requirement                 │
│    • Define success metrics and constraints                         │
│    • Scope out production features (focus on MVP)                   │
│    ↓                                                                 │
│ 4. Requirements Review & Approval                                   │
│    User reviews and approves requirements.md                        │
│    Output: .kiro/specs/ai-customer-support-system-mvp/requirements.md │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
PHASE 2: DESIGN SPECIFICATION
┌─────────────────────────────────────────────────────────────────────┐
│ 5. Technical Design (Kiro AI + User Collaboration)                  │
│    • Define architecture (local Python app + Bedrock)               │
│    • Design 13 Pydantic data models + 4 enums                       │
│    • Specify 7 agent tools with mock implementations                │
│    • Create sequence diagrams and component designs                 │
│    • Define Bedrock integration approach                            │
│    • Plan error handling and validation strategy                    │
│    ↓                                                                 │
│ 6. Design Review & Approval                                         │
│    User reviews and approves design.md                              │
│    Output: .kiro/specs/ai-customer-support-system-mvp/design.md     │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
PHASE 3: TASK PLANNING
┌─────────────────────────────────────────────────────────────────────┐
│ 7. Task Breakdown (Kiro AI)                                         │
│    • Generate 14 major tasks from design                            │
│    • Break down into 50+ subtasks                                   │
│    • Define task dependencies and order                             │
│    • Link tasks to specific requirements                            │
│    • Add checkpoints for validation                                 │
│    ↓                                                                 │
│ 8. Task Plan Review & Approval                                      │
│    User reviews and approves tasks.md                               │
│    Output: .kiro/specs/ai-customer-support-system-mvp/tasks.md      │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
PHASE 4: ITERATIVE IMPLEMENTATION
┌─────────────────────────────────────────────────────────────────────┐
│ 9. Task Execution (Kiro AI + User Supervision)                      │
│                                                                      │
│    Task 1: Project Structure                                        │
│    ├─→ Create directories (src/, tests/, docs/)                     │
│    ├─→ Create requirements.txt                                      │
│    ├─→ Create .env.example, .gitignore                             │
│    └─→ Checkpoint: User validates structure                         │
│                                                                      │
│    Task 2: Configuration & Models                                   │
│    ├─→ Implement config.py with Bedrock settings                    │
│    ├─→ Implement models.py with 13 Pydantic models                  │
│    └─→ Checkpoint: User validates models                            │
│                                                                      │
│    Task 3: Mock Data                                                │
│    ├─→ Create mock_data.py with 8 customers, 20 tickets            │
│    └─→ Checkpoint: User validates data coverage                     │
│                                                                      │
│    Task 4: Agent Tools                                              │
│    ├─→ Implement 7 tools in tools.py                               │
│    ├─→ Write 60 unit tests in tests/test_tools.py                  │
│    └─→ Checkpoint: All tests pass                                   │
│                                                                      │
│    Task 5: Agent Implementation                                     │
│    ├─→ Implement TicketRoutingAgent in agent.py                    │
│    ├─→ Write 18 unit tests in tests/test_agent.py                  │
│    ├─→ Write 10 integration tests in tests/test_agent_integration.py│
│    └─→ Checkpoint: All tests pass                                   │
│                                                                      │
│    Task 6: CLI Interface                                            │
│    ├─→ Implement main.py with 10 functions                         │
│    ├─→ Write 16 unit tests in tests/test_main.py                   │
│    ├─→ Write 11 integration tests in tests/test_main_integration.py│
│    └─→ Checkpoint: End-to-end flow works                            │
│                                                                      │
│    Task 7-12: Error Handling, Validation, Documentation            │
│    ├─→ Add comprehensive error handling                             │
│    ├─→ Implement configuration validation                           │
│    ├─→ Create documentation (README, setup, api)                    │
│    └─→ Checkpoint: MVP complete                                     │
│                                                                      │
│    Task 13: Optional AI-Powered Tools                               │
│    ├─→ Implement agent_tools.py with 3 AI tools                    │
│    ├─→ Add USE_AGENT_TOOLS configuration toggle                     │
│    ├─→ Write 21 unit tests + 20 integration tests                  │
│    ├─→ Create comparison script                                     │
│    └─→ Checkpoint: Optional enhancement complete                    │
│                                                                      │
│    Each task:                                                        │
│    • Kiro AI implements code following design specs                 │
│    • Kiro AI writes tests for validation                           │
│    • Kiro AI runs tests and fixes issues                           │
│    • User reviews and approves before next task                     │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
PHASE 5: POST-IMPLEMENTATION DOCUMENTATION
┌─────────────────────────────────────────────────────────────────────┐
│ 10. As-Built Documentation (Kiro AI)                                │
│     • Create post-implementation-design.md (1,224 lines)            │
│     • Document actual architecture and design decisions             │
│     • Add multi-agent architecture diagrams                         │
│     • Include performance metrics and lessons learned               │
│     • Document technical challenges and solutions                   │
│     ↓                                                                │
│ 11. Final Review                                                    │
│     User reviews complete implementation and documentation          │
│     Output: Complete MVP with full documentation                    │
└─────────────────────────────────────────────────────────────────────┘

RESULT: Production-Ready MVP
├─ 13 Pydantic models + 4 enums
├─ 7 mock tools + 3 AI-powered tools (optional)
├─ 88 tests (100% pass rate)
├─ Comprehensive documentation
├─ Performance validated (30-60s per ticket)
├─ Cost validated ($0.0005-0.0011 per ticket)
└─ Ready for production planning
```

**Key Characteristics of Kiro Development**:

1. **Iterative with Checkpoints**: Each phase reviewed and approved before proceeding
2. **AI-Assisted Implementation**: Kiro AI writes code following specifications
3. **Test-Driven**: Tests written alongside implementation for quality assurance
4. **Documented Throughout**: Specs, design, and documentation maintained continuously
5. **Traceable**: Every code component traces back to requirements
6. **Flexible**: Can iterate on requirements/design before implementation
7. **Validated**: Checkpoints ensure correctness at each stage

**Time Investment**:
- Requirements phase: ~30 minutes (collaborative definition)
- Design phase: ~45 minutes (architecture and models)
- Task planning: ~15 minutes (automated from design)
- Implementation: ~2-4 hours (AI-assisted with checkpoints)
- Documentation: ~30 minutes (automated from implementation)
- **Total**: ~4-6 hours from idea to complete MVP

#### Development Workflow

This project followed Kiro's structured workflow:

1. **Requirements Gathering**: Defined business needs, acceptance criteria, and success metrics
2. **Design Specification**: Created detailed technical design with architecture, data models, and component specifications
3. **Task Planning**: Broke down implementation into actionable tasks with clear dependencies
4. **Iterative Implementation**: Executed tasks incrementally with continuous validation
5. **Testing**: Comprehensive test suite (88 tests) developed alongside implementation
6. **Documentation**: Maintained documentation throughout development process

#### Benefits of Spec-Driven Development

This approach provided several advantages:

- **Clear Requirements**: Well-defined acceptance criteria guided implementation
- **Structured Design**: Architecture decisions documented before coding
- **Incremental Progress**: Tasks completed one at a time with validation checkpoints
- **Comprehensive Testing**: Test requirements defined in spec, ensuring quality
- **Traceability**: Every code component traces back to specific requirements
- **Documentation**: Specs serve as living documentation of the system
- **AI Assistance**: Kiro's AI helped implement tasks while maintaining consistency

#### Exploring the Specs

To understand how this project was built, review the spec documents in order:

1. Start with `.kiro/specs/ai-customer-support-system-mvp/requirements.md` to understand the business needs
2. Review `.kiro/specs/ai-customer-support-system-mvp/design.md` for the original technical design
3. Check `.kiro/specs/ai-customer-support-system-mvp/tasks.md` to see the implementation plan
4. Read `.kiro/specs/ai-customer-support-system-mvp/post-implementation-design.md` for as-built documentation

These documents provide complete context for every design decision and implementation detail in this codebase.

## Overview

This MVP demonstrates AI-powered ticket routing with:
- Real AI reasoning via Amazon Bedrock (Claude Sonnet 4.5)
- 7 specialized agent tools for information gathering
- Mock data interfaces for rapid development
- CLI interface with formatted output
- Processing time 30-60 seconds per ticket (with comprehensive AI analysis)

## Features

- **Intelligent Classification**: Automatically categorizes tickets into Network Outage, Billing Dispute, Technical Problem, or Account Access
- **Smart Routing**: Routes tickets to the appropriate team (Network Operations, Billing Support, Technical Support, Account Management)
- **Priority Calculation**: Assigns priority levels (P0-P3) based on VIP status, issue severity, ticket age, and service outages
- **Entity Extraction**: Identifies account numbers, service IDs, error codes, and other key information
- **Historical Context**: Considers customer history for better decision-making
- **Explainable Decisions**: Provides clear reasoning for all routing decisions
- **Dual Tool Modes**: Choose between mock tools (keyword matching) or AI-powered tools (Claude Haiku) for classification and routing

## Prerequisites

- Python 3.9 or higher
- AWS account with Bedrock access enabled
- AWS credentials configured (via `aws configure` or environment variables)
- Internet connection for Bedrock API calls

## Quick Start

### 1. Clone and Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Ensure your AWS credentials are configured. You can use one of these methods:

**Option 1: AWS CLI (Recommended)**
```bash
aws configure
```

**Option 2: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

**Option 3: Copy and edit .env file**
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Verify Bedrock Access

Ensure you have access to Claude Sonnet 4.5 in your AWS region:
- Go to AWS Console → Bedrock → Model access
- Request access to Anthropic Claude models if not already enabled
- Wait for approval (usually instant for most accounts)

### 4. Run the Application

```bash
python src/main.py
```

## Project Structure

```
ticket-routing-mvp/
├── README.md              # Main documentation (this file)
├── src/                   # Source code
│   ├── config.py          # Configuration settings
│   ├── models.py          # Pydantic data models
│   ├── tools.py           # Mock agent tool implementations
│   ├── agent_tools.py     # AI-powered tool implementations
│   ├── agent.py           # Strands agent wrapper
│   └── main.py            # CLI entry point
├── scripts/               # Utility scripts
│   └── compare_tools_performance.py  # Mock vs AI tools comparison
├── tests/                 # Test files
│   ├── test_tools.py      # Mock tools unit tests
│   ├── test_agent.py      # Agent unit tests
│   ├── test_main.py       # CLI unit tests
│   ├── test_agent_tools.py  # AI tools unit tests
│   └── test_*_integration.py  # Integration tests
├── docs/                  # Detailed documentation
│   ├── setup.md           # Detailed setup guide
│   └── api.md             # API documentation
├── mock_data.py           # Sample data and mock databases
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore file
├── CHANGELOG.md           # Change log
└── results/               # Output directory
    ├── routing_decisions.json  # Summary results
    ├── tickets/           # Individual ticket results
    ├── tools_comparison_report.txt  # Comparison report
    └── tools_comparison_results.json  # Comparison data
```

## Usage

### Process Sample Tickets

The application will automatically load and process sample tickets from `mock_data.py`:

```bash
# Run from the root directory (uses mock tools by default)
python -m src.main
```

### Using AI-Powered Tools

To enable AI-powered classification and routing:

```bash
# Set environment variable
export USE_AGENT_TOOLS=true

# Run the application
python -m src.main
```

Or create a `.env` file:
```bash
# .env
USE_AGENT_TOOLS=true
```

Then run:
```bash
python -m src.main
```

### Comparing Tool Modes

You can easily compare the performance of both modes:

```bash
# Run with mock tools
export USE_AGENT_TOOLS=false
python -m src.main
# Check results/routing_decisions.json

# Run with AI-powered tools
export USE_AGENT_TOOLS=true
python -m src.main
# Compare results/routing_decisions.json
```

### Performance Comparison Script

To run a comprehensive comparison between mock and AI-powered tools:

```bash
python scripts/compare_tools_performance.py
```

This script will:
- Process 5 sample tickets with both tool modes
- Compare processing time, cost, and routing decisions
- Generate detailed comparison report
- Save results to `results/tools_comparison_report.txt` and `results/tools_comparison_results.json`

**Comparison Metrics**:
- Processing time per ticket
- Estimated cost per ticket
- Team assignment agreement
- Priority level agreement
- Confidence score comparison
- Detailed ticket-by-ticket analysis

**Expected Results** (based on testing):
- Processing time: Mock ~21s vs AI ~23s per ticket (+8.5%)
- Cost: Mock $0.0005 vs AI $0.0011 per ticket (+117%)
- Team agreement: ~80% (4/5 tickets route to same team)
- Confidence: Mock 85% vs AI 92.8% average (+7.8%)

### View Results

Results are displayed in the console and saved to `results/routing_decisions.json`:

```
============================================================
AI-Powered Ticket Routing System - MVP
============================================================

Processing Ticket 1/10: TKT-001
Subject: Internet connection down
✓ Routed to: Network Operations
  Priority: P1
  Confidence: 95%
  Time: 2,345ms
  Reasoning: VIP customer with network outage...
```

### Summary Statistics

After processing all tickets, you'll see:
- Total tickets processed
- Average processing time
- Average confidence score
- Tickets requiring manual review
- Team distribution
- Priority distribution

## Configuration

Edit `src/config.py` to customize:

- **Bedrock Region**: Change `BEDROCK_REGION` if using a different AWS region
- **Model**: Change `BEDROCK_MODEL_ID` to use a different Claude model
- **Agent Settings**: Adjust `temperature`, `max_tokens`, `max_iterations`
- **Confidence Threshold**: Modify `CONFIDENCE_THRESHOLD` for manual review flagging

### Tool Modes: Mock vs AI-Powered

The system supports two tool modes for classification, entity extraction, and routing:

#### Mock Tools (Default)
- Uses keyword matching and regex patterns
- Fast and cost-effective
- No additional API calls beyond the main agent
- Suitable for development and testing
- **Cost**: ~$0.015-0.025 per ticket

**Enable mock tools** (default):
```bash
# In .env file or environment
USE_AGENT_TOOLS=false
```

#### AI-Powered Tools (Optional Enhancement)
- Uses Claude Haiku 4.5 for intelligent classification and routing
- More accurate and nuanced decisions
- Better handling of ambiguous or complex tickets
- Additional API calls for each tool invocation
- **Cost**: ~$0.030-0.050 per ticket (approximately 2x mock tools)

**Enable AI-powered tools**:
```bash
# In .env file or environment
USE_AGENT_TOOLS=true
```

Or set programmatically:
```python
from src.agent import TicketRoutingAgent

# Use AI-powered tools
agent = TicketRoutingAgent(use_agent_tools=True)

# Use mock tools (default)
agent = TicketRoutingAgent(use_agent_tools=False)
```

#### Comparison

| Feature | Mock Tools | AI-Powered Tools |
|---------|-----------|------------------|
| Classification | Keyword matching | LLM reasoning |
| Entity Extraction | Regex patterns | LLM extraction |
| Routing | Rule-based | LLM decision |
| Accuracy | Good for clear cases | Better for ambiguous cases |
| Speed | Fast | Moderate (additional API calls) |
| Cost per ticket | ~$0.015-0.025 | ~$0.030-0.050 |
| Best for | Development, testing, clear tickets | Production, complex tickets |

**Recommendation**: Start with mock tools for development and testing. Enable AI-powered tools in production for improved accuracy on complex or ambiguous tickets.

## Data Models

All data structures use Pydantic BaseModel for type safety and validation:

- **Ticket**: Incoming support ticket data
- **Customer**: Customer information with VIP status
- **ServiceStatus**: Service health and outage information
- **IssueClassification**: Classification results
- **ExtractedEntities**: Extracted account numbers, service IDs, etc.
- **PriorityCalculation**: Priority level and scoring
- **RoutingDecision**: Team assignment with confidence
- **FinalDecision**: Complete routing decision with reasoning

## Agent Tools

The system uses 7 specialized tools:

1. **classify_issue()**: Classifies tickets into categories
   - Mock mode: Keyword-based pattern matching
   - AI mode: Claude Haiku LLM reasoning
2. **extract_entities()**: Extracts account numbers, service IDs, error codes
   - Mock mode: Regex pattern extraction
   - AI mode: Claude Haiku LLM extraction
3. **check_vip_status()**: Determines customer VIP status (mock database lookup)
4. **check_service_status()**: Checks for active service outages (mock API)
5. **calculate_priority()**: Calculates priority level P0-P3 (weighted algorithm)
6. **route_to_team()**: Determines the best support team
   - Mock mode: Rule-based routing map
   - AI mode: Claude Haiku LLM decision
7. **get_historical_context()**: Retrieves customer history (mock database)

**Note**: Tools 1, 2, and 6 have both mock and AI-powered implementations. Tools 3, 4, 5, and 7 use mock data in both modes.

## Cost Estimates

### Mock Tools Mode (Default)
- **Per Ticket**: ~$0.015-0.025 (with 7-10 tool calls for comprehensive analysis)
- **50 Test Tickets**: ~$0.75-1.25
- **Infrastructure**: $0 (runs locally)

### AI-Powered Tools Mode (Optional)
- **Per Ticket**: ~$0.030-0.050 (additional Claude Haiku calls for classification, extraction, and routing)
- **50 Test Tickets**: ~$1.50-2.50
- **Infrastructure**: $0 (runs locally)

**Cost Breakdown**:
- Main agent (Claude Haiku 4.5): ~$0.010-0.015 per ticket
- Mock tools: No additional cost
- AI-powered tools: ~$0.015-0.035 additional per ticket (3 extra Claude Haiku calls)

Note: Processing involves multiple AI tool calls for thorough analysis, resulting in higher costs than simple classification but providing detailed reasoning and accurate routing decisions.

## Troubleshooting

### "No credentials found"
- Run `aws configure` to set up AWS credentials
- Or set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables

### "Model not found" or "Access denied"
- Ensure you have Bedrock access enabled in your AWS account
- Go to AWS Console → Bedrock → Model access
- Request access to Anthropic Claude models

### "Region not supported"
- Claude Sonnet 4.5 may not be available in all regions
- Try changing `BEDROCK_REGION` to `us-east-1` or `us-west-2`

### Slow processing
- Processing takes 30-60 seconds per ticket due to multiple AI tool calls
- This is expected for comprehensive agentic analysis with 7-10 tool invocations
- Check your internet connection if processing takes longer than 60 seconds
- Verify Bedrock service status
- For faster processing, consider reducing max_iterations in config (may reduce analysis quality)

### AI-Powered Tools Issues

#### "AI classification failed: Using fallback"
- This is a graceful fallback when AI tools encounter errors
- The system will use simple classification instead
- Check AWS Bedrock service status
- Verify you have sufficient API rate limits
- Review CloudWatch logs for detailed error messages

#### Higher costs than expected
- AI-powered tools make additional Claude Haiku API calls
- Each ticket uses 3 extra API calls (classify, extract, route)
- Switch to mock tools mode to reduce costs: `USE_AGENT_TOOLS=false`
- Monitor usage in AWS Cost Explorer

#### Inconsistent results with AI tools
- AI-powered tools may produce slightly different results on each run
- This is normal LLM behavior due to temperature settings
- For deterministic results, use mock tools mode
- For production, consider implementing result caching

## Development

### Running Tests

The project includes comprehensive unit tests and integration tests.

#### Unit Tests (No API Calls - Fast & Free)

```bash
# Install test dependencies
pip install pytest

# Run all unit tests (excludes integration tests)
pytest -m "not integration" -v

# Run specific test file
pytest tests/test_tools.py -v
pytest tests/test_agent.py -v
```

#### Integration Tests (Real Bedrock API - Requires AWS Credentials)

Integration tests validate end-to-end behavior with actual Bedrock API calls.

```bash
# Run only integration tests
pytest -m integration -v

# Run with detailed output
pytest -m integration -v -s
```

**Requirements for Integration Tests:**
- AWS credentials configured (`aws configure`)
- Bedrock access enabled in AWS account
- Claude Sonnet 4.5 model access

**Cost**: ~$0.006 per ticket, ~$0.06 for full integration test suite

**What's Tested:**
- VIP customer routing (P0/P1 priority)
- Team assignment accuracy (Network Ops, Billing, Technical, Account Mgmt)
- Priority calculation (P0-P3)
- Processing time (< 60 seconds per ticket)
- Confidence score variation
- Reasoning quality

See `RUN_INTEGRATION_TESTS.md` for detailed integration test documentation.

### Test Coverage

- **Unit Tests**: 78 tests (test_tools.py: 60, test_agent.py: 18)
- **Integration Tests**: 10 tests (test_agent_integration.py)
- **Total**: 88 tests

### Adding New Tools

1. Define tool function in `src/tools.py`
2. Use Pydantic models for input/output
3. Add tool to agent initialization in `src/agent.py`
4. Write tests in `tests/test_tools.py`

## Next Steps

After validating the MVP:

1. **Evaluate Tool Modes**: Compare mock vs AI-powered tools for your use case
2. **Production Infrastructure**: Deploy to AWS Lambda with DynamoDB
3. **Real Integrations**: Connect to actual ticketing system and customer database
4. **Monitoring**: Add CloudWatch metrics and alerting
5. **GUI**: Implement Streamlit interface for non-technical users
6. **Performance Optimization**: Fine-tune AI prompts and caching strategies

## Support

For issues or questions:
- Check the troubleshooting section above
- Review AWS Bedrock documentation
- Check Strands Agent Framework documentation

## License

MIT License - See LICENSE file for details

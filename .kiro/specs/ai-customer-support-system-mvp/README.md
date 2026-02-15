# AI-Powered Customer Support System - MVP

This folder contains the complete specification for the MVP (Minimum Viable Product) implementation of the AI-powered customer support system.

## Overview

The MVP is a local Python application designed to validate the agentic approach with real AWS Bedrock integration, using mock data interfaces for rapid development.

**Timeline**: 2-4 hours for core MVP, +2-4 hours for optional enhancements

**Goal**: Demonstrate intelligent ticket routing using AI agents with minimal infrastructure

## Documents in This Folder

### [requirements.md](./requirements.md)
Complete MVP requirements including:
- 8 core requirements for local ticket processing
- Mock data interfaces
- Automated routing with Bedrock
- Issue classification and priority calculation
- 7 agent tools specifications
- Optional enhancements (multi-agent tools, Streamlit GUI)
- Success metrics and out-of-scope items

### [design.md](./design.md)
Complete MVP design including:
- Local Python application architecture
- Project structure and file organization
- Detailed sequence diagram
- All 7 agent tools with mock implementations
- Configuration and mock data design
- Agent implementation with Strands
- CLI interface design
- Hour-by-hour development timeline
- Testing strategy and migration path

## Quick Start

1. Review [requirements.md](./requirements.md) to understand what the MVP delivers
2. Review [design.md](./design.md) to understand how to build it
3. Follow the hour-by-hour timeline in the design document
4. Use the [implementation guide](../../steering/ai-customer-support-implementation.md) for best practices

## Key Characteristics

- **Deployment**: Local Python application (no AWS infrastructure except Bedrock)
- **Data**: Mock interfaces for all external systems
- **Storage**: JSON files for results
- **Interface**: CLI or optional Streamlit GUI
- **Cost**: ~$0.006 per ticket (Bedrock API only)
- **Scalability**: 10-20 sample tickets

## Success Criteria

- ✅ Complete in 2-4 hours
- ✅ Process 10-20 sample tickets
- ✅ Agent provides clear reasoning
- ✅ Confidence scores are meaningful
- ✅ Validates agentic approach

## Next Steps

After completing the MVP:
1. Evaluate routing decisions and agent reasoning
2. Measure baseline performance metrics
3. Identify improvement areas
4. Plan migration to [production system](../ai-customer-support-system/)

## Related Documents

- [Production System Specs](../ai-customer-support-system/) - Full AWS infrastructure implementation
- [Implementation Guide](../../steering/ai-customer-support-implementation.md) - Development best practices
- [Main Requirements Overview](../ai-customer-support-system/requirements.md) - High-level comparison
- [Main Design Overview](../ai-customer-support-system/design.md) - Architecture comparison

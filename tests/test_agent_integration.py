"""
Integration tests for TicketRoutingAgent using actual Bedrock API.

These tests make real API calls to AWS Bedrock and are marked with @pytest.mark.integration.
Run separately with: pytest -m integration

Requirements:
- AWS credentials configured (aws configure or environment variables)
- Bedrock access enabled in AWS account
- Claude Sonnet 4.5 model available in configured region
"""

import pytest
import os
from datetime import datetime, timedelta

from src.agent import TicketRoutingAgent
from src.models import (
    Ticket,
    FinalDecision,
    Team,
    PriorityLevel
)
from mock_data import SAMPLE_TICKETS


# Skip all tests if AWS credentials are not configured
def check_aws_credentials():
    """Check if AWS credentials are configured."""
    # Check for AWS credentials in environment or config
    has_env_creds = (
        os.environ.get('AWS_ACCESS_KEY_ID') and 
        os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    has_profile = os.environ.get('AWS_PROFILE')
    
    # Check if credentials file exists
    aws_creds_file = os.path.expanduser('~/.aws/credentials')
    has_creds_file = os.path.exists(aws_creds_file)
    
    return has_env_creds or has_profile or has_creds_file


# Skip all tests in this module if AWS credentials not configured
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not check_aws_credentials(),
        reason="AWS credentials not configured. Run 'aws configure' or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
    )
]


# ============================================================
# Integration Tests - End-to-End with Real Bedrock API
# ============================================================

class TestAgentIntegrationWithBedrock:
    """Integration tests using actual Bedrock API calls."""
    
    @pytest.fixture(scope="class")
    def agent(self):
        """Create a real TicketRoutingAgent instance."""
        return TicketRoutingAgent()
    
    def test_vip_customer_network_outage_routing(self, agent):
        """Test VIP customer with network outage gets P0/P1 priority and routes to Network Operations."""
        # Arrange
        ticket = Ticket(
            ticket_id="TKT-INT-001",
            customer_id="CUST001",  # VIP customer in mock data
            subject="Critical network outage - all services down",
            description="My internet connection has been completely down for 3 hours. Error code: NET-500. Service ID: SVC001. This is affecting my business operations.",
            timestamp=datetime.utcnow() - timedelta(hours=3)
        )
        
        # Act
        decision = agent.process_ticket(ticket)
        
        # Assert
        assert isinstance(decision, FinalDecision)
        assert decision.ticket_id == "TKT-INT-001"
        assert decision.customer_id == "CUST001"
        assert decision.assigned_team == Team.NETWORK_OPS, f"Expected Network Operations, got {decision.assigned_team}"
        assert decision.priority_level in [PriorityLevel.P0, PriorityLevel.P1], f"Expected P0 or P1 for VIP outage, got {decision.priority_level}"
        assert decision.confidence_score >= 70, f"Expected confidence >= 70%, got {decision.confidence_score}"
        assert decision.processing_time_ms > 0
        assert decision.processing_time_ms < 60000, f"Processing took {decision.processing_time_ms}ms, expected < 60000ms (60 seconds)"
        assert len(decision.reasoning) > 0
        print(f"\n✓ VIP Network Outage: {decision.assigned_team.value}, {decision.priority_level.value}, {decision.confidence_score}% confidence")
        print(f"  Reasoning: {decision.reasoning[:200]}...")
    
    def test_standard_customer_billing_dispute_routing(self, agent):
        """Test standard customer with billing dispute gets P2/P3 priority and routes to Billing Support."""
        # Arrange
        ticket = Ticket(
            ticket_id="TKT-INT-002",
            customer_id="CUST002",  # Standard customer in mock data
            subject="Question about my bill",
            description="I was charged $150.00 on my last invoice but I expected $120.00. Can you explain the difference? Account: ACC-67890",
            timestamp=datetime.utcnow() - timedelta(hours=1)
        )
        
        # Act
        decision = agent.process_ticket(ticket)
        
        # Assert
        assert isinstance(decision, FinalDecision)
        assert decision.ticket_id == "TKT-INT-002"
        assert decision.customer_id == "CUST002"
        assert decision.assigned_team == Team.BILLING, f"Expected Billing Support, got {decision.assigned_team}"
        assert decision.priority_level in [PriorityLevel.P2, PriorityLevel.P3], f"Expected P2 or P3 for standard billing, got {decision.priority_level}"
        assert decision.confidence_score > 60, f"Expected confidence > 60%, got {decision.confidence_score}"
        assert decision.processing_time_ms > 0
        assert decision.processing_time_ms < 60000, f"Processing took {decision.processing_time_ms}ms, expected < 60000ms"
        assert len(decision.reasoning) > 0
        print(f"\n✓ Standard Billing: {decision.assigned_team.value}, {decision.priority_level.value}, {decision.confidence_score}% confidence")
        print(f"  Reasoning: {decision.reasoning[:200]}...")
    
    def test_technical_problem_routing(self, agent):
        """Test technical problem routes to Technical Support."""
        # Arrange
        ticket = Ticket(
            ticket_id="TKT-INT-003",
            customer_id="CUST003",
            subject="Router not working properly",
            description="My router keeps disconnecting every few minutes. Error code: TECH-404. I've tried restarting it but the problem persists.",
            timestamp=datetime.utcnow() - timedelta(hours=2)
        )
        
        # Act
        decision = agent.process_ticket(ticket)
        
        # Assert
        assert isinstance(decision, FinalDecision)
        assert decision.ticket_id == "TKT-INT-003"
        assert decision.assigned_team == Team.TECHNICAL, f"Expected Technical Support, got {decision.assigned_team}"
        assert decision.priority_level in [PriorityLevel.P1, PriorityLevel.P2, PriorityLevel.P3], f"Expected P1-P3, got {decision.priority_level}"
        assert decision.confidence_score > 60, f"Expected confidence > 60%, got {decision.confidence_score}"
        assert decision.processing_time_ms > 0
        assert decision.processing_time_ms < 60000, f"Processing took {decision.processing_time_ms}ms, expected < 60000ms"
        print(f"\n✓ Technical Problem: {decision.assigned_team.value}, {decision.priority_level.value}, {decision.confidence_score}% confidence")
        print(f"  Reasoning: {decision.reasoning[:200]}...")
    
    def test_account_access_routing(self, agent):
        """Test account access issue routes to Account Management."""
        # Arrange
        ticket = Ticket(
            ticket_id="TKT-INT-004",
            customer_id="CUST004",
            subject="Cannot login to my account",
            description="I forgot my password and the reset link isn't working. I need to access my account urgently. Account: ACC-11111",
            timestamp=datetime.utcnow() - timedelta(minutes=30)
        )
        
        # Act
        decision = agent.process_ticket(ticket)
        
        # Assert
        assert isinstance(decision, FinalDecision)
        assert decision.ticket_id == "TKT-INT-004"
        assert decision.assigned_team == Team.ACCOUNT_MGMT, f"Expected Account Management, got {decision.assigned_team}"
        assert decision.priority_level in [PriorityLevel.P1, PriorityLevel.P2, PriorityLevel.P3], f"Expected P1-P3, got {decision.priority_level}"
        assert decision.confidence_score > 60, f"Expected confidence > 60%, got {decision.confidence_score}"
        assert decision.processing_time_ms > 0
        assert decision.processing_time_ms < 60000, f"Processing took {decision.processing_time_ms}ms, expected < 60000ms"
        print(f"\n✓ Account Access: {decision.assigned_team.value}, {decision.priority_level.value}, {decision.confidence_score}% confidence")
        print(f"  Reasoning: {decision.reasoning[:200]}...")
    
    def test_processing_time_performance(self, agent):
        """Test that ticket processing completes within 5 seconds."""
        # Arrange
        ticket = Ticket(
            ticket_id="TKT-INT-005",
            customer_id="CUST005",
            subject="Internet speed is slow",
            description="My internet speed has been very slow for the past day. I'm getting 10 Mbps instead of the 100 Mbps I'm paying for.",
            timestamp=datetime.utcnow() - timedelta(hours=24)
        )
        
        # Act
        decision = agent.process_ticket(ticket)
        
        # Assert
        assert decision.processing_time_ms > 0
        assert decision.processing_time_ms < 60000, f"Processing took {decision.processing_time_ms}ms, expected < 60000ms (60 seconds)"
        print(f"\n✓ Performance: Processed in {decision.processing_time_ms}ms (< 60000ms required)")
    
    def test_confidence_scores_are_meaningful(self, agent):
        """Test that confidence scores vary based on ticket clarity."""
        # Arrange - Clear, unambiguous ticket
        clear_ticket = Ticket(
            ticket_id="TKT-INT-006",
            customer_id="CUST001",
            subject="Network outage",
            description="Complete network outage. All services down. Error: NET-500. Service: SVC001.",
            timestamp=datetime.utcnow()
        )
        
        # Arrange - Ambiguous ticket
        ambiguous_ticket = Ticket(
            ticket_id="TKT-INT-007",
            customer_id="CUST002",
            subject="Problem with service",
            description="I'm having some issues. Can you help?",
            timestamp=datetime.utcnow()
        )
        
        # Act
        clear_decision = agent.process_ticket(clear_ticket)
        ambiguous_decision = agent.process_ticket(ambiguous_ticket)
        
        # Assert
        assert clear_decision.confidence_score > 70, f"Clear ticket should have high confidence, got {clear_decision.confidence_score}%"
        assert ambiguous_decision.confidence_score < 90, f"Ambiguous ticket should have lower confidence, got {ambiguous_decision.confidence_score}%"
        
        # Confidence scores should not all be the same
        assert clear_decision.confidence_score != ambiguous_decision.confidence_score, "Confidence scores should vary based on ticket clarity"
        
        print(f"\n✓ Confidence Variation:")
        print(f"  Clear ticket: {clear_decision.confidence_score}% confidence")
        print(f"  Ambiguous ticket: {ambiguous_decision.confidence_score}% confidence")
    
    def test_agent_provides_clear_reasoning(self, agent):
        """Test that agent provides clear reasoning for routing decisions."""
        # Arrange
        ticket = Ticket(
            ticket_id="TKT-INT-008",
            customer_id="CUST001",
            subject="VIP customer - billing overcharge",
            description="I'm a VIP customer and I was overcharged $500 on my last bill. This needs immediate attention.",
            timestamp=datetime.utcnow()
        )
        
        # Act
        decision = agent.process_ticket(ticket)
        
        # Assert
        assert len(decision.reasoning) > 50, "Reasoning should be detailed (> 50 characters)"
        
        # Reasoning should mention key factors
        reasoning_lower = decision.reasoning.lower()
        assert any(keyword in reasoning_lower for keyword in ['vip', 'customer', 'priority', 'billing', 'charge']), \
            "Reasoning should mention relevant factors from the ticket"
        
        print(f"\n✓ Reasoning Quality:")
        print(f"  Length: {len(decision.reasoning)} characters")
        print(f"  Content: {decision.reasoning[:300]}...")
    
    def test_multiple_sample_tickets_distribution(self, agent):
        """Test that sample tickets are distributed across all teams."""
        # Arrange - Use first 5 sample tickets from mock data
        sample_tickets = SAMPLE_TICKETS[:5]
        
        # Act
        decisions = [agent.process_ticket(ticket) for ticket in sample_tickets]
        
        # Assert
        teams_assigned = set(d.assigned_team for d in decisions)
        priorities_assigned = set(d.priority_level for d in decisions)
        
        # Should have variety in routing (at least 2 different teams)
        assert len(teams_assigned) >= 2, f"Expected variety in team assignments, got only {teams_assigned}"
        
        # Should have variety in priorities (at least 2 different levels)
        assert len(priorities_assigned) >= 2, f"Expected variety in priority levels, got only {priorities_assigned}"
        
        # All should have reasonable confidence
        for decision in decisions:
            assert decision.confidence_score > 50, f"Ticket {decision.ticket_id} has low confidence: {decision.confidence_score}%"
        
        print(f"\n✓ Sample Tickets Distribution:")
        print(f"  Teams used: {[t.value for t in teams_assigned]}")
        print(f"  Priorities used: {[p.value for p in priorities_assigned]}")
        print(f"  Average confidence: {sum(d.confidence_score for d in decisions) / len(decisions):.1f}%")


# ============================================================
# Test Configuration and Utilities
# ============================================================

class TestIntegrationConfiguration:
    """Test configuration and setup for integration tests."""
    
    def test_aws_credentials_configured(self):
        """Verify AWS credentials are configured."""
        assert check_aws_credentials(), "AWS credentials must be configured to run integration tests"
    
    def test_agent_can_initialize(self):
        """Verify agent can initialize without errors."""
        try:
            agent = TicketRoutingAgent()
            assert agent is not None
            assert agent.bedrock is not None
            assert agent.agent is not None
            print("\n✓ Agent initialized successfully with Bedrock client")
        except Exception as e:
            pytest.fail(f"Agent initialization failed: {e}")


# ============================================================
# How to Run These Tests
# ============================================================

"""
To run integration tests:

1. Configure AWS credentials:
   aws configure
   
   Or set environment variables:
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_DEFAULT_REGION=eu-central-1

2. Run integration tests only:
   pytest -m integration -v

3. Run integration tests with output:
   pytest -m integration -v -s

4. Run all tests (unit + integration):
   pytest -v

5. Skip integration tests:
   pytest -m "not integration" -v

Note: Integration tests make real API calls to AWS Bedrock and will incur costs.
Estimated cost: ~$0.006 per ticket, ~$0.06 for full test suite.
"""

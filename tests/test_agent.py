"""
Unit tests for TicketRoutingAgent with Pydantic validation.

Tests the agent module to ensure it correctly processes tickets,
handles errors gracefully, and returns valid FinalDecision models.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from src.agent import TicketRoutingAgent
from src.models import (
    Ticket,
    FinalDecision,
    Team,
    PriorityLevel
)


# ============================================================
# Test TicketRoutingAgent Initialization
# ============================================================

class TestTicketRoutingAgentInit:
    """Test suite for TicketRoutingAgent initialization."""
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_agent_initialization(self, mock_agent_class, mock_boto3_client):
        """Test that agent initializes correctly with Bedrock client and Strands agent."""
        # Arrange
        mock_bedrock = Mock()
        mock_boto3_client.return_value = mock_bedrock
        mock_strands_agent = Mock()
        mock_agent_class.return_value = mock_strands_agent
        
        # Act
        agent = TicketRoutingAgent()
        
        # Assert
        mock_boto3_client.assert_called_once_with('bedrock-runtime', region_name='eu-central-1')
        assert agent.bedrock == mock_bedrock
        assert agent.agent == mock_strands_agent
        assert agent.use_agent_tools is False
        
        # Verify Strands Agent was initialized with correct parameters
        mock_agent_class.assert_called_once()
        call_kwargs = mock_agent_class.call_args[1]
        assert call_kwargs['model'] == 'global.anthropic.claude-haiku-4-5-20251001-v1:0'
        assert 'expert customer support ticket routing agent' in call_kwargs['system_prompt'].lower()
        assert len(call_kwargs['tools']) == 7  # All 7 tools
        # Note: temperature and max_tokens are not passed to Agent in Strands API
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_agent_initialization_with_agent_tools(self, mock_agent_class, mock_boto3_client):
        """Test that agent can be initialized with agent_tools flag."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_agent_class.return_value = Mock()
        
        # Act
        agent = TicketRoutingAgent(use_agent_tools=True)
        
        # Assert
        assert agent.use_agent_tools is True
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_system_prompt_contains_required_elements(self, mock_agent_class, mock_boto3_client):
        """Test that system prompt contains all required elements."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_agent_class.return_value = Mock()
        
        # Act
        agent = TicketRoutingAgent()
        
        # Assert
        system_prompt = agent.system_prompt.lower()
        
        # Check for team descriptions
        assert 'network operations' in system_prompt
        assert 'billing support' in system_prompt
        assert 'technical support' in system_prompt
        assert 'account management' in system_prompt
        
        # Check for priority levels
        assert 'p0' in system_prompt or 'critical' in system_prompt
        assert 'p1' in system_prompt or 'high' in system_prompt
        assert 'p2' in system_prompt or 'medium' in system_prompt
        assert 'p3' in system_prompt or 'low' in system_prompt
        
        # Check for process guidelines
        assert 'classify_issue' in system_prompt
        assert 'extract_entities' in system_prompt
        assert 'check_vip_status' in system_prompt
        assert 'route_to_team' in system_prompt
        assert 'calculate_priority' in system_prompt


# ============================================================
# Test process_ticket() Method
# ============================================================

class TestProcessTicket:
    """Test suite for process_ticket() method."""
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_process_ticket_success(self, mock_agent_class, mock_boto3_client):
        """Test successful ticket processing returns FinalDecision model."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_strands_agent = Mock()
        mock_agent_class.return_value = mock_strands_agent
        
        # Mock agent response (agent is called directly, not .run())
        mock_strands_agent.return_value = """
        Based on my analysis, I recommend routing this ticket to Network Operations
        with P1 (High) priority. The customer is a VIP and experiencing a network outage.
        Confidence: 95%
        """
        
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-001",
            customer_id="CUST001",
            subject="Internet down",
            description="My internet has been down for 2 hours",
            timestamp=datetime.utcnow()
        )
        
        # Act
        decision = agent.process_ticket(ticket)
        
        # Assert
        assert isinstance(decision, FinalDecision)
        assert decision.ticket_id == "TKT-001"
        assert decision.customer_id == "CUST001"
        assert isinstance(decision.assigned_team, Team)
        assert isinstance(decision.priority_level, PriorityLevel)
        assert 0 <= decision.confidence_score <= 100
        assert decision.processing_time_ms > 0
        assert len(decision.reasoning) > 0
        
        # Verify agent was called (not .run())
        mock_strands_agent.assert_called_once()
        call_args = mock_strands_agent.call_args[0][0]
        assert "TKT-001" in call_args
        assert "CUST001" in call_args
        assert "Internet down" in call_args
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_process_ticket_with_error_uses_fallback(self, mock_agent_class, mock_boto3_client):
        """Test that errors trigger fallback decision."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_strands_agent = Mock()
        mock_agent_class.return_value = mock_strands_agent
        
        # Mock agent to raise exception when called
        mock_strands_agent.side_effect = Exception("Bedrock API error")
        
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-002",
            customer_id="CUST002",
            subject="Billing issue",
            description="Overcharged on my bill",
            timestamp=datetime.utcnow()
        )
        
        # Act
        decision = agent.process_ticket(ticket)
        
        # Assert
        assert isinstance(decision, FinalDecision)
        assert decision.ticket_id == "TKT-002"
        assert decision.customer_id == "CUST002"
        assert decision.assigned_team == Team.TECHNICAL  # Fallback team
        assert decision.priority_level == PriorityLevel.P2  # Fallback priority
        assert decision.confidence_score == 50.0  # Fallback confidence
        assert decision.requires_manual_review is True
        assert "Fallback routing due to error" in decision.reasoning
        assert "Bedrock API error" in decision.reasoning
        assert decision.processing_time_ms > 0
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_process_ticket_tracks_processing_time(self, mock_agent_class, mock_boto3_client):
        """Test that processing time is tracked correctly."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_strands_agent = Mock()
        mock_agent_class.return_value = mock_strands_agent
        mock_strands_agent.return_value = "Route to Technical Support with P2 priority. Confidence: 80%"
        
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-003",
            customer_id="CUST003",
            subject="Test ticket",
            description="Test description",
            timestamp=datetime.utcnow()
        )
        
        # Act
        decision = agent.process_ticket(ticket)
        
        # Assert
        assert decision.processing_time_ms > 0
        assert decision.processing_time_ms < 10000  # Should be less than 10 seconds for mock


# ============================================================
# Test _parse_decision() Helper Method
# ============================================================

class TestParseDecision:
    """Test suite for _parse_decision() helper method."""
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_parse_decision_network_operations(self, mock_agent_class, mock_boto3_client):
        """Test parsing decision for Network Operations team."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_agent_class.return_value = Mock()
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-001",
            customer_id="CUST001",
            subject="Test",
            description="Test",
            timestamp=datetime.utcnow()
        )
        
        result = "Route to Network Operations with P0 (Critical) priority. Confidence: 95%"
        
        # Act
        decision = agent._parse_decision(result, ticket)
        
        # Assert
        assert decision.assigned_team == Team.NETWORK_OPS
        assert decision.priority_level == PriorityLevel.P0
        assert decision.confidence_score == 95.0
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_parse_decision_billing_support(self, mock_agent_class, mock_boto3_client):
        """Test parsing decision for Billing Support team."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_agent_class.return_value = Mock()
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-002",
            customer_id="CUST002",
            subject="Test",
            description="Test",
            timestamp=datetime.utcnow()
        )
        
        result = "Route to Billing Support with P1 (High) priority. Confidence: 85%"
        
        # Act
        decision = agent._parse_decision(result, ticket)
        
        # Assert
        assert decision.assigned_team == Team.BILLING
        assert decision.priority_level == PriorityLevel.P1
        assert decision.confidence_score == 85.0
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_parse_decision_technical_support(self, mock_agent_class, mock_boto3_client):
        """Test parsing decision for Technical Support team."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_agent_class.return_value = Mock()
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-003",
            customer_id="CUST003",
            subject="Test",
            description="Test",
            timestamp=datetime.utcnow()
        )
        
        result = "Route to Technical Support with P2 (Medium) priority. Confidence: 75%"
        
        # Act
        decision = agent._parse_decision(result, ticket)
        
        # Assert
        assert decision.assigned_team == Team.TECHNICAL
        assert decision.priority_level == PriorityLevel.P2
        assert decision.confidence_score == 75.0
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_parse_decision_account_management(self, mock_agent_class, mock_boto3_client):
        """Test parsing decision for Account Management team."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_agent_class.return_value = Mock()
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-004",
            customer_id="CUST004",
            subject="Test",
            description="Test",
            timestamp=datetime.utcnow()
        )
        
        result = "Route to Account Management with P3 (Low) priority. Confidence: 65%"
        
        # Act
        decision = agent._parse_decision(result, ticket)
        
        # Assert
        assert decision.assigned_team == Team.ACCOUNT_MGMT
        assert decision.priority_level == PriorityLevel.P3
        assert decision.confidence_score == 65.0
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_parse_decision_manual_review_flag(self, mock_agent_class, mock_boto3_client):
        """Test that manual review flag is detected."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_agent_class.return_value = Mock()
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-005",
            customer_id="CUST005",
            subject="Test",
            description="Test",
            timestamp=datetime.utcnow()
        )
        
        result = "Route to Technical Support with P2 priority. Flag for manual review. Confidence: 60%"
        
        # Act
        decision = agent._parse_decision(result, ticket)
        
        # Assert
        assert decision.requires_manual_review is True
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_parse_decision_defaults_to_technical(self, mock_agent_class, mock_boto3_client):
        """Test that unclear responses default to Technical Support."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_agent_class.return_value = Mock()
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-006",
            customer_id="CUST006",
            subject="Test",
            description="Test",
            timestamp=datetime.utcnow()
        )
        
        result = "This is an unclear response without team information"
        
        # Act
        decision = agent._parse_decision(result, ticket)
        
        # Assert
        assert decision.assigned_team == Team.TECHNICAL  # Default
        assert decision.priority_level == PriorityLevel.P2  # Default
        assert decision.confidence_score == 70.0  # Default


# ============================================================
# Test _fallback_decision() Helper Method
# ============================================================

class TestFallbackDecision:
    """Test suite for _fallback_decision() helper method."""
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_fallback_decision_structure(self, mock_agent_class, mock_boto3_client):
        """Test that fallback decision has correct structure."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_agent_class.return_value = Mock()
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-FALLBACK",
            customer_id="CUST-FALLBACK",
            subject="Test ticket",
            description="Test description",
            timestamp=datetime.utcnow()
        )
        
        error = "Test error message"
        
        # Act
        decision = agent._fallback_decision(ticket, error)
        
        # Assert
        assert isinstance(decision, FinalDecision)
        assert decision.ticket_id == "TKT-FALLBACK"
        assert decision.customer_id == "CUST-FALLBACK"
        assert decision.assigned_team == Team.TECHNICAL
        assert decision.priority_level == PriorityLevel.P2
        assert decision.confidence_score == 50.0
        assert decision.requires_manual_review is True
        assert "Fallback routing due to error" in decision.reasoning
        assert "Test error message" in decision.reasoning
        assert decision.processing_time_ms == 0  # Will be set by process_ticket
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_fallback_decision_includes_error_message(self, mock_agent_class, mock_boto3_client):
        """Test that fallback decision includes informative error message based on error type."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_agent_class.return_value = Mock()
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-001",
            customer_id="CUST001",
            subject="Test",
            description="Test",
            timestamp=datetime.utcnow()
        )
        
        error = "Bedrock throttling error: Rate limit exceeded"
        
        # Act
        decision = agent._fallback_decision(ticket, error)
        
        # Assert - The enhanced error handling provides informative messages
        # It should mention rate limiting and provide context
        assert "rate limit" in decision.reasoning.lower() or "throttl" in decision.reasoning.lower()
        assert "fallback routing" in decision.reasoning.lower()
        assert decision.requires_manual_review is True


# ============================================================
# Test Pydantic Validation
# ============================================================

class TestAgentPydanticValidation:
    """Test suite for Pydantic validation in agent module."""
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_process_ticket_validates_input(self, mock_agent_class, mock_boto3_client):
        """Test that process_ticket validates Ticket input."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_agent_class.return_value = Mock()
        agent = TicketRoutingAgent()
        
        # Act & Assert - should raise ValidationError for invalid ticket
        with pytest.raises((ValidationError, AttributeError, TypeError)):
            agent.process_ticket("not a ticket")  # type: ignore
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_final_decision_validates_fields(self, mock_agent_class, mock_boto3_client):
        """Test that FinalDecision validates field constraints."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_agent_class.return_value = Mock()
        
        # Act & Assert - confidence_score must be 0-100
        with pytest.raises(ValidationError):
            FinalDecision(
                ticket_id="TKT-001",
                customer_id="CUST001",
                assigned_team=Team.TECHNICAL,
                priority_level=PriorityLevel.P2,
                confidence_score=150.0,  # Invalid: > 100
                reasoning="Test",
                processing_time_ms=100
            )
        
        with pytest.raises(ValidationError):
            FinalDecision(
                ticket_id="TKT-001",
                customer_id="CUST001",
                assigned_team=Team.TECHNICAL,
                priority_level=PriorityLevel.P2,
                confidence_score=-10.0,  # Invalid: < 0
                reasoning="Test",
                processing_time_ms=100
            )


# ============================================================
# Test Integration Scenarios
# ============================================================

class TestAgentIntegration:
    """Test suite for agent integration scenarios."""
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_vip_customer_ticket_processing(self, mock_agent_class, mock_boto3_client):
        """Test processing ticket for VIP customer."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_strands_agent = Mock()
        mock_agent_class.return_value = mock_strands_agent
        mock_strands_agent.return_value = "Route to Network Operations with P0 priority. VIP customer with critical outage. Confidence: 98%"
        
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-VIP-001",
            customer_id="CUST001",  # VIP customer in mock data
            subject="Critical network outage",
            description="All services down for 3 hours",
            timestamp=datetime.utcnow() - timedelta(hours=3)
        )
        
        # Act
        decision = agent.process_ticket(ticket)
        
        # Assert
        assert isinstance(decision, FinalDecision)
        assert decision.ticket_id == "TKT-VIP-001"
        assert decision.assigned_team == Team.NETWORK_OPS
        assert decision.priority_level == PriorityLevel.P0
        assert decision.confidence_score >= 90
    
    @patch('src.agent.boto3.client')
    @patch('src.agent.Agent')
    def test_standard_customer_ticket_processing(self, mock_agent_class, mock_boto3_client):
        """Test processing ticket for standard customer."""
        # Arrange
        mock_boto3_client.return_value = Mock()
        mock_strands_agent = Mock()
        mock_agent_class.return_value = mock_strands_agent
        mock_strands_agent.return_value = "Route to Billing Support with P2 priority. Standard billing inquiry. Confidence: 80%"
        
        agent = TicketRoutingAgent()
        
        ticket = Ticket(
            ticket_id="TKT-STD-001",
            customer_id="CUST002",  # Standard customer
            subject="Question about my bill",
            description="I have a question about a charge on my bill",
            timestamp=datetime.utcnow()
        )
        
        # Act
        decision = agent.process_ticket(ticket)
        
        # Assert
        assert isinstance(decision, FinalDecision)
        assert decision.ticket_id == "TKT-STD-001"
        assert decision.assigned_team == Team.BILLING
        assert decision.priority_level == PriorityLevel.P2

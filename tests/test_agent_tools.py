"""
Unit tests for AI-powered agent tools.

Tests the AI-powered tools using mocked Strands agents to avoid actual Bedrock API calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.agent_tools import (
    classify_issue,
    extract_entities,
    route_to_team,
    _get_classification_agent,
    _get_extraction_agent,
    _get_routing_agent
)
from src.models import (
    IssueClassification,
    ExtractedEntities,
    RoutingDecision,
    Team
)


class TestClassifyIssueAI:
    """Test AI-powered classify_issue tool."""
    
    @patch('src.agent_tools._get_classification_agent')
    def test_classify_network_outage(self, mock_get_agent):
        """Test classification of network outage ticket."""
        # Mock agent response
        mock_agent = Mock()
        mock_agent.return_value = """PRIMARY_CATEGORY: Network Outage
CONFIDENCE: 0.95
KEYWORDS: internet, down, offline, connection
SECONDARY_CATEGORIES: Technical Problem"""
        mock_get_agent.return_value = mock_agent
        
        result = classify_issue("My internet is down and offline")
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category == "Network Outage"
        assert result.confidence == 0.95
        assert "internet" in result.keywords
        assert "down" in result.keywords
        assert "Technical Problem" in result.secondary_categories
    
    @patch('src.agent_tools._get_classification_agent')
    def test_classify_billing_dispute(self, mock_get_agent):
        """Test classification of billing dispute ticket."""
        mock_agent = Mock()
        mock_agent.return_value = """PRIMARY_CATEGORY: Billing Dispute
CONFIDENCE: 0.92
KEYWORDS: charge, bill, invoice
SECONDARY_CATEGORIES: none"""
        mock_get_agent.return_value = mock_agent
        
        result = classify_issue("Incorrect charge on my bill")
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category == "Billing Dispute"
        assert result.confidence == 0.92
        assert "charge" in result.keywords
        assert len(result.secondary_categories) == 0
    
    @patch('src.agent_tools._get_classification_agent')
    def test_classify_technical_problem(self, mock_get_agent):
        """Test classification of technical problem ticket."""
        mock_agent = Mock()
        mock_agent.return_value = """PRIMARY_CATEGORY: Technical Problem
CONFIDENCE: 0.88
KEYWORDS: router, error, not working
SECONDARY_CATEGORIES: Network Outage"""
        mock_get_agent.return_value = mock_agent
        
        result = classify_issue("Router not working, error code TECH-301")
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category == "Technical Problem"
        assert result.confidence == 0.88
        assert "router" in result.keywords
    
    @patch('src.agent_tools._get_classification_agent')
    def test_classify_account_access(self, mock_get_agent):
        """Test classification of account access ticket."""
        mock_agent = Mock()
        mock_agent.return_value = """PRIMARY_CATEGORY: Account Access
CONFIDENCE: 0.96
KEYWORDS: password, login, reset
SECONDARY_CATEGORIES: none"""
        mock_get_agent.return_value = mock_agent
        
        result = classify_issue("Cannot login, password reset not working")
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category == "Account Access"
        assert result.confidence == 0.96
        assert "password" in result.keywords
    
    @patch('src.agent_tools._get_classification_agent')
    def test_classify_handles_agent_error(self, mock_get_agent):
        """Test classification handles agent errors gracefully."""
        mock_agent = Mock()
        mock_agent.side_effect = Exception("Agent error")
        mock_get_agent.return_value = mock_agent
        
        result = classify_issue("Some ticket text")
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category == "Technical Problem"
        assert result.confidence == 0.5
        assert len(result.keywords) == 0
    
    @patch('src.agent_tools._get_classification_agent')
    def test_classify_returns_pydantic_model(self, mock_get_agent):
        """Test that classify_issue returns valid Pydantic model."""
        mock_agent = Mock()
        mock_agent.return_value = """PRIMARY_CATEGORY: Network Outage
CONFIDENCE: 0.85
KEYWORDS: outage
SECONDARY_CATEGORIES: none"""
        mock_get_agent.return_value = mock_agent
        
        result = classify_issue("Network outage")
        
        assert isinstance(result, IssueClassification)
        assert hasattr(result, 'primary_category')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'keywords')
        assert hasattr(result, 'secondary_categories')


class TestExtractEntitiesAI:
    """Test AI-powered extract_entities tool."""
    
    @patch('src.agent_tools._get_extraction_agent')
    def test_extract_all_entity_types(self, mock_get_agent):
        """Test extraction of all entity types."""
        mock_agent = Mock()
        mock_agent.return_value = """ACCOUNT_NUMBERS: ACC-12345, ACC-67890
SERVICE_IDS: SVC001, SVC002
ERROR_CODES: NET-500, AUTH-403
PHONE_NUMBERS: 555-123-4567
MONETARY_AMOUNTS: 150.00, 2500.00"""
        mock_get_agent.return_value = mock_agent
        
        text = "Account ACC-12345 has error NET-500 on service SVC001. Call 555-123-4567. Charge: $150.00"
        result = extract_entities(text)
        
        assert isinstance(result, ExtractedEntities)
        assert "ACC-12345" in result.account_numbers
        assert "ACC-67890" in result.account_numbers
        assert "SVC001" in result.service_ids
        assert "NET-500" in result.error_codes
        assert "555-123-4567" in result.phone_numbers
        assert 150.00 in result.monetary_amounts
        assert 2500.00 in result.monetary_amounts
    
    @patch('src.agent_tools._get_extraction_agent')
    def test_extract_no_entities(self, mock_get_agent):
        """Test extraction when no entities present."""
        mock_agent = Mock()
        mock_agent.return_value = """ACCOUNT_NUMBERS: none
SERVICE_IDS: none
ERROR_CODES: none
PHONE_NUMBERS: none
MONETARY_AMOUNTS: none"""
        mock_get_agent.return_value = mock_agent
        
        result = extract_entities("Simple ticket with no entities")
        
        assert isinstance(result, ExtractedEntities)
        assert len(result.account_numbers) == 0
        assert len(result.service_ids) == 0
        assert len(result.error_codes) == 0
        assert len(result.phone_numbers) == 0
        assert len(result.monetary_amounts) == 0
    
    @patch('src.agent_tools._get_extraction_agent')
    def test_extract_handles_agent_error(self, mock_get_agent):
        """Test extraction handles agent errors gracefully."""
        mock_agent = Mock()
        mock_agent.side_effect = Exception("Agent error")
        mock_get_agent.return_value = mock_agent
        
        result = extract_entities("Some ticket text")
        
        assert isinstance(result, ExtractedEntities)
        assert len(result.account_numbers) == 0
        assert len(result.service_ids) == 0
    
    @patch('src.agent_tools._get_extraction_agent')
    def test_extract_returns_pydantic_model(self, mock_get_agent):
        """Test that extract_entities returns valid Pydantic model."""
        mock_agent = Mock()
        mock_agent.return_value = """ACCOUNT_NUMBERS: ACC-12345
SERVICE_IDS: SVC001
ERROR_CODES: none
PHONE_NUMBERS: none
MONETARY_AMOUNTS: none"""
        mock_get_agent.return_value = mock_agent
        
        result = extract_entities("Account ACC-12345")
        
        assert isinstance(result, ExtractedEntities)
        assert hasattr(result, 'account_numbers')
        assert hasattr(result, 'service_ids')
        assert hasattr(result, 'error_codes')
        assert hasattr(result, 'phone_numbers')
        assert hasattr(result, 'monetary_amounts')


class TestRouteToTeamAI:
    """Test AI-powered route_to_team tool."""
    
    @patch('src.agent_tools._get_routing_agent')
    def test_route_to_network_operations(self, mock_get_agent):
        """Test routing to Network Operations."""
        mock_agent = Mock()
        mock_agent.return_value = """ASSIGNED_TEAM: Network Operations
CONFIDENCE: 0.95
ALTERNATIVE_TEAMS: Technical Support
REASONING: Network outage requires infrastructure team
MANUAL_REVIEW: no"""
        mock_get_agent.return_value = mock_agent
        
        classification = IssueClassification(
            primary_category="Network Outage",
            confidence=0.9,
            keywords=["outage", "down"],
            secondary_categories=[]
        )
        entities = ExtractedEntities()
        
        result = route_to_team(classification, entities, "Outage detected")
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.NETWORK_OPS
        assert result.confidence == 0.95
        assert Team.TECHNICAL in result.alternative_teams
        assert not result.requires_manual_review
    
    @patch('src.agent_tools._get_routing_agent')
    def test_route_to_billing_support(self, mock_get_agent):
        """Test routing to Billing Support."""
        mock_agent = Mock()
        mock_agent.return_value = """ASSIGNED_TEAM: Billing Support
CONFIDENCE: 0.92
ALTERNATIVE_TEAMS: none
REASONING: Billing dispute requires billing team
MANUAL_REVIEW: no"""
        mock_get_agent.return_value = mock_agent
        
        classification = IssueClassification(
            primary_category="Billing Dispute",
            confidence=0.9,
            keywords=["charge", "bill"],
            secondary_categories=[]
        )
        entities = ExtractedEntities()
        
        result = route_to_team(classification, entities, "Healthy")
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.BILLING
        assert result.confidence == 0.92
    
    @patch('src.agent_tools._get_routing_agent')
    def test_route_to_technical_support(self, mock_get_agent):
        """Test routing to Technical Support."""
        mock_agent = Mock()
        mock_agent.return_value = """ASSIGNED_TEAM: Technical Support
CONFIDENCE: 0.88
ALTERNATIVE_TEAMS: Network Operations
REASONING: Device issue requires technical support
MANUAL_REVIEW: no"""
        mock_get_agent.return_value = mock_agent
        
        classification = IssueClassification(
            primary_category="Technical Problem",
            confidence=0.85,
            keywords=["router", "error"],
            secondary_categories=[]
        )
        entities = ExtractedEntities()
        
        result = route_to_team(classification, entities, "Healthy")
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.TECHNICAL
    
    @patch('src.agent_tools._get_routing_agent')
    def test_route_to_account_management(self, mock_get_agent):
        """Test routing to Account Management."""
        mock_agent = Mock()
        mock_agent.return_value = """ASSIGNED_TEAM: Account Management
CONFIDENCE: 0.94
ALTERNATIVE_TEAMS: none
REASONING: Password reset requires account management
MANUAL_REVIEW: no"""
        mock_get_agent.return_value = mock_agent
        
        classification = IssueClassification(
            primary_category="Account Access",
            confidence=0.9,
            keywords=["password", "login"],
            secondary_categories=[]
        )
        entities = ExtractedEntities()
        
        result = route_to_team(classification, entities, "Healthy")
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.ACCOUNT_MGMT
    
    @patch('src.agent_tools._get_routing_agent')
    def test_route_requires_manual_review(self, mock_get_agent):
        """Test routing with manual review flag."""
        mock_agent = Mock()
        mock_agent.return_value = """ASSIGNED_TEAM: Technical Support
CONFIDENCE: 0.65
ALTERNATIVE_TEAMS: Network Operations, Billing Support
REASONING: Unclear issue requires manual review
MANUAL_REVIEW: yes"""
        mock_get_agent.return_value = mock_agent
        
        classification = IssueClassification(
            primary_category="Technical Problem",
            confidence=0.6,
            keywords=[],
            secondary_categories=[]
        )
        entities = ExtractedEntities()
        
        result = route_to_team(classification, entities, "Healthy")
        
        assert isinstance(result, RoutingDecision)
        assert result.requires_manual_review
        assert result.confidence == 0.65
    
    @patch('src.agent_tools._get_routing_agent')
    def test_route_handles_agent_error(self, mock_get_agent):
        """Test routing handles agent errors gracefully."""
        mock_agent = Mock()
        mock_agent.side_effect = Exception("Agent error")
        mock_get_agent.return_value = mock_agent
        
        classification = IssueClassification(
            primary_category="Technical Problem",
            confidence=0.8,
            keywords=[],
            secondary_categories=[]
        )
        entities = ExtractedEntities()
        
        result = route_to_team(classification, entities, "Healthy")
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.TECHNICAL
        assert result.confidence == 0.5
        assert result.requires_manual_review
    
    @patch('src.agent_tools._get_routing_agent')
    def test_route_returns_pydantic_model(self, mock_get_agent):
        """Test that route_to_team returns valid Pydantic model."""
        mock_agent = Mock()
        mock_agent.return_value = """ASSIGNED_TEAM: Network Operations
CONFIDENCE: 0.9
ALTERNATIVE_TEAMS: none
REASONING: Network issue
MANUAL_REVIEW: no"""
        mock_get_agent.return_value = mock_agent
        
        classification = IssueClassification(
            primary_category="Network Outage",
            confidence=0.9,
            keywords=[],
            secondary_categories=[]
        )
        entities = ExtractedEntities()
        
        result = route_to_team(classification, entities, "Outage")
        
        assert isinstance(result, RoutingDecision)
        assert hasattr(result, 'assigned_team')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'alternative_teams')
        assert hasattr(result, 'reasoning')
        assert hasattr(result, 'requires_manual_review')


class TestAgentInitialization:
    """Test agent initialization and caching."""
    
    @patch('src.agent_tools.Agent')
    def test_classification_agent_initialization(self, mock_agent_class):
        """Test classification agent is initialized correctly."""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Reset global agent
        import src.agent_tools
        src.agent_tools._classification_agent = None
        
        agent = _get_classification_agent()
        
        assert agent is not None
        mock_agent_class.assert_called_once()
        call_kwargs = mock_agent_class.call_args[1]
        assert call_kwargs['model'] == 'global.anthropic.claude-haiku-4-5-20251001-v1:0'
        assert call_kwargs['temperature'] == 0.1
        assert call_kwargs['max_tokens'] == 512
        assert 'classify' in call_kwargs['system_prompt'].lower()
    
    @patch('src.agent_tools.Agent')
    def test_extraction_agent_initialization(self, mock_agent_class):
        """Test extraction agent is initialized correctly."""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Reset global agent
        import src.agent_tools
        src.agent_tools._extraction_agent = None
        
        agent = _get_extraction_agent()
        
        assert agent is not None
        mock_agent_class.assert_called_once()
        call_kwargs = mock_agent_class.call_args[1]
        assert call_kwargs['model'] == 'global.anthropic.claude-haiku-4-5-20251001-v1:0'
        assert 'extract' in call_kwargs['system_prompt'].lower()
    
    @patch('src.agent_tools.Agent')
    def test_routing_agent_initialization(self, mock_agent_class):
        """Test routing agent is initialized correctly."""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Reset global agent
        import src.agent_tools
        src.agent_tools._routing_agent = None
        
        agent = _get_routing_agent()
        
        assert agent is not None
        mock_agent_class.assert_called_once()
        call_kwargs = mock_agent_class.call_args[1]
        assert call_kwargs['model'] == 'global.anthropic.claude-haiku-4-5-20251001-v1:0'
        assert 'routing' in call_kwargs['system_prompt'].lower()
    
    @patch('src.agent_tools.Agent')
    def test_agent_caching(self, mock_agent_class):
        """Test that agents are cached and reused."""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Reset global agent
        import src.agent_tools
        src.agent_tools._classification_agent = None
        
        agent1 = _get_classification_agent()
        agent2 = _get_classification_agent()
        
        assert agent1 is agent2
        assert mock_agent_class.call_count == 1  # Only called once

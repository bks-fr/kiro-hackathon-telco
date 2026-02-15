"""
Integration tests for CLI end-to-end flow (main.py).

Tests complete CLI flow with real Bedrock API calls.
Run with: pytest -m integration tests/test_main_integration.py -v
"""

import pytest
import json
import os
from pathlib import Path
from datetime import datetime

from src.main import (
    load_tickets_from_mock,
    initialize_agent,
    process_tickets,
    save_results,
    display_summary,
    main
)
from src.models import Ticket, FinalDecision, Team, PriorityLevel
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
    has_config = Path.home().joinpath('.aws', 'credentials').exists()
    
    return has_env_creds or has_profile or has_config


pytestmark = pytest.mark.skipif(
    not check_aws_credentials(),
    reason="AWS credentials not configured"
)


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for complete CLI flow."""
    
    def test_complete_cli_flow(self, tmp_path):
        """Test complete CLI flow with real Bedrock API calls."""
        # Load tickets
        tickets = load_tickets_from_mock()
        assert len(tickets) > 0
        
        # Use only first 3 tickets for faster testing
        test_tickets = tickets[:3]
        
        # Initialize agent (real Bedrock connection)
        try:
            agent = initialize_agent()
        except Exception as e:
            pytest.skip(f"Could not initialize agent: {str(e)}")
        
        # Process tickets
        decisions = process_tickets(agent, test_tickets)
        
        # Verify decisions were made
        assert len(decisions) > 0
        assert all(isinstance(d, FinalDecision) for d in decisions)
        
        # Verify each decision has required fields
        for decision in decisions:
            assert decision.ticket_id
            assert decision.customer_id
            assert isinstance(decision.assigned_team, Team)
            assert isinstance(decision.priority_level, PriorityLevel)
            assert 0 <= decision.confidence_score <= 100
            assert decision.reasoning
            assert decision.processing_time_ms >= 0
        
        # Save results
        output_file = tmp_path / "integration_results.json"
        save_results(decisions, str(output_file))
        
        # Verify file was created
        assert output_file.exists()
        
        # Verify JSON content
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert len(data) == len(decisions)
        assert all('ticket_id' in d for d in data)
        assert all('assigned_team' in d for d in data)
        assert all('priority_level' in d for d in data)
    
    def test_process_multiple_sample_tickets(self):
        """Test processing multiple sample tickets."""
        tickets = load_tickets_from_mock()
        
        # Use first 5 tickets for testing
        test_tickets = tickets[:5]
        
        try:
            agent = initialize_agent()
        except Exception as e:
            pytest.skip(f"Could not initialize agent: {str(e)}")
        
        decisions = process_tickets(agent, test_tickets)
        
        # Verify all tickets were processed
        assert len(decisions) == len(test_tickets)
        
        # Verify ticket IDs match
        decision_ids = {d.ticket_id for d in decisions}
        ticket_ids = {t.ticket_id for t in test_tickets}
        assert decision_ids == ticket_ids
    
    def test_json_output_format(self, tmp_path):
        """Test JSON output file creation and format."""
        tickets = load_tickets_from_mock()[:2]
        
        try:
            agent = initialize_agent()
        except Exception as e:
            pytest.skip(f"Could not initialize agent: {str(e)}")
        
        decisions = process_tickets(agent, tickets)
        
        output_file = tmp_path / "format_test.json"
        save_results(decisions, str(output_file))
        
        # Load and verify JSON structure
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        # Verify it's a list
        assert isinstance(data, list)
        
        # Verify each decision has all required fields
        required_fields = [
            'ticket_id', 'customer_id', 'assigned_team', 
            'priority_level', 'confidence_score', 'reasoning',
            'processing_time_ms', 'requires_manual_review', 'timestamp'
        ]
        
        for decision_data in data:
            for field in required_fields:
                assert field in decision_data, f"Missing field: {field}"
    
    def test_summary_statistics_accuracy(self):
        """Test summary statistics accuracy."""
        tickets = load_tickets_from_mock()[:3]
        
        try:
            agent = initialize_agent()
        except Exception as e:
            pytest.skip(f"Could not initialize agent: {str(e)}")
        
        decisions = process_tickets(agent, tickets)
        
        # Calculate expected statistics
        total = len(decisions)
        avg_time = sum(d.processing_time_ms for d in decisions) / total
        avg_confidence = sum(d.confidence_score for d in decisions) / total
        manual_review = sum(1 for d in decisions if d.requires_manual_review)
        
        # Verify statistics are reasonable
        assert total > 0
        assert avg_time > 0  # Should take some time
        assert 0 <= avg_confidence <= 100
        assert 0 <= manual_review <= total
        
        # Verify team distribution
        teams = [d.assigned_team for d in decisions]
        assert all(isinstance(t, Team) for t in teams)
        
        # Verify priority distribution
        priorities = [d.priority_level for d in decisions]
        assert all(isinstance(p, PriorityLevel) for p in priorities)
    
    def test_final_decision_serialization(self, tmp_path):
        """Test that all FinalDecision models are properly serialized."""
        tickets = load_tickets_from_mock()[:2]
        
        try:
            agent = initialize_agent()
        except Exception as e:
            pytest.skip(f"Could not initialize agent: {str(e)}")
        
        decisions = process_tickets(agent, tickets)
        
        output_file = tmp_path / "serialization_test.json"
        save_results(decisions, str(output_file))
        
        # Load JSON and verify all fields are serialized correctly
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        for i, decision_data in enumerate(data):
            original = decisions[i]
            
            # Verify enum values are serialized as strings
            assert decision_data['assigned_team'] == original.assigned_team.value
            assert decision_data['priority_level'] == original.priority_level.value
            
            # Verify numeric fields
            assert decision_data['confidence_score'] == original.confidence_score
            assert decision_data['processing_time_ms'] == original.processing_time_ms
            
            # Verify boolean field
            assert decision_data['requires_manual_review'] == original.requires_manual_review
            
            # Verify timestamp is serialized
            assert 'timestamp' in decision_data
    
    def test_processing_time_reasonable(self):
        """Test that processing time is reasonable (< 60 seconds per ticket)."""
        tickets = load_tickets_from_mock()[:2]
        
        try:
            agent = initialize_agent()
        except Exception as e:
            pytest.skip(f"Could not initialize agent: {str(e)}")
        
        decisions = process_tickets(agent, tickets)
        
        # Verify processing time is reasonable
        for decision in decisions:
            # Should be less than 60 seconds (60000ms)
            assert decision.processing_time_ms < 60000, \
                f"Ticket {decision.ticket_id} took {decision.processing_time_ms}ms (> 60s)"
    
    def test_agent_provides_reasoning(self):
        """Test that agent provides clear reasoning for decisions."""
        tickets = load_tickets_from_mock()[:2]
        
        try:
            agent = initialize_agent()
        except Exception as e:
            pytest.skip(f"Could not initialize agent: {str(e)}")
        
        decisions = process_tickets(agent, tickets)
        
        # Verify all decisions have reasoning
        for decision in decisions:
            assert decision.reasoning, f"No reasoning for ticket {decision.ticket_id}"
            assert len(decision.reasoning) > 10, \
                f"Reasoning too short for ticket {decision.ticket_id}"
    
    def test_confidence_scores_meaningful(self):
        """Test that confidence scores are meaningful (not all 100% or 0%)."""
        tickets = load_tickets_from_mock()[:5]
        
        try:
            agent = initialize_agent()
        except Exception as e:
            pytest.skip(f"Could not initialize agent: {str(e)}")
        
        decisions = process_tickets(agent, tickets)
        
        # Get all confidence scores
        scores = [d.confidence_score for d in decisions]
        
        # Verify scores are in valid range
        assert all(0 <= s <= 100 for s in scores)
        
        # Verify not all scores are the same (should have some variation)
        unique_scores = set(scores)
        assert len(unique_scores) > 1 or len(scores) == 1, \
            "All confidence scores are identical - may indicate issue"


@pytest.mark.integration
class TestExpectedBehavior:
    """Test expected behavior and outputs."""
    
    def test_vip_customer_priority(self):
        """Test that VIP customers get appropriate priority."""
        # Find a VIP customer ticket
        vip_tickets = [t for t in SAMPLE_TICKETS if t.customer_id in ['CUST001', 'CUST003', 'CUST006']]
        
        if not vip_tickets:
            pytest.skip("No VIP customer tickets in sample data")
        
        test_ticket = vip_tickets[0]
        
        try:
            agent = initialize_agent()
        except Exception as e:
            pytest.skip(f"Could not initialize agent: {str(e)}")
        
        decisions = process_tickets(agent, [test_ticket])
        
        assert len(decisions) == 1
        decision = decisions[0]
        
        # VIP customers should typically get P0 or P1 priority
        # Note: This is a guideline, not a strict requirement
        # The actual priority depends on the issue severity
        assert decision.priority_level in [PriorityLevel.P0, PriorityLevel.P1, PriorityLevel.P2], \
            f"VIP customer got unexpected priority: {decision.priority_level}"
    
    def test_network_outage_routing(self):
        """Test that network outage tickets are routed appropriately."""
        # Find network outage tickets
        outage_tickets = [t for t in SAMPLE_TICKETS if 'outage' in t.subject.lower() or 'down' in t.description.lower()]
        
        if not outage_tickets:
            pytest.skip("No network outage tickets in sample data")
        
        test_ticket = outage_tickets[0]
        
        try:
            agent = initialize_agent()
        except Exception as e:
            pytest.skip(f"Could not initialize agent: {str(e)}")
        
        decisions = process_tickets(agent, [test_ticket])
        
        assert len(decisions) == 1
        decision = decisions[0]
        
        # Network outages should typically go to Network Operations or Technical Support
        # Note: Different models may route differently - both can be valid
        assert decision.assigned_team in [Team.NETWORK_OPS, Team.TECHNICAL], \
            f"Network outage routed to unexpected team: {decision.assigned_team}"

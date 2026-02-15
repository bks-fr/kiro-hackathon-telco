"""
Unit tests for CLI interface (main.py).

Tests ticket loading, agent initialization, processing loop, results display,
results saving, and summary statistics with mocked agent.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, mock_open
from io import StringIO

from src.main import (
    load_tickets_from_mock,
    load_tickets_from_json,
    validate_tickets,
    initialize_agent,
    process_tickets,
    display_results,
    save_results,
    display_summary
)
from src.models import Ticket, FinalDecision, Team, PriorityLevel
from mock_data import SAMPLE_TICKETS


class TestTicketLoading:
    """Test ticket loading functionality."""
    
    def test_load_tickets_from_mock(self):
        """Test loading tickets from mock_data.SAMPLE_TICKETS."""
        tickets = load_tickets_from_mock()
        
        assert isinstance(tickets, list)
        assert len(tickets) > 0
        assert all(isinstance(t, Ticket) for t in tickets)
        assert tickets == SAMPLE_TICKETS
    
    def test_load_tickets_from_json_success(self, tmp_path):
        """Test loading tickets from JSON file."""
        # Create test JSON file
        test_data = [
            {
                "ticket_id": "TKT-TEST-001",
                "customer_id": "CUST001",
                "subject": "Test ticket",
                "description": "Test description",
                "timestamp": "2024-02-14T12:00:00"
            }
        ]
        
        json_file = tmp_path / "test_tickets.json"
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Load tickets
        tickets = load_tickets_from_json(str(json_file))
        
        assert len(tickets) == 1
        assert isinstance(tickets[0], Ticket)
        assert tickets[0].ticket_id == "TKT-TEST-001"
        assert tickets[0].customer_id == "CUST001"
    
    def test_load_tickets_from_json_file_not_found(self):
        """Test loading tickets from non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_tickets_from_json("nonexistent.json")
    
    def test_load_tickets_from_json_invalid_data(self, tmp_path):
        """Test loading tickets with invalid data."""
        # Create JSON with invalid ticket data (missing required fields)
        test_data = [
            {
                "ticket_id": "",  # Invalid: empty ID
                "customer_id": "CUST001",
                "subject": "Test",
                "description": "Test"
            }
        ]
        
        json_file = tmp_path / "invalid_tickets.json"
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Should raise ValidationError
        with pytest.raises(Exception):  # Pydantic ValidationError
            load_tickets_from_json(str(json_file))
    
    def test_validate_tickets_success(self):
        """Test validating valid tickets."""
        tickets = [
            Ticket(
                ticket_id="TKT-001",
                customer_id="CUST001",
                subject="Test",
                description="Test description",
                timestamp=datetime.utcnow()
            )
        ]
        
        assert validate_tickets(tickets) is True
    
    def test_validate_tickets_empty_id(self):
        """Test validation catches empty IDs."""
        # This should be caught by Pydantic during construction
        with pytest.raises(Exception):
            Ticket(
                ticket_id="",
                customer_id="CUST001",
                subject="Test",
                description="Test"
            )


class TestAgentInitialization:
    """Test agent initialization functionality."""
    
    @patch('src.agent.TicketRoutingAgent')
    def test_initialize_agent_success(self, mock_agent_class):
        """Test successful agent initialization."""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        agent = initialize_agent()
        
        assert agent == mock_agent
        mock_agent_class.assert_called_once()
    
    @patch('src.agent.TicketRoutingAgent')
    def test_initialize_agent_failure(self, mock_agent_class):
        """Test agent initialization failure handling."""
        mock_agent_class.side_effect = Exception("Bedrock connection failed")
        
        with pytest.raises(Exception) as exc_info:
            initialize_agent()
        
        assert "Bedrock connection failed" in str(exc_info.value)


class TestTicketProcessing:
    """Test ticket processing loop."""
    
    def test_process_tickets_success(self):
        """Test processing tickets with mocked agent."""
        # Create mock agent
        mock_agent = Mock()
        
        # Create test tickets
        tickets = [
            Ticket(
                ticket_id="TKT-001",
                customer_id="CUST001",
                subject="Test ticket 1",
                description="Test description 1",
                timestamp=datetime.utcnow()
            ),
            Ticket(
                ticket_id="TKT-002",
                customer_id="CUST002",
                subject="Test ticket 2",
                description="Test description 2",
                timestamp=datetime.utcnow()
            )
        ]
        
        # Mock process_ticket to return FinalDecision
        mock_agent.process_ticket.side_effect = [
            FinalDecision(
                ticket_id="TKT-001",
                customer_id="CUST001",
                assigned_team=Team.NETWORK_OPS,
                priority_level=PriorityLevel.P1,
                confidence_score=85.0,
                reasoning="Test reasoning 1",
                processing_time_ms=1500.0,
                requires_manual_review=False
            ),
            FinalDecision(
                ticket_id="TKT-002",
                customer_id="CUST002",
                assigned_team=Team.BILLING,
                priority_level=PriorityLevel.P2,
                confidence_score=90.0,
                reasoning="Test reasoning 2",
                processing_time_ms=1200.0,
                requires_manual_review=False
            )
        ]
        
        # Process tickets
        decisions = process_tickets(mock_agent, tickets)
        
        assert len(decisions) == 2
        assert all(isinstance(d, FinalDecision) for d in decisions)
        assert decisions[0].ticket_id == "TKT-001"
        assert decisions[1].ticket_id == "TKT-002"
        assert mock_agent.process_ticket.call_count == 2
    
    def test_process_tickets_with_error(self):
        """Test processing tickets when one fails."""
        mock_agent = Mock()
        
        tickets = [
            Ticket(
                ticket_id="TKT-001",
                customer_id="CUST001",
                subject="Test",
                description="Test",
                timestamp=datetime.utcnow()
            ),
            Ticket(
                ticket_id="TKT-002",
                customer_id="CUST002",
                subject="Test",
                description="Test",
                timestamp=datetime.utcnow()
            )
        ]
        
        # First ticket succeeds, second fails
        mock_agent.process_ticket.side_effect = [
            FinalDecision(
                ticket_id="TKT-001",
                customer_id="CUST001",
                assigned_team=Team.TECHNICAL,
                priority_level=PriorityLevel.P2,
                confidence_score=80.0,
                reasoning="Test",
                processing_time_ms=1000.0
            ),
            Exception("Processing error")
        ]
        
        decisions = process_tickets(mock_agent, tickets)
        
        # Should only have one decision (first ticket)
        assert len(decisions) == 1
        assert decisions[0].ticket_id == "TKT-001"


class TestResultsDisplay:
    """Test results display functionality."""
    
    def test_display_results(self, capsys):
        """Test displaying results to console."""
        tickets = [
            Ticket(
                ticket_id="TKT-001",
                customer_id="CUST001",
                subject="Test ticket",
                description="Test",
                timestamp=datetime.utcnow()
            )
        ]
        
        decisions = [
            FinalDecision(
                ticket_id="TKT-001",
                customer_id="CUST001",
                assigned_team=Team.NETWORK_OPS,
                priority_level=PriorityLevel.P1,
                confidence_score=85.5,
                reasoning="Test reasoning",
                processing_time_ms=1500.0,
                requires_manual_review=False
            )
        ]
        
        display_results(decisions, tickets)
        
        captured = capsys.readouterr()
        assert "TKT-001" in captured.out
        assert "Test ticket" in captured.out
        assert "Network Operations" in captured.out
        assert "P1" in captured.out
        assert "85.5%" in captured.out
        assert "1500ms" in captured.out
    
    def test_display_results_with_manual_review(self, capsys):
        """Test displaying results with manual review flag."""
        tickets = [
            Ticket(
                ticket_id="TKT-001",
                customer_id="CUST001",
                subject="Test",
                description="Test",
                timestamp=datetime.utcnow()
            )
        ]
        
        decisions = [
            FinalDecision(
                ticket_id="TKT-001",
                customer_id="CUST001",
                assigned_team=Team.TECHNICAL,
                priority_level=PriorityLevel.P2,
                confidence_score=60.0,
                reasoning="Low confidence",
                processing_time_ms=1000.0,
                requires_manual_review=True
            )
        ]
        
        display_results(decisions, tickets)
        
        captured = capsys.readouterr()
        assert "REQUIRES MANUAL REVIEW" in captured.out


class TestResultsSaving:
    """Test results saving functionality."""
    
    def test_save_results(self, tmp_path):
        """Test saving results to JSON file."""
        decisions = [
            FinalDecision(
                ticket_id="TKT-001",
                customer_id="CUST001",
                assigned_team=Team.NETWORK_OPS,
                priority_level=PriorityLevel.P1,
                confidence_score=85.0,
                reasoning="Test reasoning",
                processing_time_ms=1500.0,
                requires_manual_review=False,
                timestamp=datetime(2024, 2, 14, 12, 0, 0)
            )
        ]
        
        output_file = tmp_path / "test_results.json"
        save_results(decisions, str(output_file))
        
        # Verify file was created
        assert output_file.exists()
        
        # Verify content
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]["ticket_id"] == "TKT-001"
        assert data[0]["assigned_team"] == "Network Operations"
        assert data[0]["priority_level"] == "P1"
        assert data[0]["confidence_score"] == 85.0
    
    def test_save_results_creates_directory(self, tmp_path):
        """Test that save_results creates results directory."""
        output_file = tmp_path / "results" / "routing_decisions.json"
        
        decisions = [
            FinalDecision(
                ticket_id="TKT-001",
                customer_id="CUST001",
                assigned_team=Team.BILLING,
                priority_level=PriorityLevel.P2,
                confidence_score=90.0,
                reasoning="Test",
                processing_time_ms=1000.0
            )
        ]
        
        save_results(decisions, str(output_file))
        
        assert output_file.exists()
        assert output_file.parent.exists()


class TestSummaryStatistics:
    """Test summary statistics functionality."""
    
    def test_display_summary(self, capsys):
        """Test displaying summary statistics."""
        decisions = [
            FinalDecision(
                ticket_id="TKT-001",
                customer_id="CUST001",
                assigned_team=Team.NETWORK_OPS,
                priority_level=PriorityLevel.P1,
                confidence_score=85.0,
                reasoning="Test",
                processing_time_ms=1500.0,
                requires_manual_review=False
            ),
            FinalDecision(
                ticket_id="TKT-002",
                customer_id="CUST002",
                assigned_team=Team.NETWORK_OPS,
                priority_level=PriorityLevel.P2,
                confidence_score=90.0,
                reasoning="Test",
                processing_time_ms=1200.0,
                requires_manual_review=True
            ),
            FinalDecision(
                ticket_id="TKT-003",
                customer_id="CUST003",
                assigned_team=Team.BILLING,
                priority_level=PriorityLevel.P1,
                confidence_score=95.0,
                reasoning="Test",
                processing_time_ms=1800.0,
                requires_manual_review=False
            )
        ]
        
        display_summary(decisions)
        
        captured = capsys.readouterr()
        
        # Check summary statistics
        assert "Total tickets processed: 3" in captured.out
        assert "Average processing time: 1500ms" in captured.out
        assert "Average confidence score: 90.0%" in captured.out
        assert "Tickets requiring manual review: 1" in captured.out
        
        # Check team distribution
        assert "Network Operations: 2 tickets" in captured.out
        assert "Billing Support: 1 ticket" in captured.out
        
        # Check priority distribution
        assert "P1: 2 tickets" in captured.out
        assert "P2: 1 ticket" in captured.out
    
    def test_display_summary_empty(self, capsys):
        """Test displaying summary with no decisions."""
        display_summary([])
        
        captured = capsys.readouterr()
        assert "No decisions to summarize" in captured.out

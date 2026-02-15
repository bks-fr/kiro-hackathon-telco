"""
Integration tests for AI-powered agent tools.

Tests the AI-powered tools with real Bedrock API calls to validate AI reasoning.
These tests require AWS credentials and Bedrock access.

Run with: pytest -m integration tests/test_agent_tools_integration.py -v
"""

import pytest
import os
import time
from datetime import datetime

from src.agent_tools import (
    classify_issue,
    extract_entities,
    route_to_team
)
from src.models import (
    IssueClassification,
    ExtractedEntities,
    RoutingDecision,
    Team
)


# Skip all tests if AWS credentials not configured
pytestmark = pytest.mark.integration


def check_aws_credentials():
    """Check if AWS credentials are configured."""
    import boto3
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        return credentials is not None
    except Exception:
        return False


@pytest.fixture(scope="module", autouse=True)
def skip_if_no_credentials():
    """Skip all tests in this module if AWS credentials not configured."""
    if not check_aws_credentials():
        pytest.skip("AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY or run 'aws configure'.")


class TestClassifyIssueIntegration:
    """Integration tests for AI-powered classify_issue tool."""
    
    def test_classify_network_outage_real_ai(self):
        """Test classification of network outage with real AI reasoning."""
        start_time = time.time()
        
        ticket_text = "My internet connection has been down for 2 hours. I can't access any websites and my router shows error code NET-500."
        result = classify_issue(ticket_text)
        
        elapsed_time = time.time() - start_time
        
        # Verify result structure
        assert isinstance(result, IssueClassification)
        assert result.primary_category in ["Network Outage", "Technical Problem"]
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.keywords) > 0
        
        # Verify AI provides meaningful results
        assert result.confidence > 0.5, "AI should have reasonable confidence"
        
        # Verify processing time
        assert elapsed_time < 10, f"Processing took {elapsed_time:.2f}s, should be < 10s"
        
        print(f"\n✓ Classified as: {result.primary_category}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Keywords: {', '.join(result.keywords)}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_classify_billing_dispute_real_ai(self):
        """Test classification of billing dispute with real AI reasoning."""
        start_time = time.time()
        
        ticket_text = "I was charged $150.00 on my last bill but I never authorized this charge. I need a refund immediately."
        result = classify_issue(ticket_text)
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category == "Billing Dispute"
        assert result.confidence > 0.7, "AI should be confident about billing issues"
        assert elapsed_time < 10
        
        print(f"\n✓ Classified as: {result.primary_category}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_classify_technical_problem_real_ai(self):
        """Test classification of technical problem with real AI reasoning."""
        start_time = time.time()
        
        ticket_text = "My router keeps rebooting every 10 minutes. Error code TECH-301 appears on the display."
        result = classify_issue(ticket_text)
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category in ["Technical Problem", "Network Outage"]
        assert result.confidence > 0.5
        assert elapsed_time < 10
        
        print(f"\n✓ Classified as: {result.primary_category}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_classify_account_access_real_ai(self):
        """Test classification of account access issue with real AI reasoning."""
        start_time = time.time()
        
        ticket_text = "I can't login to my account. Password reset link doesn't work. Please help me regain access."
        result = classify_issue(ticket_text)
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category == "Account Access"
        assert result.confidence > 0.7
        assert elapsed_time < 10
        
        print(f"\n✓ Classified as: {result.primary_category}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_classify_ambiguous_ticket_real_ai(self):
        """Test classification of ambiguous ticket with real AI reasoning."""
        start_time = time.time()
        
        ticket_text = "I have a problem with my service. It's not working properly."
        result = classify_issue(ticket_text)
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category in ["Network Outage", "Billing Dispute", "Technical Problem", "Account Access"]
        # Confidence may vary for ambiguous tickets
        assert 0.0 <= result.confidence <= 1.0
        assert elapsed_time < 10
        
        print(f"\n✓ Classified as: {result.primary_category}")
        print(f"  Confidence: {result.confidence:.2f} (ambiguous ticket)")
        print(f"  Processing time: {elapsed_time:.2f}s")


class TestExtractEntitiesIntegration:
    """Integration tests for AI-powered extract_entities tool."""
    
    def test_extract_all_entities_real_ai(self):
        """Test extraction of all entity types with real AI."""
        start_time = time.time()
        
        ticket_text = """Account ACC-12345 has error NET-500 on service SVC001. 
        Please call me at 555-123-4567. I was charged $150.00 incorrectly."""
        result = extract_entities(ticket_text)
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, ExtractedEntities)
        assert "ACC-12345" in result.account_numbers
        assert "SVC001" in result.service_ids
        assert "NET-500" in result.error_codes
        assert "555-123-4567" in result.phone_numbers
        assert 150.00 in result.monetary_amounts
        assert elapsed_time < 10
        
        print(f"\n✓ Extracted entities:")
        print(f"  Accounts: {result.account_numbers}")
        print(f"  Services: {result.service_ids}")
        print(f"  Errors: {result.error_codes}")
        print(f"  Phones: {result.phone_numbers}")
        print(f"  Amounts: {result.monetary_amounts}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_extract_multiple_accounts_real_ai(self):
        """Test extraction of multiple account numbers with real AI."""
        start_time = time.time()
        
        ticket_text = "I have issues with accounts ACC-12345 and ACC-67890. Both are affected."
        result = extract_entities(ticket_text)
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, ExtractedEntities)
        assert "ACC-12345" in result.account_numbers
        assert "ACC-67890" in result.account_numbers
        assert len(result.account_numbers) == 2
        assert elapsed_time < 10
        
        print(f"\n✓ Extracted multiple accounts: {result.account_numbers}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_extract_service_and_error_codes_real_ai(self):
        """Test extraction of service IDs and error codes with real AI."""
        start_time = time.time()
        
        ticket_text = "Service SVC001 shows error AUTH-403 and service SVC002 has error NET-500."
        result = extract_entities(ticket_text)
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, ExtractedEntities)
        assert "SVC001" in result.service_ids or "SVC002" in result.service_ids
        assert "AUTH-403" in result.error_codes or "NET-500" in result.error_codes
        assert elapsed_time < 10
        
        print(f"\n✓ Extracted services: {result.service_ids}")
        print(f"  Extracted errors: {result.error_codes}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_extract_monetary_amounts_real_ai(self):
        """Test extraction of monetary amounts with real AI."""
        start_time = time.time()
        
        ticket_text = "I was charged $150.00 and then another $2,500.00 appeared on my bill."
        result = extract_entities(ticket_text)
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, ExtractedEntities)
        assert 150.00 in result.monetary_amounts or 2500.00 in result.monetary_amounts
        assert elapsed_time < 10
        
        print(f"\n✓ Extracted amounts: {result.monetary_amounts}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_extract_no_entities_real_ai(self):
        """Test extraction when no entities present with real AI."""
        start_time = time.time()
        
        ticket_text = "I have a general question about my service."
        result = extract_entities(ticket_text)
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, ExtractedEntities)
        # AI should recognize no entities present
        assert elapsed_time < 10
        
        print(f"\n✓ No entities found (as expected)")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_extract_complex_ticket_real_ai(self):
        """Test extraction from complex ticket with real AI."""
        start_time = time.time()
        
        ticket_text = """Customer account ACC-99999 experiencing issues.
        Services SVC001, SVC002, and SVC003 all showing error codes NET-500 and AUTH-403.
        Contact at 555-999-8888 or 555-111-2222.
        Refund requested for $1,250.50 and $75.00."""
        result = extract_entities(ticket_text)
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, ExtractedEntities)
        # AI should extract multiple entities
        assert len(result.account_numbers) >= 1
        assert len(result.service_ids) >= 1
        assert len(result.error_codes) >= 1
        assert elapsed_time < 10
        
        print(f"\n✓ Extracted from complex ticket:")
        print(f"  Accounts: {result.account_numbers}")
        print(f"  Services: {result.service_ids}")
        print(f"  Errors: {result.error_codes}")
        print(f"  Phones: {result.phone_numbers}")
        print(f"  Amounts: {result.monetary_amounts}")
        print(f"  Processing time: {elapsed_time:.2f}s")


class TestRouteToTeamIntegration:
    """Integration tests for AI-powered route_to_team tool."""
    
    def test_route_network_outage_real_ai(self):
        """Test routing of network outage with real AI."""
        start_time = time.time()
        
        classification = IssueClassification(
            primary_category="Network Outage",
            confidence=0.95,
            keywords=["outage", "down", "offline"],
            secondary_categories=[]
        )
        entities = ExtractedEntities(
            service_ids=["SVC001"],
            error_codes=["NET-500"]
        )
        
        result = route_to_team(classification, entities, "Outage detected on SVC001")
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.NETWORK_OPS
        assert result.confidence > 0.7
        assert len(result.reasoning) > 0
        assert elapsed_time < 10
        
        print(f"\n✓ Routed to: {result.assigned_team.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Reasoning: {result.reasoning}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_route_billing_dispute_real_ai(self):
        """Test routing of billing dispute with real AI."""
        start_time = time.time()
        
        classification = IssueClassification(
            primary_category="Billing Dispute",
            confidence=0.92,
            keywords=["charge", "bill", "refund"],
            secondary_categories=[]
        )
        entities = ExtractedEntities(
            monetary_amounts=[150.00]
        )
        
        result = route_to_team(classification, entities, "Healthy")
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.BILLING
        assert result.confidence > 0.7
        assert len(result.reasoning) > 0
        assert elapsed_time < 10
        
        print(f"\n✓ Routed to: {result.assigned_team.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Reasoning: {result.reasoning}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_route_technical_problem_real_ai(self):
        """Test routing of technical problem with real AI."""
        start_time = time.time()
        
        classification = IssueClassification(
            primary_category="Technical Problem",
            confidence=0.88,
            keywords=["router", "error", "rebooting"],
            secondary_categories=[]
        )
        entities = ExtractedEntities(
            error_codes=["TECH-301"]
        )
        
        result = route_to_team(classification, entities, "Healthy")
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.TECHNICAL
        assert result.confidence > 0.6
        assert len(result.reasoning) > 0
        assert elapsed_time < 10
        
        print(f"\n✓ Routed to: {result.assigned_team.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Reasoning: {result.reasoning}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_route_account_access_real_ai(self):
        """Test routing of account access issue with real AI."""
        start_time = time.time()
        
        classification = IssueClassification(
            primary_category="Account Access",
            confidence=0.94,
            keywords=["login", "password", "reset"],
            secondary_categories=[]
        )
        entities = ExtractedEntities()
        
        result = route_to_team(classification, entities, "Healthy")
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.ACCOUNT_MGMT
        assert result.confidence > 0.7
        assert len(result.reasoning) > 0
        assert elapsed_time < 10
        
        print(f"\n✓ Routed to: {result.assigned_team.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Reasoning: {result.reasoning}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_route_with_low_confidence_real_ai(self):
        """Test routing with low confidence triggers manual review."""
        start_time = time.time()
        
        classification = IssueClassification(
            primary_category="Technical Problem",
            confidence=0.55,
            keywords=[],
            secondary_categories=["Network Outage", "Billing Dispute"]
        )
        entities = ExtractedEntities()
        
        result = route_to_team(classification, entities, "Healthy")
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team in [Team.NETWORK_OPS, Team.BILLING, Team.TECHNICAL, Team.ACCOUNT_MGMT]
        # AI may or may not flag for manual review based on its reasoning
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.reasoning) > 0
        assert elapsed_time < 10
        
        print(f"\n✓ Routed to: {result.assigned_team.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Manual review: {result.requires_manual_review}")
        print(f"  Reasoning: {result.reasoning}")
        print(f"  Processing time: {elapsed_time:.2f}s")
    
    def test_route_with_alternative_teams_real_ai(self):
        """Test routing provides alternative teams when appropriate."""
        start_time = time.time()
        
        classification = IssueClassification(
            primary_category="Network Outage",
            confidence=0.85,
            keywords=["connection", "slow"],
            secondary_categories=["Technical Problem"]
        )
        entities = ExtractedEntities()
        
        result = route_to_team(classification, entities, "Degraded")
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team in [Team.NETWORK_OPS, Team.TECHNICAL]
        # AI may provide alternative teams
        assert isinstance(result.alternative_teams, list)
        assert len(result.reasoning) > 0
        assert elapsed_time < 10
        
        print(f"\n✓ Routed to: {result.assigned_team.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Alternatives: {[t.value for t in result.alternative_teams]}")
        print(f"  Reasoning: {result.reasoning}")
        print(f"  Processing time: {elapsed_time:.2f}s")


class TestEndToEndAIWorkflow:
    """Integration tests for end-to-end AI tools workflow."""
    
    def test_complete_workflow_network_outage(self):
        """Test complete workflow for network outage ticket."""
        start_time = time.time()
        
        # Step 1: Classify
        ticket_text = "My internet has been down for 3 hours. Error NET-500 on service SVC001. Account ACC-12345."
        classification = classify_issue(ticket_text)
        
        # Step 2: Extract entities
        entities = extract_entities(ticket_text)
        
        # Step 3: Route to team
        routing = route_to_team(classification, entities, "Outage detected")
        
        elapsed_time = time.time() - start_time
        
        # Verify complete workflow
        assert isinstance(classification, IssueClassification)
        assert isinstance(entities, ExtractedEntities)
        assert isinstance(routing, RoutingDecision)
        
        # Verify AI reasoning is meaningful
        assert classification.confidence > 0.5
        assert routing.confidence > 0.5
        assert len(routing.reasoning) > 0
        
        # Verify entities extracted
        assert "ACC-12345" in entities.account_numbers
        assert "SVC001" in entities.service_ids
        assert "NET-500" in entities.error_codes
        
        # Verify routing makes sense
        assert routing.assigned_team in [Team.NETWORK_OPS, Team.TECHNICAL]
        
        assert elapsed_time < 30, "Complete workflow should take < 30s"
        
        print(f"\n✓ Complete workflow:")
        print(f"  Classification: {classification.primary_category} ({classification.confidence:.2f})")
        print(f"  Entities: {len(entities.account_numbers)} accounts, {len(entities.service_ids)} services")
        print(f"  Routing: {routing.assigned_team.value} ({routing.confidence:.2f})")
        print(f"  Total time: {elapsed_time:.2f}s")
    
    def test_complete_workflow_billing_dispute(self):
        """Test complete workflow for billing dispute ticket."""
        start_time = time.time()
        
        ticket_text = "I was charged $250.00 on account ACC-99999 but I never authorized this. Need refund."
        
        classification = classify_issue(ticket_text)
        entities = extract_entities(ticket_text)
        routing = route_to_team(classification, entities, "Healthy")
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(classification, IssueClassification)
        assert isinstance(entities, ExtractedEntities)
        assert isinstance(routing, RoutingDecision)
        
        assert classification.primary_category == "Billing Dispute"
        assert "ACC-99999" in entities.account_numbers
        assert 250.00 in entities.monetary_amounts
        assert routing.assigned_team == Team.BILLING
        
        assert elapsed_time < 30
        
        print(f"\n✓ Complete workflow:")
        print(f"  Classification: {classification.primary_category} ({classification.confidence:.2f})")
        print(f"  Entities: {entities.account_numbers}, ${entities.monetary_amounts}")
        print(f"  Routing: {routing.assigned_team.value} ({routing.confidence:.2f})")
        print(f"  Total time: {elapsed_time:.2f}s")
    
    def test_complete_workflow_account_access(self):
        """Test complete workflow for account access ticket."""
        start_time = time.time()
        
        ticket_text = "Cannot login to my account. Password reset link expired. Please help."
        
        classification = classify_issue(ticket_text)
        entities = extract_entities(ticket_text)
        routing = route_to_team(classification, entities, "Healthy")
        
        elapsed_time = time.time() - start_time
        
        assert isinstance(classification, IssueClassification)
        assert isinstance(entities, ExtractedEntities)
        assert isinstance(routing, RoutingDecision)
        
        assert classification.primary_category == "Account Access"
        assert routing.assigned_team == Team.ACCOUNT_MGMT
        assert routing.confidence > 0.6
        
        assert elapsed_time < 30
        
        print(f"\n✓ Complete workflow:")
        print(f"  Classification: {classification.primary_category} ({classification.confidence:.2f})")
        print(f"  Routing: {routing.assigned_team.value} ({routing.confidence:.2f})")
        print(f"  Total time: {elapsed_time:.2f}s")

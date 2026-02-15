"""
Unit tests for agent tools with Pydantic validation.

Tests all 7 agent tools to ensure they return correct Pydantic models
and handle various input scenarios including edge cases and validation.
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.tools import (
    classify_issue,
    extract_entities,
    check_vip_status,
    check_service_status,
    calculate_priority,
    route_to_team,
    get_historical_context
)
from src.models import (
    IssueClassification,
    ExtractedEntities,
    Customer, AccountType,
    ServiceStatus, ServiceHealth, Outage,
    PriorityCalculation, PriorityLevel,
    RoutingDecision, Team,
    HistoricalContext, HistoricalTicket
)


# ============================================================
# Test classify_issue()
# ============================================================

class TestClassifyIssue:
    """Test suite for classify_issue() tool."""
    
    def test_classify_network_outage(self):
        """Test classification of network outage tickets."""
        text = "My internet connection is down and offline. Network outage."
        result = classify_issue(text)
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category == "Network Outage"
        assert result.confidence > 0
        assert len(result.keywords) > 0
        assert "down" in result.keywords or "offline" in result.keywords
    
    def test_classify_billing_dispute(self):
        """Test classification of billing dispute tickets."""
        text = "I was overcharged on my bill. Need refund for incorrect invoice."
        result = classify_issue(text)
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category == "Billing Dispute"
        assert result.confidence > 0
        assert any(kw in result.keywords for kw in ["bill", "invoice", "refund", "overcharged"])
    
    def test_classify_technical_problem(self):
        """Test classification of technical problem tickets."""
        text = "My router is broken and not working. Getting error messages."
        result = classify_issue(text)
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category == "Technical Problem"
        assert result.confidence > 0
        assert any(kw in result.keywords for kw in ["error", "broken", "not working"])
    
    def test_classify_account_access(self):
        """Test classification of account access tickets."""
        text = "Cannot login to my account. Password reset not working."
        result = classify_issue(text)
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category == "Account Access"
        assert result.confidence > 0
        assert any(kw in result.keywords for kw in ["login", "password", "account"])
    
    def test_classify_mixed_categories(self):
        """Test classification with multiple category keywords."""
        text = "Network is down and I also have billing issues with my invoice."
        result = classify_issue(text)
        
        assert isinstance(result, IssueClassification)
        assert result.primary_category in ["Network Outage", "Billing Dispute"]
        assert len(result.secondary_categories) > 0
        assert result.confidence > 0
    
    def test_classify_empty_text(self):
        """Test classification with empty text."""
        result = classify_issue("")
        
        assert isinstance(result, IssueClassification)
        # Empty text will match first category with 0 score
        assert result.primary_category in ["Network Outage", "Billing Dispute", "Technical Problem", "Account Access"]
        assert result.confidence >= 0
    
    def test_classify_returns_valid_pydantic_model(self):
        """Test that classify_issue returns a valid Pydantic model."""
        text = "Internet connection problem"
        result = classify_issue(text)
        
        # Verify it's a Pydantic model
        assert hasattr(result, 'model_dump')
        assert hasattr(result, 'model_dump_json')
        
        # Verify all required fields are present
        data = result.model_dump()
        assert 'primary_category' in data
        assert 'confidence' in data
        assert 'keywords' in data
        assert 'secondary_categories' in data
        
        # Verify confidence is within valid range
        assert 0.0 <= result.confidence <= 1.0


# ============================================================
# Test extract_entities()
# ============================================================

class TestExtractEntities:
    """Test suite for extract_entities() tool."""
    
    def test_extract_account_numbers(self):
        """Test extraction of account numbers."""
        text = "My account ACC-12345 has issues. Also check ACC-67890."
        result = extract_entities(text)
        
        assert isinstance(result, ExtractedEntities)
        assert "ACC-12345" in result.account_numbers
        assert "ACC-67890" in result.account_numbers
        assert len(result.account_numbers) == 2
    
    def test_extract_service_ids(self):
        """Test extraction of service IDs."""
        text = "Service SVC001 is down. Also SVC002 and SVC999 are affected."
        result = extract_entities(text)
        
        assert isinstance(result, ExtractedEntities)
        assert "SVC001" in result.service_ids
        assert "SVC002" in result.service_ids
        assert "SVC999" in result.service_ids
        assert len(result.service_ids) == 3
    
    def test_extract_error_codes(self):
        """Test extraction of error codes."""
        text = "Getting error NET-500 and AUTH-403. Also seeing DB-999."
        result = extract_entities(text)
        
        assert isinstance(result, ExtractedEntities)
        assert "NET-500" in result.error_codes
        assert "AUTH-403" in result.error_codes
        assert "DB-999" in result.error_codes
    
    def test_extract_phone_numbers(self):
        """Test extraction of phone numbers."""
        text = "Call me at 555-123-4567 or 800-999-8888."
        result = extract_entities(text)
        
        assert isinstance(result, ExtractedEntities)
        assert "555-123-4567" in result.phone_numbers
        assert "800-999-8888" in result.phone_numbers
    
    def test_extract_monetary_amounts(self):
        """Test extraction of monetary amounts."""
        text = "Charged $150.00 and $2,500.99 incorrectly. Also $45.50."
        result = extract_entities(text)
        
        assert isinstance(result, ExtractedEntities)
        assert 150.00 in result.monetary_amounts
        assert 2500.99 in result.monetary_amounts
        assert 45.50 in result.monetary_amounts
    
    def test_extract_mixed_entities(self):
        """Test extraction of multiple entity types."""
        text = "Account ACC-12345 has error NET-500 on service SVC001. Call 555-123-4567. Charged $150.00."
        result = extract_entities(text)
        
        assert isinstance(result, ExtractedEntities)
        assert "ACC-12345" in result.account_numbers
        assert "NET-500" in result.error_codes
        assert "SVC001" in result.service_ids
        assert "555-123-4567" in result.phone_numbers
        assert 150.00 in result.monetary_amounts
    
    def test_extract_no_entities(self):
        """Test extraction with no entities present."""
        text = "This is a simple message with no special entities."
        result = extract_entities(text)
        
        assert isinstance(result, ExtractedEntities)
        assert len(result.account_numbers) == 0
        assert len(result.service_ids) == 0
        assert len(result.error_codes) == 0
        assert len(result.phone_numbers) == 0
        assert len(result.monetary_amounts) == 0
    
    def test_extract_returns_valid_pydantic_model(self):
        """Test that extract_entities returns a valid Pydantic model."""
        text = "Account ACC-12345"
        result = extract_entities(text)
        
        # Verify it's a Pydantic model
        assert hasattr(result, 'model_dump')
        data = result.model_dump()
        assert 'account_numbers' in data
        assert 'service_ids' in data
        assert 'error_codes' in data
        assert 'phone_numbers' in data
        assert 'monetary_amounts' in data


# ============================================================
# Test check_vip_status()
# ============================================================

class TestCheckVipStatus:
    """Test suite for check_vip_status() tool."""
    
    def test_check_known_vip_customer(self):
        """Test checking VIP status for known VIP customer."""
        result = check_vip_status('CUST001')
        
        assert isinstance(result, Customer)
        assert result.customer_id == 'CUST001'
        assert result.is_vip is True
        assert result.account_type == AccountType.ENTERPRISE
        assert result.lifetime_value > 0
    
    def test_check_known_non_vip_customer(self):
        """Test checking VIP status for known non-VIP customer."""
        result = check_vip_status('CUST002')
        
        assert isinstance(result, Customer)
        assert result.customer_id == 'CUST002'
        assert result.is_vip is False
        assert result.account_type == AccountType.CONSUMER
    
    def test_check_unknown_customer(self):
        """Test checking VIP status for unknown customer."""
        result = check_vip_status('CUST999')
        
        assert isinstance(result, Customer)
        assert result.customer_id == 'CUST999'
        assert result.is_vip is False
        assert result.account_type == AccountType.CONSUMER
        assert result.lifetime_value == 0.0
        assert result.service_plan == 'Basic'
    
    def test_check_business_account(self):
        """Test checking business account customer."""
        result = check_vip_status('CUST003')
        
        assert isinstance(result, Customer)
        assert result.account_type == AccountType.BUSINESS
        assert result.is_vip is True
    
    def test_check_returns_valid_pydantic_model(self):
        """Test that check_vip_status returns a valid Pydantic model."""
        result = check_vip_status('CUST001')
        
        # Verify it's a Pydantic model
        assert hasattr(result, 'model_dump')
        data = result.model_dump()
        assert 'customer_id' in data
        assert 'is_vip' in data
        assert 'account_type' in data
        assert 'lifetime_value' in data


# ============================================================
# Test check_service_status()
# ============================================================

class TestCheckServiceStatus:
    """Test suite for check_service_status() tool."""
    
    def test_check_healthy_service(self):
        """Test checking status of healthy service."""
        result = check_service_status(['SVC002'])
        
        assert isinstance(result, ServiceStatus)
        assert result.service_health == ServiceHealth.HEALTHY
        assert len(result.active_outages) == 0
    
    def test_check_outage_service(self):
        """Test checking status of service with outage."""
        result = check_service_status(['SVC001'])
        
        assert isinstance(result, ServiceStatus)
        assert result.service_health == ServiceHealth.OUTAGE
        assert len(result.active_outages) > 0
        assert result.active_outages[0].severity == 'Critical'
    
    def test_check_degraded_service(self):
        """Test checking status of degraded service."""
        result = check_service_status(['SVC003'])
        
        assert isinstance(result, ServiceStatus)
        assert result.service_health == ServiceHealth.DEGRADED
        assert len(result.active_outages) > 0
    
    def test_check_multiple_services_with_outage(self):
        """Test checking multiple services where one has outage."""
        result = check_service_status(['SVC001', 'SVC002'])
        
        assert isinstance(result, ServiceStatus)
        assert result.service_health == ServiceHealth.OUTAGE  # Worst health wins
        assert len(result.active_outages) > 0
    
    def test_check_multiple_services_mixed_health(self):
        """Test checking multiple services with mixed health."""
        result = check_service_status(['SVC002', 'SVC003'])
        
        assert isinstance(result, ServiceStatus)
        assert result.service_health == ServiceHealth.DEGRADED
    
    def test_check_empty_service_list(self):
        """Test checking with empty service list."""
        result = check_service_status([])
        
        assert isinstance(result, ServiceStatus)
        assert result.service_health == ServiceHealth.HEALTHY
        assert len(result.active_outages) == 0
    
    def test_check_unknown_service(self):
        """Test checking unknown service."""
        result = check_service_status(['SVC999'])
        
        assert isinstance(result, ServiceStatus)
        assert result.service_health == ServiceHealth.HEALTHY
        assert len(result.active_outages) == 0
    
    def test_check_returns_valid_pydantic_model(self):
        """Test that check_service_status returns a valid Pydantic model."""
        result = check_service_status(['SVC001'])
        
        # Verify it's a Pydantic model
        assert hasattr(result, 'model_dump')
        data = result.model_dump()
        assert 'service_id' in data
        assert 'service_health' in data
        assert 'active_outages' in data


# ============================================================
# Test calculate_priority()
# ============================================================

class TestCalculatePriority:
    """Test suite for calculate_priority() tool."""
    
    def test_calculate_p0_priority_vip_outage(self):
        """Test P0 priority calculation for VIP customer with outage."""
        vip_customer = Customer(
            customer_id='CUST001',
            is_vip=True,
            account_type=AccountType.ENTERPRISE,
            lifetime_value=150000.0,
            service_plan='Enterprise'
        )
        classification = IssueClassification(
            primary_category='Network Outage',
            confidence=0.9,
            keywords=['outage', 'down']
        )
        service_status = ServiceStatus(
            service_id='SVC001',
            service_health=ServiceHealth.OUTAGE,
            active_outages=[
                Outage(
                    service_id='SVC001',
                    severity='Critical',
                    started_at=datetime.utcnow()
                )
            ]
        )
        
        result = calculate_priority(vip_customer, classification, service_status, 2.0)
        
        assert isinstance(result, PriorityCalculation)
        assert result.priority_level == PriorityLevel.P0
        assert result.priority_score >= 80
        assert 'vip_bonus' in result.factors
        assert 'severity' in result.factors
        assert 'outage_impact' in result.factors
    
    def test_calculate_p1_priority_vip_no_outage(self):
        """Test P1 priority calculation for VIP customer without outage."""
        vip_customer = Customer(
            customer_id='CUST001',
            is_vip=True,
            account_type=AccountType.ENTERPRISE,
            lifetime_value=150000.0,
            service_plan='Enterprise'
        )
        classification = IssueClassification(
            primary_category='Technical Problem',
            confidence=0.8,
            keywords=['error']
        )
        service_status = ServiceStatus(
            service_id='SVC002',
            service_health=ServiceHealth.HEALTHY,
            active_outages=[]
        )
        
        result = calculate_priority(vip_customer, classification, service_status, 1.0)
        
        assert isinstance(result, PriorityCalculation)
        # VIP (30) + Technical Problem (20) = 50, which is P2
        assert result.priority_level == PriorityLevel.P2
        assert 40 <= result.priority_score < 60
    
    def test_calculate_p2_priority_standard_customer(self):
        """Test P2 priority calculation for standard customer."""
        standard_customer = Customer(
            customer_id='CUST002',
            is_vip=False,
            account_type=AccountType.CONSUMER,
            lifetime_value=500.0,
            service_plan='Basic'
        )
        classification = IssueClassification(
            primary_category='Technical Problem',
            confidence=0.7,
            keywords=['error']
        )
        service_status = ServiceStatus(
            service_id='SVC002',
            service_health=ServiceHealth.HEALTHY,
            active_outages=[]
        )
        
        result = calculate_priority(standard_customer, classification, service_status, 5.0)
        
        assert isinstance(result, PriorityCalculation)
        # No VIP (0) + Technical Problem (20) = 20, which is P3
        assert result.priority_level == PriorityLevel.P3
        assert result.priority_score < 40
    
    def test_calculate_p3_priority_low_severity(self):
        """Test P3 priority calculation for low severity issue."""
        standard_customer = Customer(
            customer_id='CUST002',
            is_vip=False,
            account_type=AccountType.CONSUMER,
            lifetime_value=500.0,
            service_plan='Basic'
        )
        classification = IssueClassification(
            primary_category='Billing Dispute',
            confidence=0.6,
            keywords=['bill']
        )
        service_status = ServiceStatus(
            service_id='SVC002',
            service_health=ServiceHealth.HEALTHY,
            active_outages=[]
        )
        
        result = calculate_priority(standard_customer, classification, service_status, 1.0)
        
        assert isinstance(result, PriorityCalculation)
        assert result.priority_level == PriorityLevel.P3
        assert result.priority_score < 40
    
    def test_calculate_priority_with_age_penalty(self):
        """Test priority calculation with ticket age penalty."""
        standard_customer = Customer(
            customer_id='CUST002',
            is_vip=False,
            account_type=AccountType.CONSUMER,
            lifetime_value=500.0,
            service_plan='Basic'
        )
        classification = IssueClassification(
            primary_category='Technical Problem',
            confidence=0.7,
            keywords=['error']
        )
        service_status = ServiceStatus(
            service_id='SVC002',
            service_health=ServiceHealth.HEALTHY,
            active_outages=[]
        )
        
        # Old ticket (48+ hours)
        result = calculate_priority(standard_customer, classification, service_status, 50.0)
        
        assert isinstance(result, PriorityCalculation)
        assert 'age_penalty' in result.factors
        assert result.factors['age_penalty'] == 20
    
    def test_calculate_priority_enterprise_bonus(self):
        """Test priority calculation with enterprise account bonus."""
        enterprise_customer = Customer(
            customer_id='CUST005',
            is_vip=False,
            account_type=AccountType.ENTERPRISE,
            lifetime_value=50000.0,
            service_plan='Enterprise'
        )
        classification = IssueClassification(
            primary_category='Network Outage',
            confidence=0.9,
            keywords=['outage']
        )
        service_status = ServiceStatus(
            service_id='SVC001',
            service_health=ServiceHealth.OUTAGE,
            active_outages=[]
        )
        
        result = calculate_priority(enterprise_customer, classification, service_status, 1.0)
        
        assert isinstance(result, PriorityCalculation)
        assert 'enterprise_bonus' in result.factors
        assert result.factors['enterprise_bonus'] == 20
    
    def test_calculate_returns_valid_pydantic_model(self):
        """Test that calculate_priority returns a valid Pydantic model."""
        customer = Customer(
            customer_id='CUST001',
            is_vip=True,
            account_type=AccountType.ENTERPRISE,
            lifetime_value=150000.0,
            service_plan='Enterprise'
        )
        classification = IssueClassification(
            primary_category='Network Outage',
            confidence=0.9,
            keywords=['outage']
        )
        service_status = ServiceStatus(
            service_id='SVC001',
            service_health=ServiceHealth.HEALTHY,
            active_outages=[]
        )
        
        result = calculate_priority(customer, classification, service_status, 1.0)
        
        # Verify it's a Pydantic model
        assert hasattr(result, 'model_dump')
        data = result.model_dump()
        assert 'priority_level' in data
        assert 'priority_score' in data
        assert 'factors' in data
        assert 'reasoning' in data


# ============================================================
# Test route_to_team()
# ============================================================

class TestRouteToTeam:
    """Test suite for route_to_team() tool."""
    
    def test_route_network_outage(self):
        """Test routing for network outage issue."""
        classification = IssueClassification(
            primary_category='Network Outage',
            confidence=0.9,
            keywords=['outage', 'down']
        )
        entities = ExtractedEntities()
        service_status = ServiceStatus(
            service_id='SVC001',
            service_health=ServiceHealth.OUTAGE,
            active_outages=[]
        )
        
        result = route_to_team(classification, entities, service_status)
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.NETWORK_OPS
        assert result.confidence > 0.7
        assert result.requires_manual_review is False
    
    def test_route_billing_dispute(self):
        """Test routing for billing dispute issue."""
        classification = IssueClassification(
            primary_category='Billing Dispute',
            confidence=0.9,
            keywords=['bill', 'charge']
        )
        entities = ExtractedEntities()
        service_status = ServiceStatus(
            service_id='SVC002',
            service_health=ServiceHealth.HEALTHY,
            active_outages=[]
        )
        
        result = route_to_team(classification, entities, service_status)
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.BILLING
        assert result.confidence > 0.7
    
    def test_route_technical_problem(self):
        """Test routing for technical problem issue."""
        classification = IssueClassification(
            primary_category='Technical Problem',
            confidence=0.8,
            keywords=['error', 'broken']
        )
        entities = ExtractedEntities()
        service_status = ServiceStatus(
            service_id='SVC002',
            service_health=ServiceHealth.HEALTHY,
            active_outages=[]
        )
        
        result = route_to_team(classification, entities, service_status)
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.TECHNICAL
        assert result.confidence > 0.5
    
    def test_route_account_access(self):
        """Test routing for account access issue."""
        classification = IssueClassification(
            primary_category='Account Access',
            confidence=0.9,
            keywords=['password', 'login']
        )
        entities = ExtractedEntities()
        service_status = ServiceStatus(
            service_id='SVC002',
            service_health=ServiceHealth.HEALTHY,
            active_outages=[]
        )
        
        result = route_to_team(classification, entities, service_status)
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.ACCOUNT_MGMT
        assert result.confidence > 0.7
    
    def test_route_low_confidence_manual_review(self):
        """Test routing with low confidence triggers manual review."""
        classification = IssueClassification(
            primary_category='Technical Problem',
            confidence=0.5,  # Low confidence
            keywords=['issue']
        )
        entities = ExtractedEntities()
        service_status = ServiceStatus(
            service_id='SVC002',
            service_health=ServiceHealth.HEALTHY,
            active_outages=[]
        )
        
        result = route_to_team(classification, entities, service_status)
        
        assert isinstance(result, RoutingDecision)
        assert result.requires_manual_review is True
        assert result.confidence < 0.7
    
    def test_route_with_alternative_teams(self):
        """Test routing identifies alternative teams."""
        classification = IssueClassification(
            primary_category='Network Outage',
            confidence=0.9,
            keywords=['outage'],
            secondary_categories=['Technical Problem']
        )
        entities = ExtractedEntities()
        service_status = ServiceStatus(
            service_id='SVC001',
            service_health=ServiceHealth.OUTAGE,
            active_outages=[]
        )
        
        result = route_to_team(classification, entities, service_status)
        
        assert isinstance(result, RoutingDecision)
        assert result.assigned_team == Team.NETWORK_OPS
        assert len(result.alternative_teams) > 0
        assert Team.TECHNICAL in result.alternative_teams
    
    def test_route_returns_valid_pydantic_model(self):
        """Test that route_to_team returns a valid Pydantic model."""
        classification = IssueClassification(
            primary_category='Network Outage',
            confidence=0.9,
            keywords=['outage']
        )
        entities = ExtractedEntities()
        service_status = ServiceStatus(
            service_id='SVC001',
            service_health=ServiceHealth.HEALTHY,
            active_outages=[]
        )
        
        result = route_to_team(classification, entities, service_status)
        
        # Verify it's a Pydantic model
        assert hasattr(result, 'model_dump')
        data = result.model_dump()
        assert 'assigned_team' in data
        assert 'confidence' in data
        assert 'alternative_teams' in data
        assert 'reasoning' in data
        assert 'requires_manual_review' in data


# ============================================================
# Test get_historical_context()
# ============================================================

class TestGetHistoricalContext:
    """Test suite for get_historical_context() tool."""
    
    def test_get_history_for_customer_with_tickets(self):
        """Test getting historical context for customer with tickets."""
        result = get_historical_context('CUST001', limit=5)
        
        assert isinstance(result, HistoricalContext)
        assert len(result.recent_tickets) > 0
        assert len(result.common_issues) > 0
        assert isinstance(result.escalation_history, bool)
    
    def test_get_history_for_customer_without_tickets(self):
        """Test getting historical context for customer without tickets."""
        result = get_historical_context('CUST999', limit=5)
        
        assert isinstance(result, HistoricalContext)
        assert len(result.recent_tickets) == 0
        assert len(result.common_issues) == 0
        assert result.escalation_history is False
    
    def test_get_history_with_limit(self):
        """Test getting historical context with ticket limit."""
        result = get_historical_context('CUST001', limit=1)
        
        assert isinstance(result, HistoricalContext)
        assert len(result.recent_tickets) <= 1
    
    def test_get_history_identifies_escalations(self):
        """Test getting historical context identifies escalation history."""
        result = get_historical_context('CUST003', limit=10)
        
        assert isinstance(result, HistoricalContext)
        assert result.escalation_history is True
    
    def test_get_history_identifies_common_issues(self):
        """Test getting historical context identifies common issues."""
        result = get_historical_context('CUST003', limit=10)
        
        assert isinstance(result, HistoricalContext)
        assert len(result.common_issues) > 0
        assert all(isinstance(issue, str) for issue in result.common_issues)
    
    def test_get_history_returns_valid_pydantic_model(self):
        """Test that get_historical_context returns a valid Pydantic model."""
        result = get_historical_context('CUST001', limit=5)
        
        # Verify it's a Pydantic model
        assert hasattr(result, 'model_dump')
        data = result.model_dump()
        assert 'recent_tickets' in data
        assert 'common_issues' in data
        assert 'escalation_history' in data


# ============================================================
# Test Pydantic Validation
# ============================================================

class TestPydanticValidation:
    """Test suite for Pydantic validation across all models."""
    
    def test_issue_classification_confidence_validation(self):
        """Test IssueClassification validates confidence range."""
        # Valid confidence
        valid = IssueClassification(
            primary_category='Network Outage',
            confidence=0.5,
            keywords=['outage']
        )
        assert valid.confidence == 0.5
        
        # Invalid confidence (too high)
        with pytest.raises(ValidationError):
            IssueClassification(
                primary_category='Network Outage',
                confidence=1.5,
                keywords=['outage']
            )
        
        # Invalid confidence (negative)
        with pytest.raises(ValidationError):
            IssueClassification(
                primary_category='Network Outage',
                confidence=-0.1,
                keywords=['outage']
            )
    
    def test_customer_lifetime_value_validation(self):
        """Test Customer validates lifetime_value is non-negative."""
        # Valid lifetime value
        valid = Customer(
            customer_id='CUST001',
            lifetime_value=1000.0,
            service_plan='Basic'
        )
        assert valid.lifetime_value == 1000.0
        
        # Invalid lifetime value (negative)
        with pytest.raises(ValidationError):
            Customer(
                customer_id='CUST001',
                lifetime_value=-100.0,
                service_plan='Basic'
            )
    
    def test_priority_calculation_score_validation(self):
        """Test PriorityCalculation validates priority_score range."""
        # Valid score
        valid = PriorityCalculation(
            priority_level=PriorityLevel.P1,
            priority_score=65.0,
            factors={'vip_bonus': 30},
            reasoning='Test'
        )
        assert valid.priority_score == 65.0
        
        # Invalid score (too high)
        with pytest.raises(ValidationError):
            PriorityCalculation(
                priority_level=PriorityLevel.P1,
                priority_score=150.0,
                factors={},
                reasoning='Test'
            )
        
        # Invalid score (negative)
        with pytest.raises(ValidationError):
            PriorityCalculation(
                priority_level=PriorityLevel.P1,
                priority_score=-10.0,
                factors={},
                reasoning='Test'
            )
    
    def test_routing_decision_confidence_validation(self):
        """Test RoutingDecision validates confidence range."""
        # Valid confidence
        valid = RoutingDecision(
            assigned_team=Team.TECHNICAL,
            confidence=0.8,
            reasoning='Test'
        )
        assert valid.confidence == 0.8
        
        # Invalid confidence (too high)
        with pytest.raises(ValidationError):
            RoutingDecision(
                assigned_team=Team.TECHNICAL,
                confidence=1.5,
                reasoning='Test'
            )
    
    def test_invalid_enum_values(self):
        """Test that invalid enum values are rejected."""
        # Invalid Team enum
        with pytest.raises(ValidationError):
            RoutingDecision(
                assigned_team='Invalid Team',
                confidence=0.8,
                reasoning='Test'
            )
        
        # Invalid PriorityLevel enum
        with pytest.raises(ValidationError):
            PriorityCalculation(
                priority_level='P5',
                priority_score=50.0,
                factors={},
                reasoning='Test'
            )
        
        # Invalid AccountType enum
        with pytest.raises(ValidationError):
            Customer(
                customer_id='CUST001',
                account_type='Premium',
                lifetime_value=1000.0,
                service_plan='Basic'
            )
        
        # Invalid ServiceHealth enum
        with pytest.raises(ValidationError):
            ServiceStatus(
                service_id='SVC001',
                service_health='Unknown',
                active_outages=[]
            )
    
    def test_empty_id_validation(self):
        """Test that empty IDs are rejected by validators."""
        from src.models import Ticket
        
        # Empty ticket_id
        with pytest.raises(ValidationError):
            Ticket(
                ticket_id='',
                customer_id='CUST001',
                subject='Test',
                description='Test description'
            )
        
        # Empty customer_id
        with pytest.raises(ValidationError):
            Ticket(
                ticket_id='TKT-001',
                customer_id='',
                subject='Test',
                description='Test description'
            )
        
        # Whitespace-only ticket_id
        with pytest.raises(ValidationError):
            Ticket(
                ticket_id='   ',
                customer_id='CUST001',
                subject='Test',
                description='Test description'
            )
    
    def test_historical_ticket_resolution_time_validation(self):
        """Test HistoricalTicket validates resolution_time_hours is non-negative."""
        # Valid resolution time
        valid = HistoricalTicket(
            ticket_id='TKT-001',
            issue_type='Network Outage',
            resolution_time_hours=2.5,
            resolved_at=datetime.utcnow()
        )
        assert valid.resolution_time_hours == 2.5
        
        # Invalid resolution time (negative)
        with pytest.raises(ValidationError):
            HistoricalTicket(
                ticket_id='TKT-001',
                issue_type='Network Outage',
                resolution_time_hours=-1.0,
                resolved_at=datetime.utcnow()
            )
    
    def test_pydantic_model_serialization(self):
        """Test that all models can be serialized and deserialized."""
        # Create a complex model
        classification = IssueClassification(
            primary_category='Network Outage',
            confidence=0.9,
            keywords=['outage', 'down'],
            secondary_categories=['Technical Problem']
        )
        
        # Serialize to dict
        data = classification.model_dump()
        assert isinstance(data, dict)
        assert data['primary_category'] == 'Network Outage'
        
        # Deserialize from dict
        restored = IssueClassification(**data)
        assert restored.primary_category == classification.primary_category
        assert restored.confidence == classification.confidence
        
        # Serialize to JSON
        json_str = classification.model_dump_json()
        assert isinstance(json_str, str)
        assert 'Network Outage' in json_str


# ============================================================
# Integration Tests
# ============================================================

class TestToolIntegration:
    """Test suite for tool integration scenarios."""
    
    def test_full_ticket_analysis_workflow(self):
        """Test complete workflow using all tools together."""
        # Step 1: Classify issue
        ticket_text = "My internet connection is down. Error NET-500 on service SVC001. Account ACC-12345."
        classification = classify_issue(ticket_text)
        assert classification.primary_category == 'Network Outage'
        
        # Step 2: Extract entities
        entities = extract_entities(ticket_text)
        assert 'ACC-12345' in entities.account_numbers
        assert 'SVC001' in entities.service_ids
        assert 'NET-500' in entities.error_codes
        
        # Step 3: Check VIP status
        customer = check_vip_status('CUST001')
        assert customer.is_vip is True
        
        # Step 4: Check service status
        service_status = check_service_status(entities.service_ids)
        assert service_status.service_health in [ServiceHealth.HEALTHY, ServiceHealth.DEGRADED, ServiceHealth.OUTAGE]
        
        # Step 5: Calculate priority
        priority = calculate_priority(customer, classification, service_status, 2.0)
        assert priority.priority_level in [PriorityLevel.P0, PriorityLevel.P1, PriorityLevel.P2, PriorityLevel.P3]
        
        # Step 6: Route to team
        routing = route_to_team(classification, entities, service_status)
        assert routing.assigned_team == Team.NETWORK_OPS
        
        # Step 7: Get historical context
        history = get_historical_context(customer.customer_id)
        assert isinstance(history, HistoricalContext)
    
    def test_vip_customer_high_priority_workflow(self):
        """Test workflow for VIP customer with critical issue."""
        # VIP customer with network outage
        ticket_text = "Complete network outage affecting all services. Critical business impact."
        
        classification = classify_issue(ticket_text)
        customer = check_vip_status('CUST001')  # VIP customer
        service_status = check_service_status(['SVC001'])  # Service with outage
        
        priority = calculate_priority(customer, classification, service_status, 1.0)
        
        # Should be P0 or P1 for VIP with outage
        assert priority.priority_level in [PriorityLevel.P0, PriorityLevel.P1]
        assert priority.priority_score >= 60
    
    def test_standard_customer_low_priority_workflow(self):
        """Test workflow for standard customer with low severity issue."""
        # Standard customer with billing question
        ticket_text = "I have a question about my bill charges."
        
        classification = classify_issue(ticket_text)
        customer = check_vip_status('CUST002')  # Non-VIP customer
        service_status = check_service_status([])  # No service issues
        
        priority = calculate_priority(customer, classification, service_status, 1.0)
        
        # Should be P2 or P3 for standard customer with billing issue
        assert priority.priority_level in [PriorityLevel.P2, PriorityLevel.P3]
        assert priority.priority_score < 60
    
    def test_all_tools_return_pydantic_models(self):
        """Test that all tools return proper Pydantic models."""
        ticket_text = "Test ticket with ACC-12345 and SVC001"
        
        # Test each tool returns a Pydantic model
        result1 = classify_issue(ticket_text)
        assert hasattr(result1, 'model_dump')
        
        result2 = extract_entities(ticket_text)
        assert hasattr(result2, 'model_dump')
        
        result3 = check_vip_status('CUST001')
        assert hasattr(result3, 'model_dump')
        
        result4 = check_service_status(['SVC001'])
        assert hasattr(result4, 'model_dump')
        
        result5 = calculate_priority(result3, result1, result4, 1.0)
        assert hasattr(result5, 'model_dump')
        
        result6 = route_to_team(result1, result2, result4)
        assert hasattr(result6, 'model_dump')
        
        result7 = get_historical_context('CUST001')
        assert hasattr(result7, 'model_dump')

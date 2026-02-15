"""
Agent tools for AI-Powered Customer Support System MVP.

Implements 7 agent tools with mock logic using Pydantic models for type safety.
"""

import re
from typing import List
from datetime import datetime
from strands import tool
from .models import (
    IssueClassification,
    ExtractedEntities,
    Customer, AccountType,
    ServiceStatus, ServiceHealth, Outage,
    PriorityCalculation, PriorityLevel,
    RoutingDecision, Team,
    HistoricalContext, HistoricalTicket
)
from mock_data import MOCK_CUSTOMERS, MOCK_SERVICE_STATUS, MOCK_HISTORY


@tool
def classify_issue(ticket_text: str) -> IssueClassification:
    """
    Classify ticket using keyword-based pattern matching.
    
    Args:
        ticket_text: Combined ticket subject and description text
        
    Returns:
        IssueClassification model with primary_category, confidence, keywords, secondary_categories
    """
    text_lower = ticket_text.lower()
    
    # Define keyword patterns for each category
    patterns = {
        'Network Outage': ['outage', 'down', 'offline', 'connection', 'connectivity', 'network', 'internet'],
        'Billing Dispute': ['bill', 'charge', 'invoice', 'payment', 'refund', 'overcharged', 'dispute', 'cost'],
        'Technical Problem': ['error', 'not working', 'broken', 'slow', 'issue', 'problem', 'technical', 'router'],
        'Account Access': ['password', 'login', 'access', 'account', 'locked', 'authentication', 'reset', 'credentials']
    }
    
    # Calculate scores for each category
    scores = {}
    matched_keywords_by_category = {}
    
    for category, keywords in patterns.items():
        matched = [kw for kw in keywords if kw in text_lower]
        score = len(matched) / len(keywords) if keywords else 0
        scores[category] = score
        matched_keywords_by_category[category] = matched
    
    # Determine primary category (highest score)
    if scores:
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]
        matched_keywords = matched_keywords_by_category[best_category]
    else:
        best_category = 'Technical Problem'
        best_score = 0.5
        matched_keywords = []
    
    # Identify secondary categories (score > 0 and not primary)
    secondary_categories = [
        cat for cat, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if score > 0 and cat != best_category
    ][:2]  # Limit to top 2 alternatives
    
    return IssueClassification(
        primary_category=best_category,
        confidence=min(best_score, 1.0),
        keywords=matched_keywords,
        secondary_categories=secondary_categories
    )


@tool
def extract_entities(ticket_text: str) -> ExtractedEntities:
    """
    Extract entities from ticket text using regex patterns.
    
    Args:
        ticket_text: Combined ticket subject and description text
        
    Returns:
        ExtractedEntities model with account_numbers, service_ids, error_codes, phone_numbers, monetary_amounts
    """
    # Extract account numbers: ACC-12345
    account_numbers = re.findall(r'ACC-\d+', ticket_text, re.IGNORECASE)
    
    # Extract service IDs: SVC001, SVC002, etc.
    service_ids = re.findall(r'SVC\d+', ticket_text, re.IGNORECASE)
    
    # Extract error codes: NET-500, AUTH-202, etc.
    error_codes = re.findall(r'[A-Z]+-\d+', ticket_text)
    
    # Extract phone numbers: 555-123-4567
    phone_numbers = re.findall(r'\d{3}-\d{3}-\d{4}', ticket_text)
    
    # Extract monetary amounts: $150.00, $2,500.00
    monetary_matches = re.findall(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', ticket_text)
    monetary_amounts = [float(m.replace(',', '')) for m in monetary_matches]
    
    return ExtractedEntities(
        account_numbers=account_numbers,
        service_ids=service_ids,
        error_codes=error_codes,
        phone_numbers=phone_numbers,
        monetary_amounts=monetary_amounts
    )


@tool
def check_vip_status(customer_id: str) -> Customer:
    """
    Check VIP status from mock customer database.
    
    Args:
        customer_id: Customer identifier
        
    Returns:
        Customer model with is_vip, account_type, lifetime_value, etc.
    """
    # Look up customer in mock database
    customer = MOCK_CUSTOMERS.get(customer_id)
    
    if customer:
        return customer
    
    # Return default Customer model for unknown customers
    return Customer(
        customer_id=customer_id,
        is_vip=False,
        account_type=AccountType.CONSUMER,
        lifetime_value=0.0,
        account_standing='Good',
        service_plan='Basic'
    )


@tool
def check_service_status(service_ids: List[str]) -> ServiceStatus:
    """
    Check service status from mock service API.
    
    Args:
        service_ids: List of service identifiers to check
        
    Returns:
        ServiceStatus model with aggregated active_outages and worst service_health
    """
    if not service_ids:
        # No services to check - return healthy status
        return ServiceStatus(
            service_id='NONE',
            service_health=ServiceHealth.HEALTHY,
            active_outages=[]
        )
    
    all_outages: List[Outage] = []
    worst_health = ServiceHealth.HEALTHY
    
    # Aggregate outages and determine worst health status
    for svc_id in service_ids:
        status = MOCK_SERVICE_STATUS.get(svc_id)
        if status:
            all_outages.extend(status.active_outages)
            
            # Determine worst health (OUTAGE > DEGRADED > HEALTHY)
            if status.service_health == ServiceHealth.OUTAGE:
                worst_health = ServiceHealth.OUTAGE
            elif status.service_health == ServiceHealth.DEGRADED and worst_health != ServiceHealth.OUTAGE:
                worst_health = ServiceHealth.DEGRADED
    
    return ServiceStatus(
        service_id=','.join(service_ids),
        service_health=worst_health,
        active_outages=all_outages
    )


@tool
def calculate_priority(
    vip_status: Customer,
    issue_classification: IssueClassification,
    service_status: ServiceStatus,
    ticket_age_hours: float
) -> PriorityCalculation:
    """
    Calculate priority using weighted scoring algorithm.
    
    Scoring weights:
    - VIP status: 30%
    - Issue severity: 40%
    - Ticket age: 20%
    - Outage status: 10%
    
    Priority levels:
    - P0 (Critical): score >= 80
    - P1 (High): score >= 60
    - P2 (Medium): score >= 40
    - P3 (Low): score < 40
    
    Args:
        vip_status: Customer model with VIP and account information
        issue_classification: IssueClassification model
        service_status: ServiceStatus model
        ticket_age_hours: Age of ticket in hours
        
    Returns:
        PriorityCalculation model with priority_level, priority_score, factors, reasoning
    """
    score = 0.0
    factors = {}
    
    # VIP contribution (30%)
    if vip_status.is_vip:
        score += 30
        factors['vip_bonus'] = 30
    elif vip_status.account_type == AccountType.ENTERPRISE:
        score += 20
        factors['enterprise_bonus'] = 20
    elif vip_status.account_type == AccountType.BUSINESS:
        score += 10
        factors['business_bonus'] = 10
    
    # Severity contribution (40%)
    severity_map = {
        'Network Outage': 40,
        'Account Access': 30,
        'Technical Problem': 20,
        'Billing Dispute': 10
    }
    severity_score = severity_map.get(issue_classification.primary_category, 20)
    score += severity_score
    factors['severity'] = severity_score
    
    # Age contribution (20%)
    if ticket_age_hours >= 48:
        age_score = 20
        score += age_score
        factors['age_penalty'] = age_score
    elif ticket_age_hours >= 24:
        age_score = 10
        score += age_score
        factors['age_penalty'] = age_score
    
    # Outage contribution (10%)
    if service_status.service_health == ServiceHealth.OUTAGE:
        outage_score = 10
        score += outage_score
        factors['outage_impact'] = outage_score
    elif service_status.service_health == ServiceHealth.DEGRADED:
        degraded_score = 5
        score += degraded_score
        factors['degraded_impact'] = degraded_score
    
    # Determine priority level based on score
    if score >= 80:
        priority_level = PriorityLevel.P0
    elif score >= 60:
        priority_level = PriorityLevel.P1
    elif score >= 40:
        priority_level = PriorityLevel.P2
    else:
        priority_level = PriorityLevel.P3
    
    # Build reasoning string
    factor_strings = [f"{k}={v}" for k, v in factors.items()]
    reasoning = f"Score: {score:.1f} - {', '.join(factor_strings)}"
    
    return PriorityCalculation(
        priority_level=priority_level,
        priority_score=score,
        factors=factors,
        reasoning=reasoning
    )


@tool
def route_to_team(
    issue_classification: IssueClassification,
    entities: ExtractedEntities,
    service_status: ServiceStatus
) -> RoutingDecision:
    """
    Route to team based on issue classification and context.
    
    Args:
        issue_classification: IssueClassification model
        entities: ExtractedEntities model
        service_status: ServiceStatus model
        
    Returns:
        RoutingDecision model with assigned_team, confidence, alternative_teams, reasoning, requires_manual_review
    """
    # Define routing map for issue categories
    routing_map = {
        'Network Outage': (Team.NETWORK_OPS, 0.9),
        'Billing Dispute': (Team.BILLING, 0.9),
        'Technical Problem': (Team.TECHNICAL, 0.8),
        'Account Access': (Team.ACCOUNT_MGMT, 0.9)
    }
    
    category = issue_classification.primary_category
    team, base_confidence = routing_map.get(category, (Team.TECHNICAL, 0.6))
    
    # Adjust confidence based on classification confidence
    confidence = base_confidence * issue_classification.confidence
    
    # Identify alternative teams from secondary categories
    alternative_teams = []
    for secondary_cat in issue_classification.secondary_categories:
        alt_team, _ = routing_map.get(secondary_cat, (None, 0))
        if alt_team and alt_team != team:
            alternative_teams.append(alt_team)
    
    # Build reasoning
    reasoning = f"Classified as {category} with {issue_classification.confidence:.2f} confidence, routing to {team.value}"
    
    # Flag for manual review if confidence is low
    requires_manual_review = confidence < 0.7
    
    if requires_manual_review:
        reasoning += " - Low confidence, flagged for manual review"
    
    return RoutingDecision(
        assigned_team=team,
        confidence=confidence,
        alternative_teams=alternative_teams,
        reasoning=reasoning,
        requires_manual_review=requires_manual_review
    )


@tool
def get_historical_context(customer_id: str, limit: int = 5) -> HistoricalContext:
    """
    Get historical tickets from mock history database.
    
    Args:
        customer_id: Customer identifier
        limit: Maximum number of recent tickets to return
        
    Returns:
        HistoricalContext model with recent_tickets, common_issues, escalation_history
    """
    # Look up customer history in mock database
    history = MOCK_HISTORY.get(customer_id, [])
    
    # Limit recent tickets
    recent_tickets = history[:limit]
    
    # Identify common issues
    common_issues = list(set(ticket.issue_type for ticket in history))
    
    # Check for escalation history
    escalation_history = any(ticket.escalated for ticket in history)
    
    return HistoricalContext(
        recent_tickets=recent_tickets,
        common_issues=common_issues,
        escalation_history=escalation_history
    )

"""
AI-powered agent tools for AI-Powered Customer Support System MVP.

Implements AI-powered versions of tools using Claude Haiku via Strands agents.
These tools use LLM reasoning instead of simple keyword matching.
"""

from strands import Agent, tool

from .models import (
    IssueClassification,
    ExtractedEntities,
    RoutingDecision, Team
)
from .config import BEDROCK_REGION


# Initialize specialized Strands agents for each AI-powered tool
# Using Claude Haiku 4.5 for faster, cheaper specialized tasks

_classification_agent = None
_extraction_agent = None
_routing_agent = None


def _get_classification_agent() -> Agent:
    """Get or create the classification agent."""
    global _classification_agent
    if _classification_agent is None:
        _classification_agent = Agent(
            model='global.anthropic.claude-haiku-4-5-20251001-v1:0',
            system_prompt="""You are an expert at classifying customer support tickets for a telecom company.

Classify tickets into one of these categories:
- Network Outage: Internet/network connectivity issues, service down, outages
- Billing Dispute: Billing problems, charges, invoices, refunds, payment issues
- Technical Problem: Device issues, technical errors, configuration problems
- Account Access: Login issues, password resets, authentication problems

Respond in this exact format:
PRIMARY_CATEGORY: <category>
CONFIDENCE: <0.0-1.0>
KEYWORDS: <comma-separated keywords found>
SECONDARY_CATEGORIES: <comma-separated alternative categories, if any>"""
        )
    return _classification_agent


def _get_extraction_agent() -> Agent:
    """Get or create the entity extraction agent."""
    global _extraction_agent
    if _extraction_agent is None:
        _extraction_agent = Agent(
            model='global.anthropic.claude-haiku-4-5-20251001-v1:0',
            system_prompt="""You are an expert at extracting structured information from customer support tickets.

Extract these entities:
- Account numbers (format: ACC-12345)
- Service IDs (format: SVC001, SVC002)
- Error codes (format: NET-500, AUTH-403)
- Phone numbers (format: 555-123-4567)
- Monetary amounts (format: $150.00, $2,500.00)

Respond in this exact format:
ACCOUNT_NUMBERS: <comma-separated list or "none">
SERVICE_IDS: <comma-separated list or "none">
ERROR_CODES: <comma-separated list or "none">
PHONE_NUMBERS: <comma-separated list or "none">
MONETARY_AMOUNTS: <comma-separated numbers without $ or "none">"""
        )
    return _extraction_agent


def _get_routing_agent() -> Agent:
    """Get or create the routing agent."""
    global _routing_agent
    if _routing_agent is None:
        _routing_agent = Agent(
            model='global.anthropic.claude-haiku-4-5-20251001-v1:0',
            system_prompt="""You are an expert at routing customer support tickets to the correct team.

Available teams:
- Network Operations: Network outages, connectivity issues, service disruptions
- Billing Support: Billing disputes, payment issues, invoice questions, refunds
- Technical Support: Device issues, technical problems, configuration help
- Account Management: Account access, password resets, authentication issues

Respond in this exact format:
ASSIGNED_TEAM: <team name>
CONFIDENCE: <0.0-1.0>
ALTERNATIVE_TEAMS: <comma-separated team names or "none">
REASONING: <brief explanation>
MANUAL_REVIEW: <yes or no>"""
        )
    return _routing_agent


@tool
def classify_issue(ticket_text: str) -> IssueClassification:
    """
    AI-powered ticket classification using Claude Haiku via Strands agent.
    
    Uses LLM reasoning to classify tickets more accurately than keyword matching.
    
    Args:
        ticket_text: Combined ticket subject and description text
        
    Returns:
        IssueClassification model with primary_category, confidence, keywords, secondary_categories
    """
    prompt = f"""Classify this support ticket:

{ticket_text}

Provide your classification following the specified format."""
    
    try:
        # Use Strands agent to call Claude Haiku
        agent = _get_classification_agent()
        response = agent(prompt)
        
        # Parse response
        response_text = str(response)
        lines = response_text.strip().split('\n')
        primary_category = 'Technical Problem'
        confidence = 0.7
        keywords = []
        secondary_categories = []
        
        for line in lines:
            if line.startswith('PRIMARY_CATEGORY:'):
                primary_category = line.split(':', 1)[1].strip()
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line.split(':', 1)[1].strip())
                except ValueError:
                    confidence = 0.7
            elif line.startswith('KEYWORDS:'):
                keywords_str = line.split(':', 1)[1].strip()
                keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
            elif line.startswith('SECONDARY_CATEGORIES:'):
                sec_str = line.split(':', 1)[1].strip()
                if sec_str and sec_str.lower() != 'none':
                    secondary_categories = [s.strip() for s in sec_str.split(',') if s.strip()]
        
        return IssueClassification(
            primary_category=primary_category,
            confidence=confidence,
            keywords=keywords,
            secondary_categories=secondary_categories
        )
        
    except Exception as e:
        # Fallback to simple classification on error
        print(f"⚠️  AI classification failed: {e}. Using fallback.")
        return IssueClassification(
            primary_category='Technical Problem',
            confidence=0.5,
            keywords=[],
            secondary_categories=[]
        )


@tool
def extract_entities(ticket_text: str) -> ExtractedEntities:
    """
    AI-powered entity extraction using Claude Haiku via Strands agent.
    
    Uses LLM reasoning to extract entities more accurately than regex patterns.
    
    Args:
        ticket_text: Combined ticket subject and description text
        
    Returns:
        ExtractedEntities model with account_numbers, service_ids, error_codes, phone_numbers, monetary_amounts
    """
    prompt = f"""Extract entities from this support ticket:

{ticket_text}

Provide your extraction following the specified format."""
    
    try:
        # Use Strands agent to call Claude Haiku
        agent = _get_extraction_agent()
        response = agent(prompt)
        
        # Parse response
        response_text = str(response)
        lines = response_text.strip().split('\n')
        account_numbers = []
        service_ids = []
        error_codes = []
        phone_numbers = []
        monetary_amounts = []
        
        for line in lines:
            if line.startswith('ACCOUNT_NUMBERS:'):
                values_str = line.split(':', 1)[1].strip()
                if values_str.lower() != 'none':
                    account_numbers = [v.strip() for v in values_str.split(',') if v.strip()]
            elif line.startswith('SERVICE_IDS:'):
                values_str = line.split(':', 1)[1].strip()
                if values_str.lower() != 'none':
                    service_ids = [v.strip() for v in values_str.split(',') if v.strip()]
            elif line.startswith('ERROR_CODES:'):
                values_str = line.split(':', 1)[1].strip()
                if values_str.lower() != 'none':
                    error_codes = [v.strip() for v in values_str.split(',') if v.strip()]
            elif line.startswith('PHONE_NUMBERS:'):
                values_str = line.split(':', 1)[1].strip()
                if values_str.lower() != 'none':
                    phone_numbers = [v.strip() for v in values_str.split(',') if v.strip()]
            elif line.startswith('MONETARY_AMOUNTS:'):
                values_str = line.split(':', 1)[1].strip()
                if values_str.lower() != 'none':
                    try:
                        monetary_amounts = [float(v.strip()) for v in values_str.split(',') if v.strip()]
                    except ValueError:
                        monetary_amounts = []
        
        return ExtractedEntities(
            account_numbers=account_numbers,
            service_ids=service_ids,
            error_codes=error_codes,
            phone_numbers=phone_numbers,
            monetary_amounts=monetary_amounts
        )
        
    except Exception as e:
        # Fallback to empty extraction on error
        print(f"⚠️  AI entity extraction failed: {e}. Using fallback.")
        return ExtractedEntities(
            account_numbers=[],
            service_ids=[],
            error_codes=[],
            phone_numbers=[],
            monetary_amounts=[]
        )


@tool
def route_to_team(
    issue_classification: IssueClassification,
    entities: ExtractedEntities,
    service_status: str  # Simplified for AI tool
) -> RoutingDecision:
    """
    AI-powered team routing using Claude Haiku via Strands agent.
    
    Uses LLM reasoning to make more nuanced routing decisions.
    
    Args:
        issue_classification: IssueClassification model
        entities: ExtractedEntities model
        service_status: Service status description
        
    Returns:
        RoutingDecision model with assigned_team, confidence, alternative_teams, reasoning, requires_manual_review
    """
    prompt = f"""Route this ticket to the correct support team:

Issue Classification:
- Primary Category: {issue_classification.primary_category}
- Confidence: {issue_classification.confidence}
- Keywords: {', '.join(issue_classification.keywords)}
- Secondary Categories: {', '.join(issue_classification.secondary_categories)}

Extracted Entities:
- Account Numbers: {', '.join(entities.account_numbers) if entities.account_numbers else 'none'}
- Service IDs: {', '.join(entities.service_ids) if entities.service_ids else 'none'}
- Error Codes: {', '.join(entities.error_codes) if entities.error_codes else 'none'}

Service Status: {service_status}

Provide your routing decision following the specified format."""
    
    try:
        # Use Strands agent to call Claude Haiku
        agent = _get_routing_agent()
        response = agent(prompt)
        
        # Parse response
        response_text = str(response)
        lines = response_text.strip().split('\n')
        assigned_team = Team.TECHNICAL
        confidence = 0.7
        alternative_teams = []
        reasoning = "AI-powered routing decision"
        requires_manual_review = False
        
        for line in lines:
            if line.startswith('ASSIGNED_TEAM:'):
                team_str = line.split(':', 1)[1].strip()
                # Map team name to Team enum
                if 'network' in team_str.lower():
                    assigned_team = Team.NETWORK_OPS
                elif 'billing' in team_str.lower():
                    assigned_team = Team.BILLING
                elif 'technical' in team_str.lower():
                    assigned_team = Team.TECHNICAL
                elif 'account' in team_str.lower():
                    assigned_team = Team.ACCOUNT_MGMT
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line.split(':', 1)[1].strip())
                except ValueError:
                    confidence = 0.7
            elif line.startswith('ALTERNATIVE_TEAMS:'):
                alt_str = line.split(':', 1)[1].strip()
                if alt_str.lower() != 'none':
                    # Parse alternative teams
                    for alt in alt_str.split(','):
                        alt = alt.strip().lower()
                        if 'network' in alt:
                            alternative_teams.append(Team.NETWORK_OPS)
                        elif 'billing' in alt:
                            alternative_teams.append(Team.BILLING)
                        elif 'technical' in alt:
                            alternative_teams.append(Team.TECHNICAL)
                        elif 'account' in alt:
                            alternative_teams.append(Team.ACCOUNT_MGMT)
            elif line.startswith('REASONING:'):
                reasoning = line.split(':', 1)[1].strip()
            elif line.startswith('MANUAL_REVIEW:'):
                review_str = line.split(':', 1)[1].strip().lower()
                requires_manual_review = review_str == 'yes'
        
        return RoutingDecision(
            assigned_team=assigned_team,
            confidence=confidence,
            alternative_teams=alternative_teams,
            reasoning=reasoning,
            requires_manual_review=requires_manual_review
        )
        
    except Exception as e:
        # Fallback to safe routing on error
        print(f"⚠️  AI routing failed: {e}. Using fallback.")
        return RoutingDecision(
            assigned_team=Team.TECHNICAL,
            confidence=0.5,
            alternative_teams=[],
            reasoning=f"Fallback routing due to error: {str(e)}",
            requires_manual_review=True
        )


"""
Agent implementation for AI-Powered Customer Support System MVP.

Implements TicketRoutingAgent using Strands Agent Framework with AWS Bedrock.
"""

import boto3
import time
from typing import Any
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError

from strands import Agent, tool

from .models import Ticket, FinalDecision, Team, PriorityLevel
from .config import BEDROCK_REGION, BEDROCK_MODEL_ID, AGENT_CONFIG, USE_AGENT_TOOLS


class TicketRoutingAgent:
    """
    AI-powered ticket routing agent using AWS Bedrock and Strands framework.
    
    This agent analyzes support tickets and makes intelligent routing decisions
    using multiple tools and AI reasoning.
    """
    
    def __init__(self, use_agent_tools: bool = None):
        """
        Initialize the TicketRoutingAgent.
        
        Args:
            use_agent_tools: If True, use AI-powered tools (Claude Haiku).
                           If False, use mock tools.
                           If None, use value from config.USE_AGENT_TOOLS (default).
        """
        # Determine which tools to use
        if use_agent_tools is None:
            use_agent_tools = USE_AGENT_TOOLS
        
        self.use_agent_tools = use_agent_tools
        
        # Import appropriate tools based on configuration
        if self.use_agent_tools:
            print("🤖 Using AI-powered tools (Claude Haiku)")
            from .agent_tools import (
                classify_issue as ai_classify_issue,
                extract_entities as ai_extract_entities,
                route_to_team as ai_route_to_team
            )
            from .tools import (
                check_vip_status,
                check_service_status,
                calculate_priority,
                get_historical_context
            )
            # Use AI-powered versions for these tools
            tools_list = [
                ai_classify_issue,
                ai_extract_entities,
                check_vip_status,
                check_service_status,
                calculate_priority,
                ai_route_to_team,
                get_historical_context
            ]
        else:
            print("📋 Using mock tools (keyword matching)")
            from .tools import (
                classify_issue,
                extract_entities,
                check_vip_status,
                check_service_status,
                calculate_priority,
                route_to_team,
                get_historical_context
            )
            # Use mock versions for all tools
            tools_list = [
                classify_issue,
                extract_entities,
                check_vip_status,
                check_service_status,
                calculate_priority,
                route_to_team,
                get_historical_context
            ]
        
        # Initialize boto3 Bedrock client
        self.bedrock = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
        
        # Define comprehensive system prompt for ticket routing
        self.system_prompt = """You are an expert customer support ticket routing agent for a telecom company.

Your goal is to analyze incoming support tickets and route them to the correct team with appropriate priority.

AVAILABLE TEAMS:
- Network Operations: Handles network outages, connectivity issues, service disruptions
- Billing Support: Handles billing disputes, payment issues, invoice questions, refunds
- Technical Support: Handles device issues, technical problems, configuration help
- Account Management: Handles account access, password resets, authentication issues

PRIORITY LEVELS:
- P0 (Critical): VIP customer + service outage, or critical business impact
- P1 (High): VIP customer issues, major problems, or significant service degradation
- P2 (Medium): Standard customer issues, moderate problems
- P3 (Low): General inquiries, minor issues

YOUR PROCESS:
1. Use classify_issue() to understand the ticket's primary issue category
2. Use extract_entities() to identify account numbers, service IDs, error codes
3. Use check_vip_status() to determine customer importance and account type
4. Use check_service_status() to identify active outages affecting the customer
5. Use route_to_team() to determine the best support team
6. Use calculate_priority() to set appropriate priority level
7. Make your final decision with clear reasoning

IMPORTANT GUIDELINES:
- Always explain your reasoning clearly
- Consider VIP status when setting priority
- Flag tickets for manual review if confidence is low (< 70%)
- Network outages should be P0 or P1 priority
- VIP customers should receive higher priority
- Use all available context to make informed decisions

Provide your final decision in a clear, structured format with:
- Assigned team
- Priority level
- Confidence score (0-100)
- Detailed reasoning for your decision
"""
        
        # Initialize Strands Agent with model, system prompt, and tools
        # Note: When passing model as string, don't use "bedrock/" prefix
        self.agent = Agent(
            model=BEDROCK_MODEL_ID,
            system_prompt=self.system_prompt,
            tools=tools_list
        )
        
        self.use_agent_tools = use_agent_tools
    
    def process_ticket(self, ticket: Ticket) -> FinalDecision:
        """
        Process a support ticket and return routing decision.
        
        Args:
            ticket: Ticket Pydantic model with ticket data
            
        Returns:
            FinalDecision Pydantic model with routing decision and reasoning
        """
        start_time = time.time()
        
        # Calculate ticket age in hours
        ticket_age_hours = (datetime.utcnow() - ticket.timestamp).total_seconds() / 3600
        
        # Format ticket data into agent prompt using Pydantic model fields
        ticket_prompt = f"""Route this support ticket:

Ticket ID: {ticket.ticket_id}
Customer ID: {ticket.customer_id}
Subject: {ticket.subject}
Description: {ticket.description}
Ticket Age: {ticket_age_hours:.1f} hours

Analyze this ticket and determine:
1. The correct support team to handle it
2. The appropriate priority level
3. Your confidence in this decision

Use the available tools to gather information and make an informed decision.
Provide clear reasoning for your routing decision."""
        
        try:
            # Execute agent by calling it directly (Strands API)
            result = self.agent(ticket_prompt)
            
            # Parse agent result into FinalDecision Pydantic model
            decision = self._parse_decision(result, ticket)
            
            # Track processing time and add to FinalDecision model
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            decision.processing_time_ms = processing_time
            
            return decision
            
        except ClientError as e:
            # Handle boto3 client errors (AWS-specific errors)
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            # Handle rate limiting and throttling
            if error_code in ['ThrottlingException', 'TooManyRequestsException', 'ProvisionedThroughputExceededException']:
                print(f"⚠️  Rate limit exceeded for ticket {ticket.ticket_id}. Retrying after delay...")
                time.sleep(2)  # Wait 2 seconds before fallback
                processing_time = (time.time() - start_time) * 1000
                fallback = self._fallback_decision(
                    ticket, 
                    f"Rate limit exceeded: {error_message}. Please try again later."
                )
                fallback.processing_time_ms = processing_time
                return fallback
            
            # Handle access denied errors
            elif error_code in ['AccessDeniedException', 'UnauthorizedException']:
                processing_time = (time.time() - start_time) * 1000
                fallback = self._fallback_decision(
                    ticket,
                    f"Access denied to Bedrock: {error_message}. Check AWS credentials and permissions."
                )
                fallback.processing_time_ms = processing_time
                return fallback
            
            # Handle model not found or unavailable
            elif error_code in ['ResourceNotFoundException', 'ModelNotReadyException']:
                processing_time = (time.time() - start_time) * 1000
                fallback = self._fallback_decision(
                    ticket,
                    f"Bedrock model unavailable: {error_message}. Check model ID and region."
                )
                fallback.processing_time_ms = processing_time
                return fallback
            
            # Handle validation errors
            elif error_code == 'ValidationException':
                processing_time = (time.time() - start_time) * 1000
                fallback = self._fallback_decision(
                    ticket,
                    f"Invalid request to Bedrock: {error_message}"
                )
                fallback.processing_time_ms = processing_time
                return fallback
            
            # Handle other AWS client errors
            else:
                processing_time = (time.time() - start_time) * 1000
                fallback = self._fallback_decision(
                    ticket,
                    f"AWS Bedrock error ({error_code}): {error_message}"
                )
                fallback.processing_time_ms = processing_time
                return fallback
        
        except BotoCoreError as e:
            # Handle boto3 core errors (connection, network issues)
            processing_time = (time.time() - start_time) * 1000
            fallback = self._fallback_decision(
                ticket,
                f"Network error connecting to Bedrock: {str(e)}. Check internet connectivity."
            )
            fallback.processing_time_ms = processing_time
            return fallback
        
        except Exception as e:
            # Handle all other exceptions with fallback decision logic
            processing_time = (time.time() - start_time) * 1000
            fallback = self._fallback_decision(ticket, str(e))
            fallback.processing_time_ms = processing_time
            return fallback
    
    def _parse_decision(self, result: Any, ticket: Ticket) -> FinalDecision:
        """
        Parse agent result into FinalDecision Pydantic model.
        
        Extracts routing decision from agent result and validates structure.
        
        Args:
            result: Agent execution result
            ticket: Original Ticket model
            
        Returns:
            FinalDecision Pydantic model with all required fields
        """
        # Extract the final response text from agent result
        response_text = str(result)
        
        # Initialize default values
        assigned_team = Team.TECHNICAL
        priority_level = PriorityLevel.P2
        confidence_score = 70.0
        reasoning = response_text
        requires_manual_review = False
        
        # Parse team assignment from response
        response_lower = response_text.lower()
        if 'network operations' in response_lower or 'network ops' in response_lower:
            assigned_team = Team.NETWORK_OPS
        elif 'billing support' in response_lower or 'billing' in response_lower:
            assigned_team = Team.BILLING
        elif 'technical support' in response_lower or 'technical' in response_lower:
            assigned_team = Team.TECHNICAL
        elif 'account management' in response_lower or 'account' in response_lower:
            assigned_team = Team.ACCOUNT_MGMT
        
        # Parse priority level from response
        if 'p0' in response_lower or 'critical' in response_lower:
            priority_level = PriorityLevel.P0
        elif 'p1' in response_lower or 'high' in response_lower:
            priority_level = PriorityLevel.P1
        elif 'p2' in response_lower or 'medium' in response_lower:
            priority_level = PriorityLevel.P2
        elif 'p3' in response_lower or 'low' in response_lower:
            priority_level = PriorityLevel.P3
        
        # Parse confidence score from response (look for percentages or scores)
        import re
        # Look for "Confidence Score: XX" or "Confidence: XX%" patterns
        confidence_matches = re.findall(r'confidence\s*score[:\s]+(\d+(?:\.\d+)?)\s*[/\%]?', response_lower)
        if not confidence_matches:
            # Try alternative pattern: "Confidence: XX%"
            confidence_matches = re.findall(r'confidence[:\s]+(\d+(?:\.\d+)?)\s*[/\%]', response_lower)
        if confidence_matches:
            # Take the highest confidence score found (likely the final one)
            confidence_score = max(float(m) for m in confidence_matches)
        
        # Check if manual review is mentioned
        if 'manual review' in response_lower or 'flag' in response_lower:
            requires_manual_review = True
        
        # Create and return FinalDecision Pydantic model
        return FinalDecision(
            ticket_id=ticket.ticket_id,
            customer_id=ticket.customer_id,
            assigned_team=assigned_team,
            priority_level=priority_level,
            confidence_score=confidence_score,
            reasoning=reasoning,
            processing_time_ms=0,  # Will be set by process_ticket
            requires_manual_review=requires_manual_review
        )
    
    def _fallback_decision(self, ticket: Ticket, error: str) -> FinalDecision:
        """
        Provide fallback decision when agent fails.
        
        Returns a safe default routing decision with manual review flag.
        Uses fallback FinalDecision models when Bedrock unavailable.
        
        Args:
            ticket: Ticket Pydantic model
            error: Error string describing the failure
            
        Returns:
            FinalDecision Pydantic model with safe defaults and requires_manual_review=True
        """
        # Log error information with informative error messages
        print(f"⚠️  Agent error for ticket {ticket.ticket_id}: {error}")
        print(f"    Using fallback routing decision with manual review flag.")
        
        # Provide informative error messages based on error type
        if "rate limit" in error.lower() or "throttl" in error.lower():
            reasoning = (
                f"Fallback routing due to rate limiting. "
                f"The system is experiencing high load. "
                f"Defaulting to Technical Support with medium priority. "
                f"Manual review required to ensure proper routing."
            )
        elif "access denied" in error.lower() or "unauthorized" in error.lower():
            reasoning = (
                f"Fallback routing due to access denied error. "
                f"AWS credentials may be invalid or insufficient permissions. "
                f"Defaulting to Technical Support with medium priority. "
                f"Manual review required. Please check AWS configuration."
            )
        elif "model unavailable" in error.lower() or "not found" in error.lower():
            reasoning = (
                f"Fallback routing due to model unavailability. "
                f"The AI model may not be available in this region. "
                f"Defaulting to Technical Support with medium priority. "
                f"Manual review required. Please verify Bedrock model configuration."
            )
        elif "network" in error.lower() or "connection" in error.lower():
            reasoning = (
                f"Fallback routing due to network connectivity issue. "
                f"Unable to reach AWS Bedrock service. "
                f"Defaulting to Technical Support with medium priority. "
                f"Manual review required. Please check internet connectivity."
            )
        else:
            reasoning = (
                f"Fallback routing due to error: {error}. "
                f"Defaulting to Technical Support with medium priority. "
                f"Manual review required to ensure proper routing."
            )
        
        # Return FinalDecision Pydantic model with safe defaults
        return FinalDecision(
            ticket_id=ticket.ticket_id,
            customer_id=ticket.customer_id,
            assigned_team=Team.TECHNICAL,
            priority_level=PriorityLevel.P2,
            confidence_score=50.0,
            reasoning=reasoning,
            processing_time_ms=0,  # Will be set by process_ticket
            requires_manual_review=True
        )

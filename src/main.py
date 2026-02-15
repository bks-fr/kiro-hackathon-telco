"""CLI interface for the AI-Powered Customer Support System MVP"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from pydantic import ValidationError

from .models import Ticket, FinalDecision
from mock_data import SAMPLE_TICKETS


def load_tickets_from_mock() -> List[Ticket]:
    """
    Load sample tickets from mock_data.SAMPLE_TICKETS.
    
    Returns:
        List[Ticket]: List of Pydantic Ticket models
    """
    return SAMPLE_TICKETS


def load_tickets_from_json(file_path: str) -> List[Ticket]:
    """
    Load tickets from a JSON file and parse into Ticket models (optional).
    
    Args:
        file_path: Path to JSON file containing ticket data
        
    Returns:
        List[Ticket]: List of Pydantic Ticket models
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValidationError: If ticket data is invalid
        json.JSONDecodeError: If JSON is malformed
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Ticket file not found: {file_path}")
    
    with open(path, 'r') as f:
        data = json.load(f)
    
    # Parse each ticket dict into Ticket model
    tickets = []
    for idx, ticket_data in enumerate(data):
        try:
            # Convert timestamp string to datetime if needed
            if 'timestamp' in ticket_data and isinstance(ticket_data['timestamp'], str):
                ticket_data['timestamp'] = datetime.fromisoformat(ticket_data['timestamp'])
            
            # Validate and create Ticket model - Pydantic will validate automatically
            ticket = Ticket(**ticket_data)
            tickets.append(ticket)
            
        except ValidationError as e:
            # Log validation errors with details from Pydantic error messages
            print(f"✗ Validation error for ticket at index {idx}:")
            for error in e.errors():
                field = '.'.join(str(loc) for loc in error['loc'])
                message = error['msg']
                error_type = error['type']
                print(f"  Field '{field}': {message} (type: {error_type})")
            print(f"  Ticket data: {ticket_data}")
            raise
    
    return tickets


def validate_tickets(tickets: List[Ticket]) -> bool:
    """
    Validate ticket data structure using Pydantic validation.
    
    This function performs additional validation beyond Pydantic's automatic validation
    to ensure all required fields are present and properly formatted.
    
    Args:
        tickets: List of Ticket models to validate
        
    Returns:
        bool: True if all tickets are valid
        
    Raises:
        ValidationError: If any ticket is invalid
    """
    for idx, ticket in enumerate(tickets):
        try:
            # Validate required fields using Pydantic validators
            # Check ticket_id is not empty (already validated by Pydantic, but double-check)
            if not ticket.ticket_id or not ticket.ticket_id.strip():
                raise ValidationError(
                    f"Ticket at index {idx}: ticket_id cannot be empty",
                    model=Ticket
                )
            
            # Check customer_id is not empty
            if not ticket.customer_id or not ticket.customer_id.strip():
                raise ValidationError(
                    f"Ticket at index {idx}: customer_id cannot be empty",
                    model=Ticket
                )
            
            # Check subject is not empty
            if not ticket.subject or not ticket.subject.strip():
                raise ValidationError(
                    f"Ticket {ticket.ticket_id}: subject cannot be empty",
                    model=Ticket
                )
            
            # Check description is not empty
            if not ticket.description or not ticket.description.strip():
                raise ValidationError(
                    f"Ticket {ticket.ticket_id}: description cannot be empty",
                    model=Ticket
                )
            
            # Validate timestamp is a valid datetime
            if not isinstance(ticket.timestamp, datetime):
                raise ValidationError(
                    f"Ticket {ticket.ticket_id}: timestamp must be a datetime object",
                    model=Ticket
                )
                
        except ValidationError as e:
            # Log validation errors with details from Pydantic error messages
            print(f"✗ Validation error for ticket at index {idx}:")
            if hasattr(e, 'errors'):
                for error in e.errors():
                    field = '.'.join(str(loc) for loc in error['loc'])
                    message = error['msg']
                    error_type = error['type']
                    print(f"  Field '{field}': {message} (type: {error_type})")
            else:
                print(f"  {str(e)}")
            raise
    
    return True



def initialize_agent():
    """
    Initialize TicketRoutingAgent with error handling.
    
    Returns:
        TicketRoutingAgent: Initialized agent instance
        
    Raises:
        Exception: If agent initialization fails
    """
    from .agent import TicketRoutingAgent
    from .config import validate_configuration
    
    print("Validating configuration...")
    
    # Validate configuration before initializing agent
    config_valid, config_errors = validate_configuration()
    
    if not config_valid:
        print("✗ Configuration validation failed:\n")
        for error in config_errors:
            print(f"  • {error}")
        print("\nTroubleshooting tips:")
        print("  1. Ensure AWS credentials are configured (aws configure)")
        print("  2. Verify Bedrock access is enabled in your AWS account")
        print("  3. Check that the region supports Claude models")
        print("  4. Verify network connectivity to AWS")
        raise Exception("Configuration validation failed. Please fix the errors above.")
    
    print("✓ Configuration validated successfully")
    print("\nInitializing agent with Bedrock...")
    
    try:
        agent = TicketRoutingAgent()
        print("✓ Agent initialized successfully")
        return agent
    except Exception as e:
        print(f"✗ Agent initialization failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("  1. Ensure AWS credentials are configured (aws configure)")
        print("  2. Verify Bedrock access is enabled in your AWS account")
        print("  3. Check that the region supports Claude Sonnet 4.5")
        print("  4. Verify network connectivity to AWS")
        raise



def process_tickets(agent, tickets: List[Ticket]) -> List[FinalDecision]:
    """
    Process Ticket Pydantic models sequentially.
    
    Args:
        agent: TicketRoutingAgent instance
        tickets: List of Ticket models to process
        
    Returns:
        List[FinalDecision]: List of routing decisions
    """
    decisions: List[FinalDecision] = []
    total = len(tickets)
    
    print(f"\nProcessing {total} tickets...\n")
    
    for idx, ticket in enumerate(tickets, 1):
        print(f"Processing Ticket {idx}/{total}: {ticket.ticket_id}")
        print(f"  Subject: {ticket.subject}")
        
        try:
            # Process ticket and track time
            decision = agent.process_ticket(ticket)
            decisions.append(decision)
            
            # Display brief progress
            print(f"  ✓ Routed to: {decision.assigned_team.value}")
            print(f"  Priority: {decision.priority_level.value}")
            print(f"  Time: {decision.processing_time_ms:.0f}ms")
            
        except Exception as e:
            print(f"  ✗ Error processing ticket: {str(e)}")
            # Continue with next ticket
            continue
        
        print()  # Blank line between tickets
    
    return decisions



def display_results(decisions: List[FinalDecision], tickets: List[Ticket]):
    """
    Format and display each FinalDecision model in console.
    
    Args:
        decisions: List of FinalDecision models
        tickets: List of original Ticket models (for subject lookup)
    """
    if not decisions:
        print("No decisions to display.")
        return
    
    # Create ticket lookup for subjects
    ticket_map = {t.ticket_id: t for t in tickets}
    
    print("\n" + "=" * 80)
    print("ROUTING DECISIONS")
    print("=" * 80 + "\n")
    
    for decision in decisions:
        ticket = ticket_map.get(decision.ticket_id)
        subject = ticket.subject if ticket else "Unknown"
        
        print(f"Ticket ID: {decision.ticket_id}")
        print(f"Subject: {subject}")
        print(f"Customer: {decision.customer_id}")
        print(f"Assigned Team: {decision.assigned_team.value}")
        print(f"Priority Level: {decision.priority_level.value}")
        print(f"Confidence Score: {decision.confidence_score:.1f}%")
        print(f"Processing Time: {decision.processing_time_ms:.0f}ms")
        
        if decision.requires_manual_review:
            print("⚠️  REQUIRES MANUAL REVIEW")
        
        print(f"Reasoning: {decision.reasoning}")
        print("-" * 80 + "\n")



def save_individual_ticket_results(tickets: List[Ticket], decisions: List[FinalDecision]):
    """
    Save individual ticket results to separate JSON files.
    
    Creates results/tickets/ subdirectory and saves each ticket with its decision
    to a separate file: results/tickets/{ticket_id}.json
    
    Args:
        tickets: List of original Ticket models
        decisions: List of FinalDecision models
    """
    # Create results/tickets/ subdirectory
    tickets_dir = Path('results/tickets')
    tickets_dir.mkdir(parents=True, exist_ok=True)
    
    # Create ticket lookup map
    ticket_map = {t.ticket_id: t for t in tickets}
    
    # Handle datetime serialization
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    # Save each decision with its original ticket data
    for decision in decisions:
        ticket = ticket_map.get(decision.ticket_id)
        if not ticket:
            print(f"⚠️  Warning: No ticket found for decision {decision.ticket_id}")
            continue
        
        # Create combined output with original ticket and decision
        output_data = {
            'ticket': ticket.model_dump(),
            'decision': decision.model_dump()
        }
        
        # Save to individual file
        output_file = tickets_dir / f"{decision.ticket_id}.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, default=serialize_datetime)
    
    print(f"\n✓ Individual ticket results saved to: results/tickets/")
    print(f"  Total files created: {len(decisions)}")


def save_results(decisions: List[FinalDecision], output_path: str = 'results/routing_decisions.json'):
    """
    Save all FinalDecision models to JSON file using Pydantic serialization.
    
    Args:
        decisions: List of FinalDecision models
        output_path: Path to output JSON file
    """
    # Create results/ directory if it doesn't exist
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert FinalDecision models to dicts using Pydantic's model_dump()
    decisions_data = [d.model_dump() for d in decisions]
    
    # Handle datetime serialization by converting to ISO format strings
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    # Save to JSON with proper indentation
    with open(output_file, 'w') as f:
        json.dump(decisions_data, f, indent=2, default=serialize_datetime)
    
    print(f"\n✓ Results saved to: {output_path}")



def display_summary(decisions: List[FinalDecision]):
    """
    Calculate and display summary statistics.
    
    Args:
        decisions: List of FinalDecision models
    """
    if not decisions:
        print("\nNo decisions to summarize.")
        return
    
    # Calculate statistics
    total_tickets = len(decisions)
    avg_processing_time = sum(d.processing_time_ms for d in decisions) / total_tickets
    avg_confidence = sum(d.confidence_score for d in decisions) / total_tickets
    manual_review_count = sum(1 for d in decisions if d.requires_manual_review)
    
    # Team distribution using Team enum values
    from collections import Counter
    team_counts = Counter(d.assigned_team.value for d in decisions)
    
    # Priority distribution using PriorityLevel enum values
    priority_counts = Counter(d.priority_level.value for d in decisions)
    
    # Display formatted summary
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"\nTotal tickets processed: {total_tickets}")
    print(f"Average processing time: {avg_processing_time:.0f}ms")
    print(f"Average confidence score: {avg_confidence:.1f}%")
    print(f"Tickets requiring manual review: {manual_review_count}")
    
    print("\nTeam Distribution:")
    for team, count in sorted(team_counts.items()):
        percentage = (count / total_tickets) * 100
        print(f"  {team}: {count} tickets ({percentage:.1f}%)")
    
    print("\nPriority Distribution:")
    for priority, count in sorted(priority_counts.items()):
        percentage = (count / total_tickets) * 100
        print(f"  {priority}: {count} tickets ({percentage:.1f}%)")
    
    print("=" * 80 + "\n")



def main():
    """
    Main CLI entry point for the AI-Powered Customer Support System MVP.
    """
    print("=" * 80)
    print("AI-Powered Customer Support System - MVP")
    print("=" * 80 + "\n")
    
    try:
        # Load tickets
        print("Loading sample tickets...")
        tickets = load_tickets_from_mock()
        print(f"✓ Loaded {len(tickets)} tickets\n")
        
        # Validate tickets using Pydantic validation
        try:
            validate_tickets(tickets)
            print("✓ All tickets validated successfully\n")
        except ValidationError as e:
            print(f"\n✗ Ticket validation failed:")
            # Handle Pydantic ValidationError for missing or malformed ticket data
            if hasattr(e, 'errors'):
                for error in e.errors():
                    field = '.'.join(str(loc) for loc in error['loc'])
                    message = error['msg']
                    print(f"  Field '{field}': {message}")
            else:
                print(f"  {str(e)}")
            print("\nPlease fix the ticket data and try again.")
            return
        
        # Initialize agent
        agent = initialize_agent()
        
        # Process tickets
        decisions = process_tickets(agent, tickets)
        
        if not decisions:
            print("No tickets were successfully processed.")
            return
        
        # Display results
        display_results(decisions, tickets)
        
        # Save results (summary file)
        save_results(decisions)
        
        # Save individual ticket results
        save_individual_ticket_results(tickets, decisions)
        
        # Display summary
        display_summary(decisions)
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
    except ValidationError as e:
        # Handle Pydantic ValidationError at top level
        print(f"\n✗ Validation error: {str(e)}")
        if hasattr(e, 'errors'):
            for error in e.errors():
                field = '.'.join(str(loc) for loc in error['loc'])
                message = error['msg']
                print(f"  Field '{field}': {message}")
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()

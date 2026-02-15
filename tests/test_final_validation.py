#!/usr/bin/env python
"""
Quick test script for Task 11.2 and 11.3
Processes a small subset of tickets to verify functionality
"""

import json
from pathlib import Path
from datetime import datetime
from src.agent import TicketRoutingAgent
from src.models import FinalDecision
from mock_data import SAMPLE_TICKETS

def test_small_batch():
    """Process first 3 tickets to test functionality"""
    print("=" * 80)
    print("QUICK VALIDATION TEST - Processing 3 sample tickets")
    print("=" * 80)
    
    # Take first 3 tickets
    test_tickets = SAMPLE_TICKETS[:3]
    
    print(f"\nProcessing {len(test_tickets)} tickets...")
    
    # Initialize agent
    try:
        agent = TicketRoutingAgent()
        print("✓ Agent initialized")
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False
    
    # Process tickets
    decisions = []
    for idx, ticket in enumerate(test_tickets, 1):
        print(f"\nProcessing ticket {idx}/{len(test_tickets)}: {ticket.ticket_id}")
        try:
            decision = agent.process_ticket(ticket)
            decisions.append(decision)
            print(f"  ✓ Routed to: {decision.assigned_team.value}")
            print(f"  Priority: {decision.priority_level.value}")
            print(f"  Confidence: {decision.confidence_score:.1f}%")
            print(f"  Time: {decision.processing_time_ms:.0f}ms")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    # Save results
    print("\n--- Saving Results ---")
    
    # Create results directory
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)
    
    # Save summary file
    summary_file = results_dir / 'routing_decisions.json'
    decisions_data = [d.model_dump() for d in decisions]
    
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    with open(summary_file, 'w') as f:
        json.dump(decisions_data, f, indent=2, default=serialize_datetime)
    
    print(f"✓ Summary file saved: {summary_file}")
    
    # Save individual ticket files
    tickets_dir = results_dir / 'tickets'
    tickets_dir.mkdir(exist_ok=True)
    
    ticket_map = {t.ticket_id: t for t in test_tickets}
    
    for decision in decisions:
        ticket = ticket_map[decision.ticket_id]
        output_data = {
            'ticket': ticket.model_dump(),
            'decision': decision.model_dump()
        }
        
        output_file = tickets_dir / f"{decision.ticket_id}.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, default=serialize_datetime)
    
    print(f"✓ Individual ticket files saved: {tickets_dir}")
    print(f"  Total files: {len(decisions)}")
    
    # Validate results
    print("\n--- Validation ---")
    
    # Check processing times
    max_time = max(d.processing_time_ms for d in decisions) / 1000
    print(f"✓ Max processing time: {max_time:.2f}s")
    
    # Check team distribution
    teams = set(d.assigned_team.value for d in decisions)
    print(f"✓ Teams represented: {teams}")
    
    # Check priority distribution
    priorities = set(d.priority_level.value for d in decisions)
    print(f"✓ Priorities represented: {priorities}")
    
    # Check confidence scores
    confidences = [d.confidence_score for d in decisions]
    print(f"✓ Confidence range: {min(confidences):.1f}% - {max(confidences):.1f}%")
    
    # Verify files exist
    assert summary_file.exists(), "Summary file not created"
    assert tickets_dir.exists(), "Tickets directory not created"
    assert len(list(tickets_dir.glob('*.json'))) == len(decisions), "Not all ticket files created"
    
    print("\n" + "=" * 80)
    print("✓ QUICK VALIDATION TEST PASSED")
    print("=" * 80)
    print("\nAll functionality working correctly!")
    print("To process all 20 tickets, run: python -m src.main")
    
    return True


if __name__ == "__main__":
    try:
        success = test_small_batch()
        if not success:
            print("\n❌ Test failed")
            exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

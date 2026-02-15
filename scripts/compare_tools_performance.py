"""
Performance comparison script for mock vs AI-powered tools.

Processes a subset of sample tickets with both tool modes and compares:
- Processing time
- Cost differences
- Confidence scores
- Routing decisions
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from src.agent import TicketRoutingAgent
from src.models import Ticket, FinalDecision
from mock_data import SAMPLE_TICKETS


# Pricing constants (as of Feb 2024)
# Claude Haiku 4.5 pricing
HAIKU_INPUT_PRICE_PER_1K = 0.00025  # $0.25 per million input tokens
HAIKU_OUTPUT_PRICE_PER_1K = 0.00125  # $1.25 per million output tokens

# Estimated token usage per tool call
CLASSIFY_ISSUE_TOKENS = {'input': 200, 'output': 100}
EXTRACT_ENTITIES_TOKENS = {'input': 200, 'output': 80}
ROUTE_TO_TEAM_TOKENS = {'input': 300, 'output': 150}

# Main agent call tokens (approximate)
MAIN_AGENT_TOKENS = {'input': 500, 'output': 300}


def estimate_cost_per_ticket(use_agent_tools: bool) -> float:
    """
    Estimate cost per ticket based on tool mode.
    
    Args:
        use_agent_tools: If True, calculate cost for AI-powered tools
        
    Returns:
        Estimated cost in USD
    """
    if not use_agent_tools:
        # Mock tools: only main agent call
        input_cost = (MAIN_AGENT_TOKENS['input'] / 1000) * HAIKU_INPUT_PRICE_PER_1K
        output_cost = (MAIN_AGENT_TOKENS['output'] / 1000) * HAIKU_OUTPUT_PRICE_PER_1K
        return input_cost + output_cost
    else:
        # AI-powered tools: main agent + 3 AI tool calls
        # Main agent
        main_input = (MAIN_AGENT_TOKENS['input'] / 1000) * HAIKU_INPUT_PRICE_PER_1K
        main_output = (MAIN_AGENT_TOKENS['output'] / 1000) * HAIKU_OUTPUT_PRICE_PER_1K
        
        # classify_issue tool
        classify_input = (CLASSIFY_ISSUE_TOKENS['input'] / 1000) * HAIKU_INPUT_PRICE_PER_1K
        classify_output = (CLASSIFY_ISSUE_TOKENS['output'] / 1000) * HAIKU_OUTPUT_PRICE_PER_1K
        
        # extract_entities tool
        extract_input = (EXTRACT_ENTITIES_TOKENS['input'] / 1000) * HAIKU_INPUT_PRICE_PER_1K
        extract_output = (EXTRACT_ENTITIES_TOKENS['output'] / 1000) * HAIKU_OUTPUT_PRICE_PER_1K
        
        # route_to_team tool
        route_input = (ROUTE_TO_TEAM_TOKENS['input'] / 1000) * HAIKU_INPUT_PRICE_PER_1K
        route_output = (ROUTE_TO_TEAM_TOKENS['output'] / 1000) * HAIKU_OUTPUT_PRICE_PER_1K
        
        total = (main_input + main_output + 
                classify_input + classify_output +
                extract_input + extract_output +
                route_input + route_output)
        
        return total


def process_tickets_with_mode(
    tickets: List[Ticket], 
    use_agent_tools: bool
) -> tuple[List[FinalDecision], float, float]:
    """
    Process tickets with specified tool mode.
    
    Args:
        tickets: List of Ticket models to process
        use_agent_tools: If True, use AI-powered tools; if False, use mock tools
        
    Returns:
        Tuple of (decisions, total_time_ms, estimated_cost)
    """
    mode_name = "AI-powered" if use_agent_tools else "Mock"
    print(f"\n{'='*60}")
    print(f"Processing with {mode_name} tools...")
    print(f"{'='*60}\n")
    
    # Initialize agent with specified mode
    agent = TicketRoutingAgent(use_agent_tools=use_agent_tools)
    
    decisions: List[FinalDecision] = []
    total_time = 0.0
    
    for i, ticket in enumerate(tickets, 1):
        print(f"[{i}/{len(tickets)}] Processing {ticket.ticket_id}: {ticket.subject[:50]}...")
        
        start_time = time.time()
        decision = agent.process_ticket(ticket)
        elapsed = (time.time() - start_time) * 1000  # Convert to ms
        
        decisions.append(decision)
        total_time += elapsed
        
        print(f"  ✓ Routed to: {decision.assigned_team.value}")
        print(f"  ✓ Priority: {decision.priority_level.value}")
        print(f"  ✓ Confidence: {decision.confidence_score:.1f}%")
        print(f"  ✓ Time: {elapsed:.0f}ms\n")
    
    # Estimate cost
    estimated_cost = estimate_cost_per_ticket(use_agent_tools) * len(tickets)
    
    print(f"{'='*60}")
    print(f"{mode_name} tools completed")
    print(f"Total time: {total_time:.0f}ms")
    print(f"Estimated cost: ${estimated_cost:.4f}")
    print(f"{'='*60}\n")
    
    return decisions, total_time, estimated_cost


def compare_decisions(
    mock_decisions: List[FinalDecision],
    agent_decisions: List[FinalDecision]
) -> Dict[str, Any]:
    """
    Compare routing decisions between mock and AI-powered tools.
    
    Args:
        mock_decisions: Decisions from mock tools
        agent_decisions: Decisions from AI-powered tools
        
    Returns:
        Dictionary with comparison metrics
    """
    comparison = {
        'total_tickets': len(mock_decisions),
        'team_agreement': 0,
        'priority_agreement': 0,
        'team_differences': [],
        'priority_differences': [],
        'confidence_comparison': {
            'mock_avg': 0.0,
            'agent_avg': 0.0,
            'mock_min': 100.0,
            'mock_max': 0.0,
            'agent_min': 100.0,
            'agent_max': 0.0
        }
    }
    
    mock_confidences = []
    agent_confidences = []
    
    for mock_dec, agent_dec in zip(mock_decisions, agent_decisions):
        # Compare team assignments
        if mock_dec.assigned_team == agent_dec.assigned_team:
            comparison['team_agreement'] += 1
        else:
            comparison['team_differences'].append({
                'ticket_id': mock_dec.ticket_id,
                'mock_team': mock_dec.assigned_team.value,
                'agent_team': agent_dec.assigned_team.value
            })
        
        # Compare priority levels
        if mock_dec.priority_level == agent_dec.priority_level:
            comparison['priority_agreement'] += 1
        else:
            comparison['priority_differences'].append({
                'ticket_id': mock_dec.ticket_id,
                'mock_priority': mock_dec.priority_level.value,
                'agent_priority': agent_dec.priority_level.value
            })
        
        # Collect confidence scores
        mock_confidences.append(mock_dec.confidence_score)
        agent_confidences.append(agent_dec.confidence_score)
    
    # Calculate confidence statistics
    comparison['confidence_comparison']['mock_avg'] = sum(mock_confidences) / len(mock_confidences)
    comparison['confidence_comparison']['agent_avg'] = sum(agent_confidences) / len(agent_confidences)
    comparison['confidence_comparison']['mock_min'] = min(mock_confidences)
    comparison['confidence_comparison']['mock_max'] = max(mock_confidences)
    comparison['confidence_comparison']['agent_min'] = min(agent_confidences)
    comparison['confidence_comparison']['agent_max'] = max(agent_confidences)
    
    return comparison


def generate_report(
    mock_decisions: List[FinalDecision],
    agent_decisions: List[FinalDecision],
    mock_time: float,
    agent_time: float,
    mock_cost: float,
    agent_cost: float,
    comparison: Dict[str, Any]
) -> str:
    """
    Generate comprehensive comparison report.
    
    Args:
        mock_decisions: Decisions from mock tools
        agent_decisions: Decisions from AI-powered tools
        mock_time: Total processing time for mock tools (ms)
        agent_time: Total processing time for AI-powered tools (ms)
        mock_cost: Estimated cost for mock tools
        agent_cost: Estimated cost for AI-powered tools
        comparison: Comparison metrics dictionary
        
    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 80)
    report.append("MOCK VS AI-POWERED TOOLS PERFORMANCE COMPARISON")
    report.append("=" * 80)
    report.append("")
    
    # Summary
    report.append("SUMMARY")
    report.append("-" * 80)
    report.append(f"Tickets processed: {comparison['total_tickets']}")
    report.append(f"Test date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("")
    
    # Processing Time Comparison
    report.append("PROCESSING TIME")
    report.append("-" * 80)
    report.append(f"Mock tools total time:      {mock_time:>10.0f} ms")
    report.append(f"AI-powered tools total:     {agent_time:>10.0f} ms")
    report.append(f"Difference:                 {agent_time - mock_time:>10.0f} ms ({((agent_time / mock_time - 1) * 100):+.1f}%)")
    report.append("")
    report.append(f"Mock tools avg per ticket:  {mock_time / comparison['total_tickets']:>10.0f} ms")
    report.append(f"AI-powered avg per ticket:  {agent_time / comparison['total_tickets']:>10.0f} ms")
    report.append("")
    
    # Cost Comparison
    report.append("COST COMPARISON")
    report.append("-" * 80)
    report.append(f"Mock tools estimated cost:      ${mock_cost:>8.4f}")
    report.append(f"AI-powered tools estimated:     ${agent_cost:>8.4f}")
    report.append(f"Cost difference:                ${agent_cost - mock_cost:>8.4f} ({((agent_cost / mock_cost - 1) * 100):+.1f}%)")
    report.append("")
    report.append(f"Mock tools cost per ticket:     ${mock_cost / comparison['total_tickets']:>8.4f}")
    report.append(f"AI-powered cost per ticket:     ${agent_cost / comparison['total_tickets']:>8.4f}")
    report.append("")
    
    # Routing Decision Comparison
    report.append("ROUTING DECISION COMPARISON")
    report.append("-" * 80)
    team_agreement_pct = (comparison['team_agreement'] / comparison['total_tickets']) * 100
    priority_agreement_pct = (comparison['priority_agreement'] / comparison['total_tickets']) * 100
    
    report.append(f"Team assignment agreement:  {comparison['team_agreement']}/{comparison['total_tickets']} ({team_agreement_pct:.1f}%)")
    report.append(f"Priority level agreement:   {comparison['priority_agreement']}/{comparison['total_tickets']} ({priority_agreement_pct:.1f}%)")
    report.append("")
    
    if comparison['team_differences']:
        report.append("Team assignment differences:")
        for diff in comparison['team_differences']:
            report.append(f"  • {diff['ticket_id']}: Mock={diff['mock_team']}, AI={diff['agent_team']}")
        report.append("")
    
    if comparison['priority_differences']:
        report.append("Priority level differences:")
        for diff in comparison['priority_differences']:
            report.append(f"  • {diff['ticket_id']}: Mock={diff['mock_priority']}, AI={diff['agent_priority']}")
        report.append("")
    
    # Confidence Score Comparison
    report.append("CONFIDENCE SCORE COMPARISON")
    report.append("-" * 80)
    conf = comparison['confidence_comparison']
    report.append(f"Mock tools average:     {conf['mock_avg']:>6.1f}% (range: {conf['mock_min']:.1f}% - {conf['mock_max']:.1f}%)")
    report.append(f"AI-powered average:     {conf['agent_avg']:>6.1f}% (range: {conf['agent_min']:.1f}% - {conf['agent_max']:.1f}%)")
    report.append(f"Difference:             {conf['agent_avg'] - conf['mock_avg']:>+6.1f}%")
    report.append("")
    
    # Detailed Ticket-by-Ticket Comparison
    report.append("DETAILED TICKET-BY-TICKET COMPARISON")
    report.append("-" * 80)
    report.append(f"{'Ticket ID':<12} {'Mock Team':<20} {'AI Team':<20} {'Mock Pri':<10} {'AI Pri':<10} {'Mock Conf':<12} {'AI Conf':<12}")
    report.append("-" * 80)
    
    for mock_dec, agent_dec in zip(mock_decisions, agent_decisions):
        team_match = "✓" if mock_dec.assigned_team == agent_dec.assigned_team else "✗"
        pri_match = "✓" if mock_dec.priority_level == agent_dec.priority_level else "✗"
        
        report.append(
            f"{mock_dec.ticket_id:<12} "
            f"{mock_dec.assigned_team.value:<20} "
            f"{agent_dec.assigned_team.value:<20} "
            f"{mock_dec.priority_level.value:<10} "
            f"{agent_dec.priority_level.value:<10} "
            f"{mock_dec.confidence_score:>6.1f}%     "
            f"{agent_dec.confidence_score:>6.1f}%"
        )
    
    report.append("")
    report.append("=" * 80)
    report.append("KEY FINDINGS")
    report.append("=" * 80)
    report.append("")
    
    # Generate key findings
    if agent_time > mock_time * 2:
        report.append("• AI-powered tools are significantly slower (>2x) than mock tools")
    elif agent_time > mock_time * 1.5:
        report.append("• AI-powered tools are moderately slower (1.5-2x) than mock tools")
    else:
        report.append("• AI-powered tools have comparable speed to mock tools")
    
    if agent_cost > mock_cost * 2:
        report.append("• AI-powered tools cost significantly more (>2x) than mock tools")
    elif agent_cost > mock_cost * 1.5:
        report.append("• AI-powered tools cost moderately more (1.5-2x) than mock tools")
    else:
        report.append("• AI-powered tools have comparable cost to mock tools")
    
    if team_agreement_pct >= 80:
        report.append(f"• High team assignment agreement ({team_agreement_pct:.0f}%) - both modes route similarly")
    elif team_agreement_pct >= 60:
        report.append(f"• Moderate team assignment agreement ({team_agreement_pct:.0f}%) - some routing differences")
    else:
        report.append(f"• Low team assignment agreement ({team_agreement_pct:.0f}%) - significant routing differences")
    
    if conf['agent_avg'] > conf['mock_avg'] + 10:
        report.append("• AI-powered tools show higher confidence scores")
    elif conf['agent_avg'] < conf['mock_avg'] - 10:
        report.append("• Mock tools show higher confidence scores")
    else:
        report.append("• Both modes show similar confidence levels")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Main comparison execution."""
    print("\n" + "=" * 80)
    print("MOCK VS AI-POWERED TOOLS PERFORMANCE COMPARISON")
    print("=" * 80)
    print("\nThis script will process 5 sample tickets with both tool modes")
    print("and compare processing time, cost, and routing decisions.\n")
    
    # Select 5 diverse tickets for comparison
    # Choose tickets that cover different issue types and customer types
    test_tickets = [
        SAMPLE_TICKETS[0],   # TKT-001: VIP customer, network outage
        SAMPLE_TICKETS[3],   # TKT-004: Standard customer, billing dispute
        SAMPLE_TICKETS[6],   # TKT-007: Standard customer, technical problem
        SAMPLE_TICKETS[10],  # TKT-011: Standard customer, account access
        SAMPLE_TICKETS[13],  # TKT-014: VIP customer, mixed issues
    ]
    
    print(f"Selected {len(test_tickets)} tickets for comparison:")
    for ticket in test_tickets:
        print(f"  • {ticket.ticket_id}: {ticket.subject[:60]}")
    print()
    
    # Process with mock tools
    mock_decisions, mock_time, mock_cost = process_tickets_with_mode(
        test_tickets, 
        use_agent_tools=False
    )
    
    # Process with AI-powered tools
    agent_decisions, agent_time, agent_cost = process_tickets_with_mode(
        test_tickets,
        use_agent_tools=True
    )
    
    # Compare decisions
    comparison = compare_decisions(mock_decisions, agent_decisions)
    
    # Generate report
    report = generate_report(
        mock_decisions,
        agent_decisions,
        mock_time,
        agent_time,
        mock_cost,
        agent_cost,
        comparison
    )
    
    # Display report
    print("\n" + report)
    
    # Save results
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)
    
    # Save detailed results as JSON
    results_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'test_tickets': [t.ticket_id for t in test_tickets],
        'mock_tools': {
            'decisions': [d.model_dump() for d in mock_decisions],
            'total_time_ms': mock_time,
            'estimated_cost_usd': mock_cost
        },
        'agent_tools': {
            'decisions': [d.model_dump() for d in agent_decisions],
            'total_time_ms': agent_time,
            'estimated_cost_usd': agent_cost
        },
        'comparison': comparison
    }
    
    results_file = results_dir / 'tools_comparison_results.json'
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2, default=str)
    
    print(f"\n✓ Detailed results saved to: {results_file}")
    
    # Save report as text file
    report_file = results_dir / 'tools_comparison_report.txt'
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"✓ Comparison report saved to: {report_file}")
    print()


if __name__ == '__main__':
    main()

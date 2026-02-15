"""
Mock data module for AI-Powered Customer Support System MVP.

Provides sample data using Pydantic models for testing without external dependencies.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from src.models import (
    Customer, AccountType,
    ServiceStatus, ServiceHealth, Outage,
    HistoricalTicket,
    Ticket
)


# Mock Customer Database (5-10 customers with VIP and non-VIP examples)
MOCK_CUSTOMERS: Dict[str, Customer] = {
    'CUST001': Customer(
        customer_id='CUST001',
        is_vip=True,
        account_type=AccountType.ENTERPRISE,
        lifetime_value=150000.0,
        account_standing='Excellent',
        service_plan='Enterprise Premium'
    ),
    'CUST002': Customer(
        customer_id='CUST002',
        is_vip=False,
        account_type=AccountType.CONSUMER,
        lifetime_value=500.0,
        account_standing='Good',
        service_plan='Basic'
    ),
    'CUST003': Customer(
        customer_id='CUST003',
        is_vip=True,
        account_type=AccountType.BUSINESS,
        lifetime_value=75000.0,
        account_standing='Good',
        service_plan='Business Plus'
    ),
    'CUST004': Customer(
        customer_id='CUST004',
        is_vip=False,
        account_type=AccountType.CONSUMER,
        lifetime_value=1200.0,
        account_standing='Good',
        service_plan='Standard'
    ),
    'CUST005': Customer(
        customer_id='CUST005',
        is_vip=False,
        account_type=AccountType.BUSINESS,
        lifetime_value=25000.0,
        account_standing='Fair',
        service_plan='Business Basic'
    ),
    'CUST006': Customer(
        customer_id='CUST006',
        is_vip=True,
        account_type=AccountType.ENTERPRISE,
        lifetime_value=200000.0,
        account_standing='Excellent',
        service_plan='Enterprise Elite'
    ),
    'CUST007': Customer(
        customer_id='CUST007',
        is_vip=False,
        account_type=AccountType.CONSUMER,
        lifetime_value=300.0,
        account_standing='Good',
        service_plan='Basic'
    ),
    'CUST008': Customer(
        customer_id='CUST008',
        is_vip=False,
        account_type=AccountType.CONSUMER,
        lifetime_value=800.0,
        account_standing='Good',
        service_plan='Standard'
    ),
}


# Mock Service Status (healthy and outage scenarios)
MOCK_SERVICE_STATUS: Dict[str, ServiceStatus] = {
    'SVC001': ServiceStatus(
        service_id='SVC001',
        service_health=ServiceHealth.OUTAGE,
        active_outages=[
            Outage(
                service_id='SVC001',
                severity='Critical',
                started_at=datetime.utcnow() - timedelta(hours=2),
                description='Network connectivity issues in East region'
            )
        ]
    ),
    'SVC002': ServiceStatus(
        service_id='SVC002',
        service_health=ServiceHealth.HEALTHY,
        active_outages=[]
    ),
    'SVC003': ServiceStatus(
        service_id='SVC003',
        service_health=ServiceHealth.DEGRADED,
        active_outages=[
            Outage(
                service_id='SVC003',
                severity='Medium',
                started_at=datetime.utcnow() - timedelta(minutes=30),
                description='Intermittent slowness in billing system'
            )
        ]
    ),
    'SVC004': ServiceStatus(
        service_id='SVC004',
        service_health=ServiceHealth.HEALTHY,
        active_outages=[]
    ),
    'SVC005': ServiceStatus(
        service_id='SVC005',
        service_health=ServiceHealth.OUTAGE,
        active_outages=[
            Outage(
                service_id='SVC005',
                severity='Critical',
                started_at=datetime.utcnow() - timedelta(hours=4),
                description='Authentication service down'
            )
        ]
    ),
}


# Mock Historical Tickets
MOCK_HISTORY: Dict[str, List[HistoricalTicket]] = {
    'CUST001': [
        HistoricalTicket(
            ticket_id='TKT-HIST-001',
            issue_type='Network Outage',
            resolution_time_hours=2.5,
            escalated=True,
            resolved_at=datetime.utcnow() - timedelta(days=30)
        ),
        HistoricalTicket(
            ticket_id='TKT-HIST-002',
            issue_type='Technical Problem',
            resolution_time_hours=1.0,
            escalated=False,
            resolved_at=datetime.utcnow() - timedelta(days=15)
        ),
    ],
    'CUST002': [
        HistoricalTicket(
            ticket_id='TKT-HIST-003',
            issue_type='Billing Dispute',
            resolution_time_hours=24.0,
            escalated=False,
            resolved_at=datetime.utcnow() - timedelta(days=60)
        ),
    ],
    'CUST003': [
        HistoricalTicket(
            ticket_id='TKT-HIST-004',
            issue_type='Account Access',
            resolution_time_hours=0.5,
            escalated=False,
            resolved_at=datetime.utcnow() - timedelta(days=10)
        ),
        HistoricalTicket(
            ticket_id='TKT-HIST-005',
            issue_type='Technical Problem',
            resolution_time_hours=3.0,
            escalated=True,
            resolved_at=datetime.utcnow() - timedelta(days=5)
        ),
        HistoricalTicket(
            ticket_id='TKT-HIST-006',
            issue_type='Network Outage',
            resolution_time_hours=4.0,
            escalated=True,
            resolved_at=datetime.utcnow() - timedelta(days=2)
        ),
    ],
    'CUST005': [
        HistoricalTicket(
            ticket_id='TKT-HIST-007',
            issue_type='Billing Dispute',
            resolution_time_hours=48.0,
            escalated=True,
            resolved_at=datetime.utcnow() - timedelta(days=90)
        ),
    ],
}


# Sample Tickets (10-20 diverse tickets covering all issue types)
SAMPLE_TICKETS: List[Ticket] = [
    # Network Outage tickets
    Ticket(
        ticket_id='TKT-001',
        customer_id='CUST001',
        subject='Internet connection down - URGENT',
        description='My internet has been down for 2 hours. Error code: NET-500. Service SVC001 is completely offline. This is affecting our entire office.',
        timestamp=datetime.utcnow() - timedelta(hours=2)
    ),
    Ticket(
        ticket_id='TKT-002',
        customer_id='CUST004',
        subject='No internet connection',
        description='Cannot connect to the internet since this morning. Getting error NET-404.',
        timestamp=datetime.utcnow() - timedelta(hours=5)
    ),
    Ticket(
        ticket_id='TKT-003',
        customer_id='CUST006',
        subject='Network outage affecting multiple locations',
        description='We are experiencing a complete network outage across all our branch offices. Service SVC001 is down. This is critical for our business operations.',
        timestamp=datetime.utcnow() - timedelta(minutes=30)
    ),
    
    # Billing Dispute tickets
    Ticket(
        ticket_id='TKT-004',
        customer_id='CUST002',
        subject='Incorrect charge on my bill',
        description='I was charged $150.00 for services I did not use. My account ACC-12345 shows charges that do not match my plan.',
        timestamp=datetime.utcnow() - timedelta(days=1)
    ),
    Ticket(
        ticket_id='TKT-005',
        customer_id='CUST005',
        subject='Billing dispute - overcharged',
        description='My invoice shows $2,500.00 but my contract states $1,800.00 per month. Account ACC-67890. Please review and adjust.',
        timestamp=datetime.utcnow() - timedelta(hours=12)
    ),
    Ticket(
        ticket_id='TKT-006',
        customer_id='CUST007',
        subject='Double payment charged',
        description='I was charged twice for my monthly bill. $75.99 was deducted twice from my account. Service SVC003.',
        timestamp=datetime.utcnow() - timedelta(hours=8)
    ),
    
    # Technical Problem tickets
    Ticket(
        ticket_id='TKT-007',
        customer_id='CUST004',
        subject='Router not working properly',
        description='My router keeps disconnecting every few minutes. Error code: TECH-301. I have tried restarting it multiple times.',
        timestamp=datetime.utcnow() - timedelta(hours=3)
    ),
    Ticket(
        ticket_id='TKT-008',
        customer_id='CUST008',
        subject='Slow internet speed',
        description='Internet speed is very slow, only getting 10 Mbps instead of the promised 100 Mbps. Service SVC002.',
        timestamp=datetime.utcnow() - timedelta(hours=6)
    ),
    Ticket(
        ticket_id='TKT-009',
        customer_id='CUST003',
        subject='Email service not working',
        description='Cannot send or receive emails through your service. Error AUTH-202. This is impacting our business communications.',
        timestamp=datetime.utcnow() - timedelta(hours=4)
    ),
    Ticket(
        ticket_id='TKT-010',
        customer_id='CUST002',
        subject='WiFi signal weak',
        description='WiFi signal is very weak in certain areas of my house. Need technical assistance to improve coverage.',
        timestamp=datetime.utcnow() - timedelta(days=2)
    ),
    
    # Account Access tickets
    Ticket(
        ticket_id='TKT-011',
        customer_id='CUST007',
        subject='Cannot login to my account',
        description='I forgot my password and the reset link is not working. Account ACC-11111. Need urgent access.',
        timestamp=datetime.utcnow() - timedelta(hours=1)
    ),
    Ticket(
        ticket_id='TKT-012',
        customer_id='CUST008',
        subject='Account locked',
        description='My account has been locked after multiple login attempts. Service SVC005. Please unlock it.',
        timestamp=datetime.utcnow() - timedelta(minutes=45)
    ),
    Ticket(
        ticket_id='TKT-013',
        customer_id='CUST001',
        subject='Need to reset authentication credentials',
        description='Our admin account ACC-99999 needs password reset. Authentication service SVC005 is showing errors.',
        timestamp=datetime.utcnow() - timedelta(hours=2)
    ),
    
    # Mixed/Complex tickets
    Ticket(
        ticket_id='TKT-014',
        customer_id='CUST006',
        subject='Multiple issues - billing and service',
        description='I am experiencing network outages on SVC001 and also noticed incorrect charges of $500.00 on my bill. Account ACC-55555.',
        timestamp=datetime.utcnow() - timedelta(hours=10)
    ),
    Ticket(
        ticket_id='TKT-015',
        customer_id='CUST003',
        subject='Service degradation and billing question',
        description='Service SVC003 has been slow for the past week. Also, I have a question about my recent invoice showing $3,200.00.',
        timestamp=datetime.utcnow() - timedelta(days=1, hours=6)
    ),
    
    # Additional diverse tickets
    Ticket(
        ticket_id='TKT-016',
        customer_id='CUST005',
        subject='Cannot access customer portal',
        description='The customer portal login page is not loading. Error code: WEB-500. Need to access my account urgently.',
        timestamp=datetime.utcnow() - timedelta(hours=7)
    ),
    Ticket(
        ticket_id='TKT-017',
        customer_id='CUST004',
        subject='Installation appointment issue',
        description='My scheduled installation for tomorrow was cancelled without notice. Need to reschedule ASAP. Contact: 555-123-4567.',
        timestamp=datetime.utcnow() - timedelta(hours=15)
    ),
    Ticket(
        ticket_id='TKT-018',
        customer_id='CUST002',
        subject='Service upgrade inquiry',
        description='I want to upgrade from Basic to Standard plan. What are the costs and how long will it take?',
        timestamp=datetime.utcnow() - timedelta(days=3)
    ),
    Ticket(
        ticket_id='TKT-019',
        customer_id='CUST006',
        subject='Critical: Complete service failure',
        description='All services are down for our enterprise account ACC-88888. Network SVC001, email, and authentication SVC005 all failing. This is costing us thousands per hour.',
        timestamp=datetime.utcnow() - timedelta(minutes=15)
    ),
    Ticket(
        ticket_id='TKT-020',
        customer_id='CUST008',
        subject='Refund request',
        description='Requesting refund of $45.00 for service outage last week. My service was down for 3 days.',
        timestamp=datetime.utcnow() - timedelta(days=1, hours=2)
    ),
]

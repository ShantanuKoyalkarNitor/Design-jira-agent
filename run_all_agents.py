#!/usr/bin/env python3
"""
Design Review Agent - Reviews design documents against Jira ticket requirements
Input: Requirement Ticket ID, Design Ticket ID
Output: Comprehensive design document review report
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Make console output safe on Windows shells that default to a legacy code page.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from run_agent import AgentRunner


def review_design_document(requirement_ticket_id: str, design_ticket_id: str):
    """Review design document based on Jira ticket requirements
    
    Args:
        requirement_ticket_id: Ticket ID containing requirements
        design_ticket_id: Ticket ID containing design document
    """
    
    print("\n" + "=" * 80)
    print(f"DESIGN DOCUMENT REVIEW")
    print(f"Requirements: {requirement_ticket_id} | Design: {design_ticket_id}")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Agent sequence: requirement_analysis → design → security → scalability
    agents = [
        'requirement_analysis',
        'design_document_review',
        'design_security_review',
        'design_scalability_review'
    ]
    
    all_results = {
        'requirement_ticket_id': requirement_ticket_id,
        'design_ticket_id': design_ticket_id,
        'timestamp': datetime.now().isoformat(),
        'review_type': 'design_document_review',
        'results': {}
    }
    
    for agent_name in agents:
        print(f"\n{'='*80}")
        print(f"AGENT: {agent_name.upper()}")
        print(f"{'='*80}")
        
        try:
            runner = AgentRunner(agent_name)
            print(f"\n✓ {agent_name} runner initialized")
            
            # Use requirement ticket for requirement analysis, design ticket for others
            ticket_id = requirement_ticket_id if agent_name == 'requirement_analysis' else design_ticket_id
            
            # Review design document - call analyze method
            print(f"\n📋 Analyzing for ticket: {ticket_id}")
            
            # Call the analyze method
            if agent_name == 'requirement_analysis':
                result = runner.analyze_requirement(ticket_id)
            else:
                # Pull the design ticket content from Jira and review the text directly
                design_content = runner.jira.format_ticket_for_review(design_ticket_id)

                if agent_name == 'design_document_review':
                    result = runner.analyze_architecture(design_content, source_name=design_ticket_id)
                elif agent_name == 'design_security_review':
                    result = runner.analyze_security(design_content, source_name=design_ticket_id)
                elif agent_name == 'design_scalability_review':
                    result = runner.analyze_scalability(design_content, source_name=design_ticket_id)
                else:
                    raise ValueError(f"Unsupported agent: {agent_name}")
            
            all_results['results'][agent_name] = result
            
            print(f"\n✓ {agent_name} analysis complete")
            if 'analysis' in result:
                print(f"Analysis Summary: {str(result['analysis'])[:200]}...")
            
        except Exception as e:
            error_msg = f"❌ Error running {agent_name}: {type(e).__name__}: {str(e)}"
            print(error_msg)
            all_results['results'][agent_name] = {
                'status': 'error',
                'error': str(e),
                'agent': agent_name
            }
    
    # Save results to file
    output_file = f"review_results_{requirement_ticket_id}_vs_{design_ticket_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n{'='*80}")
    print(f"REVIEW COMPLETE")
    print(f"{'='*80}")
    print(f"Results saved to: {output_file}\n")
    
    return all_results


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        requirement_ticket = sys.argv[1]
        design_ticket = sys.argv[2]
    elif len(sys.argv) == 2:
        # Single ticket - use for both
        requirement_ticket = sys.argv[1]
        design_ticket = sys.argv[1]
    else:
        # Default
        requirement_ticket = 'SK101-13'
        design_ticket = 'SK101-10'
    
    review_design_document(requirement_ticket, design_ticket)

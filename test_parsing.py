#!/usr/bin/env python3
"""Test the log parsing function directly"""

import os
import sys
import json

# Add the frontend directory to the Python path
frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
sys.path.insert(0, frontend_dir)

# Import the parsing function
from app import parse_results_from_logs

def test_parsing():
    """Test the log parsing function"""
    print("Testing log parsing function...")
    
    try:
        results = parse_results_from_logs()
        print(f"Results: {json.dumps(results, indent=2)}")
        
        # Check if we got any data
        if not results:
            print("No results returned - parsing failed")
        else:
            print("\nParsing successful! Summary:")
            
            if 'prospect_search' in results:
                total = results['prospect_search'].get('total_found', 0)
                print(f"  - Leads found: {total}")
            
            if 'scoring' in results:
                scores = len(results['scoring'].get('ranked_leads', []))
                print(f"  - Leads scored: {scores}")
            
            if 'outreach_content' in results:
                messages = len(results['outreach_content'].get('messages', []))
                print(f"  - Messages generated: {messages}")
            
            if 'send' in results:
                sent = len(results['send'].get('sent_status', []))
                print(f"  - Emails sent: {sent}")
                
    except Exception as e:
        print(f"Error testing parsing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parsing()
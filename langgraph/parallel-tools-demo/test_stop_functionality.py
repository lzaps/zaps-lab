#!/usr/bin/env python3
"""
Test script for the stop functionality.
This script demonstrates how to start an execution and stop it programmatically.
"""

import requests
import json
import time
import sys
from datetime import datetime


def print_event(prefix: str, data: dict):
    """Pretty print an event."""
    timestamp = data.get('timestamp', datetime.now().strftime("%H:%M:%S.%f")[:-3])
    event_type = data.get('event_type') or data.get('event', 'unknown')
    
    if event_type == 'execution_start':
        print(f"\n🚀 {prefix} Execution started")
        print(f"   ID: {data.get('execution_id')}")
        print(f"   Query: {data.get('query')}")
        print(f"   Tools: {data.get('num_tools')}")
    elif event_type == 'tool_start':
        print(f"⏳ [{timestamp}] {data.get('tool_name')} starting (delay: {data.get('delay', 0):.2f}s)")
    elif event_type == 'tool_complete':
        print(f"✅ [{timestamp}] {data.get('tool_name')} completed in {data.get('duration', 0):.2f}s")
        print(f"   Result: {data.get('result')}")
    elif event_type == 'tool_interrupted':
        print(f"🛑 [{timestamp}] {data.get('tool_name')} INTERRUPTED after {data.get('duration', 0):.2f}s")
    elif event_type == 'aggregate':
        print(f"\n📊 [{timestamp}] Aggregating results...")
        summary = data.get('summary', {})
        if summary:
            print(f"   Total duration: {summary.get('total_duration', 0):.2f}s")
            print(f"   Results collected: {summary.get('num_tools', 0)}")
    elif event_type == 'execution_complete':
        print(f"\n✨ [{timestamp}] Execution completed")
        print(f"   ID: {data.get('execution_id')}")
    else:
        print(f"📝 [{timestamp}] {event_type}: {json.dumps(data)}")


def test_stop_after_n_tools(n: int = 2, base_url: str = "http://localhost:8000"):
    """
    Test case: Stop execution after N tools complete.
    
    Args:
        n: Number of tools to wait for before stopping
        base_url: Base URL of the API
    """
    print("=" * 80)
    print(f"TEST: Stop after {n} tools complete")
    print("=" * 80)
    
    # Start execution
    print(f"\n📡 Starting streaming execution at {base_url}/execute")
    try:
        response = requests.get(
            f'{base_url}/execute?query=test_stop',
            stream=True,
            timeout=60
        )
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        print(f"   Make sure the server is running: python api.py")
        return
    
    execution_id = None
    completed_tools = []
    
    try:
        # Process stream
        for line in response.iter_lines():
            if not line:
                continue
            
            # Skip keepalive comments
            if line.startswith(b'#') or line.startswith(b':'):
                continue
            
            # Parse JSON event
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            # Print event
            print_event("", data)
            
            # Get execution ID from first event
            if data.get('event') == 'execution_start':
                execution_id = data['execution_id']
            
            # Track completed tools
            if data.get('event_type') == 'tool_complete':
                completed_tools.append(data['tool_name'])
                
                # Stop after N tools
                if len(completed_tools) == n:
                    print(f"\n🎯 Reached {n} completed tools: {', '.join(completed_tools)}")
                    print(f"🛑 Sending stop signal for execution {execution_id}...")
                    
                    try:
                        stop_response = requests.post(
                            f'{base_url}/stop/{execution_id}',
                            timeout=5
                        )
                        stop_data = stop_response.json()
                        print(f"✅ Stop response: {stop_data['message']}")
                    except requests.exceptions.RequestException as e:
                        print(f"❌ Error sending stop: {e}")
            
            # Execution complete
            if data.get('event') == 'execution_complete':
                break
    
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted by user")
        if execution_id:
            print(f"🛑 Attempting to stop execution {execution_id}...")
            try:
                requests.post(f'{base_url}/stop/{execution_id}', timeout=5)
            except:
                pass
    
    print(f"\n{'=' * 80}")
    print(f"Test completed. Tools that finished: {len(completed_tools)}/{n}")
    print(f"{'=' * 80}\n")


def test_stop_after_timeout(timeout_seconds: int = 5, base_url: str = "http://localhost:8000"):
    """
    Test case: Stop execution after timeout.
    
    Args:
        timeout_seconds: How long to wait before stopping
        base_url: Base URL of the API
    """
    print("=" * 80)
    print(f"TEST: Stop after {timeout_seconds} seconds timeout")
    print("=" * 80)
    
    # Start execution
    print(f"\n📡 Starting streaming execution at {base_url}/execute")
    try:
        response = requests.get(
            f'{base_url}/execute?query=test_timeout',
            stream=True,
            timeout=60
        )
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        return
    
    execution_id = None
    start_time = time.time()
    
    try:
        # Process stream
        for line in response.iter_lines():
            if not line:
                continue
            
            # Skip keepalive comments
            if line.startswith(b'#') or line.startswith(b':'):
                continue
            
            # Parse JSON event
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            # Print event
            print_event("", data)
            
            # Get execution ID from first event
            if data.get('event') == 'execution_start':
                execution_id = data['execution_id']
            
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed >= timeout_seconds and execution_id:
                print(f"\n⏰ Timeout reached after {elapsed:.2f}s")
                print(f"🛑 Sending stop signal for execution {execution_id}...")
                
                try:
                    stop_response = requests.post(
                        f'{base_url}/stop/{execution_id}',
                        timeout=5
                    )
                    stop_data = stop_response.json()
                    print(f"✅ Stop response: {stop_data['message']}")
                except requests.exceptions.RequestException as e:
                    print(f"❌ Error sending stop: {e}")
            
            # Execution complete
            if data.get('event') == 'execution_complete':
                break
    
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted by user")
    
    total_time = time.time() - start_time
    print(f"\n{'=' * 80}")
    print(f"Test completed in {total_time:.2f}s (timeout was {timeout_seconds}s)")
    print(f"{'=' * 80}\n")


def test_list_executions(base_url: str = "http://localhost:8000"):
    """Test listing active executions."""
    print("=" * 80)
    print("TEST: List active executions")
    print("=" * 80)
    
    try:
        response = requests.get(f'{base_url}/executions', timeout=5)
        data = response.json()
        
        print(f"\n📋 Active executions: {data['count']}")
        for exec_id in data['active_executions']:
            print(f"   • {exec_id}")
        
        if data['count'] == 0:
            print("   (none)")
        
        print(f"\n⏰ Timestamp: {data['timestamp']}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
    
    print(f"\n{'=' * 80}\n")


def main():
    """Run tests."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test the stop functionality of the parallel tools API'
    )
    parser.add_argument(
        '--test',
        choices=['tools', 'timeout', 'list', 'all'],
        default='all',
        help='Which test to run (default: all)'
    )
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='Base URL of the API (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--tools',
        type=int,
        default=2,
        help='Number of tools to wait for before stopping (default: 2)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=5,
        help='Timeout in seconds before stopping (default: 5)'
    )
    
    args = parser.parse_args()
    
    # Check API is reachable
    print(f"🔍 Checking API at {args.url}...")
    try:
        response = requests.get(f'{args.url}/health', timeout=5)
        if response.status_code == 200:
            print(f"✅ API is healthy\n")
        else:
            print(f"⚠️  API returned status {response.status_code}\n")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print(f"   Make sure the server is running:")
        print(f"   cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo")
        print(f"   source venv/bin/activate")
        print(f"   python api.py\n")
        sys.exit(1)
    
    # Run tests
    if args.test in ['list', 'all']:
        test_list_executions(args.url)
        if args.test == 'all':
            time.sleep(2)
    
    if args.test in ['tools', 'all']:
        test_stop_after_n_tools(args.tools, args.url)
        if args.test == 'all':
            time.sleep(2)
    
    if args.test in ['timeout', 'all']:
        test_stop_after_timeout(args.timeout, args.url)
    
    print("🎉 All tests completed!")


if __name__ == "__main__":
    main()


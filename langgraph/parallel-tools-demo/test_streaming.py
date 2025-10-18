#!/usr/bin/env python3
"""
Test client for streaming API - Shows real-time events!
Run: python test_streaming.py
"""

import requests
import json
import sys

def main():
    url = "http://localhost:8000/execute"
    params = {"query": "test streaming"}

    print("\n🚀 Connecting to streaming API...")
    print(f"📡 URL: {url}")
    print(f"🎯 Query: {params['query']}\n")
    print("=" * 80)
    
    try:
        response = requests.get(url, params=params, stream=True, timeout=120)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server!")
        print("   Make sure the server is running: python api.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    print("📺 Streaming events (real-time!):\n")
    
    event_count = 0
    tool_starts = []
    tool_completes = []
    
    for line in response.iter_lines():
        if not line:
            continue
            
        line_str = line.decode('utf-8')
        
        # Skip keepalive comments
        if line_str.startswith('#'):
            print(f"💭 {line_str}")
            continue
        
        # Parse JSON event
        try:
            event = json.loads(line_str)
            event_count += 1
            event_type = event.get('event_type')
            timestamp = event.get('timestamp', '')
            
            if event_type == 'execution_start':
                print(f"🎬 [{timestamp}] Execution Started")
                print(f"   📋 Query: {event.get('query')}")
                print(f"   🔧 Tools: {event.get('num_tools')}")
                print()
                
            elif event_type == 'prepare':
                print(f"⚙️  [{timestamp}] Graph preparation complete\n")
                
            elif event_type == 'tool_start':
                tool = event.get('tool_name', '?')
                delay = event.get('delay', 0)
                tool_starts.append(tool)
                print(f"🚀 [{timestamp}] {tool.upper()} started")
                print(f"   ⏱️  Estimated duration: {delay:.2f}s")
                
            elif event_type == 'tool_complete':
                tool = event.get('tool_name', '?')
                duration = event.get('duration', 0)
                result = event.get('result', 'No result')
                tool_completes.append((tool, duration))
                
                print(f"\n✅ [{timestamp}] {tool.upper()} completed")
                print(f"   ⏱️  Duration: {duration:.2f}s")
                print(f"   📊 Result: {result}")
                
            elif event_type == 'aggregate':
                summary = event.get('summary', {})
                print(f"\n{'=' * 80}")
                print(f"📊 [{timestamp}] SUMMARY")
                print(f"{'=' * 80}")
                print(f"   ⚡ Parallel execution: {summary.get('total_duration', 0):.2f}s")
                print(f"   🐌 Sequential would be: {summary.get('sequential_duration', 0):.2f}s")
                print(f"   💾 Time saved: {summary.get('time_saved', 0):.2f}s")
                print(f"   📈 Performance gain: {(summary.get('time_saved', 0) / summary.get('sequential_duration', 1) * 100):.1f}%")
                print(f"   ⚡ Fastest tool: {summary.get('fastest', 0):.2f}s")
                print(f"   🐌 Slowest tool: {summary.get('slowest', 0):.2f}s")
                print(f"   📊 Average: {summary.get('avg_duration', 0):.2f}s")
                print(f"   🔢 Total tools: {summary.get('num_tools', 0)}")
                print(f"{'=' * 80}\n")
                
            elif event_type == 'execution_complete':
                print(f"✨ [{timestamp}] Execution Complete!\n")
                
            else:
                print(f"❓ [{timestamp}] Unknown event: {event_type}")
                
        except json.JSONDecodeError:
            print(f"⚠️  Cannot parse: {line_str[:50]}...")
        except Exception as e:
            print(f"⚠️  Error processing event: {e}")
    
    # Final stats
    print("=" * 80)
    print("📈 Session Statistics:")
    print(f"   Total events received: {event_count}")
    print(f"   Tools started: {len(tool_starts)}")
    print(f"   Tools completed: {len(tool_completes)}")
    print("=" * 80)
    print("\n🔌 Connection closed\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)


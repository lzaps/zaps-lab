# Esempi di Integrazione della Funzionalità Stop

Questa guida mostra come integrare la funzionalità di stop in diversi scenari applicativi.

## 📱 Esempio 1: Frontend React con Stop Button

### Component React

```typescript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Tool {
  tool: string;
  status: 'success' | 'interrupted';
  duration: number;
  result: string;
}

interface ExecutionEvent {
  event?: string;
  event_type?: string;
  execution_id?: string;
  tool_name?: string;
  duration?: number;
  result?: string;
}

const ParallelToolsExecutor: React.FC = () => {
  const [executionId, setExecutionId] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [events, setEvents] = useState<ExecutionEvent[]>([]);
  const [completedTools, setCompletedTools] = useState<Tool[]>([]);

  const startExecution = async (query: string) => {
    setIsRunning(true);
    setEvents([]);
    setCompletedTools([]);

    try {
      const response = await fetch(
        `http://localhost:8000/execute?query=${encodeURIComponent(query)}`
      );
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const event = JSON.parse(line);
            
            // Capture execution ID
            if (event.event === 'execution_start') {
              setExecutionId(event.execution_id);
            }

            // Track completed/interrupted tools
            if (event.event_type === 'tool_complete' || 
                event.event_type === 'tool_interrupted') {
              setCompletedTools(prev => [...prev, {
                tool: event.tool_name,
                status: event.event_type === 'tool_complete' ? 'success' : 'interrupted',
                duration: event.duration,
                result: event.result
              }]);
            }

            // Stop if execution complete
            if (event.event === 'execution_complete') {
              setIsRunning(false);
            }

            setEvents(prev => [...prev, event]);
          } catch (e) {
            // Skip invalid JSON
          }
        }
      }
    } catch (error) {
      console.error('Execution error:', error);
      setIsRunning(false);
    }
  };

  const stopExecution = async () => {
    if (!executionId) return;

    try {
      const response = await axios.post(
        `http://localhost:8000/stop/${executionId}`
      );
      console.log('Stop response:', response.data);
    } catch (error) {
      console.error('Stop error:', error);
    }
  };

  return (
    <div className="executor-container">
      <div className="controls">
        <button 
          onClick={() => startExecution('Execute all tools')}
          disabled={isRunning}
        >
          {isRunning ? '⏳ Running...' : '▶️ Start Execution'}
        </button>
        
        <button 
          onClick={stopExecution}
          disabled={!isRunning || !executionId}
          className="stop-button"
        >
          🛑 Stop Execution
        </button>
      </div>

      {executionId && (
        <div className="execution-info">
          <strong>Execution ID:</strong> {executionId}
        </div>
      )}

      <div className="results">
        <h3>Tools Progress ({completedTools.length}/5)</h3>
        {completedTools.map((tool, idx) => (
          <div key={idx} className={`tool-result ${tool.status}`}>
            <span className="icon">
              {tool.status === 'success' ? '✅' : '🛑'}
            </span>
            <span className="name">{tool.tool}</span>
            <span className="duration">{tool.duration.toFixed(2)}s</span>
            <span className="result">{tool.result}</span>
          </div>
        ))}
      </div>

      <div className="events-log">
        <h3>Event Log</h3>
        <pre>
          {events.map((e, i) => (
            <div key={i}>{JSON.stringify(e)}</div>
          ))}
        </pre>
      </div>
    </div>
  );
};

export default ParallelToolsExecutor;
```

### CSS Styles

```css
.executor-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.controls button {
  padding: 12px 24px;
  font-size: 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.controls button:first-child {
  background: #4CAF50;
  color: white;
}

.controls button.stop-button {
  background: #f44336;
  color: white;
}

.controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tool-result {
  padding: 12px;
  margin: 8px 0;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.tool-result.success {
  background: #e8f5e9;
  border-left: 4px solid #4CAF50;
}

.tool-result.interrupted {
  background: #ffebee;
  border-left: 4px solid #f44336;
}

.events-log {
  margin-top: 20px;
  background: #f5f5f5;
  padding: 15px;
  border-radius: 6px;
  max-height: 300px;
  overflow-y: auto;
}
```

## 🐍 Esempio 2: Script Python con Progress Bar

```python
#!/usr/bin/env python3
"""
Script con progress bar e stop automatico.
"""

import requests
import json
import time
import signal
import sys
from tqdm import tqdm

class ExecutionManager:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.execution_id = None
        self.should_stop = False
        self.completed_tools = []
        self.total_tools = 5
        
        # Handle Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C by stopping execution."""
        print("\n⚠️  Ctrl+C detected!")
        if self.execution_id:
            print(f"🛑 Stopping execution {self.execution_id}...")
            self.stop_execution()
        sys.exit(0)
    
    def start_execution(self, query: str, max_tools: int = None):
        """Start execution with optional auto-stop after N tools."""
        print(f"🚀 Starting execution: {query}")
        
        response = requests.get(
            f'{self.base_url}/execute',
            params={'query': query},
            stream=True,
            timeout=120
        )
        
        # Progress bar
        pbar = tqdm(
            total=self.total_tools,
            desc="Tools Progress",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]"
        )
        
        try:
            for line in response.iter_lines():
                if not line:
                    continue
                
                # Skip keepalive
                if line.startswith(b'#') or line.startswith(b':'):
                    continue
                
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                # Get execution ID
                if event.get('event') == 'execution_start':
                    self.execution_id = event['execution_id']
                    self.total_tools = event.get('num_tools', 5)
                    pbar.total = self.total_tools
                    print(f"📋 Execution ID: {self.execution_id}")
                
                # Update progress on tool completion
                if event.get('event_type') in ['tool_complete', 'tool_interrupted']:
                    tool_name = event['tool_name']
                    duration = event['duration']
                    status = '✅' if event['event_type'] == 'tool_complete' else '🛑'
                    
                    self.completed_tools.append(event)
                    pbar.update(1)
                    pbar.set_postfix_str(f"{status} {tool_name} ({duration:.1f}s)")
                    
                    # Auto-stop after N tools
                    if max_tools and len(self.completed_tools) >= max_tools:
                        print(f"\n🎯 Reached {max_tools} tools, stopping...")
                        self.stop_execution()
                
                # Execution complete
                if event.get('event') == 'execution_complete':
                    break
        
        finally:
            pbar.close()
        
        return self.completed_tools
    
    def stop_execution(self):
        """Stop current execution."""
        if not self.execution_id:
            print("❌ No execution to stop")
            return False
        
        try:
            response = requests.post(
                f'{self.base_url}/stop/{self.execution_id}',
                timeout=5
            )
            data = response.json()
            print(f"✅ {data['message']}")
            return True
        except Exception as e:
            print(f"❌ Error stopping: {e}")
            return False
    
    def print_summary(self):
        """Print execution summary."""
        if not self.completed_tools:
            print("No tools completed")
            return
        
        print("\n" + "=" * 60)
        print("EXECUTION SUMMARY")
        print("=" * 60)
        
        for tool in self.completed_tools:
            status_icon = '✅' if tool.get('event_type') == 'tool_complete' else '🛑'
            print(f"{status_icon} {tool['tool_name']:<20} {tool['duration']:>6.2f}s  {tool['result']}")
        
        total_completed = sum(1 for t in self.completed_tools 
                             if t.get('event_type') == 'tool_complete')
        total_interrupted = len(self.completed_tools) - total_completed
        
        print(f"\n📊 Results: {total_completed} completed, {total_interrupted} interrupted")
        print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', default='test', help='Query to execute')
    parser.add_argument('--max-tools', type=int, help='Stop after N tools complete')
    parser.add_argument('--url', default='http://localhost:8000', help='API base URL')
    
    args = parser.parse_args()
    
    manager = ExecutionManager(args.url)
    manager.start_execution(args.query, args.max_tools)
    manager.print_summary()


if __name__ == "__main__":
    main()
```

**Uso:**
```bash
# Esecuzione normale
python progress_executor.py --query "Execute all tools"

# Stop dopo 2 tools
python progress_executor.py --max-tools 2

# Ctrl+C per stop manuale
python progress_executor.py
# [Dopo qualche secondo premere Ctrl+C]
```

## 🔄 Esempio 3: Queue System con Multiple Executions

```python
"""
Sistema di code per gestire multiple esecuzioni con stop selettivo.
"""

import asyncio
import aiohttp
import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class Execution:
    id: str
    query: str
    started_at: datetime
    status: str  # 'running', 'completed', 'stopped'
    completed_tools: List[dict]
    
class ExecutionQueue:
    def __init__(self, base_url="http://localhost:8000", max_concurrent=3):
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.executions: Dict[str, Execution] = {}
        self.queue: List[str] = []
    
    async def start_execution(self, query: str) -> str:
        """Start a new execution."""
        print(f"🚀 Starting: {query}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.base_url}/execute',
                params={'query': query}
            ) as response:
                # Read first event to get execution_id
                async for line in response.content:
                    if line:
                        try:
                            event = json.loads(line)
                            if event.get('event') == 'execution_start':
                                exec_id = event['execution_id']
                                
                                # Register execution
                                self.executions[exec_id] = Execution(
                                    id=exec_id,
                                    query=query,
                                    started_at=datetime.now(),
                                    status='running',
                                    completed_tools=[]
                                )
                                
                                print(f"📋 Registered: {exec_id}")
                                
                                # Continue processing in background
                                asyncio.create_task(
                                    self._process_execution(exec_id, response)
                                )
                                
                                return exec_id
                        except:
                            pass
        
        raise Exception("Failed to start execution")
    
    async def _process_execution(self, exec_id: str, response):
        """Process execution events."""
        try:
            async for line in response.content:
                if not line:
                    continue
                
                try:
                    event = json.loads(line)
                    
                    if event.get('event_type') in ['tool_complete', 'tool_interrupted']:
                        self.executions[exec_id].completed_tools.append(event)
                    
                    if event.get('event') == 'execution_complete':
                        self.executions[exec_id].status = 'completed'
                        print(f"✅ Completed: {exec_id}")
                        break
                        
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"❌ Error processing {exec_id}: {e}")
            self.executions[exec_id].status = 'error'
    
    async def stop_execution(self, exec_id: str) -> bool:
        """Stop a specific execution."""
        if exec_id not in self.executions:
            print(f"❌ Execution not found: {exec_id}")
            return False
        
        print(f"🛑 Stopping: {exec_id}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/stop/{exec_id}'
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.executions[exec_id].status = 'stopped'
                    print(f"✅ {data['message']}")
                    return True
                else:
                    print(f"❌ Failed to stop: {response.status}")
                    return False
    
    async def list_active(self) -> List[Execution]:
        """List active executions."""
        return [
            exec for exec in self.executions.values()
            if exec.status == 'running'
        ]
    
    def get_summary(self, exec_id: str) -> Optional[Dict]:
        """Get summary for an execution."""
        if exec_id not in self.executions:
            return None
        
        exec = self.executions[exec_id]
        completed = sum(1 for t in exec.completed_tools 
                       if t.get('event_type') == 'tool_complete')
        
        return {
            'id': exec.id,
            'query': exec.query,
            'status': exec.status,
            'started_at': exec.started_at.isoformat(),
            'completed_tools': completed,
            'interrupted_tools': len(exec.completed_tools) - completed,
            'duration': (datetime.now() - exec.started_at).total_seconds()
        }


async def main():
    """Demo del queue system."""
    queue = ExecutionQueue()
    
    # Start multiple executions
    print("Starting 3 executions...")
    exec_ids = []
    for i in range(3):
        exec_id = await queue.start_execution(f"Query {i+1}")
        exec_ids.append(exec_id)
        await asyncio.sleep(1)  # Stagger starts
    
    # Wait a bit
    await asyncio.sleep(5)
    
    # Stop first execution
    print(f"\nStopping first execution...")
    await queue.stop_execution(exec_ids[0])
    
    # Wait for others to complete
    await asyncio.sleep(30)
    
    # Print summaries
    print("\n" + "=" * 60)
    print("FINAL SUMMARIES")
    print("=" * 60)
    for exec_id in exec_ids:
        summary = queue.get_summary(exec_id)
        if summary:
            print(f"\n{summary['id']}:")
            print(f"  Status: {summary['status']}")
            print(f"  Completed: {summary['completed_tools']}")
            print(f"  Interrupted: {summary['interrupted_tools']}")
            print(f"  Duration: {summary['duration']:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
```

## 🌐 Esempio 4: Webhook Notification su Stop

```python
"""
Sistema che invia webhook quando un'esecuzione viene fermata.
"""

import requests
import json
from typing import Callable, Optional

class WebhookExecutor:
    def __init__(self, 
                 base_url="http://localhost:8000",
                 webhook_url: Optional[str] = None):
        self.base_url = base_url
        self.webhook_url = webhook_url
        self.execution_id = None
        self.tools_data = []
    
    def on_tool_event(self, callback: Callable):
        """Register callback for tool events."""
        self.tool_callback = callback
    
    def on_stop(self, callback: Callable):
        """Register callback for stop event."""
        self.stop_callback = callback
    
    def start_execution(self, query: str):
        """Start execution with event tracking."""
        response = requests.get(
            f'{self.base_url}/execute',
            params={'query': query},
            stream=True
        )
        
        for line in response.iter_lines():
            if not line or line.startswith(b'#'):
                continue
            
            try:
                event = json.loads(line)
                
                if event.get('event') == 'execution_start':
                    self.execution_id = event['execution_id']
                    self._send_webhook('execution_started', event)
                
                if event.get('event_type') in ['tool_complete', 'tool_interrupted']:
                    self.tools_data.append(event)
                    
                    if hasattr(self, 'tool_callback'):
                        self.tool_callback(event)
                    
                    # Check if stopped
                    if event.get('event_type') == 'tool_interrupted':
                        self._handle_stop(event)
                
                if event.get('event') == 'execution_complete':
                    self._send_webhook('execution_completed', {
                        'execution_id': self.execution_id,
                        'tools_completed': len([t for t in self.tools_data 
                                               if t.get('event_type') == 'tool_complete']),
                        'tools_interrupted': len([t for t in self.tools_data 
                                                 if t.get('event_type') == 'tool_interrupted'])
                    })
                    break
                    
            except json.JSONDecodeError:
                pass
    
    def _handle_stop(self, event):
        """Handle stop event."""
        if hasattr(self, 'stop_callback'):
            self.stop_callback(event)
        
        # Send webhook
        self._send_webhook('execution_stopped', {
            'execution_id': self.execution_id,
            'stopped_at': event.get('timestamp'),
            'tool_name': event.get('tool_name'),
            'partial_results': len(self.tools_data)
        })
    
    def _send_webhook(self, event_type: str, data: dict):
        """Send webhook notification."""
        if not self.webhook_url:
            return
        
        payload = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )
            print(f"📨 Webhook sent: {event_type}")
        except Exception as e:
            print(f"❌ Webhook failed: {e}")


# Uso
executor = WebhookExecutor(
    webhook_url="https://your-webhook-url.com/notifications"
)

executor.on_tool_event(lambda event: print(f"Tool: {event['tool_name']}"))
executor.on_stop(lambda event: print(f"⚠️  Stopped!"))

executor.start_execution("test")
```

## 🎯 Best Practices

### 1. Gestione Errori

```python
async def safe_stop(execution_id: str):
    """Stop con retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = await stop_execution(execution_id)
            if response['success']:
                return True
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
    return False
```

### 2. Timeout Automatico

```python
async def execution_with_timeout(query: str, timeout: int = 60):
    """Esecuzione con timeout automatico."""
    exec_id = await start_execution(query)
    
    try:
        await asyncio.wait_for(
            wait_for_completion(exec_id),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        print(f"⏰ Timeout reached, stopping...")
        await stop_execution(exec_id)
```

### 3. Graceful Shutdown

```python
class Application:
    def __init__(self):
        self.active_executions = set()
        signal.signal(signal.SIGTERM, self.shutdown)
    
    async def shutdown(self, sig, frame):
        """Stop all executions on shutdown."""
        print("🛑 Shutting down, stopping all executions...")
        tasks = [stop_execution(eid) for eid in self.active_executions]
        await asyncio.gather(*tasks)
        sys.exit(0)
```

---

Questi esempi mostrano come integrare la funzionalità di stop in vari contesti applicativi, dal frontend al backend, con diverse strategie di gestione e notifica.


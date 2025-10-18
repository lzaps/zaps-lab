# HTTP Streaming - Guida Completa

## 🌊 Cos'è l'HTTP Streaming?

L'API usa **HTTP Chunked Transfer Encoding** per inviare eventi in tempo reale.

Invece di aspettare che tutto sia pronto, il server invia **chunk** di dati man mano che sono disponibili.

## 📦 Formato: JSON Lines (NDJSON)

Ogni evento è un **oggetto JSON su una riga separata**.

### Esempio di Risposta

```json
{"event_type":"execution_start","query":"test","num_tools":5}
{"event_type":"tool_start","tool_name":"weather_check","delay":12.5}
{"event_type":"tool_start","tool_name":"database_query","delay":17.3}
{"event_type":"tool_complete","tool_name":"weather_check","duration":12.52}
{"event_type":"execution_complete"}
```

Ogni linea è un JSON valido che puoi parsare subito! ✨

## 🎯 Come Funziona

### 1. Client fa la richiesta
```http
GET /execute?query=test HTTP/1.1
Host: localhost:8000
```

### 2. Server risponde con headers di streaming
```http
HTTP/1.1 200 OK
Content-Type: application/x-ndjson
Transfer-Encoding: chunked
Cache-Control: no-cache
Connection: keep-alive
```

### 3. Server invia chunk man mano
```
[chunk 1] {"event_type":"execution_start",...}
[chunk 2] {"event_type":"tool_start",...}
[chunk 3] {"event_type":"tool_start",...}
...
[chunk N] {"event_type":"execution_complete"}
```

### 4. Connessione si chiude
Il server chiude lo stream dopo l'ultimo evento.

## 🧪 Test con Postman

### Setup
1. **Method**: GET
2. **URL**: `http://localhost:8000/execute?query=test`
3. **Send**

### Cosa Vedi
Postman mostra gli eventi uno per uno nel pannello Response:

```json
{"timestamp":"14:23:45.123","event_type":"execution_start","query":"test","num_tools":5}
```

Poi dopo qualche secondo:

```json
{"timestamp":"14:23:45.125","event_type":"tool_start","tool_name":"weather_check","delay":12.52}
```

E così via fino alla fine! 🎉

## 💻 Test con curl

```bash
curl -N http://localhost:8000/execute?query=test
```

**Flag `-N`**: Disabilita buffering, vedi eventi in real-time.

### Output
```json
{"timestamp":"14:23:45.123","event_type":"execution_start"...}
{"timestamp":"14:23:45.125","event_type":"tool_start"...}
{"timestamp":"14:23:45.126","event_type":"tool_start"...}
...
```

Ogni linea appare quando l'evento succede! ⚡

## 🐍 Client Python

### Con Requests (Streaming)

```python
import requests
import json

url = "http://localhost:8000/execute"
params = {"query": "test"}

# stream=True abilita lo streaming
response = requests.get(url, params=params, stream=True)

# Itera sulle linee mentre arrivano
for line in response.iter_lines():
    if line:
        # Parse JSON
        event = json.loads(line)
        
        # Processa evento
        event_type = event.get("event_type")
        
        if event_type == "tool_start":
            tool_name = event["tool_name"]
            delay = event["delay"]
            print(f"🚀 {tool_name} started (ETA: {delay:.1f}s)")
            
        elif event_type == "tool_complete":
            tool_name = event["tool_name"]
            duration = event["duration"]
            result = event["result"]
            print(f"✅ {tool_name} done in {duration:.2f}s")
            print(f"   Result: {result}")
            
        elif event_type == "aggregate":
            summary = event["summary"]
            print(f"\n📊 Summary:")
            print(f"   Parallel: {summary['total_duration']:.2f}s")
            print(f"   Would be sequential: {summary['sequential_duration']:.2f}s")
            print(f"   Saved: {summary['time_saved']:.2f}s")
            
        elif event_type == "execution_complete":
            print("\n✨ All done!")
            break

print("\nConnection closed.")
```

### Output del Client Python
```
🚀 weather_check started (ETA: 12.5s)
🚀 database_query started (ETA: 17.3s)
🚀 api_call started (ETA: 19.1s)
🚀 ml_inference started (ETA: 28.4s)
🚀 data_processing started (ETA: 29.8s)

... (aspetta) ...

✅ weather_check done in 12.52s
   Result: Weather: Sunny, 22°C in Milan
✅ database_query done in 17.45s
   Result: Found 1,247 matching records
...

📊 Summary:
   Parallel: 30.12s
   Would be sequential: 106.80s
   Saved: 76.68s

✨ All done!
Connection closed.
```

## 🌐 Client JavaScript (Browser)

### Con Fetch API

```javascript
async function streamExecution() {
  const response = await fetch('http://localhost:8000/execute?query=test');
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  let buffer = '';
  
  while (true) {
    const { done, value } = await reader.read();
    
    if (done) break;
    
    // Decodifica chunk
    buffer += decoder.decode(value, { stream: true });
    
    // Processa linee complete
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Mantieni linea incompleta
    
    for (const line of lines) {
      if (line.trim()) {
        const event = JSON.parse(line);
        handleEvent(event);
      }
    }
  }
}

function handleEvent(event) {
  switch (event.event_type) {
    case 'tool_start':
      console.log(`🚀 ${event.tool_name} started`);
      break;
      
    case 'tool_complete':
      console.log(`✅ ${event.tool_name} completed in ${event.duration.toFixed(2)}s`);
      break;
      
    case 'aggregate':
      console.log('📊 Summary:', event.summary);
      break;
      
    case 'execution_complete':
      console.log('✨ Done!');
      break;
  }
}

// Esegui
streamExecution();
```

## 🔄 Formato Alternativo: SSE

Se preferisci **Server-Sent Events**, aggiungi `format=sse`:

```
GET http://localhost:8000/execute?query=test&format=sse
```

### Differenza

**JSON Lines (default)**:
```json
{"event":"A"}
{"event":"B"}
```

**SSE (con format=sse)**:
```
data: {"event":"A"}

data: {"event":"B"}

```

SSE ha il prefisso `data: ` e doppio newline.

### Quando Usare SSE?
- Browser con EventSource API
- Librerie che richiedono SSE esplicitamente

### Quando Usare JSON Lines?
- Postman (più leggibile)
- curl (più semplice)
- Client custom (più facile da parsare)
- Python/JavaScript moderni

## 📊 Confronto Formati

| Aspetto | JSON Lines | SSE |
|---------|-----------|-----|
| **Leggibilità** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Parsing** | Molto semplice | Standard built-in |
| **Postman** | ✅ Perfetto | ⚠️ Verboso |
| **curl** | ✅ Pulito | ⚠️ Con prefissi |
| **Browser** | ✅ Fetch API | ✅ EventSource |
| **Standard** | NDJSON (RFC) | W3C Standard |

## 🎯 Best Practices

### 1. Usa JSON Lines (default)
È più semplice e leggibile per la maggior parte dei casi.

### 2. Buffer Management
Gestisci le linee incomplete correttamente:
```python
buffer = ""
for chunk in response.iter_content(chunk_size=None):
    buffer += chunk.decode()
    while '\n' in buffer:
        line, buffer = buffer.split('\n', 1)
        process_event(json.loads(line))
```

### 3. Timeout
Imposta timeout adeguati (almeno 60s per questa demo):
```python
response = requests.get(url, stream=True, timeout=60)
```

### 4. Error Handling
Gestisci disconnessioni:
```python
try:
    for line in response.iter_lines():
        event = json.loads(line)
        handle_event(event)
except requests.exceptions.ChunkedEncodingError:
    print("Connection interrupted")
```

## 🚀 Vantaggi HTTP Streaming

✅ **Real-time**: Eventi arrivano istantaneamente  
✅ **Efficiente**: No polling, una sola connessione  
✅ **Scalabile**: Minimo overhead sul server  
✅ **Semplice**: Standard HTTP, niente WebSocket  
✅ **Universale**: Funziona ovunque  
✅ **Debuggabile**: Leggibile in Postman/curl  

## 🎓 Conclusione

HTTP Streaming con JSON Lines è:
- **Più semplice** di WebSocket
- **Più efficiente** di polling
- **Più universale** di tecnologie proprietarie
- **Perfetto** per notifiche e progress tracking!

Buon streaming! 🌊✨


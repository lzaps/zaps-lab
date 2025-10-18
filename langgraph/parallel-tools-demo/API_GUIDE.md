# API Streaming Guide

## 🚀 Avvio del Server

```bash
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo
source venv/bin/activate
python api.py
```

Il server sarà disponibile su: **http://localhost:8000**

## 📡 Endpoints Disponibili

### 1. Root - Informazioni API
```
GET http://localhost:8000/
```

### 2. Health Check
```
GET http://localhost:8000/health
```

### 3. Lista Tools
```
GET http://localhost:8000/tools
```

### 4. Esecuzione con Streaming (GET)
```
GET http://localhost:8000/execute?query=test
```

### 5. Esecuzione con Streaming (POST)
```
POST http://localhost:8000/execute
Content-Type: application/json

{
  "query": "Execute all tools"
}
```

## 🧪 Test con Postman

### Setup in Postman

1. **Crea una nuova richiesta**
   - Method: `GET`
   - URL: `http://localhost:8000/execute?query=test`

2. **Importante**: Lascia Postman APERTO durante l'esecuzione
   - Vedrai gli eventi arrivare in real-time
   - Ci vorranno ~30 secondi per completare

### Cosa Vedrai

Gli eventi arrivano in formato **Server-Sent Events (SSE)**:

```
data: {"timestamp":"14:23:45.123","event_type":"execution_start","query":"test","num_tools":5}

data: {"timestamp":"14:23:45.125","event_type":"tool_start","tool_name":"weather_check","delay":12.5}

data: {"timestamp":"14:23:45.126","event_type":"tool_start","tool_name":"database_query","delay":17.3}

data: {"timestamp":"14:23:45.127","event_type":"tool_start","tool_name":"api_call","delay":19.1}

data: {"timestamp":"14:23:45.128","event_type":"tool_start","tool_name":"ml_inference","delay":28.4}

data: {"timestamp":"14:23:45.129","event_type":"tool_start","tool_name":"data_processing","delay":29.8}

data: {"timestamp":"14:23:57.650","event_type":"tool_complete","tool_name":"weather_check","duration":12.52,"result":"Weather: Sunny, 22°C in Milan"}

data: {"timestamp":"14:24:02.426","event_type":"tool_complete","tool_name":"database_query","duration":17.30,"result":"Found 1,247 matching records"}

... (altri tool completano)

data: {"timestamp":"14:24:15.000","event_type":"aggregate","summary":{...}}

data: {"timestamp":"14:24:15.001","event_type":"execution_complete"}
```

## 🖥️ Test con curl

### Streaming in Tempo Reale
```bash
curl -N http://localhost:8000/execute?query=test
```

Il flag `-N` disabilita il buffering per vedere gli eventi in real-time.

### POST con JSON
```bash
curl -N -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"query": "Run all tools"}'
```

## 📊 Tipi di Eventi

### 1. `execution_start`
Emesso all'inizio dell'esecuzione
```json
{
  "timestamp": "14:23:45.123",
  "event_type": "execution_start",
  "query": "test",
  "num_tools": 5
}
```

### 2. `prepare`
Graph preparation
```json
{
  "timestamp": "14:23:45.124",
  "event_type": "prepare"
}
```

### 3. `tool_start`
Un tool inizia l'esecuzione
```json
{
  "timestamp": "14:23:45.125",
  "event_type": "tool_start",
  "tool_name": "weather_check",
  "delay": 12.5
}
```

### 4. `tool_complete`
Un tool completa l'esecuzione
```json
{
  "timestamp": "14:23:57.650",
  "event_type": "tool_complete",
  "tool_name": "weather_check",
  "duration": 12.52,
  "result": "Weather: Sunny, 22°C in Milan"
}
```

### 5. `aggregate`
Risultati aggregati
```json
{
  "timestamp": "14:24:15.000",
  "event_type": "aggregate",
  "summary": {
    "total_duration": 30.12,
    "sequential_duration": 106.80,
    "time_saved": 76.68,
    "avg_duration": 21.36,
    "fastest": 12.22,
    "slowest": 29.67,
    "num_tools": 5,
    "results": [...]
  }
}
```

### 6. `execution_complete`
Esecuzione completata
```json
{
  "timestamp": "14:24:15.001",
  "event_type": "execution_complete"
}
```

## 🎯 Esempio Completo in Python

```python
import requests
import json

url = "http://localhost:8000/execute"
params = {"query": "test"}

response = requests.get(url, params=params, stream=True)

for line in response.iter_lines():
    if line:
        # Rimuovi "data: " prefix
        if line.startswith(b"data: "):
            data = json.loads(line[6:])
            event_type = data.get("event_type")
            
            if event_type == "tool_start":
                print(f"🚀 {data['tool_name']} started")
            elif event_type == "tool_complete":
                print(f"✅ {data['tool_name']} completed in {data['duration']:.2f}s")
            elif event_type == "aggregate":
                summary = data['summary']
                print(f"\n📊 Summary:")
                print(f"   Total: {summary['total_duration']:.2f}s")
                print(f"   Saved: {summary['time_saved']:.2f}s")
```

## 🌐 Esempio in JavaScript

```javascript
const eventSource = new EventSource('http://localhost:8000/execute?query=test');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.event_type) {
    case 'tool_start':
      console.log(`🚀 ${data.tool_name} started`);
      break;
    case 'tool_complete':
      console.log(`✅ ${data.tool_name} completed in ${data.duration.toFixed(2)}s`);
      break;
    case 'aggregate':
      console.log('📊 Summary:', data.summary);
      break;
    case 'execution_complete':
      console.log('✨ Done!');
      eventSource.close();
      break;
  }
};

eventSource.onerror = (error) => {
  console.error('Error:', error);
  eventSource.close();
};
```

## 📝 Note Importanti

1. **Streaming**: Gli eventi arrivano in real-time mentre i tool eseguono
2. **Durata**: L'esecuzione completa richiede ~30 secondi (tool più lento)
3. **Parallelismo**: Tutti i 5 tool partono contemporaneamente
4. **SSE**: Usa Server-Sent Events, standard per streaming HTTP
5. **CORS**: Abilitato per chiamate da browser

## 🔧 Opzioni Avanzate

### Cambiare Porta
```bash
# Modifica api.py, ultima riga:
uvicorn.run("api:app", host="0.0.0.0", port=3000)
```

### Hot Reload (Development)
```bash
uvicorn api:app --reload --port 8000
```

### Produzione
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🐛 Troubleshooting

### Problema: Porta già in uso
```bash
# Trova processo sulla porta 8000
lsof -ti:8000 | xargs kill -9

# Oppure usa porta diversa
python api.py  # e modifica la porta nel codice
```

### Problema: Eventi non arrivano in Postman
- Assicurati che la richiesta sia ancora in esecuzione
- Non chiudere Postman durante i 30 secondi di esecuzione
- Controlla che il server sia avviato

### Problema: Timeout
- È normale! I tool impiegano 10-30 secondi
- Aumenta il timeout in Postman se necessario

## 📚 Documentazione Automatica

FastAPI genera documentazione automatica:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Puoi testare l'API direttamente da lì!


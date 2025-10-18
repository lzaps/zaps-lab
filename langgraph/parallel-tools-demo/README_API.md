# 🌊 API con HTTP Streaming - Riepilogo

## ✨ Cos'hai Ora

Un'**API FastAPI** che esegue 5 tool LangGraph in parallelo con **HTTP Streaming in tempo reale**!

## 🎯 Caratteristiche Principali

### ✅ HTTP Streaming Puro
- Usa **JSON Lines** (NDJSON) - una riga JSON per evento
- **Chunked Transfer Encoding** per streaming real-time
- Niente WebSocket, solo HTTP standard!

### ✅ Real-Time Updates
- Vedi quando ogni tool **parte**
- Vedi quando ogni tool **finisce**
- Vedi i **risultati** man mano che arrivano
- Vedi il **riepilogo** finale con statistiche

### ✅ Facile da Testare
- **Postman**: Apri e testa subito
- **curl**: `curl -N http://localhost:8000/execute?query=test`
- **Browser**: http://localhost:8000/docs (Swagger UI)
- **Python**: Script inclusi

## 🚀 Quick Start

```bash
# 1. Vai nella cartella
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo

# 2. Attiva virtual environment
source venv/bin/activate

# 3. Avvia il server
python api.py
```

Server pronto su: **http://localhost:8000** 🎉

## 🧪 Test Immediato

### Con Postman
```
GET http://localhost:8000/execute?query=test
```

### Con curl
```bash
curl -N http://localhost:8000/execute?query=test
```

## 📊 Formato Risposta

### JSON Lines (Default)
Ogni evento è una riga JSON:

```json
{"event_type":"execution_start","query":"test","num_tools":5}
{"event_type":"tool_start","tool_name":"weather_check","delay":12.5}
{"event_type":"tool_start","tool_name":"database_query","delay":17.3}
...
{"event_type":"tool_complete","tool_name":"weather_check","duration":12.52}
...
{"event_type":"aggregate","summary":{...}}
{"event_type":"execution_complete"}
```

### SSE (Opzionale)
Aggiungi `?format=sse` per Server-Sent Events:
```
GET http://localhost:8000/execute?query=test&format=sse
```

## 🔥 Endpoints Disponibili

| Endpoint | Descrizione |
|----------|-------------|
| `GET /` | Info API |
| `GET /health` | Health check |
| `GET /tools` | Lista dei 5 tool |
| `GET /execute` | **Streaming execution** |
| `POST /execute` | **Streaming execution** (JSON body) |
| `GET /docs` | Swagger UI interattivo |
| `GET /redoc` | Documentazione ReDoc |

## 📚 Documentazione

| File | Contenuto |
|------|-----------|
| **START_HERE.md** | 🚀 Inizia da qui! |
| **POSTMAN_TEST.md** | 🧪 Guida Postman completa |
| **HTTP_STREAMING_GUIDE.md** | 📖 Guida HTTP Streaming |
| **API_GUIDE.md** | 📚 Documentazione API completa |

## 💻 Esempio Client Python

```python
import requests
import json

response = requests.get(
    "http://localhost:8000/execute",
    params={"query": "test"},
    stream=True
)

for line in response.iter_lines():
    if line:
        event = json.loads(line)
        
        if event["event_type"] == "tool_start":
            print(f"🚀 {event['tool_name']} started")
            
        elif event["event_type"] == "tool_complete":
            print(f"✅ {event['tool_name']} done in {event['duration']:.2f}s")
```

## 🌐 Esempio JavaScript (Browser)

```javascript
const response = await fetch('http://localhost:8000/execute?query=test');
const reader = response.body.getReader();
const decoder = new TextDecoder();

let buffer = '';

while (true) {
  const {done, value} = await reader.read();
  if (done) break;
  
  buffer += decoder.decode(value, {stream: true});
  const lines = buffer.split('\n');
  buffer = lines.pop();
  
  for (const line of lines) {
    if (line.trim()) {
      const event = JSON.parse(line);
      console.log(event);
    }
  }
}
```

## 🎨 Vantaggi

✅ **Semplice**: JSON puro, niente protocolli complicati  
✅ **Universal**: Funziona con qualsiasi client HTTP  
✅ **Debuggabile**: Leggi in Postman/curl  
✅ **Efficiente**: Una connessione, zero polling  
✅ **Standard**: HTTP Chunked Transfer Encoding  
✅ **Real-time**: Eventi istantanei  

## 🏗️ Architettura

```
Client (Postman/curl/browser)
    ↓ HTTP GET /execute?query=test
FastAPI Server
    ↓ Build LangGraph
LangGraph Parallel Execution
    ↓ Fan-out to 5 tools
Tool 1 (10-15s) ──┐
Tool 2 (15-20s) ──┤
Tool 3 (15-20s) ──┼→ Events → Queue → Stream → Client
Tool 4 (25-30s) ──┤
Tool 5 (25-30s) ──┘
    ↓ Fan-in
Aggregate Results
    ↓ Final event
Client receives complete stream
```

## 🎯 Use Cases

### 1. Progress Monitoring
Mostra progresso di operazioni lunghe

### 2. Real-time Analytics
Stream di metriche e risultati

### 3. Multi-tool Orchestration
Coordina tool multipli e mostra stato

### 4. Agent Debugging
Vedi cosa sta facendo l'agent in tempo reale

### 5. User Feedback
Mostra all'utente cosa sta succedendo

## 🔧 Personalizzazione

### Cambia Porta
In `api.py`, ultima riga:
```python
uvicorn.run("api:app", host="0.0.0.0", port=3000)
```

### Aggiungi Tool
1. Crea nuova classe in `tools.py`
2. Aggiungi a `AVAILABLE_TOOLS`
3. Riavvia server
4. Nuovo tool eseguito in parallelo! ✨

### Modifica Tempi
In ogni tool class:
```python
self.delay = random.uniform(5.0, 10.0)  # Cambia qui!
```

## 🐛 Troubleshooting

### Porta già in uso
```bash
lsof -ti:8000 | xargs kill -9
```

### Dipendenze mancanti
```bash
pip install -r requirements.txt
```

### Server non risponde
```bash
# Verifica health
curl http://localhost:8000/health
```

## 📦 Dipendenze

```
fastapi>=0.115.0    # Web framework
uvicorn>=0.34.0     # ASGI server
langgraph>=0.2.0    # Graph framework
langchain>=0.3.0    # LangChain
colorama>=0.4.6     # Colors
```

## 🎉 Conclusione

Hai creato un'API moderna con:
- ✅ Streaming HTTP real-time
- ✅ Esecuzione parallela LangGraph
- ✅ Progress tracking dettagliato
- ✅ Documentazione completa
- ✅ Pronto per produzione!

**Inizia ora**: Leggi [START_HERE.md](START_HERE.md)

**Test in Postman**: Leggi [POSTMAN_TEST.md](POSTMAN_TEST.md)

Buon coding! 🚀✨


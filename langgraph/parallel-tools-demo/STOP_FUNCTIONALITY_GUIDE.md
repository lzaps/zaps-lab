# Guida alla Funzionalità di STOP

## 🎯 Panoramica

La funzionalità di STOP permette di **interrompere un'esecuzione in corso** durante lo streaming, fermando tutti i tools ancora in esecuzione e passando direttamente allo stato finale con i risultati parziali già ottenuti.

## 🔧 Come Funziona

### Architettura

1. **Execution ID Univoco**: Ogni esecuzione riceve un UUID univoco
2. **Stop Events Registry**: Sistema globale di eventi threading per gestire gli stop
3. **Interruptible Sleep**: I tools controllano periodicamente (ogni 0.5s) se devono fermarsi
4. **Gestione Stato**: I risultati parziali vengono aggregati anche quando interrotti

### Componenti Modificati

#### 1. `tools.py` - Tools Interrompibili

```python
# Ogni tool ora usa interruptible_sleep invece di time.sleep
completed = interruptible_sleep(self.delay, execution_id)

if not completed:
    # Tool interrotto
    return {
        "tool_results": [{
            "tool": self.name,
            "duration": duration,
            "result": "Interrupted",
            "status": "interrupted"
        }]
    }
```

#### 2. `state.py` - Execution ID nello Stato

```python
class GraphState(TypedDict):
    # ... altri campi ...
    execution_id: str  # Nuovo campo per tracking
```

#### 3. `api.py` - Gestione dello Stop

- **Tracking esecuzioni attive**: `active_executions: Set[str]`
- **Registry stop events**: Gestione globale degli eventi di interruzione
- **Nuovi endpoint**: `/stop/{execution_id}`, `/executions`

## 📡 Nuovi Endpoint API

### 1. GET `/executions`

Lista le esecuzioni attualmente attive.

**Risposta:**
```json
{
  "active_executions": [
    "550e8400-e29b-41d4-a716-446655440000"
  ],
  "count": 1,
  "timestamp": "2025-10-18T10:30:45.123456"
}
```

### 2. POST `/stop/{execution_id}`

Ferma un'esecuzione specifica.

**Esempio:**
```bash
curl -X POST http://localhost:8000/stop/550e8400-e29b-41d4-a716-446655440000
```

**Risposta di Successo:**
```json
{
  "success": true,
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Stop signal sent. Tools will be interrupted.",
  "timestamp": "2025-10-18T10:30:50.789012"
}
```

**Errore - Esecuzione Non Trovata:**
```json
{
  "detail": "Execution 550e8400-e29b-41d4-a716-446655440000 not found or already completed"
}
```

## 🚀 Caso d'Uso Completo

### Scenario 1: Esecuzione e Stop via API

#### Passo 1: Avvia l'esecuzione

```bash
# Terminal 1: Start streaming execution
curl -N http://localhost:8000/execute?query=test
```

**Output:**
```json
{"event": "execution_start", "query": "test", "num_tools": 5, "execution_id": "abc-123"}
{"timestamp": "10:30:45.123", "event_type": "tool_start", "tool_name": "Weather Check", "delay": 12.5}
{"timestamp": "10:30:45.124", "event_type": "tool_start", "tool_name": "Database Query", "delay": 17.8}
...
```

#### Passo 2: Verifica esecuzioni attive

```bash
# Terminal 2: Check active executions
curl http://localhost:8000/executions
```

**Output:**
```json
{
  "active_executions": ["abc-123"],
  "count": 1,
  "timestamp": "2025-10-18T10:30:47.000000"
}
```

#### Passo 3: Ferma l'esecuzione

```bash
# Terminal 2: Stop the execution
curl -X POST http://localhost:8000/stop/abc-123
```

**Output:**
```json
{
  "success": true,
  "execution_id": "abc-123",
  "message": "Stop signal sent. Tools will be interrupted.",
  "timestamp": "2025-10-18T10:30:48.500000"
}
```

#### Passo 4: Osserva l'interruzione nello stream

**Terminal 1 continua a mostrare:**
```json
{"timestamp": "10:30:48.567", "event_type": "tool_interrupted", "tool_name": "ML Inference", "duration": 3.44, "result": "Interrupted"}
{"timestamp": "10:30:48.568", "event_type": "tool_interrupted", "tool_name": "Data Processing", "duration": 3.45, "result": "Interrupted"}
{"timestamp": "10:30:48.569", "event_type": "aggregate", "summary": {...}}
{"event": "execution_complete", "execution_id": "abc-123", "timestamp": "10:30:48.570"}
```

### Scenario 2: Script Automatico con Stop

```python
import requests
import time
import json

# Start execution
response = requests.get('http://localhost:8000/execute?query=test', stream=True)

execution_id = None
tool_count = 0

# Process stream
for line in response.iter_lines():
    if line:
        data = json.loads(line)
        
        # Get execution ID from first event
        if data.get('event') == 'execution_start':
            execution_id = data['execution_id']
            print(f"🚀 Started execution: {execution_id}")
        
        # Track completed tools
        if data.get('event_type') == 'tool_complete':
            tool_count += 1
            print(f"✅ Tool completed: {data['tool_name']}")
            
            # Stop after 2 tools complete
            if tool_count == 2:
                print(f"🛑 Stopping execution after 2 tools...")
                stop_response = requests.post(
                    f'http://localhost:8000/stop/{execution_id}'
                )
                print(f"Stop response: {stop_response.json()}")
```

## 🔬 Dettagli Tecnici

### Timing della Risposta allo Stop

- **Check Interval**: 0.5 secondi (configurabile in `interruptible_sleep`)
- **Tempo massimo di risposta**: 0.5 secondi dal trigger dello stop
- **Tools già completati**: Non vengono influenzati
- **Tools non ancora avviati**: Potrebbero comunque partire (dipende dal timing)

### Gestione della Concorrenza

```python
# Thread-safe stop events registry
_stop_events: Dict[str, threading.Event] = {}
_stop_events_lock = threading.Lock()

# Async-safe active executions tracking
active_executions: Set[str] = set()
active_executions_lock = asyncio.Lock()
```

### Pulizia Risorse

Quando un'esecuzione termina (normalmente o interrotta):

1. Il `stop_event` viene rimosso dal registry
2. L'`execution_id` viene rimosso da `active_executions`
3. L'executor viene chiuso (`executor.shutdown(wait=False)`)

## 📊 Eventi di Streaming

### Nuovi Eventi

#### `execution_start` (modificato)
```json
{
  "event": "execution_start",
  "query": "test",
  "num_tools": 5,
  "execution_id": "abc-123"  // Nuovo campo
}
```

#### `tool_interrupted` (nuovo)
```json
{
  "timestamp": "10:30:48.567",
  "event_type": "tool_interrupted",
  "tool_name": "ML Inference",
  "duration": 3.44,
  "result": "Interrupted"
}
```

#### `execution_complete` (modificato)
```json
{
  "event": "execution_complete",
  "execution_id": "abc-123",  // Nuovo campo
  "timestamp": "10:30:48.570"
}
```

## 🧪 Testing

### Test Manuale con curl

```bash
# Terminal 1: Start server
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo
source venv/bin/activate
python api.py

# Terminal 2: Start execution
curl -N http://localhost:8000/execute?query=test | tee output.json

# Terminal 3: Wait 5 seconds, then check executions
sleep 5
curl http://localhost:8000/executions

# Terminal 3: Stop the execution
# (copy the execution_id from Terminal 2 output)
curl -X POST http://localhost:8000/stop/YOUR_EXECUTION_ID
```

### Test con Postman

1. **Start Execution:**
   - Method: GET
   - URL: `http://localhost:8000/execute?query=test`
   - Wait for streaming to start
   - Copy the `execution_id` from first event

2. **Stop Execution:**
   - Method: POST
   - URL: `http://localhost:8000/stop/{execution_id}`
   - Send request
   - Observe interruption in first request's stream

## 🎨 Risultati Visivi

### Console Output con Interruzione

```
[10:30:45.123] 🚀 Weather Check started
[10:30:45.124] 🚀 Database Query started
[10:30:45.125] 🚀 API Call started
[10:30:45.126] 🚀 ML Inference started
[10:30:45.127] 🚀 Data Processing started

[10:30:57.623] ✅ Weather Check completed in 12.50s
[10:30:58.567] 🛑 ML Inference interrupted after 3.44s
[10:30:58.568] 🛑 Data Processing interrupted after 3.45s
[10:30:58.569] 🛑 Database Query interrupted after 3.45s
[10:30:58.570] 🛑 API Call interrupted after 3.45s
```

### Summary con Risultati Parziali

```
===============================================================================
                           EXECUTION SUMMARY
===============================================================================

Tool Name                Duration     Status      Result
-------------------------------------------------------------------------------
⚡ Weather Check          12.50s       success     Weather: Sunny, 22°C in Milan
🛑 ML Inference           3.44s        interrupted Interrupted
🛑 Data Processing        3.45s        interrupted Interrupted
🛑 Database Query         3.45s        interrupted Interrupted
🛑 API Call               3.45s        interrupted Interrupted

Statistics:
  • Total execution time: 3.57s (with parallel execution)
  • Tools completed: 1/5
  • Tools interrupted: 4/5
  • Execution stopped by user request
```

## 🔐 Sicurezza e Limitazioni

### Sicurezza

- **ID Validation**: Gli UUID sono verificati prima di tentare lo stop
- **Not Found Handling**: Errore 404 se l'esecuzione non esiste
- **Race Conditions**: Gestite con lock appropriati

### Limitazioni

1. **Tools già avviati**: Se un tool è già in fase di sleep, risponderà entro 0.5s
2. **Tools completati**: Non possono essere "de-completati"
3. **Network**: In caso di disconnessione client, l'esecuzione server continua
4. **Aggregation**: Il nodo di aggregazione processa sempre i risultati disponibili

## 📝 Note di Implementazione

### Performance Impact

- **Check Interval**: 0.5s è un buon compromesso tra responsività e overhead
- **Memory**: Ogni esecuzione mantiene un `threading.Event` in memoria
- **Cleanup**: Importante per evitare memory leaks con esecuzioni long-running

### Estensioni Future

1. **Timeout Automatico**: Stop automatico dopo X secondi
2. **Priority Stop**: Stop selettivo per tool specifici
3. **Resume Capability**: Riprendere un'esecuzione interrotta
4. **Client-Side Stop Button**: UI web per gestire le esecuzioni

## 🎯 Best Practices

1. **Salva sempre l'execution_id** dal primo evento dello stream
2. **Usa /executions** per verificare lo stato prima dello stop
3. **Implementa timeout** lato client per esecuzioni troppo lunghe
4. **Gestisci gracefully** i casi di esecuzione già completata
5. **Logga gli stop events** per debugging e analytics

## 🔗 Link Utili

- **API Documentation**: `GET http://localhost:8000/`
- **Health Check**: `GET http://localhost:8000/health`
- **Tools List**: `GET http://localhost:8000/tools`
- **Active Executions**: `GET http://localhost:8000/executions`

---

**Versione API**: 2.0.0  
**Data**: Ottobre 2025  
**Autore**: Implementazione funzionalità Stop per LangGraph Parallel Tools


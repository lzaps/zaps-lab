# 🔧 Fix: Streaming in Postman

## ❓ Problema

Vedi il JSON solo alla **fine** invece che in **real-time**?

Questo è dovuto al **buffering** - Postman accumula la risposta invece di mostrarla chunk per chunk.

## ✅ Soluzione 1: Keep-Alive (Già Implementato!)

L'API ora invia messaggi "keepalive" ogni secondo per forzare il flush del buffer.

Vedrai linee tipo:
```
# keepalive 1697548325.123
```

Queste righe iniziano con `#` e possono essere ignorate - servono solo a forzare Postman a mostrare i dati.

## ✅ Soluzione 2: curl invece di Postman

**curl** non ha buffering problems:

```bash
curl -N http://localhost:8000/execute?query=test
```

Flag `-N` disabilita il buffering completamente! 

Vedrai gli eventi arrivare in **real-time**: ⚡

```json
{"event_type":"execution_start"...}
# keepalive 1697548325.123
{"event_type":"tool_start"...}
# keepalive 1697548326.234
{"event_type":"tool_complete"...}
...
```

## ✅ Soluzione 3: Postman Settings

### Aumenta Timeout
1. Postman → Settings (⚙️)
2. General → Request timeout
3. Imposta a **120000 ms** (2 minuti)

### Disable Response Buffering
Purtroppo Postman **non ha** un'opzione per disabilitare il buffering completamente.

## ✅ Soluzione 4: Browser DevTools

Apri il browser e usa console:

```javascript
fetch('http://localhost:8000/execute?query=test')
  .then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    function read() {
      reader.read().then(({done, value}) => {
        if (done) {
          console.log('✨ Done!');
          return;
        }
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        lines.forEach(line => {
          if (line.trim() && !line.startsWith('#')) {
            const event = JSON.parse(line);
            console.log(event);
          }
        });
        
        read(); // Continue reading
      });
    }
    
    read();
  });
```

Vedrai eventi in **console in real-time**! 🎯

## ✅ Soluzione 5: Python Client

Crea `test_streaming.py`:

```python
import requests
import json

url = "http://localhost:8000/execute"
params = {"query": "test"}

print("🚀 Connecting to API...")
response = requests.get(url, params=params, stream=True)

print("📡 Streaming events:\n")

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        
        # Skip keepalive comments
        if line_str.startswith('#'):
            print(f"  {line_str}")  # Show keepalive
            continue
        
        # Parse event
        try:
            event = json.loads(line_str)
            event_type = event.get('event_type')
            timestamp = event.get('timestamp', '')
            
            if event_type == 'execution_start':
                print(f"\n🎬 [{timestamp}] Execution started")
                print(f"   Query: {event.get('query')}")
                print(f"   Tools: {event.get('num_tools')}\n")
                
            elif event_type == 'tool_start':
                tool = event.get('tool_name')
                delay = event.get('delay', 0)
                print(f"🚀 [{timestamp}] {tool} started (ETA: {delay:.1f}s)")
                
            elif event_type == 'tool_complete':
                tool = event.get('tool_name')
                duration = event.get('duration', 0)
                result = event.get('result', '')
                print(f"✅ [{timestamp}] {tool} completed in {duration:.2f}s")
                print(f"   → {result}")
                
            elif event_type == 'aggregate':
                summary = event.get('summary', {})
                print(f"\n📊 [{timestamp}] Summary:")
                print(f"   Total duration: {summary.get('total_duration', 0):.2f}s")
                print(f"   Sequential would be: {summary.get('sequential_duration', 0):.2f}s")
                print(f"   Time saved: {summary.get('time_saved', 0):.2f}s\n")
                
            elif event_type == 'execution_complete':
                print(f"✨ [{timestamp}] Execution complete!\n")
                
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse: {line_str}")

print("🔌 Connection closed")
```

Esegui:
```bash
python test_streaming.py
```

Output bellissimo in real-time! 🌟

## ✅ Soluzione 6: Verifica Server

Assicurati che il server sia avviato correttamente:

```bash
# NO buffering
python api.py
```

**Importante**: Non usare `--reload` di uvicorn perché potrebbe causare buffering!

## 🎯 Confronto Tools

| Tool | Real-time? | Leggibilità | Facilità |
|------|-----------|-------------|----------|
| **curl** | ✅ Perfetto | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Python** | ✅ Perfetto | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Browser** | ✅ Perfetto | ⭐⭐⭐ | ⭐⭐⭐ |
| **Postman** | ⚠️ Bufferizzato | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 📝 Perché Postman Bufferizza?

Postman è progettato per **API REST** tradizionali, dove:
- Ricevi una risposta completa
- La formatti e la mostri

Per **HTTP Streaming**:
- Postman accumula i chunk
- Li mostra tutti insieme alla fine
- È una limitazione del tool

## 💡 Raccomandazione

### Per Sviluppo e Test:
Usa **curl** o **Python client** per vedere lo streaming reale.

### Per Documentazione:
Usa **Postman** per vedere il risultato finale formattato bene.

### Best of Both:
1. **curl** in un terminale per vedere eventi real-time
2. **Postman** in parallelo per vedere JSON formattato

```bash
# Terminal 1: Server
python api.py

# Terminal 2: curl (real-time)
curl -N http://localhost:8000/execute?query=test

# Postman: JSON formattato (alla fine)
GET http://localhost:8000/execute?query=test
```

## 🔍 Debug: Verifica Streaming

Test veloce per verificare che lo streaming funzioni:

```bash
curl -N http://localhost:8000/execute?query=test 2>&1 | while IFS= read -r line; do
  echo "[$(date +%H:%M:%S)] $line"
done
```

Vedrai il timestamp di quando **arriva** ogni riga!

Se vedi:
```
[14:23:45] {"event_type":"execution_start"...}
[14:23:45] {"event_type":"tool_start"...}
[14:23:46] # keepalive...
[14:23:57] {"event_type":"tool_complete"...}
```

**✅ Streaming funziona perfettamente!**

Se vedi tutto insieme alle 14:24:15:
```
[14:24:15] {"event_type":"execution_start"...}
[14:24:15] {"event_type":"tool_start"...}
[14:24:15] {"event_type":"tool_complete"...}
```

**❌ C'è buffering da qualche parte**

## 🎓 Conclusione

**Postman** è ottimo per API REST ma ha limitazioni con streaming.

**Usa curl o Python** per vedere lo streaming real-time funzionante!

L'API funziona correttamente - è solo Postman che bufferizza. ✅

---

**TL;DR**: Usa `curl -N` per vedere eventi in real-time! 🚀


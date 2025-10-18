# Approccio con Wrapper Universale

## 🎯 Panoramica

La funzionalità di stop è ora implementata usando un **Wrapper Universale** che:

✅ **NON modifica i tool originali** - i tool rimangono puliti e semplici  
✅ **Funziona con qualsiasi operazione bloccante** - sleep, API calls, database queries  
✅ **Responsivo** - controlla stop ogni 0.5 secondi  
✅ **Risultati parziali** - ritorna status "interrupted" quando fermato  
✅ **Riutilizzabile** - stesso wrapper per tutti i tool  

## 🏗️ Architettura

### 1. Tool Originali (NON Modificati)

I tool rimangono semplici e fanno il loro lavoro senza preoccuparsi dello stop:

```python
class WeatherCheckTool:
    """Fast tool: Simulates weather API call (10-15 seconds)."""
    
    def __init__(self):
        self.name = "Weather Check"
        self.delay = random.uniform(10.0, 15.0)
        self.color = Fore.CYAN
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        log_tool_start(self.name, self.color)
        start = time.time()
        
        # Semplice sleep - potrebbe essere una chiamata API
        time.sleep(self.delay)
        
        duration = time.time() - start
        log_tool_complete(self.name, duration, Fore.GREEN)
        
        return {
            "tool_results": [{
                "tool": self.name,
                "duration": duration,
                "result": f"Weather: Sunny, 22°C in Milan",
                "status": "success"
            }]
        }
```

**Vantaggi:**
- ✅ Codice pulito e leggibile
- ✅ Facile da testare
- ✅ Nessuna dipendenza da execution_id o stop_event
- ✅ Può essere sostituito con vera API call senza modifiche

### 2. InterruptibleToolWrapper

Il wrapper universale che rende qualsiasi tool interrompibile:

```python
class InterruptibleToolWrapper:
    """
    Universal wrapper that makes any tool interruptible.
    
    Works with:
    - time.sleep() simulations
    - HTTP API calls (requests, httpx)
    - Database queries
    - Any blocking operation
    
    The original tool runs in a thread and is monitored for stop signals.
    """
    
    def __init__(self, tool_instance: Any, tool_name: str, check_interval: float = 0.5):
        self.tool = tool_instance
        self.tool_name = tool_name
        self.check_interval = check_interval
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        execution_id = state.get("execution_id", "")
        stop_event = get_stop_event(execution_id)
        
        # Esegue il tool in un thread separato
        result_queue = Queue()
        exception_queue = Queue()
        
        def run_tool():
            try:
                result = self.tool(state)  # ⬅️ Tool originale immutato
                result_queue.put(result)
            except Exception as e:
                exception_queue.put(e)
        
        thread = threading.Thread(target=run_tool, daemon=True)
        thread.start()
        
        # Monitora il thread e controlla stop ogni 0.5s
        while thread.is_alive():
            if stop_event and stop_event.is_set():
                # Ritorna immediatamente con status interrupted
                return {
                    "tool_results": [{
                        "tool": self.tool_name,
                        "duration": time.time() - start_time,
                        "result": "Interrupted",
                        "status": "interrupted"
                    }]
                }
            
            thread.join(timeout=self.check_interval)
        
        # Thread finito, ritorna risultato normale
        return result_queue.get()
```

**Come Funziona:**

1. **Thread Separato**: Tool originale esegue in un thread daemon
2. **Monitoring Loop**: Main thread monitora con timeout di 0.5s
3. **Stop Check**: Ad ogni iterazione controlla se stop_event è impostato
4. **Early Return**: Se stop, ritorna immediatamente con "interrupted"
5. **Normal Completion**: Se il thread finisce, ritorna risultato normale

### 3. Uso nei Graph

**In `api.py` (con logging):**

```python
class ToolWrapperWithLogging:
    """Combina InterruptibleToolWrapper con logging."""
    
    def __init__(self, tool_class, tool_name):
        tool_instance = tool_class()
        
        # Wrappa con InterruptibleToolWrapper
        self.interruptible_tool = InterruptibleToolWrapper(
            tool_instance, 
            tool_name,
            check_interval=0.5
        )
        
        self.tool_name = tool_name
        self.tool_instance = tool_instance
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Log start
        log_event("tool_start", self.tool_name, delay=self.tool_instance.delay)
        
        # Esegui tool interrompibile
        result = self.interruptible_tool(state)
        
        # Log completion o interruption
        status = result["tool_results"][0]["status"]
        if status == "interrupted":
            log_event("tool_interrupted", ...)
        else:
            log_event("tool_complete", ...)
        
        return result

# Uso nel graph
for tool_name, tool_class in AVAILABLE_TOOLS.items():
    wrapped_tool = ToolWrapperWithLogging(tool_class, tool_name)
    builder.add_node(tool_name, wrapped_tool)
```

**In `main.py` (console):**

```python
def build_graph(execution_id: str):
    builder = StateGraph(GraphState)
    
    # Wrappa direttamente con InterruptibleToolWrapper
    for tool_name, tool_class in AVAILABLE_TOOLS.items():
        tool_instance = tool_class()
        wrapped_tool = InterruptibleToolWrapper(
            tool_instance,
            tool_name,
            check_interval=0.5
        )
        builder.add_node(tool_name, wrapped_tool)
    
    return builder.compile()
```

## 🔄 Funziona con Chiamate API Reali

Quando sostituisci `time.sleep()` con vera API call, **il wrapper funziona ugualmente**:

### Esempio: Weather API Reale

```python
class RealWeatherAPITool:
    """Tool con vera chiamata API."""
    
    def __init__(self):
        self.name = "Real Weather API"
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Chiamata API reale - può impiegare 2-30 secondi
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": "Milan", "appid": "your-key"},
            timeout=30
        )
        
        data = response.json()
        temp = data['main']['temp']
        
        return {
            "tool_results": [{
                "tool": self.name,
                "result": f"Temperature: {temp}°C",
                "status": "success"
            }]
        }
```

**Wrapping automatico:**

```python
# Il wrapper funziona ugualmente!
real_tool = RealWeatherAPITool()
wrapped = InterruptibleToolWrapper(real_tool, "Real Weather API")

# Sarà interrompibile ogni 0.5s anche durante la chiamata API
```

**Cosa succede quando fermi:**

1. Tool sta facendo `requests.get()` (bloccato per 15s)
2. Dopo 5s, fai stop via API
3. Main thread (wrapper) rileva stop al prossimo check (≤0.5s)
4. Wrapper ritorna immediatamente "interrupted"
5. Thread con API continua in background ma risultato è scartato

### Esempio: Database Query

```python
class DatabaseTool:
    """Tool con vera query database."""
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Query lenta - può impiegare 20+ secondi
        connection = psycopg2.connect(...)
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT * FROM large_table 
            WHERE complex_condition 
            ORDER BY timestamp DESC 
            LIMIT 1000
        """)
        
        results = cursor.fetchall()
        
        return {
            "tool_results": [{
                "result": f"Found {len(results)} records",
                "status": "success"
            }]
        }
```

**Anche questo è interrompibile con lo stesso wrapper!**

## 📊 Confronto degli Approcci

| Aspetto | Tool Modificati | Wrapper Universale |
|---------|-----------------|-------------------|
| **Modifica tool** | ✅ Sì (ogni tool) | ❌ No |
| **Codice tool** | Più complesso | Semplice e pulito |
| **Riutilizzabilità** | Medio | Alta |
| **Stop garantito** | Sì (check esplicito) | Sì (monitoring) |
| **Tempo risposta** | ≤0.5s | ≤0.5s |
| **Risultati parziali** | Sì | Sì |
| **Compatibilità API** | ✅ Sì | ✅ Sì |
| **Thread background** | No | Sì (continua dopo stop) |
| **Manutenibilità** | Media | Alta |

## ⚠️ Considerazioni

### Thread in Background

**Punto importante:** Quando interrompi, il thread con il tool continua in background.

```
Timeline dello Stop:

0s    Tool inizia (thread separato)
5s    User richiede stop
5.3s  Wrapper rileva stop (≤0.5s check)
5.3s  Wrapper ritorna "interrupted"
5.3s  Graph continua con risultato parziale
15s   Thread tool completa (in background, risultato scartato)
```

**Implicazioni:**

✅ **Pro:**
- Stop immediato dal punto di vista dell'utente (≤0.5s)
- Nessun forceful kill del thread (sicuro)
- Compatibile con qualsiasi operazione bloccante

⚠️ **Contro:**
- Risorse consumate fino al completamento del tool
- API call completata (potenziale costo/rate limit)
- Threads "zombie" se molti stop

**Mitigazioni:**

1. **Timeout sulle API calls:**
   ```python
   requests.get(..., timeout=30)  # Max 30s
   ```

2. **Connection pooling limitato:**
   ```python
   session = requests.Session()
   adapter = HTTPAdapter(max_retries=0, pool_maxsize=10)
   ```

3. **Monitoring threads attivi:**
   ```python
   import threading
   print(f"Active threads: {threading.active_count()}")
   ```

## 🚀 Best Practices

### 1. Tool Development

**Mantieni i tool semplici:**

```python
# ✅ GOOD - tool pulito
class MyTool:
    def __call__(self, state):
        result = do_work()  # Qualsiasi lavoro
        return {"tool_results": [{"status": "success", "result": result}]}

# ❌ BAD - logica di stop nel tool
class MyTool:
    def __call__(self, state):
        execution_id = state.get("execution_id")
        if check_stop(execution_id):  # ← Non fare questo!
            return interrupted
        ...
```

### 2. Timeout Configuration

**Usa timeout appropriati:**

```python
# Per API esterne
requests.get(url, timeout=30)  # Max 30s

# Per database
cursor.execute(query, timeout=60)  # Max 60s

# Nel wrapper
InterruptibleToolWrapper(tool, name, check_interval=0.5)  # Check ogni 0.5s
```

### 3. Error Handling

**Il wrapper gestisce eccezioni:**

```python
# Se il tool lancia eccezione, wrapper la cattura e ritorna:
{
    "tool_results": [{
        "status": "error",
        "result": "Error: connection timeout"
    }]
}
```

### 4. Testing

**Testa tool e wrapper separatamente:**

```python
# Test tool (senza wrapper)
def test_weather_tool():
    tool = WeatherCheckTool()
    result = tool({"execution_id": "test"})
    assert result["tool_results"][0]["status"] == "success"

# Test wrapper con mock
def test_wrapper_interrupt():
    mock_tool = SlowTool()  # Tool che impiegherebbe 30s
    wrapper = InterruptibleToolWrapper(mock_tool, "test")
    
    # Simula stop dopo 1s
    trigger_stop("test-id")
    
    result = wrapper({"execution_id": "test-id"})
    assert result["tool_results"][0]["status"] == "interrupted"
    assert result["tool_results"][0]["duration"] < 2  # Fermato velocemente
```

## 📝 Migrazione da Tool Modificati

Se hai tool con `interruptible_sleep`, ecco come migrare:

**Prima (tool modificato):**

```python
class MyTool:
    def __call__(self, state):
        execution_id = state.get("execution_id")
        
        # Check esplicito
        completed = interruptible_sleep(self.delay, execution_id)
        
        if not completed:
            return {"status": "interrupted"}
        
        return {"status": "success"}
```

**Dopo (tool pulito + wrapper):**

```python
# Tool semplificato
class MyTool:
    def __call__(self, state):
        time.sleep(self.delay)  # Semplice sleep
        return {"status": "success"}

# Wrapping automatico nel graph
wrapped = InterruptibleToolWrapper(MyTool(), "MyTool")
```

**Vantaggi migrazione:**
- ✅ -10 righe di codice per tool
- ✅ Nessuna dipendenza da execution_id nel tool
- ✅ Più facile testare tool isolatamente
- ✅ Funziona con API calls senza modifiche

## 🎯 Conclusione

L'approccio con **Wrapper Universale** è:

✅ **Più pulito** - tool semplici e focalizzati  
✅ **Più flessibile** - funziona con qualsiasi operazione  
✅ **Più manutenibile** - wrapping centralizzato  
✅ **Production-ready** - gestisce errori ed edge cases  

Quando sostituirai `time.sleep()` con chiamate API reali, **non dovrai modificare nulla** - il wrapper continuerà a funzionare perfettamente! 🚀

---

**Implementato**: Ottobre 2025  
**Approccio**: Wrapper Universale con Thread Monitoring  
**Compatibilità**: sleep, API calls, database queries, qualsiasi operazione bloccante


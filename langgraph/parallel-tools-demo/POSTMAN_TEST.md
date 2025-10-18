# 🧪 Test con Postman - Guida Pratica

## 🚀 Setup Veloce

### 1. Avvia il Server
```bash
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo
source venv/bin/activate
python api.py
```

### 2. Apri Postman

### 3. Crea Richiesta
- **Method**: `GET`
- **URL**: `http://localhost:8000/execute?query=test`

### 4. Clicca Send

### 5. Guarda lo Streaming! 🎉

## 📺 Cosa Vedrai in Postman

### Formato: JSON Lines (Pulito!)

Ogni evento è una riga JSON separata:

```json
{"timestamp":"14:23:45.123","event_type":"execution_start","query":"test","num_tools":5}
{"timestamp":"14:23:45.125","event_type":"tool_start","tool_name":"weather_check","delay":12.523}
{"timestamp":"14:23:45.126","event_type":"tool_start","tool_name":"database_query","delay":17.345}
{"timestamp":"14:23:45.127","event_type":"tool_start","tool_name":"api_call","delay":19.123}
{"timestamp":"14:23:45.128","event_type":"tool_start","tool_name":"ml_inference","delay":28.456}
{"timestamp":"14:23:45.129","event_type":"tool_start","tool_name":"data_processing","delay":29.789}
```

Poi aspetti ~12 secondi e vedi:

```json
{"timestamp":"14:23:57.648","event_type":"tool_complete","tool_name":"weather_check","duration":12.523,"result":"Weather: Sunny, 22°C in Milan"}
```

Poi altri tool completano:

```json
{"timestamp":"14:24:02.471","event_type":"tool_complete","tool_name":"database_query","duration":17.345,"result":"Found 1,247 matching records in database"}
{"timestamp":"14:24:04.250","event_type":"tool_complete","tool_name":"api_call","duration":19.123,"result":"API response: 200 OK - Data retrieved successfully"}
{"timestamp":"14:24:13.584","event_type":"tool_complete","tool_name":"ml_inference","duration":28.456,"result":"ML prediction: Sentiment = Positive (confidence: 0.94)"}
{"timestamp":"14:24:14.918","event_type":"tool_complete","tool_name":"data_processing","duration":29.789,"result":"Processed 50,000 rows - Average value: 42.7"}
```

Infine il riepilogo:

```json
{"timestamp":"14:24:14.920","event_type":"aggregate","summary":{"total_duration":29.792,"sequential_duration":107.236,"time_saved":77.444,"avg_duration":21.447,"fastest":12.523,"slowest":29.789,"num_tools":5,"results":[...]}}
{"timestamp":"14:24:14.921","event_type":"execution_complete"}
```

## 🎯 Test Specifici

### Test 1: Query Personalizzata
```
GET http://localhost:8000/execute?query=Trova informazioni meteo
```

### Test 2: POST Request
**Method**: POST  
**URL**: `http://localhost:8000/execute`  
**Body (JSON)**:
```json
{
  "query": "Esegui analisi completa"
}
```

### Test 3: Formato SSE (Opzionale)
```
GET http://localhost:8000/execute?query=test&format=sse
```

Vedrai:
```
data: {"event_type":"execution_start",...}

data: {"event_type":"tool_start",...}

```

## 📊 Timeline degli Eventi

### Secondi 0-1: Avvio
```json
{"event_type":"execution_start"} → Esecuzione parte
{"event_type":"prepare"}         → Graph preparato
{"event_type":"tool_start"} × 5   → Tutti i tool partono
```

### Secondi 1-12: In Esecuzione
```
... nessun evento (tool lavorano in parallelo) ...
```

### Secondi 12-15: Completamenti Veloci
```json
{"event_type":"tool_complete","tool_name":"weather_check"}
```

### Secondi 15-20: Completamenti Medi
```json
{"event_type":"tool_complete","tool_name":"database_query"}
{"event_type":"tool_complete","tool_name":"api_call"}
```

### Secondi 20-30: Completamenti Lenti
```json
{"event_type":"tool_complete","tool_name":"ml_inference"}
{"event_type":"tool_complete","tool_name":"data_processing"}
```

### Secondo 30: Fine
```json
{"event_type":"aggregate"}           → Riepilogo
{"event_type":"execution_complete"}  → Done!
```

## 🔍 Dettagli degli Eventi

### execution_start
```json
{
  "timestamp": "14:23:45.123",
  "event_type": "execution_start",
  "query": "test",
  "num_tools": 5
}
```

### tool_start
```json
{
  "timestamp": "14:23:45.125",
  "event_type": "tool_start",
  "tool_name": "weather_check",
  "delay": 12.523
}
```
`delay` = tempo stimato di esecuzione

### tool_complete
```json
{
  "timestamp": "14:23:57.648",
  "event_type": "tool_complete",
  "tool_name": "weather_check",
  "duration": 12.523,
  "result": "Weather: Sunny, 22°C in Milan"
}
```
`duration` = tempo effettivo impiegato  
`result` = risultato del tool

### aggregate
```json
{
  "timestamp": "14:24:14.920",
  "event_type": "aggregate",
  "summary": {
    "total_duration": 29.792,
    "sequential_duration": 107.236,
    "time_saved": 77.444,
    "avg_duration": 21.447,
    "fastest": 12.523,
    "slowest": 29.789,
    "num_tools": 5,
    "results": [...]
  }
}
```

## 🎨 Tips per Postman

### 1. Leggi mentre arriva
Non aspettare la fine! Scorri il pannello Response mentre gli eventi arrivano.

### 2. Pretty Print
Postman formatta automaticamente il JSON per leggibilità.

### 3. Salva la Collection
Salva la richiesta per usarla di nuovo.

### 4. Environment Variables
Crea variabili per URL e query:
```
{{base_url}}/execute?query={{query}}
```

### 5. Tests / Scripts
Aggiungi uno script per parsare gli eventi:
```javascript
pm.test("Events received", function () {
    const response = pm.response.text();
    const events = response.split('\n').filter(l => l.trim());
    
    console.log(`Received ${events.length} events`);
    
    events.forEach(line => {
        const event = JSON.parse(line);
        console.log(`[${event.timestamp}] ${event.event_type}`);
    });
});
```

## 🐛 Troubleshooting

### Problema: Non vedo eventi
✅ **Soluzione**: Assicurati che il server sia avviato (`python api.py`)

### Problema: Timeout
✅ **Soluzione**: Aumenta timeout in Postman (Settings → General → Request timeout)

### Problema: Risposta vuota
✅ **Soluzione**: Controlla che l'URL sia corretto: `http://localhost:8000/execute`

### Problema: Eventi non formattati
✅ **Soluzione**: Postman formatta automaticamente JSON. Se vedi testo grezzo va bene!

### Problema: Server non risponde
✅ **Soluzione**: 
1. Controlla che il server sia in esecuzione
2. Verifica la porta (default: 8000)
3. Prova: `curl http://localhost:8000/health`

## 📚 Endpoint Alternativi

### Health Check (Veloce)
```
GET http://localhost:8000/health
```
Response immediata per verificare che il server funzioni.

### Lista Tools
```
GET http://localhost:8000/tools
```
Vedi i 5 tool disponibili e i loro tempi.

### API Info
```
GET http://localhost:8000/
```
Info generali sull'API.

### Swagger UI (Interattivo!)
```
http://localhost:8000/docs
```
Testa l'API direttamente nel browser! 🎉

## 🎯 Sfide / Esercizi

### Sfida 1: Timing
Cronometra quanto tempo impiega dal primo `tool_start` al ultimo `tool_complete`.
**Risposta attesa**: ~30 secondi

### Sfida 2: Calcolo
Calcola manualmente:
```
time_saved = sequential_duration - total_duration
```
Verifica che corrisponda al valore nell'evento `aggregate`.

### Sfida 3: Tool più Veloce
Quale tool finisce per primo?
**Risposta attesa**: `weather_check` (~12-15s)

### Sfida 4: Tool più Lento
Quale tool finisce per ultimo?
**Risposta attesa**: `data_processing` o `ml_inference` (~25-30s)

### Sfida 5: Parsing
Scrivi uno script che:
1. Parse tutti gli eventi
2. Stampa solo i `tool_complete`
3. Ordina per durata

## ✨ Conclusione

HTTP Streaming con JSON Lines in Postman è:
- ✅ **Semplice**: Ogni riga è un JSON
- ✅ **Leggibile**: Formattazione automatica
- ✅ **Real-time**: Vedi eventi mentre succedono
- ✅ **Pratico**: Niente configurazione extra

Buon testing! 🚀🧪


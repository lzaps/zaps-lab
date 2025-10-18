# 🚀 Quick Start - API Streaming

## ✨ Hai ora un'API con Streaming Real-Time!

L'API mostra **in tempo reale** l'esecuzione parallela dei tool, proprio come vedi nel terminale.

## 📋 Setup Rapido

### 1. Avvia il Server

```bash
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo
source venv/bin/activate
python api.py
```

Vedrai:
```
🚀 FastAPI server starting...
📡 Streaming endpoint: http://localhost:8000/execute
📝 Test with Postman or curl
   curl -N http://localhost:8000/execute?query=test

INFO:     Started server process [xxxxx]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Testa con Postman

**In Postman:**
1. Nuovo tab
2. Method: `GET`
3. URL: `http://localhost:8000/execute?query=test`
4. Clicca **Send**
5. Guarda gli eventi arrivare! 🎉

**⚠️ Nota**: Postman potrebbe **bufferizzare** e mostrare tutto alla fine. Questo è normale! Per vedere eventi in **real-time**, usa **curl** (vedi sotto).

**Vedrai qualcosa tipo:**

```json
{"timestamp":"14:23:45.123","event_type":"execution_start","query":"test","num_tools":5}
{"timestamp":"14:23:45.125","event_type":"tool_start","tool_name":"weather_check","delay":12.5}
{"timestamp":"14:23:45.126","event_type":"tool_start","tool_name":"database_query","delay":17.3}
{"timestamp":"14:23:45.127","event_type":"tool_start","tool_name":"api_call","delay":19.1}
{"timestamp":"14:23:45.128","event_type":"tool_start","tool_name":"ml_inference","delay":28.4}
{"timestamp":"14:23:45.129","event_type":"tool_start","tool_name":"data_processing","delay":29.8}

... (aspetta ~12 secondi) ...

{"timestamp":"14:23:57.650","event_type":"tool_complete","tool_name":"weather_check","duration":12.52,"result":"Weather: Sunny, 22°C in Milan"}

... (altri tool completano via via) ...

{"timestamp":"14:24:15.000","event_type":"aggregate","summary":{"total_duration":30.12,"time_saved":76.68,...}}
{"timestamp":"14:24:15.001","event_type":"execution_complete"}
```

**Nota**: Ogni riga è un oggetto JSON completo (formato **JSON Lines / NDJSON**) 🎯

### 3. Test Real-Time con curl (Raccomandato!)

**Per vedere eventi in tempo reale**, usa curl:

```bash
curl -N 'http://localhost:8000/execute?query=test'
```

**Nota**: Le virgolette sono **necessarie** per zsh (macOS)!

Gli eventi appariranno uno per uno mentre succedono! ⚡

**Perché curl e non Postman?**  
Postman bufferizza le risposte streaming. curl mostra tutto immediatamente.

👉 Vedi **[POSTMAN_STREAMING_FIX.md](POSTMAN_STREAMING_FIX.md)** per dettagli e soluzioni alternative.

## 🎯 Endpoints Disponibili

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/` | GET | Info API |
| `/health` | GET | Health check |
| `/tools` | GET | Lista tools disponibili |
| `/execute` | GET | Streaming execution (query param) |
| `/execute` | POST | Streaming execution (JSON body) |
| `/docs` | GET | Swagger UI interattivo |
| `/redoc` | GET | Documentazione ReDoc |

## 📱 Test Interattivo nel Browser

Apri: **http://localhost:8000/docs**

- Vedrai Swagger UI
- Prova l'endpoint `/execute`
- Clicca "Try it out"
- Modifica la query
- Clicca "Execute"
- Vedi lo streaming in azione! 🚀

## 🔍 Eventi in Streaming

### 1. `execution_start` - Inizio
Indica che l'esecuzione è partita

### 2. `tool_start` - Tool Parte
Ogni tool emette questo evento quando inizia
- Include il `delay` stimato

### 3. `tool_complete` - Tool Finisce
Ogni tool emette questo evento quando finisce
- Include `duration` e `result`

### 4. `aggregate` - Riepilogo
Riepilogo finale con statistiche
- Total duration (parallelo)
- Sequential duration (somma)
- Time saved
- Tutti i risultati

### 5. `execution_complete` - Fine
Ultimo evento, tutto completato

## 💡 Esempio Postman POST

**Method:** POST  
**URL:** `http://localhost:8000/execute`  
**Body (JSON):**
```json
{
  "query": "Esegui tutti i tool"
}
```

**Send** → Vedi streaming!

## 🎨 Vantaggi dello Streaming HTTP

✅ **Real-time Updates**: Vedi ogni evento mentre succede  
✅ **No Timeout**: Il client riceve dati costantemente  
✅ **Progressivo**: Sai esattamente cosa sta succedendo  
✅ **Semplice**: Usa HTTP Streaming puro (JSON Lines / NDJSON)  
✅ **Universale**: Funziona con qualsiasi client HTTP

### Formato JSON Lines (Default)
Ogni evento è una riga JSON separata:
```
{"event":"A"}\n
{"event":"B"}\n
```

### Formato SSE (Opzionale)
Aggiungi `?format=sse` per Server-Sent Events:
```
GET http://localhost:8000/execute?query=test&format=sse
```  

## 📚 Documentazione Completa

Vedi **[API_GUIDE.md](API_GUIDE.md)** per:
- Esempi Python e JavaScript
- Tutti i tipi di eventi
- Troubleshooting
- Deployment in produzione

## 🎯 Cosa Hai Creato

1. ✅ **5 Tool Paralleli** con delay realistici (10-30s)
2. ✅ **LangGraph** con pattern fan-out/fan-in
3. ✅ **API FastAPI** con streaming real-time
4. ✅ **Server-Sent Events** (SSE) standard
5. ✅ **Documentazione** Swagger interattiva
6. ✅ **Testabile** con Postman, curl, browser

## 🚀 Pronto?

```bash
# Terminal 1: Avvia server
python api.py

# Terminal 2 (o Postman): Testa
curl -N http://localhost:8000/execute?query=test
```

Buon divertimento! 🎉


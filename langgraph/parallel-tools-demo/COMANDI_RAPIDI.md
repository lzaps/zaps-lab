# ⚡ Comandi Rapidi

## 🚀 Avvia Server

```bash
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo
source venv/bin/activate
python api.py
```

## 🧪 Test Streaming (Real-Time)

### Opzione 1: Python Script (Raccomandato! 🌟)
```bash
python test_streaming.py
```

### Opzione 2: curl
```bash
curl -N 'http://localhost:8000/execute?query=test'
```

**Nota**: Virgolette necessarie per zsh!

### Opzione 3: curl con timestamps
```bash
curl -N 'http://localhost:8000/execute?query=test' 2>&1 | \
  while IFS= read -r line; do echo "[$(date +%H:%M:%S)] $line"; done
```

## 📋 Altri Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Lista Tools
```bash
curl http://localhost:8000/tools
```

### API Info
```bash
curl http://localhost:8000/
```

## 🌐 Browser

### Swagger UI (Interattivo)
```
http://localhost:8000/docs
```

### ReDoc (Documentazione)
```
http://localhost:8000/redoc
```

## 🔧 Setup Iniziale (Una Volta Sola)

```bash
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 Demo Completo

```bash
# Terminal 1: Avvia server
python api.py

# Terminal 2: Vedi streaming real-time
python test_streaming.py
```

## 🐛 Debug

### Problema: Porta già in uso
```bash
lsof -ti:8000 | xargs kill -9
```

### Problema: Modulo non trovato
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problema: Server non risponde
```bash
curl http://localhost:8000/health
```

## 📚 Documentazione

```bash
# Leggi in ordine:
cat START_HERE.md
cat SOLUZIONE_STREAMING.md
cat POSTMAN_TEST.md
```

## 🎯 Quick Start (Copy-Paste)

```bash
# 1. Vai nella cartella
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo

# 2. Attiva environment
source venv/bin/activate

# 3. Avvia server (Terminal 1)
python api.py &

# 4. Aspetta 2 secondi
sleep 2

# 5. Test streaming (Terminal 2)
python test_streaming.py
```

## 🏃 One-Liner

```bash
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo && \
source venv/bin/activate && \
python api.py
```

Poi in altro terminale:

```bash
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo && \
source venv/bin/activate && \
python test_streaming.py
```

## ✨ Conclusione

**Comando più utile:**
```bash
python test_streaming.py
```

Questo mostra perfettamente lo streaming HTTP in real-time! 🎉


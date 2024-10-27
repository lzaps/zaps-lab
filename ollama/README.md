# Ollama

Ollama is a open-source tool that lets easily run open LLMs locally on your system.

https://ollama.com/

`ollama-local.html` is a very basic html page that you can open locally to call models running locally on Ollama.
To avoid CORS error you need to shotdown Ollama server, go on the teriminal:

```
launchctl setenv OLLAMA_ORIGINS "*"
```

and restart Ollama server.
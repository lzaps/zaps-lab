#!/bin/bash

# Test script for the streaming API

echo "🧪 Testing Parallel Tools Streaming API"
echo ""
echo "Make sure the server is running: python api.py"
echo ""
echo "Testing in 3 seconds..."
sleep 3
echo ""
echo "📡 Calling streaming endpoint..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

curl -N http://localhost:8000/execute?query=test

echo ""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Test complete!"


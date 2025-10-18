#!/bin/bash
# Simple test script for stop functionality

echo "🧪 Testing Stop Functionality"
echo "=============================="
echo ""

# Check if server is running
echo "🔍 Checking if API is running..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ API is not running!"
    echo "   Start it with: python api.py"
    exit 1
fi
echo "✅ API is running"
echo ""

# Start execution in background
echo "🚀 Starting execution..."
TEMP_FILE=$(mktemp)
curl -N -s http://localhost:8000/execute?query=test_stop > "$TEMP_FILE" &
CURL_PID=$!

# Wait a moment for execution to start
sleep 2

# Extract execution ID from first line
EXECUTION_ID=$(head -n 1 "$TEMP_FILE" | jq -r '.execution_id // empty')

if [ -z "$EXECUTION_ID" ]; then
    echo "⚠️  Could not extract execution_id, waiting longer..."
    sleep 2
    EXECUTION_ID=$(head -n 1 "$TEMP_FILE" | jq -r '.execution_id // empty')
fi

if [ -z "$EXECUTION_ID" ]; then
    echo "❌ Failed to get execution_id"
    kill $CURL_PID 2>/dev/null
    rm "$TEMP_FILE"
    exit 1
fi

echo "📋 Execution ID: $EXECUTION_ID"
echo ""

# Show current output
echo "📊 Current events:"
head -n 10 "$TEMP_FILE" | while read line; do
    if [ ! -z "$line" ]; then
        echo "$line" | jq -c '.' 2>/dev/null || echo "$line"
    fi
done
echo ""

# Wait a few more seconds
echo "⏳ Waiting 15 seconds before sending stop signal..."
sleep 15

# Send stop
echo "🛑 Sending stop signal..."
STOP_RESPONSE=$(curl -s -X POST "http://localhost:8000/stop/$EXECUTION_ID")
echo "📬 Stop response:"
echo "$STOP_RESPONSE" | jq '.' 2>/dev/null || echo "$STOP_RESPONSE"
echo ""

# Wait for stream to end
echo "⏳ Waiting for stream to complete..."
wait $CURL_PID 2>/dev/null

# Show final results
echo ""
echo "📊 Final events received:"
tail -n 15 "$TEMP_FILE" | while read line; do
    if [ ! -z "$line" ]; then
        EVENT_TYPE=$(echo "$line" | jq -r '.event_type // .event // empty' 2>/dev/null)
        case "$EVENT_TYPE" in
            "tool_complete")
                TOOL=$(echo "$line" | jq -r '.tool_name // empty')
                echo "  ✅ $TOOL completed"
                ;;
            "tool_interrupted")
                TOOL=$(echo "$line" | jq -r '.tool_name // empty')
                echo "  🛑 $TOOL interrupted"
                ;;
            "execution_complete")
                echo "  ✨ Execution finished"
                ;;
        esac
    fi
done
echo ""

# Cleanup
rm "$TEMP_FILE"

echo "✅ Test completed!"
echo ""
echo "💡 Tip: Run full test suite with:"
echo "   python test_stop_functionality.py --test all"


#!/bin/bash
# watchdog.sh

echo "🛡️ Starting Stealth Bot v13 Watchdog..."

while true; do
    # Run the bot
    python3 app.py
    
    # If app.py crashes or exits, this line triggers
    echo "⚠️ Bot process died! Watchdog restarting in 5 seconds..."
    sleep 5
done
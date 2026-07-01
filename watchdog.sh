#!/bin/bash
# watchdog.sh

# Load variables from your config.py (Quick regex extraction)
BOT_TOKEN=$(grep -E '^BOT_TOKEN[[:space:]]*=[[:space:]]*["'\'']' config.py | sed -E 's/BOT_TOKEN[[:space:]]*=[[:space:]]*["'\'']([^"'\'']+)["'\'']/\1/')
TARGET_CHANNEL_ID=$(grep -E '^TARGET_CHANNEL_ID[[:space:]]*=[[:space:]]*' config.py | sed -E 's/TARGET_CHANNEL_ID[[:space:]]*=[[:space:]]*(-?[0-9]+).*/\1/')

send_telegram_msg() {
    local text="$1"
    if [ -n "$BOT_TOKEN" ] && [ -n "$TARGET_CHANNEL_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TARGET_CHANNEL_ID}" \
            -d "parse_mode=Markdown" \
            -d "text=${text}" > /dev/null
    fi
}

echo "🛡️ Starting Stealth Bot v13.1 Watchdog..."

while true; do
    # Run the bot
    python3 app.py
    EXIT_CODE=$?
    
    # Check if the bot requested a Git Update (Exit Code 5)
    if [ $EXIT_CODE -eq 5 ]; then
        echo "🔄 Watchdog intercepted update trigger code (5)."
        send_telegram_msg "⚠️ *System Update Triggered:* Going offline briefly to sync patches..."
        
        echo "📥 Pulling latest codebase from GitHub..."
        git fetch origin
        
        # Capture the upcoming commit messages for the changelog
        CHANGELOG=$(git log HEAD..origin/main --oneline 2>/dev/null)
        if [ -z "$CHANGELOG" ]; then
            CHANGELOG="No remote changes found. Local environment reset/reloaded."
        fi
        
        # Save the changelog to disk so Python can read it and print it when it boots back up
        echo "$CHANGELOG" > .update_changelog
        
        # Apply the changes
        git pull origin main
        
        echo "🚀 Re-booting optimized bot core..."
        sleep 2
    elif [ $EXIT_CODE -eq 0 ]; then
        echo "🛑 Clean exit. Stopping watchdog loop."
        break
    else
        echo "⚠️ Bot process crashed with code $EXIT_CODE! Watchdog restarting in 5 seconds..."
        sleep 5
    fi
done
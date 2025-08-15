# Setup Instructions

## Prerequisites

- Python 3.11+
- macOS (for auto-start setup)
- Telegram account

## Step 1: Create Telegram Bot

1. Open Telegram on your phone
2. Search for **@BotFather**
3. Send `/newbot`
4. Choose a display name (e.g., "Voice Notes Bot")
5. Choose a username ending in `bot` (e.g., `YourVoiceNotesBot`)
6. **Save the token** you receive (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Configure Environment

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your bot token:
```
TELEGRAM_TOKEN=YOUR_BOT_TOKEN_HERE
```

## Step 3: Install Dependencies

The project uses `uv` for Python package management:

```bash
# If you don't have uv installed:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

## Step 4: Test the Bot

Run the bot manually first:

```bash
uv run python bot.py
```

You should see:
```
[timestamp] Bot initialized with projects dir: projects
[timestamp] Loading Whisper model: base
[timestamp] Starting bot...
```

## Step 5: Test Basic Commands

In Telegram, message your bot:

1. Send `/start` - Should show welcome message
2. Send `/new My First Project` - Creates a project
3. Send `/projects` - Lists your projects
4. Send `/pick 001` - Selects the project
5. Send a voice message - Should transcribe and save

## Step 6: Set Up Auto-Start (macOS)

Create a LaunchAgent to start the bot on login:

1. Create the plist file:
```bash
cat > ~/Library/LaunchAgents/com.user.telegram-voice-bot.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.telegram-voice-bot</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/env</string>
        <string>uv</string>
        <string>run</string>
        <string>python</string>
        <string>bot.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/yabo/Documents/Code/phone-to-laptop</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/Users/yabo/Documents/Code/phone-to-laptop/logs/launchd.out.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/yabo/Documents/Code/phone-to-laptop/logs/launchd.err.log</string>
</dict>
</plist>
EOF
```

2. Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.user.telegram-voice-bot.plist
```

3. Start the service:
```bash
launchctl start com.user.telegram-voice-bot
```

4. Check status:
```bash
launchctl list | grep telegram-voice-bot
```

## Managing the Service

**Stop the bot:**
```bash
launchctl stop com.user.telegram-voice-bot
```

**Restart the bot:**
```bash
launchctl stop com.user.telegram-voice-bot
launchctl start com.user.telegram-voice-bot
```

**Disable auto-start:**
```bash
launchctl unload ~/Library/LaunchAgents/com.user.telegram-voice-bot.plist
```

**View logs:**
```bash
tail -f logs/bot.log
tail -f logs/launchd.err.log
```

## Troubleshooting

### Bot doesn't respond
- Check token in `.env` file
- Check logs: `cat logs/bot.log`
- Ensure bot is running: `ps aux | grep bot.py`

### Whisper takes too long
- First run downloads the model (~140MB for base)
- Consider using "tiny" model for faster processing
- Change in `.env`: `WHISPER_MODEL=tiny`

### Voice messages not processing
- Check you've selected a project first with `/pick`
- Ensure Whisper model downloaded successfully
- Check audio directory permissions

### Auto-start not working
- Check launchd logs: `tail logs/launchd.err.log`
- Verify plist syntax: `plutil ~/Library/LaunchAgents/com.user.telegram-voice-bot.plist`
- Ensure full paths in plist file

## Usage Flow

1. **On your phone:** Open Telegram, message your bot
2. **Create project:** `/new Shopping List`
3. **Select project:** `/pick 001`
4. **Send voice notes:** Just record and send
5. **On laptop:** Find transcriptions in `projects/project-001-shopping-list/notes.md`

## Notes

- Bot processes queued messages when laptop comes online
- Voice files are deleted after transcription
- All data stays local on your laptop
- Projects are numbered sequentially (001, 002, etc.)
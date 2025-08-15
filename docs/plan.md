# Telegram Voice Notes to Local Project System - Implementation Plan

## Overview
A frictionless voice capture system where you send voice messages via Telegram to organize thoughts into local project folders on your laptop.

## Architecture

### Components
1. **Telegram Bot** (Phone Interface)
   - Receives commands and voice messages
   - Provides interactive feedback
   - Works even when laptop is offline
   
2. **Python Bot Server** (Laptop)
   - Runs locally on laptop
   - Processes queued messages on startup
   - Handles all processing
   - Manages project structure
   - Transcribes audio using Whisper

3. **Message Queue** (Telegram Cloud)
   - Stores messages while laptop is offline
   - Telegram's getUpdates API maintains queue
   - Persistent message history

4. **File System** (Storage)
   - Project-based folder structure
   - Markdown notes with timestamps
   - Configuration files
   - Processed message tracking

## User Flow

### When Laptop is Online:
```
User → Telegram Bot → Python Server → Whisper → File System
         ↑                                          ↓
         └──────────── Confirmation ←───────────────┘
```

### When Laptop is Offline:
```
User → Telegram Bot → Queue (Telegram Cloud)
         ↑                    
         └─ "Laptop offline, queued for processing"

[Later when laptop comes online]
Python Server → Fetch Queue → Process All → Send Confirmations
```

## Implementation Steps

### Phase 1: Setup & Structure
1. Create project folder structure
2. Set up Python environment with dependencies
3. Create configuration system for bot token and settings

### Phase 2: Telegram Bot
1. Create bot via BotFather
2. Implement command handlers:
   - `/start` - Welcome message
   - `/projects` - List all projects
   - `/new <name>` - Create new project
   - `/pick <id>` - Select active project
   - `/status` - Show current project

### Phase 3: Queue Management
1. Implement message tracking (processed vs unprocessed)
2. On startup, fetch all unprocessed messages
3. Batch process queued messages
4. Send delayed confirmations for each processed message
5. Handle offline indicator responses

### Phase 4: Voice Processing
1. Set up voice message handler
2. Download audio files from Telegram
3. Integrate Whisper for transcription
4. Format transcribed text with timestamps

### Phase 5: Project Management
1. Create project ID system
2. Implement session management (active project)
3. File writing with append mode
4. Error handling for no active project

### Phase 6: Feedback System
1. Processing indicators
2. Success confirmations with character count
3. Error messages for failures
4. Project switch confirmations
5. Offline queue notifications
6. Batch processing summaries

## Technical Specifications

### Dependencies
- `python-telegram-bot` - Telegram API wrapper
- `openai-whisper` - Local transcription
- `pydantic` - Configuration management
- `rich` - Console output formatting

### File Structure
```
/Users/yabo/Documents/Code/phone-to-laptop/
├── bot.py                 # Main bot application
├── config.json           # Bot configuration
├── requirements.txt      # Python dependencies
├── state.json           # Tracks processed messages
├── projects/            # All project folders
│   └── project-XXX-name/
│       └── notes.md     # Voice transcriptions
├── audio/               # Temporary audio files
├── logs/               # Bot operation logs
└── docs/
    ├── plan.md         # This file
    └── setup.md        # Setup instructions
```

### Configuration Format
```json
{
  "telegram_token": "YOUR_BOT_TOKEN",
  "whisper_model": "base",
  "projects_dir": "./projects",
  "audio_dir": "./audio",
  "timezone": "UTC",
  "check_interval": 60,
  "offline_response": "💻 Laptop is offline. Message queued for processing."
}
```

### State Tracking Format
```json
{
  "last_update_id": 12345678,
  "active_sessions": {
    "user_id": "project_id"
  },
  "processed_messages": [
    "message_id_1",
    "message_id_2"
  ]
}
```

### Note Format
```markdown
## YYYY-MM-DD HH:MM

[Transcribed text from voice message]

```

## Features

### Core Features (MVP)
- [x] Project creation and selection
- [x] Voice message reception
- [x] Local Whisper transcription
- [x] Markdown note generation
- [x] Session persistence
- [x] Error handling
- [x] Interactive feedback
- [x] Offline queue handling
- [x] Auto-start on system boot
- [x] Batch processing of queued messages

### Future Enhancements
- [ ] Project archiving
- [ ] Search across projects
- [ ] Voice message batching
- [ ] Multiple language support
- [ ] Export functionality
- [ ] Project statistics
- [ ] Backup system

## Testing Strategy

### Unit Tests
- Project creation/deletion
- Session management
- File writing operations
- Configuration loading

### Integration Tests
- Telegram message handling
- Whisper transcription pipeline
- End-to-end voice to text flow

### Manual Testing Checklist
- [ ] Bot responds to all commands
- [ ] Voice messages are received
- [ ] Transcription accuracy acceptable
- [ ] Files created in correct location
- [ ] Session persists between messages
- [ ] Error messages are clear
- [ ] Confirmations show character count

## Security Considerations
- Bot token stored securely (not in git)
- Audio files deleted after processing
- No external API calls (all local)
- Project names sanitized for file system
- Rate limiting for commands

## Performance Goals
- Voice processing: < 30 seconds for 1-minute audio
- Command response: < 1 second
- Memory usage: < 500MB idle, < 2GB during transcription
- Disk usage: Minimal (audio files cleaned up)

## Success Metrics
- Zero friction from thought to capture
- 100% transcription completion rate
- Clear project organization
- No lost voice messages
- Instant feedback on every action

## Auto-Start Configuration

### macOS (LaunchAgent)
- Create plist file in `~/Library/LaunchAgents/`
- Auto-starts when user logs in
- Runs in background continuously

### Linux (systemd)
- Create service file in `~/.config/systemd/user/`
- Enable with `systemctl --user enable telegram-bot`

### Windows (Task Scheduler)
- Create task to run at startup
- Run whether user logged in or not

## Queue Processing Logic

### On Startup:
1. Check `state.json` for last processed update_id
2. Fetch all messages since last update_id
3. Filter unprocessed voice messages
4. Process each in chronological order
5. Send batch summary to user

### Message Handling:
- **Online**: Process immediately, send confirmation
- **Offline**: Telegram stores, user gets offline notice (via webhook or polling timeout)
- **Restart**: Process queue, send delayed confirmations

## Next Steps
1. Get Telegram bot token from BotFather
2. Install Python dependencies
3. Create initial project structure
4. Implement basic bot with project management
5. Add queue management system
6. Add voice handling and transcription
7. Set up auto-start configuration
8. Test end-to-end flow with offline scenarios
9. Document usage instructions
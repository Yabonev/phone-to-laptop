# Test Plan for Voice Notes Bot

## Test Case 1: Bot Startup and Configuration

**Arrange:**
- .env file with valid TELEGRAM_TOKEN
- Empty state.json or no state file
- Required directories don't exist

**Act:**
- Run `uv run python bot.py`

**Assert:**
- Bot starts without errors
- Creates projects/, audio/, logs/ directories
- Creates state.json if missing
- Connects to Telegram successfully

## Test Case 2: Create New Project

**Arrange:**
- Bot is running
- No existing projects

**Act:**
- Send `/new My Test Project` to bot

**Assert:**
- Bot responds with "✅ Created project: My Test Project (ID: 001)"
- Directory `projects/project-001-my-test-project/` is created
- File `notes.md` exists with header

## Test Case 3: List Projects

**Arrange:**
- Bot has created projects

**Act:**
- Send `/projects` command

**Assert:**
- Bot lists all projects with IDs and names
- Format: "001. My Test Project"

## Test Case 4: Select Project

**Arrange:**
- Project 001 exists
- No active project selected

**Act:**
- Send `/pick 1` or `/pick 001`

**Assert:**
- Bot responds "✅ Selected: My Test Project"
- Session saved in state.json

## Test Case 5: Voice Message Processing

**Arrange:**
- Project selected
- Whisper model available

**Act:**
- Send voice message saying "This is a test note"

**Assert:**
- Bot shows "📝 Processing..."
- Then "✅ Added to My Test Project (X chars)"
- Text appears in project's notes.md with timestamp

## Test Case 6: No Project Selected Error

**Arrange:**
- No active project

**Act:**
- Send voice message

**Assert:**
- Bot responds "❌ No project selected. Use /pick <id> first."

## Test Case 7: Queue Processing

**Arrange:**
- Bot is offline
- User sends messages

**Act:**
- Start bot
- Bot checks for queued messages

**Assert:**
- All queued messages are processed
- Confirmations sent for each
- state.json updated with processed message IDs

## Test Case 8: Status Command

**Arrange:**
- Project 001 is active

**Act:**
- Send `/status`

**Assert:**
- Bot responds "📂 Current project: My Test Project (ID: 001)"

## Manual Testing Checklist:

- [ ] Bot responds to /start with welcome message
- [ ] Can create multiple projects with /new
- [ ] Projects list shows all created projects
- [ ] Can switch between projects with /pick
- [ ] Voice messages are transcribed accurately
- [ ] Timestamps are correct in notes.md
- [ ] Audio files are deleted after processing
- [ ] State persists after bot restart
- [ ] Queued messages process on startup
- [ ] Error messages are clear and helpful
# Test: Cleanup Service

## Test Case 1: Old Audio File Cleanup

**Arrange:**
- Create test audio files with different ages in audio/ directory
- Set some files to be 8+ days old (older than retention)
- Set some files to be recent (within 7 days)

**Act:**
- Run cleanup_old_audio_files()

**Assert:**
- Files older than 7 days are deleted
- Files within 7 days are kept
- Deleted count matches expected number
- Log shows deleted file names

## Test Case 2: Log Rotation

**Arrange:**
- Create a log file with 1500 lines
- Set max_log_lines to 1000

**Act:**
- Run rotate_log_file("bot.log")

**Assert:**
- Log file now contains exactly 1000 lines
- The 1000 lines are the most recent ones
- Returns True indicating rotation occurred
- Log message confirms rotation

## Test Case 3: Startup Cleanup

**Arrange:**
- Bot has old audio files and large log files
- Bot is restarted

**Act:**
- Bot startup routine runs

**Assert:**
- Cleanup runs before processing messages
- Old audio files are removed
- Large logs are rotated
- Bot continues normal operation

## Test Case 4: No Cleanup Needed

**Arrange:**
- All audio files are recent
- Log file has < 1000 lines

**Act:**
- Run cleanup service

**Assert:**
- No files deleted
- No log rotation occurs
- Service completes without errors

## Manual Test Commands

```bash
# Create old test audio file
touch -t 202501010000 audio/test_old.ogg

# Check audio directory
ls -la audio/

# Check log size
wc -l logs/bot.log

# Restart bot to trigger cleanup
# Then check if old files were removed
```

## Implementation Details

- **Audio retention**: 7 days (configurable)
- **Log max lines**: 1000 lines (configurable)
- **Cleanup timing**: Runs on every bot startup
- **Files cleaned**: 
  - Audio files (*.ogg) in audio/
  - Log files: bot.log, launchd.out.log, launchd.err.log
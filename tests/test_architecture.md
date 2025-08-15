# Test Plan for Clean Architecture

## Test 1: Command Registration

**Arrange:**
- Create a bot instance
- Create a custom command class

**Act:**
- Register the command with `bot.register_command(CustomCommand)`

**Assert:**
- Command appears in registry
- Command handlers are created
- Command shows in menu if `show_in_menu=True`

## Test 2: Service Injection

**Arrange:**
- Create ServiceContainer with test config
- Create a command class

**Act:**
- Initialize command with services
- Access services within command

**Assert:**
- All services are accessible
- Services are properly initialized
- No direct dependencies in commands

## Test 3: Adding New Command Without Modification

**Arrange:**
- Running bot with existing commands
- Create new command class implementing Command interface

**Act:**
- Add new command to main.py registration
- Run bot

**Assert:**
- New command works
- No changes needed in bot.py, registry.py, or other commands
- Demonstrates Open/Closed Principle

## Test 4: State Service Isolation

**Arrange:**
- Create StateService with test file

**Act:**
- Add project
- Set active project
- Mark message processed

**Assert:**
- State persists to file
- State loads correctly on restart
- No coupling with other services

## Test 5: Project Service Independence

**Arrange:**
- Create ProjectService with test directory

**Act:**
- Create project
- Add notes
- Get statistics
- Delete project

**Assert:**
- Files created in correct structure
- Statistics calculated correctly
- Deletion removes files
- Service works independently

## Test 6: Command Callback Routing

**Arrange:**
- Register ProjectsCommand (handles callbacks)
- Simulate button press

**Act:**
- Send callback with "pick_001"
- Send callback with "del_001"

**Assert:**
- Correct command handles callback
- State updated appropriately
- Response sent to user

## Test 7: Queue Processing

**Arrange:**
- Bot offline
- Messages sent to Telegram

**Act:**
- Start bot
- Process queued messages

**Assert:**
- All messages processed in order
- State updated with last_update_id
- Voice messages transcribed

## Test 8: Pluggable Architecture

**Arrange:**
- Create custom command extending Command
- Custom command with unique functionality

**Act:**
- Register only this command (remove others)
- Run bot

**Assert:**
- Bot works with just this command
- Demonstrates true pluggability
- No dependencies on other commands
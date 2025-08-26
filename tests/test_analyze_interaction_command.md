# Test Scenarios for /analyze-interaction Slash Command

## Test Case 1: File Creation Instead of Edit
### Arrange
- User asks agent to update existing file
- Agent creates new file with suffix (_v2, _new, _improved, etc.) instead of editing original
- Conversation log available at path

### Act
Run: `/analyze-interaction conversation_log.json`

### Assert
Command should identify:
- Pattern: Creating duplicate files with suffixes
- Root cause: Missing explicit rule against file versioning
- Suggestion: Add rule "NEVER create file versions, ALWAYS edit original files"
- Generic application: Applies to any file type (.py, .js, .tsx, .md, etc.)

## Test Case 2: Not Following User Intent
### Arrange
- User asks for specific type of improvement (e.g., "real tests", "simpler code", "remove abstraction")
- Agent makes partial changes but keeps unwanted patterns
- Description provided as text

### Act
Run: `/analyze-interaction Agent made partial changes but kept unwanted patterns`

### Assert
Command should identify:
- Pattern: Not fully implementing requested changes
- Root cause: Ambiguous instructions about complete replacement
- Suggestion: "When asked to replace/remove, do so COMPLETELY"
- Generic application: Testing, refactoring, simplification tasks

## Test Case 3: Over-engineering Simple Task
### Arrange
- User asks to add logging
- Agent creates 3 abstraction layers and factory pattern
- Conversation file provided

### Act
Run: `/analyze-interaction overengineered_logging.json`

### Assert
Command should identify:
- Pattern: Unnecessary complexity
- Root cause: No simplicity directive
- Suggestion: Add "KISS principle - Keep implementations simple"

## Test Case 4: Ignoring Existing Patterns
### Arrange
- Codebase has established patterns (imports, naming, structure)
- Agent uses different patterns
- Both file and context provided

### Act
Run: `/analyze-interaction patterns.log following existing conventions is critical`

### Assert
Command should identify:
- Pattern: Not following established conventions
- Root cause: Didn't analyze existing code first
- Suggestion: "ALWAYS examine neighboring files for patterns"
- Generic application: Any codebase with established conventions

## Test Case 5: Context Blindness
### Arrange
- Agent doesn't read related files
- Makes assumptions instead of checking
- Log shows missed opportunities

### Act
Run: `/analyze-interaction missed_context.json`

### Assert
Command should identify:
- Pattern: Making assumptions without verification
- Root cause: Not using Read tool proactively
- Suggestion: "Read related files BEFORE making changes"
- Should ask: "Is this pattern specific to your project or a general issue?"
- Generic application: Any task requiring context awareness
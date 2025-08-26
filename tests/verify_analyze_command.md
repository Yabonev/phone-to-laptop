# How to Test /analyze-interaction Command

## Testing Strategy (Per R002)

### 1. How Claude Can Test (Automated)
Cannot directly invoke slash commands from tools, but can verify:
- Command file exists at ~/.claude/commands/analyze-interaction.md
- Frontmatter is properly formatted YAML
- Command will be recognized by Claude Code

### 2. How Human Can Test (Manual)

#### Test Case 1: File Duplication Pattern
```bash
# In Claude Code session:
/analyze-interaction tests/sample_bad_interaction.txt
```

**Expected Output Should Include:**

⚠️ **Specificity Check**: The example appears to involve test files. Should this solution be generic or specific to testing?

🔍 **What Went Wrong**: Agent created new file with suffix instead of updating existing file

🎯 **Why It Happened**: 
- Primary: No explicit rule against creating file versions
- Contributing: Ambiguous instruction about "improving" vs "updating"

🛠️ **How to Fix It**:
```xml
<rule id="R###" importance="critical">
NEVER create file versions with suffixes (_new, _v2, _improved, _real, etc.)
YOU MUST edit original files directly
Examples: test.py not test_v2.py, index.js not index_new.js, config.yaml not config_updated.yaml
</rule>
```

**Better Prompt Examples (Generic)**:
```
❌ AVOID: "Improve the [files]"
✅ BETTER: "Update [specific_file] to [specific_change]"

Domain Examples:
- Web: "Update components/Button.tsx to use new design system"
- API: "Update routes/auth.py to add rate limiting"
- Tests: "Update test_module.py to replace mocks with real calls"
```

#### Test Case 2: Description Only
```bash
/analyze-interaction Agent kept creating new files even after I said to edit existing ones
```

**Expected Output Should Include:**
- Recognition that this is a generic file management issue
- Request for clarification: "What types of files? In what context?"
- Generic rule that applies to all file types
- Multiple examples from different domains

#### Test Case 3: Real Conversation Log
```bash
# If you have an actual .jsonl conversation file:
/analyze-interaction ~/.claude/projects/[project]/[session].jsonl
```

## Verification Checklist
- [ ] Command appears in `/help` list showing "(user)"
- [ ] Accepts file paths (.txt, .log, .json, .jsonl)
- [ ] Accepts text descriptions
- [ ] Identifies specific anti-patterns (file duplication, mock overuse, etc.)
- [ ] Provides CLAUDE.md rule in proper XML format
- [ ] Shows before/after prompt examples with ❌ and ✅
- [ ] Suggests subagent configuration if applicable
- [ ] Includes actionable implementation checklist
- [ ] References Claude Code documentation patterns

## Success Criteria
The command successfully helps when it:
1. Detects when examples might be too project-specific
2. Asks for clarification when patterns seem narrow
3. Correctly identifies the root cause (not just symptoms)
4. Provides generic rules that work across project types
5. Shows how the pattern applies in multiple domains
6. Gives prompt templates with placeholders, not just specific examples
7. Suggests configuration changes that enforce better behavior
8. Teaches principles that apply broadly, not just to one case
# 🚀 CI/CD Setup for AI-Safe Development

This guide helps you set up guardrails so AI can safely contribute via PRs.

## Quick Start

### 1. Install Pre-commit Hooks (Local Safety)
```bash
# Install pre-commit hooks to catch issues before pushing
pre-commit install

# Test the hooks manually
pre-commit run --all-files
```

### 2. Test CI Locally
```bash
# Run the same checks CI will run
uv run ruff format --check .    # Check formatting
uv run ruff check .              # Lint code
uv run pytest                    # Run tests
```

### 3. Fix Issues Automatically
```bash
# Auto-fix formatting
uv run ruff format .

# Auto-fix some lint issues
uv run ruff check . --fix
```

## GitHub Setup (One-Time)

### Enable Branch Protection

1. Go to: Settings → Branches → Add rule
2. Branch pattern: `main`
3. Enable these protections:
   - ✅ **Require a pull request before merging**
   - ✅ **Require status checks to pass**
   - ✅ **Require branches to be up to date**
   
4. Select these required status checks:
   - `validate` - Quick validation
   - `test (3.11)` - Tests pass
   - `security` - Security scan

### What This Gives You

- ❌ **Cannot push directly to main** (must use PRs)
- ✅ **Automatic validation** on every PR
- 🛡️ **Protection from broken code** merging to main
- 🤖 **AI-safe development** - AI creates PRs, CI validates

## AI Workflow

When AI wants to make changes:

```bash
# 1. Create feature branch
git checkout -b feature/ai-improvement

# 2. Make changes
# ... AI modifies files ...

# 3. Run pre-commit checks
pre-commit run --all-files

# 4. Commit and push
git add .
git commit -m "AI: Add new feature"
git push -u origin feature/ai-improvement

# 5. Create PR
gh pr create --title "AI: Add new feature" --body "AI-generated improvement"

# 6. CI runs automatically!
# If green ✅ → Can merge
# If red ❌ → AI must fix
```

## What the CI Checks

### 1. Quick Validation (fails fast)
- **Formatting** - Code style is consistent
- **Linting** - No obvious errors
- **Secrets** - No hardcoded tokens
- **Structure** - Bot files are correct

### 2. Tests
- **Unit tests** - Core functionality works
- **Coverage** - At least 60% code tested
- **Type checking** - Types are correct (warning only)

### 3. Security
- **Bandit** - No security vulnerabilities
- **Dependencies** - No known vulnerabilities

## Monitoring PR Status

Check PR status on GitHub or via CLI:
```bash
# See PR checks status
gh pr checks

# View PR in browser
gh pr view --web
```

## Troubleshooting

### "CI Failed" - What to do?

1. Check which job failed in GitHub Actions
2. Run that specific check locally:
   ```bash
   # If formatting failed
   uv run ruff format .
   
   # If tests failed
   uv run pytest -v
   
   # If validation failed
   uv run python scripts/validate_bot.py
   ```
3. Fix the issue and push again

### Common AI Mistakes CI Will Catch

- ❌ Hardcoded secrets/tokens
- ❌ Breaking existing tests
- ❌ Import errors
- ❌ Missing required files
- ❌ Bad code formatting
- ❌ Security vulnerabilities

## Summary

With this setup:
1. **AI creates PRs** instead of pushing to main
2. **CI automatically validates** every PR
3. **Only good code** can be merged
4. **You stay in control** of what gets merged

This gives you confidence that AI changes won't break your bot!
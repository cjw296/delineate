This file provides guidance to LLM tools such as [aider](https://aider.chat/)
and [Claude Code](claude.ai/code) when working with code in this repository.

## Commands
- Build: `uv sync`
- Run tests: `uv run pytest`
- Run single test: `uv run pytest tests/test_file.py::TestClass::test_method -v`
- Run with coverage: `uv run pytest --cov`
- Coverage report: `uv run coverage report --show-missing --skip-covered --fail-under 100`
- Type check: `uv run mypy src tests`
- Lint: Don't run any linters.
- Format: `ruff format .`

## Important: Always Format Code
**ALWAYS run `ruff format .` after making any code changes.** This ensures consistent code formatting across the entire codebase. Do not commit code without formatting it first.

## Code Style
- Python 3.13+ with strict type annotations
- Line length: 100 characters
- Imports: standard library first, then third-party, then local, clean up unused imports
- Naming: snake_case for functions/variables, CamelCase for classes
- Custom exceptions inherit from standard exceptions
- Comprehensive error handling with context
- Testing: pytest with fixtures
- Testing: Maintain 100% test coverage for all code
- Docstrings with clear parameter descriptions
- Automated formatting with ruff

## Git commits
- Keep commit messages succinct, do not use any emojis
- Do not add prefixes such as "feat:", "chore:", "test:", "fix:", etc.
- Capitalize the first letter of any commit message

## Issue Tracking with bd

This project uses `bd` (beads) for issue tracking. **Always use bd instead of in-memory task tools.**

**Core workflow:**
- `bd ready` - See what issues are ready to work on (no blocking deps)
- `bd list` - List all issues
- `bd show <id>` - Show issue details
- `bd create "Title"` - Create new issue
- `bd update <id> --status in_progress` - Mark as in progress
- `bd close <id>` - Close completed issue

**When starting work:**
1. Run `bd ready` to see available work
2. Pick an issue and run `bd update <id> --status in_progress`

**When discovering new work:**
- Create issues for anything that needs follow-up: `bd create "Fix the thing"`
- Add dependencies if needed: `bd dep add <blocked> <blocker>`

**When finishing work:**
- Close completed issues: `bd close <id>`
- Create issues for any remaining TODOs

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

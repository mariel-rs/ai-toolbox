# Commit Command

Generate AI-powered commit messages following the Conventional Commits specification.

## Usage

```bash
ai-toolbox commit
```

## How It Works

1. **Retrieves staged changes**: Runs `git diff --staged` to get your changes
2. **Generates commit message**: Sends the diff to an LLM with instructions to follow Conventional Commits
3. **Interactive review**: Presents the message with options to approve, edit, or reject
4. **Commits on approval**: Executes `git commit` with the approved message

## Interactive Options

After generating a commit message, you'll see:

```
==================================================
Generated commit message:
==================================================
feat(auth): add password reset functionality
==================================================

[A]pprove  [E]dit  [R]eject
```

- **[A]pprove**: Accept the message and create the commit
- **[E]dit**: Provide feedback to regenerate the message
- **[R]eject**: Abort without committing

## Conventional Commits Format

The generated messages follow this structure:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Formatting, white-space, etc. (no code change) |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `build` | Changes to build system or dependencies |
| `ci` | Changes to CI configuration |
| `chore` | Other changes that don't modify src or test files |

### Examples

Simple feature:
```
feat(api): add user authentication endpoint
```

Bug fix with body:
```
fix(parser): handle empty input gracefully

The parser was throwing an exception when receiving empty strings.
This change adds null checking to prevent runtime errors.

Fixes #123
```

Breaking change:
```
refactor(config)!: migrate to YAML configuration

BREAKING CHANGE: configuration files must be converted from JSON to YAML
```

## CLI Options

### Model Selection

Use a different LLM model:

```bash
ai-toolbox -m anthropic/claude-3-sonnet commit
ai-toolbox -m openai/gpt-4 commit
```

Default model: `openai/gpt-4o-mini`

### Verbose Logging

Enable debug output:

```bash
ai-toolbox -v commit
```

## Requirements

- Git must be installed and available in PATH
- You must be in a git repository
- Changes must be staged (`git add`)
- Valid API key for your chosen LLM provider

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "No staged changes found" | Nothing staged | Run `git add` first |
| "Authentication failed" | Invalid API key | Check your API key environment variable |
| "Git is not installed" | Git not found | Install git and ensure it's in PATH |
| "Not a git repository" | Not in a repo | Navigate to a git repository |

# Claude Code Instructions

## Commit Message Format

This project uses **Conventional Commits** via [commitizen](https://commitizen-tools.github.io/commitizen/).

### Format

```
type(scope)?: description

[optional body]

[optional footer(s)]
```

### Types and Version Bumps

| Type | Description | Version Bump |
|------|-------------|--------------|
| `feat` | A new feature | MINOR |
| `fix` | A bug fix | PATCH |
| `docs` | Documentation only | - |
| `style` | Code style (formatting) | - |
| `refactor` | Neither fix nor feature | - |
| `perf` | Performance improvement | PATCH |
| `test` | Adding/correcting tests | - |
| `build` | Build system changes | - |
| `ci` | CI configuration | - |
| `chore` | Maintenance tasks | - |
| `revert` | Reverts a commit | - |

### Breaking Changes

Add `!` after type/scope or `BREAKING CHANGE:` in footer → MAJOR bump:
```
feat!: remove deprecated API
feat(api)!: change auth method

feat: new feature

BREAKING CHANGE: description of breaking change
```

### Examples

```
feat: add user login
fix(auth): resolve token bug
docs: update API docs
feat!: redesign API (breaking)
```

### Version Bumping

Commitizen automatically determines version bumps from commit history:

```bash
cz bump          # bump version based on commits
cz bump --dry-run  # preview what would happen
```

### Co-Authored-By

Include when creating commits:
```
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Commands

```bash
cz commit        # interactive commit (optional)
cz check         # validate last commit
cz bump          # bump version + changelog
cz changelog     # generate changelog only
```

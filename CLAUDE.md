# Claude Code Instructions

## Commit Message Format

This project uses **Conventional Commits** (https://www.conventionalcommits.org/) and **Semantic Versioning** (https://semver.org/).

### Commit Message Structure

```
type(scope)?: description

[optional body]

[optional footer(s)]
```

### Types

| Type | Description | Version Bump |
|------|-------------|--------------|
| `feat` | A new feature | MINOR |
| `fix` | A bug fix | PATCH |
| `docs` | Documentation only changes | - |
| `style` | Code style (formatting, semicolons, etc) | - |
| `refactor` | Code change that neither fixes a bug nor adds a feature | - |
| `perf` | Performance improvement | PATCH |
| `test` | Adding or correcting tests | - |
| `build` | Build system or external dependencies | - |
| `ci` | CI configuration changes | - |
| `chore` | Other changes (don't modify src or test) | - |
| `revert` | Reverts a previous commit | - |

### Breaking Changes

Add `!` after type/scope for breaking changes (MAJOR version bump):
```
feat!: remove deprecated API endpoints
feat(api)!: change authentication method
```

### Examples

```
feat: add user login functionality
fix(auth): resolve token expiration bug
docs: update API documentation
refactor(core): simplify request handling
feat!: redesign user API (breaking change)
```

### Rules

1. Use lowercase for type and description
2. No period at the end of the description
3. Use imperative mood ("add" not "added" or "adds")
4. Keep first line under 72 characters
5. Separate subject from body with blank line (if body present)

### Co-Authored-By

When creating commits, include the co-author footer:
```
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Versioning

This project follows Semantic Versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes (`feat!`, `fix!`, etc.)
- **MINOR**: New features (`feat`)
- **PATCH**: Bug fixes (`fix`, `perf`)

## Git Hooks

A `commit-msg` hook validates all commit messages. To enable hooks after cloning:

```bash
git config core.hooksPath .githooks
```

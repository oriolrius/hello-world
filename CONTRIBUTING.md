# Contributing

## Setup

```bash
git clone https://github.com/oriolrius/hello-world.git
cd hello-world
git config core.hooksPath .githooks
uv sync
```

## Commit Messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
type(scope)?: description
```

### Types

- `feat` - New feature (bumps MINOR version)
- `fix` - Bug fix (bumps PATCH version)
- `docs` - Documentation changes
- `style` - Code style changes
- `refactor` - Code refactoring
- `perf` - Performance improvements
- `test` - Test changes
- `build` - Build system changes
- `ci` - CI configuration
- `chore` - Maintenance tasks

### Examples

```bash
git commit -m "feat: add health check endpoint"
git commit -m "fix(server): handle empty request body"
git commit -m "docs: add API examples to README"
```

### Breaking Changes

Use `!` after type for breaking changes:

```bash
git commit -m "feat!: change default port to 8080"
```

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- `feat` → MINOR (1.0.0 → 1.1.0)
- `fix` → PATCH (1.0.0 → 1.0.1)
- `!` (breaking) → MAJOR (1.0.0 → 2.0.0)

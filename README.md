# hello-world

Simple web server that returns `hello-world`.

## Installation

```bash
uv sync
```

## Usage

### Development mode

```bash
uv run hello-world
```

### From virtual environment

```bash
.venv/bin/hello-world
```

### With uvx (no install)

```bash
uvx --from git+https://github.com/oriolrius/hello-world hello-world
```

### From wheel

```bash
uv build
uvx --from ./dist/hello_world-*.whl hello-world
```

## Development

```bash
uv run ruff check src/ tests/   # lint
uv run ruff format src/ tests/  # format
uv run pytest -v                # test
uv build                        # build .tar.gz and .whl
```

## Parameters

| Flag | Description | Default |
|------|-------------|---------|
| `-b, --bind` | Bind address | `0.0.0.0` |
| `-p, --port` | Port number | `49000` |

## Examples

```bash
hello-world                        # http://0.0.0.0:49000
hello-world -p 8080                # http://0.0.0.0:8080
hello-world -b 127.0.0.1 -p 3000   # http://127.0.0.1:3000
```

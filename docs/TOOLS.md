# S3 development toolchain & commit guardrail (APP-04)

S3 ships a **pinned** dev toolchain and a local commit-message guardrail so
message quality is deterministic *before* server-side branch protection exists.
You still author your own feature/test and CI workflow — these files do not.

## What's provided

- `ruff`, `pytest` and `commitizen` locked as dev dependencies in
  `pyproject.toml` + `uv.lock` (no global installs, no `requirements.txt`).
- `.githooks/commit-msg` — validates each message with the **locked** Commitizen.
- `[tool.commitizen]` config with the course Conventional Commit contract.

## Activate after clone

The hook lives in the repo but Git only runs it once you point at it:

```bash
git config core.hooksPath .githooks
```

## Use it

```bash
uv sync --locked            # recreate the exact toolchain in a clean environment
git commit -m "feat: add X" # the message is checked by uv run cz check
```

Accepted: the conventional types (`feat`, `fix`, `docs`, `style`, `refactor`,
`test`, `build`, `ci`, `chore`, `perf`, …) as `type(scope): subject`, plus
generated merge/revert/bump prefixes. Rejected: anything non-conventional
(`"WIP"`, `"update stuff"`).

## Bypass (single commit)

```bash
git commit --no-verify -m "…"   # skips the LOCAL hook only
```

## Why the server-side check is still required

The local hook is **advisory** — it only runs on machines that enabled
`core.hooksPath`, and `--no-verify` skips it. It cannot gate what lands on a
protected branch. The student-authored CI workflow therefore runs an
**independent** server-side Conventional Commit check over the push's event
range; that server check, not this hook, is what branch protection enforces.

# S1 instructor fixture (APP-01)

This is the **starter** students template from. It is intentionally minimal.

## Present (the S1 scaffold)

- `hello.py` — prints `hello, world`; run via `uv run python hello.py`.
- `pyproject.toml` — uv-managed, no third-party deps.
- `.github/workflows/hello.yml` — runs on push: checkout → setup uv → run hello.py.
- `README.md` — lab + homework (one deliberately marked typo `frist`→`first`) + evidence rules.
- `ABOUT.md` — placeholders only.
- `JOURNAL.md` — signed AI-use contract header + the four-line entry format.
- `evidence/` — target for `s01-actions-green.png`.

## Deliberately ABSENT in S1 (recorded intended absence — AC#5)

- **No** student quality/release workflow (`ci.yml`, release pipeline) — written in S3+.
- **No** solution greeting test / `greet(name)` solution — that is a later exercise.
- **No** cloud credentials, secrets, Dockerfile, compose, k8s or app package.

## Lab / homework / evidence rules (same as README + JOURNAL — AC#6)

- Create a **private** repo from this template; add the professor as collaborator; submit the URL.
- Edit in the **browser** (github.dev); make **≥3 Conventional Commits**.
- Homework: fix the marked README typo `frist`→`first` with a `fix:` commit.
- Upload the green Actions screenshot to `evidence/s01-actions-green.png`.
- No terminal, no AWS in S1.

# S5 — versioned releases with Commitizen (APP-08)

Releases are derived from your Conventional Commits, so a meaningful version tag
and a visible change ship together. The config is in `pyproject.toml`
(`[tool.commitizen]`): `cz_conventional_commits`, PEP 621 versioning, and the
`v$version` tag format bound to `pyproject.toml:^version`.

## Cut a release

```bash
uv run cz bump --dry-run     # preview the next version from the commits
uv run cz bump --yes         # bump pyproject version, make the bump commit, create v<version>
git push origin main --follow-tags   # push main AND the release tag(s) to your origin
```

## What the version increment means

| Commits since the last tag | Increment | Example |
|---|---|---|
| a `feat:` change | **MINOR** | `1.0.0 → 1.1.0` |
| only `fix:` changes | **PATCH** | `1.1.0 → 1.1.1` |
| a breaking change (`feat!:` / `BREAKING CHANGE`) | MAJOR | `1.1.1 → 2.0.0` |

The bump commit, the `[project].version` in `pyproject.toml`, and the immutable
`v*` tag all point at the **same** released source. The release is owner-driven
and possible right after S3.

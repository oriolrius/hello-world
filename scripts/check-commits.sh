#!/usr/bin/env bash
# APP-05 — validate EXACTLY the commits a CI event introduced, with the locked
# Commitizen. A bypassed local commit-msg hook (`--no-verify`) must not slip a
# bad message past this required quality job. Requires FULL git history in CI
# (actions/checkout with fetch-depth: 0).
#
# Event inputs (wired from the workflow):
#   GITHUB_EVENT_NAME = pull_request | push
#   pull_request:  PR_BASE_SHA, PR_HEAD_SHA        (base..head)
#   push:          PUSH_BEFORE,  PUSH_AFTER         (before..after)
#                  PUSH_BEFORE all-zeros => new branch / zero base
# Optional:
#   EXCLUDE_REF (default: origin/main) — unrelated template/default-branch
#     history that a zero-base push must NOT be blamed for.
set -euo pipefail
ZERO=0000000000000000000000000000000000000000
EXCLUDE_REF="${EXCLUDE_REF:-origin/main}"

die() { echo "check-commits: $*" >&2; exit 2; }

range_args() {
  case "${GITHUB_EVENT_NAME:-}" in
    pull_request | pull_request_target)
      [ -n "${PR_BASE_SHA:-}" ] && [ -n "${PR_HEAD_SHA:-}" ] || die "pull_request needs PR_BASE_SHA and PR_HEAD_SHA"
      git cat-file -e "${PR_BASE_SHA}^{commit}" 2>/dev/null || die "base ${PR_BASE_SHA} not found — CI needs full history (fetch-depth: 0)"
      git cat-file -e "${PR_HEAD_SHA}^{commit}" 2>/dev/null || die "head ${PR_HEAD_SHA} not found"
      printf '%s..%s' "$PR_BASE_SHA" "$PR_HEAD_SHA" ;;
    push)
      [ -n "${PUSH_AFTER:-}" ] || die "push needs PUSH_AFTER"
      git cat-file -e "${PUSH_AFTER}^{commit}" 2>/dev/null || die "after ${PUSH_AFTER} not found — CI needs full history (fetch-depth: 0)"
      if [ "${PUSH_BEFORE:-$ZERO}" = "$ZERO" ]; then
        # New branch: check the introduced commits only, excluding unrelated
        # template/default-branch history (so a --allow-unrelated-histories
        # import does not fail the student's first push).
        if git rev-parse --verify -q "${EXCLUDE_REF}^{commit}" >/dev/null; then
          printf '%s --not %s' "$PUSH_AFTER" "$EXCLUDE_REF"
        else
          printf '%s' "$PUSH_AFTER"
        fi
      else
        git cat-file -e "${PUSH_BEFORE}^{commit}" 2>/dev/null || die "before ${PUSH_BEFORE} not found — CI needs full history (fetch-depth: 0)"
        printf '%s..%s' "$PUSH_BEFORE" "$PUSH_AFTER"
      fi ;;
    *) die "unsupported or missing GITHUB_EVENT_NAME='${GITHUB_EVENT_NAME:-}'" ;;
  esac
}

main() {
  local args commits
  args="$(range_args)"
  # args may be "A..B" or "SHA --not REF"; word-splitting is intended here.
  # shellcheck disable=SC2086
  commits="$(git rev-list --no-merges $args)"
  if [ -z "$commits" ]; then
    echo "check-commits: no non-merge commits in range (${args}) — nothing to check"
    exit 0
  fi
  echo "check-commits: validating $(printf '%s\n' "$commits" | grep -c .) commit(s) in range: ${args}"
  local rc=0 c
  while IFS= read -r c; do
    [ -z "$c" ] && continue
    if uv run cz check --message "$(git log -1 --format=%B "$c")" >/dev/null 2>&1; then
      echo "  OK   ${c:0:9} $(git log -1 --format=%s "$c")"
    else
      echo "  FAIL ${c:0:9} $(git log -1 --format=%s "$c")"
      rc=1
    fi
  done <<< "$commits"
  [ "$rc" = 0 ] && echo "check-commits: PASS" || echo "check-commits: FAIL"
  exit "$rc"
}

main "$@"

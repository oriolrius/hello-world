#!/usr/bin/env python3
"""S1 hello-world bootstrap — the first-session artifact.

Run it with `uv run python hello.py`. In S1 you create this repository entirely
through the browser (GitHub template + github.dev), commit with Conventional
Commits, and prove the Actions workflow is green — before any VM or terminal.
Later sessions grow this into the full HTTP app; S1 ships no later solution.
"""


def main() -> None:
    print("hello, world")


if __name__ == "__main__":
    main()

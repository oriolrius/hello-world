#!/usr/bin/env python3
"""Retained S1 bootstrap.

The first-session artifact. The S2 HTTP application lives in the
``hello_world/`` package (run with ``uv run hello-world``); this minimal script
is kept so the S1 history and the later student ``greet(name)`` exercise still
have their starting point. The initial S2 increment does NOT ship that solution.
"""


def main() -> None:
    print("hello, world")


if __name__ == "__main__":
    main()

"""`uv run hello-world` entry point: load settings, bind and serve."""
from __future__ import annotations

from hello_world.app import make_server
from hello_world.config import load_settings


def main() -> None:
    s = load_settings()
    httpd = make_server(str(s["host"]), int(s["port"]), str(s["greeting"]))
    host, port = httpd.server_address[0], httpd.server_address[1]
    print(f"hello-world serving on http://{host}:{port}/  (greeting={s['greeting']!r})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped (no supervisor — the process does not survive Ctrl-C)")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()

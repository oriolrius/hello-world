import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"hello-world")


def main():
    parser = argparse.ArgumentParser(description="Simple hello-world web server")
    parser.add_argument("-b", "--bind", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("-p", "--port", type=int, default=49000, help="Port (default: 49000)")
    args = parser.parse_args()

    server = HTTPServer((args.bind, args.port), Handler)
    print(f"Server running on http://{args.bind}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

import argparse
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        hostname = socket.gethostname()
        self.wfile.write(f"hello-world from {hostname}\n".encode())


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

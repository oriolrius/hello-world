from http.server import HTTPServer, BaseHTTPRequestHandler


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"hello-world")


def main():
    server = HTTPServer(("127.0.0.1", 9000), Handler)
    print("Server running on http://127.0.0.1:9000")
    server.serve_forever()


if __name__ == "__main__":
    main()

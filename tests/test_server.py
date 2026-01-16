import threading
import urllib.request

from hello_world import Handler, HTTPServer


def test_hello_world_response():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]

    thread = threading.Thread(target=server.handle_request)
    thread.start()

    response = urllib.request.urlopen(f"http://127.0.0.1:{port}/")
    body = response.read().decode()
    assert body.startswith("hello-world from ")
    assert response.status == 200

    thread.join()
    server.server_close()

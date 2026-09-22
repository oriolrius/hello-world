"""DBAI course hello-world HTTP application.

The app realizes one fixed HTTP contract that every later session reuses
(containers in S4, Kubernetes probes in S8+, monitoring in S10):

    GET  /        -> 200 JSON {"message": <greeting>, "hostname": <server host>}
    GET  /health  -> 200 JSON {"status": "ok"}
    GET  /boom    -> 500 JSON (deliberate failure endpoint for drills)
    <other path>  -> 404 JSON
    POST /        -> 405 JSON (only GET is served)

Host, port and greeting come from config/settings.yaml.
"""

__version__ = "1.0.0"

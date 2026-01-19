#!/usr/bin/env python3
"""
Generate Kubernetes architecture diagram for the hello-world application.
Produces PNG, SVG, and DOT files.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.k8s.compute import Deployment, Pod, ReplicaSet
from diagrams.k8s.network import Service
from diagrams.k8s.group import Namespace
from diagrams.onprem.client import Users
from diagrams.onprem.container import Docker

graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
}

with Diagram(
    "Hello World - Kubernetes Architecture",
    filename="../k8s/docs/k8s-architecture",
    show=False,
    direction="LR",
    outformat=["png", "dot"],
    graph_attr=graph_attr,
):
    users = Users("Users\n(HTTP :80)")
    registry = Docker("ghcr.io\noriolrius/hello-world")

    with Cluster("Kubernetes Cluster"):

        with Cluster("Namespace: hello-world"):

            svc = Service("Service\nhello-world\n(LoadBalancer)")

            with Cluster("Deployment: hello-world\n(replicas: 2)"):

                with Cluster("ReplicaSet"):
                    pod1 = Pod("Pod 1\n:49000")
                    pod2 = Pod("Pod 2\n:49000")

    # Traffic flow (green)
    users >> Edge(color="green", style="bold", label="HTTP") >> svc
    svc >> Edge(color="green", label=":80→:49000") >> pod1
    svc >> Edge(color="green") >> pod2

    # Image pull (orange dashed)
    registry >> Edge(color="orange", style="dashed", label="pull image") >> pod1
    registry >> Edge(color="orange", style="dashed") >> pod2

print("Generated: ../k8s/docs/k8s-architecture.png and ../k8s/docs/k8s-architecture.dot")

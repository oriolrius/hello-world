#!/usr/bin/env python3
"""
Generate architecture overview diagram for README.md.
v6.x - EKS + Kubernetes deployment.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EKS
from diagrams.aws.network import ELB
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.container import Docker
from diagrams.onprem.registry import Harbor
from diagrams.k8s.compute import Pod
from diagrams.k8s.network import Service

OUTPUT_PATH = "../assets/diagrams/architecture"

graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.8",
    "splines": "ortho",
    "nodesep": "0.6",
    "ranksep": "0.8",
}

with Diagram(
    "Architecture Overview (v6.x)",
    filename=OUTPUT_PATH,
    show=False,
    direction="TB",
    outformat=["png", "dot"],
    graph_attr=graph_attr,
):
    with Cluster("GitHub Actions (CI/CD)"):
        lint = GithubActions("lint & test")
        docker = Docker("build image")
        registry = Harbor("ghcr.io")
        deploy = GithubActions("deploy to EKS")

        lint >> Edge(color="#666666") >> docker >> Edge(color="#666666") >> registry
        registry >> Edge(color="#666666") >> deploy

    with Cluster("EKS Cluster: esade-teaching\neu-west-1"):
        with Cluster("Namespace: hello-world"):
            pod1 = Pod("Pod")
            pod2 = Pod("Pod")
            svc = Service("Service")
            elb = ELB("LoadBalancer\n(AWS ELB)")

            [pod1, pod2] >> svc >> elb

    deploy >> Edge(color="#48BB78", style="bold", label="kubectl apply") >> svc
    registry >> Edge(color="#48BB78", style="dashed", label="pull image") >> pod1

print(f"Generated: {OUTPUT_PATH}.png")
print(f"Generated: {OUTPUT_PATH}.dot")

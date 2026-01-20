#!/usr/bin/env python3
"""
Generate deployment diagram for deploy/docs/
v5.x - Ansible playbook deployment flow.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.iac import Ansible
from diagrams.onprem.container import Docker
from diagrams.aws.compute import EC2
from diagrams.onprem.registry import Harbor
from diagrams.generic.os import Ubuntu

OUTPUT_PATH = "../deploy/docs/deploy-architecture"

graph_attr = {
    "fontsize": "12",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.5",
    "ranksep": "0.6",
}

with Diagram(
    "Ansible Deployment Flow (v5.x)",
    filename=OUTPUT_PATH,
    show=False,
    direction="LR",
    outformat=["png", "dot"],
    graph_attr=graph_attr,
):
    ansible = Ansible("Ansible\nplaybook.yml")
    registry = Harbor("ghcr.io\nhello-world")

    with Cluster("EC2 Instance"):
        ubuntu = Ubuntu("Ubuntu 24.04")

        with Cluster("Installed by Ansible"):
            docker = Docker("Docker Engine")

            with Cluster("Docker Compose"):
                container = Docker("hello-world\n:49000")

    ansible >> Edge(color="#48BB78", style="bold", label="1. SSH") >> ubuntu
    ansible >> Edge(color="#4299E1", label="2. Install packages") >> docker
    ansible >> Edge(color="#9F7AEA", label="3. docker compose up") >> container
    registry >> Edge(color="#ED8936", style="dashed", label="pull image") >> container

print(f"Generated: {OUTPUT_PATH}.png")
print(f"Generated: {OUTPUT_PATH}.dot")

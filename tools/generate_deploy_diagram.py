#!/usr/bin/env python3
"""Generate Ansible deployment architecture diagram for v5.0.x.

This script creates a visual representation of the Ansible deployment process
including package installation, Docker setup, and container deployment
via Docker Compose.
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.generic.os import Ubuntu
from diagrams.onprem.container import Docker
from diagrams.onprem.iac import Ansible
from diagrams.programming.language import Python

# Output paths
OUTPUT_DIR = "../deploy/docs"
DIAGRAM_NAME = "deploy-architecture"


def main():
    graph_attr = {
        "splines": "ortho",
        "nodesep": "0.8",
        "ranksep": "1.0",
        "fontsize": "14",
    }

    with Diagram(
        "Ansible Deployment - v5.0.x",
        filename=f"{OUTPUT_DIR}/{DIAGRAM_NAME}",
        outformat=["png", "dot"],
        direction="TB",
        show=False,
        graph_attr=graph_attr,
    ):
        # Control node
        with Cluster("Control Node"):
            ansible = Ansible("Ansible\nPlaybook")

        # Target EC2
        with Cluster("EC2 Instance (Ubuntu 24.04)"):
            with Cluster("1. System Setup"):
                apt = Ubuntu("apt\ninstall packages")

            with Cluster("2. Docker Setup"):
                docker_install = Docker("Docker CE\n+ Compose")

            with Cluster("3. App Deployment"):
                container = Docker("hello-world\ncontainer")

        # Flow
        ansible >> Edge(color="blue", label="SSH") >> apt
        apt >> Edge(color="green") >> docker_install
        docker_install >> Edge(color="green") >> container


if __name__ == "__main__":
    main()

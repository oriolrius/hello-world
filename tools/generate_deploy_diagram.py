#!/usr/bin/env python3
"""Generate Ansible deployment architecture diagram for v4.0.x.

This script creates a visual representation of the Ansible deployment process
including package installation, uv setup, application installation, and
systemd service configuration.
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.generic.os import Ubuntu
from diagrams.onprem.compute import Server
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
        "Ansible Deployment - v4.0.x",
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
                apt = Ubuntu("apt\ninstall curl")

            with Cluster("2. uv Installation"):
                uv = Python("uv\n(astral.sh)")

            with Cluster("3. App Installation"):
                app = Python("hello-world\n(uv tool)")

            with Cluster("4. Service Config"):
                systemd = Server("systemd\nservice")

        # Flow
        ansible >> Edge(color="blue", label="SSH") >> apt
        apt >> Edge(color="green") >> uv
        uv >> Edge(color="green") >> app
        app >> Edge(color="green") >> systemd


if __name__ == "__main__":
    main()

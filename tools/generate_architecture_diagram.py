#!/usr/bin/env python3
"""
Generate architecture overview diagram for README.md.
v5.x - CloudFormation + Ansible + Docker deployment.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.management import Cloudformation
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.iac import Ansible
from diagrams.onprem.container import Docker
from diagrams.onprem.registry import Harbor

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
    "Architecture Overview (v5.x)",
    filename=OUTPUT_PATH,
    show=False,
    direction="TB",
    outformat=["png", "dot"],
    graph_attr=graph_attr,
):
    with Cluster("GitHub Actions"):
        with Cluster("Release Workflow"):
            lint = GithubActions("Lint")
            test = GithubActions("Test")
            build = GithubActions("Build\nwheel")
            docker_build = Docker("Docker\nBuild")
            registry = Harbor("Push to\nghcr.io")

            lint >> Edge(color="#666666") >> test >> Edge(color="#666666") >> build
            build >> Edge(color="#666666") >> docker_build >> Edge(color="#666666") >> registry

        with Cluster("Deploy Workflow"):
            cfn = Cloudformation("CloudFormation")
            ansible = Ansible("Ansible")

            cfn >> Edge(color="#666666") >> ansible

    with Cluster("EC2 Instance"):
        with Cluster("Docker Engine"):
            container = Docker("hello-world\ncontainer\nport 49000")

    registry >> Edge(color="#48BB78", style="dashed", label="pull image") >> container
    ansible >> Edge(color="#48BB78", style="bold", label="SSH + docker compose") >> container

print(f"Generated: {OUTPUT_PATH}.png")
print(f"Generated: {OUTPUT_PATH}.dot")

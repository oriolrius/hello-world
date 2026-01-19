#!/usr/bin/env python3
"""
Generate architecture overview diagram for README.md.
v4.x - CloudFormation + Ansible deployment.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.network import VPC
from diagrams.aws.management import Cloudformation
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.iac import Ansible

OUTPUT_PATH = "../assets/diagrams/architecture"

graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.8",
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.0",
}

with Diagram(
    "Architecture Overview (v4.x)",
    filename=OUTPUT_PATH,
    show=False,
    direction="TB",
    outformat=["png", "dot"],
    graph_attr=graph_attr,
):
    with Cluster("GitHub Actions - Deploy Workflow"):
        cfn = Cloudformation("CloudFormation\n(infra only)")
        get_ip = GithubActions("Get EC2 IP\nfrom Outputs")
        ansible = Ansible("Ansible\nPlaybook")

        cfn >> Edge(color="#666666") >> get_ip >> Edge(color="#666666") >> ansible

    with Cluster("AWS Cloud"):
        with Cluster("VPC (10.0.0.0/16)"):
            with Cluster("Public Subnet"):
                ec2 = EC2("EC2 Instance\n─────────────\nAnsible installs:\n• curl (apt)\n• uv (astral.sh)\n• hello-world\n• systemd service")

    ansible >> Edge(color="#48BB78", style="bold", label="SSH") >> ec2

print(f"Generated: {OUTPUT_PATH}.png")
print(f"Generated: {OUTPUT_PATH}.dot")

#!/usr/bin/env python3
"""
Generate architecture overview diagram for README.md.
v3.x - CloudFormation + EC2 deployment.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.network import VPC, InternetGateway
from diagrams.aws.management import Cloudformation

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
    "Architecture Overview (v3.x)",
    filename=OUTPUT_PATH,
    show=False,
    direction="TB",
    outformat=["png", "dot"],
    graph_attr=graph_attr,
):
    cfn = Cloudformation("CloudFormation\ninfra/cloudformation.yml")

    with Cluster("VPC (10.0.0.0/16)"):
        igw = InternetGateway("Internet\nGateway")

        with Cluster("Public Subnet (10.0.1.0/24)"):
            with Cluster("Security Group\nPorts: 22, 49000"):
                ec2 = EC2("EC2 (t3.micro)\nUbuntu 24.04\n─────────────\nUserData:\n• Install uv\n• Install hello-world\n• systemd service\n• Port 49000")

    cfn >> Edge(color="#666666", style="dashed", label="deploys") >> igw
    igw >> Edge(color="#48BB78") >> ec2

print(f"Generated: {OUTPUT_PATH}.png")
print(f"Generated: {OUTPUT_PATH}.dot")

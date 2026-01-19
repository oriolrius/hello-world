#!/usr/bin/env python3
"""
Generate CloudFormation infrastructure diagram for the hello-world application.
v3.0.x version - Simple EC2 deployment.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.network import VPC, InternetGateway, RouteTable
from diagrams.aws.management import Cloudformation
from diagrams.aws.general import Users
from diagrams.onprem.client import User

graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "1.0",
    "splines": "ortho",
    "nodesep": "1.0",
    "ranksep": "1.2",
}

with Diagram(
    "CloudFormation Infrastructure (v3.0.x)",
    filename="../infra/docs/infra-architecture",
    show=False,
    direction="TB",
    outformat=["png", "dot"],
    graph_attr=graph_attr,
):
    # External actors
    users = Users("End Users\n─────────────\nHTTP :49000")
    admin = User("Admin\n─────────────\nSSH :22")

    # CloudFormation
    cfn = Cloudformation("CloudFormation\n─────────────\nhello-world stack\ncloudformation.yml")

    with Cluster("AWS Cloud (eu-west-1)\n─────────────────────────────────────────\nDeployed via CloudFormation"):

        with Cluster("VPC: 10.0.0.0/16\n─────────────────────────────────────────\nhello-world-vpc"):

            igw = InternetGateway("Internet Gateway\n─────────────\nhello-world-igw")

            rt = RouteTable("Route Table\n─────────────\n0.0.0.0/0 → IGW")

            with Cluster("Public Subnet: 10.0.1.0/24\n─────────────────────────────────────────\nhello-world-subnet (AZ-a)"):

                with Cluster("Security Group\n─────────────\nhello-world-sg\nInbound: 22, 49000"):

                    ec2 = EC2("EC2 Instance\n─────────────\nt3.micro\nUbuntu 24.04\nhello-world service")

    # CloudFormation creates (gray dotted)
    cfn >> Edge(color="gray", style="dotted", label="creates") >> igw
    cfn >> Edge(color="gray", style="dotted") >> rt
    cfn >> Edge(color="gray", style="dotted") >> ec2

    # Traffic flow (green)
    users >> Edge(color="green", style="bold", label="HTTP") >> igw
    igw >> Edge(color="green") >> ec2

    # Admin SSH (blue dashed)
    admin >> Edge(color="blue", style="dashed", label="SSH") >> igw
    igw >> Edge(color="blue", style="dashed") >> ec2

print("Generated: ../infra/docs/infra-architecture.png")

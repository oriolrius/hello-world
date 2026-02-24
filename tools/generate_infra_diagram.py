#!/usr/bin/env python3
"""
Generate infrastructure diagram for infra/docs/
v4.x - AWS CloudFormation resources.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.network import VPC, InternetGateway, RouteTable
from diagrams.aws.security import IAMRole
from diagrams.onprem.client import Users

OUTPUT_PATH = "../infra/docs/infra-architecture"

graph_attr = {
    "fontsize": "12",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.5",
    "ranksep": "0.6",
}

with Diagram(
    "AWS Infrastructure (v4.x)",
    filename=OUTPUT_PATH,
    show=False,
    direction="TB",
    outformat=["png", "dot"],
    graph_attr=graph_attr,
):
    users = Users("Internet\nUsers")

    with Cluster("AWS (eu-west-1)"):
        igw = InternetGateway("Internet\nGateway")

        with Cluster("VPC 10.0.0.0/16"):
            rt = RouteTable("Route Table\n0.0.0.0/0 → IGW")

            with Cluster("Public Subnet 10.0.1.0/24"):
                with Cluster("Security Group\nports 22, 49000"):
                    ec2 = EC2("EC2 t3a.micro\nUbuntu 24.04")

    users >> Edge(color="#4299E1", label="HTTP :49000") >> igw
    igw >> Edge(color="#4299E1") >> rt
    rt >> Edge(color="#4299E1") >> ec2

print(f"Generated: {OUTPUT_PATH}.png")
print(f"Generated: {OUTPUT_PATH}.dot")

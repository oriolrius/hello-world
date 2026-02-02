#!/usr/bin/env python3
"""Generate infrastructure architecture diagram for v5.0.x.

This script creates a visual representation of the AWS infrastructure
deployed via CloudFormation: VPC, Subnet, Internet Gateway, Security Group,
and EC2 instance with the hello-world application.
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.network import InternetGateway, RouteTable, VPC
from diagrams.generic.network import Firewall, Subnet
from diagrams.onprem.client import Users

# Output paths
OUTPUT_DIR = "../infra/docs"
DIAGRAM_NAME = "infra-architecture"


def main():
    graph_attr = {
        "splines": "ortho",
        "nodesep": "0.8",
        "ranksep": "1.0",
        "fontsize": "14",
    }

    with Diagram(
        "AWS Infrastructure - v5.0.x",
        filename=f"{OUTPUT_DIR}/{DIAGRAM_NAME}",
        outformat=["png", "dot"],
        direction="LR",
        show=False,
        graph_attr=graph_attr,
    ):
        users = Users("Internet\nUsers")

        with Cluster("AWS Region (eu-west-1)"):
            igw = InternetGateway("Internet\nGateway")

            with Cluster("VPC (10.0.0.0/16)"):
                rt = RouteTable("Route\nTable")

                with Cluster("Public Subnet (10.0.1.0/24)"):
                    sg = Firewall("Security\nGroup")

                    with Cluster("EC2 Instance"):
                        ec2 = EC2("hello-world\n(t3.micro)")

        # Traffic flow
        users >> Edge(color="blue", label="HTTP:49000") >> igw
        igw >> Edge(color="blue") >> rt
        rt >> Edge(color="blue") >> sg
        sg >> Edge(color="green", label="Allow") >> ec2

        # SSH access (dashed)
        users >> Edge(color="orange", style="dashed", label="SSH:22") >> igw


if __name__ == "__main__":
    main()

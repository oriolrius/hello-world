#!/usr/bin/env python3
"""Generate credentials flow architecture diagram for v4.0.x.

This script creates a visual representation of how credentials flow
from GitHub Secrets through AWS CLI, CloudFormation, and Ansible
to deploy to EC2.
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.management import Cloudformation
from diagrams.custom import Custom
from diagrams.generic.storage import Storage
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.iac import Ansible
from diagrams.programming.language import Python

# Output paths
OUTPUT_DIR = "../.github/workflows/docs"
DIAGRAM_NAME = "credentials-flow"


def main():
    graph_attr = {
        "splines": "ortho",
        "nodesep": "0.6",
        "ranksep": "0.8",
        "fontsize": "12",
        "compound": "true",
    }

    with Diagram(
        "Credentials Flow - v4.0.x",
        filename=f"{OUTPUT_DIR}/{DIAGRAM_NAME}",
        outformat=["png", "dot"],
        direction="TB",
        show=False,
        graph_attr=graph_attr,
    ):
        with Cluster("GitHub Actions Runner"):
            with Cluster("1. Secrets Source"):
                secrets = GithubActions("GitHub Secrets\n\nAWS_ACCESS_KEY_ID\nAWS_SECRET_ACCESS_KEY\nAWS_SESSION_TOKEN\nEC2_SSH_KEY")

            with Cluster("2. Environment Setup"):
                aws_env = Python("AWS CLI\nEnvironment\n\nAWS_ACCESS_KEY_ID\nAWS_SECRET_ACCESS_KEY\nAWS_REGION")
                ssh_key = Storage("/tmp/deploy-key.pem\n\n(SSH private key)")

            with Cluster("3. Infrastructure"):
                cfn = Cloudformation("CloudFormation\n\nDeploy stack with\nKeyName parameter")
                get_ip = Cloudformation("Get EC2 IP\n\nfrom Stack Outputs")

            with Cluster("4. Deployment Config"):
                inventory = Storage("inventory.ini\n\nEC2_IP +\nkey path")

            with Cluster("5. Application Deployment"):
                ansible = Ansible("Ansible\nPlaybook")

        # External
        ec2 = EC2("EC2 Instance\n(Ubuntu 24.04)")

        # Credentials flow
        secrets >> Edge(color="blue", label="AWS creds") >> aws_env
        secrets >> Edge(color="orange", label="SSH key") >> ssh_key

        aws_env >> Edge(color="blue") >> cfn
        cfn >> Edge(color="blue") >> get_ip

        get_ip >> Edge(color="green", label="EC2 IP") >> inventory
        ssh_key >> Edge(color="orange", label="key path") >> inventory

        inventory >> Edge(color="purple") >> ansible
        ansible >> Edge(color="red", style="bold", label="SSH") >> ec2


if __name__ == "__main__":
    main()

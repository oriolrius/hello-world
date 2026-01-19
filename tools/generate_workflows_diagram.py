#!/usr/bin/env python3
"""Generate CI/CD pipeline architecture diagram for v4.0.x.

This script creates a visual representation of the GitHub Actions workflows
including the release pipeline (lint, test, build, release) and deploy pipeline
(CloudFormation + Ansible deployment).
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.management import Cloudformation
from diagrams.generic.compute import Rack
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.iac import Ansible
from diagrams.programming.language import Python

# Output paths
OUTPUT_DIR = "../.github/workflows/docs"
DIAGRAM_NAME = "cicd-architecture"


def main():
    graph_attr = {
        "splines": "ortho",
        "nodesep": "0.8",
        "ranksep": "1.0",
        "fontsize": "14",
    }

    with Diagram(
        "CI/CD Pipeline - v4.0.x",
        filename=f"{OUTPUT_DIR}/{DIAGRAM_NAME}",
        outformat=["png", "dot"],
        direction="LR",
        show=False,
        graph_attr=graph_attr,
    ):
        # Triggers
        with Cluster("Triggers"):
            tag_push = GithubActions("Tag Push\n(v*)")
            release_event = GithubActions("Release\nPublished")
            manual = GithubActions("Manual\nDispatch")

        # Release workflow
        with Cluster("Release Workflow"):
            with Cluster("Quality Checks"):
                lint = Python("Lint\n(ruff)")
                test = Python("Test\n(pytest)")

            build = Rack("Build\n(uv build)")
            release = GithubActions("GitHub\nRelease")

        # Deploy workflow
        with Cluster("Deploy Workflow"):
            cfn = Cloudformation("CloudFormation\nDeploy")
            wait_ec2 = EC2("Wait for\nEC2 Ready")
            ansible = Ansible("Ansible\nPlaybook")

        # AWS Infrastructure
        with Cluster("AWS (eu-west-1)"):
            ec2 = EC2("EC2 Instance\n(t3.micro)")

        # Release workflow connections (blue)
        tag_push >> Edge(color="blue", style="bold") >> lint
        tag_push >> Edge(color="blue", style="bold") >> test
        lint >> Edge(color="blue") >> build
        test >> Edge(color="blue") >> build
        build >> Edge(color="blue") >> release

        # Deploy workflow connections (green)
        release_event >> Edge(color="green", style="bold") >> cfn
        manual >> Edge(color="green", style="bold") >> cfn
        cfn >> Edge(color="green") >> wait_ec2
        wait_ec2 >> Edge(color="green") >> ansible
        ansible >> Edge(color="orange", style="dashed") >> ec2


if __name__ == "__main__":
    main()

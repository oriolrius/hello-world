#!/usr/bin/env python3
"""
Generate GitHub Actions workflow diagram for the hello-world CI/CD pipeline.
v3.0.x version - CloudFormation deployment.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import GithubActions
from diagrams.aws.management import Cloudformation
from diagrams.aws.compute import EC2
from diagrams.aws.general import Users

graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "1.0",
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.0",
}

with Diagram(
    "GitHub Actions CI/CD Pipeline (v3.0.x)",
    filename="../.github/workflows/docs/cicd-architecture",
    show=False,
    direction="TB",
    outformat=["png", "dot"],
    graph_attr=graph_attr,
):
    # Trigger
    dev = Users("Developer\n─────────────\ngit push tag v*")

    with Cluster("GitHub"):
        repo = Github("Repository\n─────────────\noriolrius/hello-world")

    with Cluster("GitHub Actions - release.yml\n─────────────────────────────────────────\nTriggered by: push tags v*"):

        with Cluster("Stage 1: Quality Gates\n(parallel)"):
            lint = GithubActions("Lint\n─────────────\nruff check\nruff format")
            test = GithubActions("Test\n─────────────\npytest -v")

        with Cluster("Stage 2: Build\n(after Stage 1)"):
            build = GithubActions("Build\n─────────────\nuv build\nupload artifact")

        with Cluster("Stage 3: Release\n(after Build)"):
            release = GithubActions("Release\n─────────────\nGitHub Release\nattach dist/*")

    with Cluster("GitHub Actions - deploy.yml\n─────────────────────────────────────────\nTriggered by: release published / manual"):

        deploy = GithubActions("Deploy\n─────────────\naws cloudformation\ndeploy")

    with Cluster("AWS (eu-west-1)"):
        cfn = Cloudformation("CloudFormation\n─────────────\nhello-world stack")
        ec2 = EC2("EC2 Instance\n─────────────\nApplication")

    users = Users("End Users\n─────────────\nHTTP requests")

    # Flow - Trigger (blue)
    dev >> Edge(color="blue", label="push tag") >> repo

    # Flow - Release workflow (purple)
    repo >> Edge(color="purple", label="trigger") >> lint
    repo >> Edge(color="purple") >> test
    lint >> Edge(color="purple", style="dashed", label="pass") >> build
    test >> Edge(color="purple", style="dashed") >> build
    build >> Edge(color="purple", style="dashed", label="artifact") >> release

    # Flow - Deploy workflow (green)
    release >> Edge(color="green", label="published") >> deploy
    deploy >> Edge(color="green", label="deploy") >> cfn

    # Flow - CloudFormation creates (gray)
    cfn >> Edge(color="gray", style="dotted", label="creates") >> ec2

    # Flow - User traffic (orange)
    users >> Edge(color="orange", style="bold", label="HTTP") >> ec2

print("Generated: ../.github/workflows/docs/cicd-architecture.png")

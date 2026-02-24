#!/usr/bin/env python3
"""
Generate CI/CD workflow diagram for .github/workflows/docs/
v4.x - Release workflow with lint, test, build, docker, release, and deploy jobs.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.vcs import Github
from diagrams.aws.management import Cloudformation
from diagrams.onprem.container import Docker
from diagrams.programming.language import Python

OUTPUT_PATH = "../.github/workflows/docs/cicd-architecture"

graph_attr = {
    "fontsize": "12",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.5",
    "ranksep": "0.6",
}

with Diagram(
    "CI/CD Pipeline (v4.x)",
    filename=OUTPUT_PATH,
    show=False,
    direction="TB",
    outformat=["png", "dot"],
    graph_attr=graph_attr,
):
    trigger = Github("Push tag v*\nor workflow_dispatch")

    with Cluster("Release Workflow"):
        with Cluster("Quality Gates"):
            lint = GithubActions("lint\nruff check/format")
            test = GithubActions("test\npytest")

        with Cluster("Build Artifacts"):
            build = GithubActions("build\nuv build")
            docker_job = Docker("docker\nbuild & push")

        with Cluster("Publish"):
            release = GithubActions("release\nGitHub Release")

        with Cluster("Deploy to AWS"):
            deploy = GithubActions("deploy")
            cfn = Cloudformation("CloudFormation\n+ UserData")

    trigger >> Edge(color="#4299E1") >> lint
    trigger >> Edge(color="#4299E1") >> test

    lint >> Edge(color="#48BB78") >> build
    test >> Edge(color="#48BB78") >> build
    lint >> Edge(color="#48BB78") >> docker_job
    test >> Edge(color="#48BB78") >> docker_job

    build >> Edge(color="#9F7AEA") >> release
    build >> Edge(color="#ED8936") >> deploy
    deploy >> Edge(color="#ED8936") >> cfn

print(f"Generated: {OUTPUT_PATH}.png")
print(f"Generated: {OUTPUT_PATH}.dot")

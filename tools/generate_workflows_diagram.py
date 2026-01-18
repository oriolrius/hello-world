#!/usr/bin/env python3
"""
Generate GitHub Actions workflow diagram for the hello-world CI/CD pipeline.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.container import Docker
from diagrams.aws.compute import EKS
from diagrams.aws.general import Users
from diagrams.k8s.compute import Pod
from diagrams.k8s.network import Service
from diagrams.custom import Custom
import os

graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "1.0",
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.0",
}

with Diagram(
    "GitHub Actions CI/CD Pipeline",
    filename="../.github/workflows/cicd-architecture",
    show=False,
    direction="LR",
    outformat=["png", "dot"],
    graph_attr=graph_attr,
):
    # Trigger
    dev = Users("Developer\n─────────────\ngit push tag v*\nor workflow_dispatch")

    with Cluster("GitHub"):
        repo = Github("Repository\n─────────────\noriolrius/hello-world\nsource code")

    with Cluster("GitHub Actions\n─────────────────────────────────────────\nCI/CD Pipeline (release.yml)"):

        with Cluster("Stage 1: Quality Gates\n(parallel)"):
            lint = GithubActions("Lint\n─────────────\nruff check\nruff format")
            test = GithubActions("Test\n─────────────\npytest -v\nunit tests")

        with Cluster("Stage 2: Build & Release\n(parallel, after Stage 1)"):
            release = GithubActions("Release\n─────────────\nGitHub Release\nauto release notes")
            docker = GithubActions("Docker\n─────────────\nBuild image\nPush to ghcr.io")

        with Cluster("Stage 3: Deploy\n(after Docker)"):
            deploy = GithubActions("Deploy\n─────────────\nkubectl apply -k\nrollout status")

    with Cluster("Container Registry"):
        registry = Docker("ghcr.io\n─────────────\noriolrius/hello-world\n:latest, :v*, :sha")

    with Cluster("AWS EKS\n─────────────────────────────────────────\nesade-teaching cluster (eu-west-1)"):
        eks = EKS("EKS\n─────────────\nKubernetes API")

        with Cluster("Namespace: hello-world"):
            svc = Service("Service\n─────────────\nLoadBalancer")
            pod1 = Pod("Pod 1")
            pod2 = Pod("Pod 2")

    users = Users("End Users\n─────────────\nHTTP requests")

    # Flow - Trigger (blue)
    dev >> Edge(color="blue", label="push tag") >> repo

    # Flow - CI stages (purple)
    repo >> Edge(color="purple", label="trigger") >> lint
    repo >> Edge(color="purple") >> test

    # Flow - After quality gates (purple dashed)
    lint >> Edge(color="purple", style="dashed", label="pass") >> release
    lint >> Edge(color="purple", style="dashed") >> docker
    test >> Edge(color="purple", style="dashed") >> release
    test >> Edge(color="purple", style="dashed") >> docker

    # Flow - Docker to registry (orange)
    docker >> Edge(color="orange", label="push image") >> registry

    # Flow - Deploy (green)
    docker >> Edge(color="green", style="dashed", label="triggers") >> deploy
    deploy >> Edge(color="green", label="kubectl") >> eks

    # Flow - Image pull (orange dashed)
    registry >> Edge(color="orange", style="dashed", label="pull") >> pod1
    registry >> Edge(color="orange", style="dashed") >> pod2

    # Flow - K8s internal (gray)
    eks >> Edge(color="gray", style="dotted") >> svc
    svc >> Edge(color="gray", style="dotted") >> pod1
    svc >> Edge(color="gray", style="dotted") >> pod2

    # Flow - User traffic (green bold)
    users >> Edge(color="green", style="bold", label="HTTP") >> svc

print("Generated: ../.github/workflows/cicd-architecture.png")

#!/usr/bin/env python3
"""Generate CI/CD pipeline diagram for hello-world v2.x."""

from diagrams import Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.ci import GithubActions
from diagrams.programming.language import Python

# Output path relative to this script
OUTPUT_PATH = "../assets/diagrams/cicd-pipeline"

graph_attr = {
    "splines": "ortho",
    "nodesep": "1.0",
    "ranksep": "1.0",
    "fontname": "Sans-Serif",
    "fontsize": "14",
    "bgcolor": "white",
}

node_attr = {
    "fontname": "Sans-Serif",
    "fontsize": "12",
}

edge_attr = {
    "color": "#2D3748",
    "penwidth": "2.0",
}

with Diagram(
    "CI/CD Pipeline (v2.x)",
    filename=OUTPUT_PATH,
    outformat=["png", "dot"],
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
):
    # Pipeline stages using GitHub Actions icons
    lint = GithubActions("Lint\n(ruff)")
    test = GithubActions("Test\n(pytest)")
    build = GithubActions("Build\n(uv build)")
    release = GithubActions("Release\n(GitHub)")

    # Flow: Lint -> Test -> Build -> Release
    lint >> Edge(color="#48BB78", label="pass") >> test
    test >> Edge(color="#48BB78", label="pass") >> build
    build >> Edge(color="#48BB78", label="pass") >> release

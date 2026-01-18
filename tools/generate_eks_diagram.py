#!/usr/bin/env python3
"""
Generate EKS architecture diagram using the diagrams library.
Produces PNG with proper AWS/K8s icons.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EKS, EC2
from diagrams.aws.network import VPC, PublicSubnet, PrivateSubnet, InternetGateway, NATGateway, ELB
from diagrams.aws.management import Cloudformation
from diagrams.aws.general import Users
from diagrams.k8s.compute import Pod
from diagrams.k8s.network import Service
from diagrams.k8s.infra import Node
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.client import User
from diagrams.onprem.container import Docker

# Graph attributes for better layout
graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "1.0",
    "splines": "ortho",
    "nodesep": "1.0",
    "ranksep": "1.2",
}

with Diagram(
    "EKS Architecture: esade-teaching",
    filename="../infra/eks-architecture",
    show=False,
    direction="TB",
    outformat=["png", "dot"],
    graph_attr=graph_attr,
):
    # External actors
    users = Users("Users/Clients\n─────────────\nExternal HTTP requests")
    developer = User("Developer\n─────────────\nkubectl/eksctl\ncluster management")
    github = GithubActions("GitHub Actions\n─────────────\nCI/CD pipeline\nautomates build & deploy")
    registry = Docker("ghcr.io\n─────────────\nContainer Registry\nstores Docker images")

    with Cluster("AWS Cloud (eu-west-1)"):

        # CloudFormation stacks (vertical layout)
        with Cluster("CloudFormation Stacks\n─────────────────────────────────────────\nfile: eksctl-cluster.yaml\nautomates deployment of managed K8s cluster",
                     graph_attr={"rankdir": "TB"}):
            cfn_cluster = Cloudformation("eksctl-esade-teaching-cluster\n─────────────\nVPC, Control Plane\nIAM Roles, OIDC")
            cfn_nodegroup = Cloudformation("eksctl-esade-teaching-nodegroup-students\n─────────────\nEC2, Auto Scaling Group\nLaunch Template")
            # Force vertical layout
            cfn_cluster - Edge(style="invis") - cfn_nodegroup

        # EKS Control Plane (AWS Managed)
        eks_control = EKS("EKS Control Plane\n─────────────\nesade-teaching (K8s 1.32)\nAWS-managed API server")

        with Cluster("VPC: 192.168.0.0/16\n─────────────────────────────────────────\nIsolated network for all cluster resources"):

            # Gateways
            igw = InternetGateway("Internet Gateway\n─────────────\nEnables internet\naccess for VPC")
            nat = NATGateway("NAT Gateway\n─────────────\nOutbound internet\nfor private subnets")

            with Cluster("Public Subnets (eu-west-1a, 1b, 1c)\n─────────────────────────────────────────\nInternet-facing resources, Load Balancers"):
                elb = ELB("AWS ELB\n─────────────\nLoadBalancer\nroutes HTTP traffic")

            with Cluster("Private Subnets (eu-west-1a, 1b, 1c)\n─────────────────────────────────────────\nIsolated workloads, no direct internet access"):

                with Cluster("Node Group: students\n─────────────────────────────────────────\nAuto Scaling 1-3 nodes, managed by AWS"):

                    with Cluster("Node 1 - t3.medium"):
                        node1 = Node("kubelet\n─────────────\nNode agent\nruns pods")
                        with Cluster("EKS Add-ons\n(AWS-managed)"):
                            pod_addon1 = Pod("vpc-cni\nCoreDNS\nkube-proxy\nmetrics-server")

                    with Cluster("Node 2 - t3.medium"):
                        node2 = Node("kubelet\n─────────────\nNode agent\nruns pods")
                        with Cluster("EKS Add-ons\n(AWS-managed)"):
                            pod_addon2 = Pod("vpc-cni\nCoreDNS\nkube-proxy\nmetrics-server")

                with Cluster("Namespace: hello-world\n─────────────────────────────────────────\nApplication isolation boundary"):
                    svc = Service("Service\n─────────────\nLoadBalancer\nexposes app on :80")
                    pod1 = Pod("Pod 1\n─────────────\nhello-world\ncontainer :49000")
                    pod2 = Pod("Pod 2\n─────────────\nhello-world\ncontainer :49000")

    # Connections - HTTP Traffic (green)
    users >> Edge(color="green", style="bold", label="HTTP") >> igw
    igw >> Edge(color="green", style="bold") >> elb
    elb >> Edge(color="green", style="bold", label="traffic") >> svc
    svc >> Edge(color="green") >> pod1
    svc >> Edge(color="green") >> pod2

    # Connections - Control Plane (blue dashed)
    developer >> Edge(color="blue", style="dashed", label="kubectl") >> eks_control
    eks_control >> Edge(color="blue", style="dashed", label="kubelet") >> node1
    eks_control >> Edge(color="blue", style="dashed") >> node2

    # Connections - CI/CD (purple)
    github >> Edge(color="purple", label="push image") >> registry
    github >> Edge(color="purple", style="dashed", label="deploy") >> eks_control

    # Connections - Image Pull (orange)
    registry >> Edge(color="orange", style="dashed", label="pull image") >> node1
    registry >> Edge(color="orange", style="dashed") >> node2

    # Connections - NAT outbound (amber)
    node1 >> Edge(color="goldenrod", style="dashed", label="outbound") >> nat
    node2 >> Edge(color="goldenrod", style="dashed") >> nat
    nat >> Edge(color="goldenrod", style="dashed") >> igw

    # Connections - Pod placement (gray dotted)
    pod1 >> Edge(color="gray", style="dotted", label="runs on") >> node1
    pod2 >> Edge(color="gray", style="dotted", label="runs on") >> node2

    # Connections - CloudFormation creates (gray dotted)
    cfn_cluster >> Edge(color="darkgray", style="dotted", label="creates") >> eks_control
    cfn_cluster >> Edge(color="darkgray", style="dotted") >> igw
    cfn_cluster >> Edge(color="darkgray", style="dotted") >> nat
    cfn_nodegroup >> Edge(color="darkgray", style="dotted", label="creates") >> node1
    cfn_nodegroup >> Edge(color="darkgray", style="dotted") >> node2

print("Generated: ../infra/eks-architecture.png and ../infra/eks-architecture.dot")

#!/usr/bin/env python3
"""
Generate native draw.io diagram with AWS stencils.
Uses mxGraph XML format with draw.io AWS shape library references.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom

# AWS shape styles from draw.io's AWS 19 library
AWS_SHAPES = {
    "vpc": "sketch=0;outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc;strokeColor=#879196;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;dashed=0;",
    "public_subnet": "sketch=0;outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_public_subnet;strokeColor=#7AA116;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;dashed=0;",
    "private_subnet": "sketch=0;outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_private_subnet;strokeColor=#147EBA;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;dashed=0;",
    "eks": "sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=#F78E04;gradientDirection=north;fillColor=#ED7100;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.eks;",
    "ec2": "sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=#F78E04;gradientDirection=north;fillColor=#ED7100;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;",
    "elb": "sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=#F78E04;gradientDirection=north;fillColor=#ED7100;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.elastic_load_balancing;",
    "igw": "sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=#945DF2;gradientDirection=north;fillColor=#5A30B5;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.internet_gateway;",
    "nat": "sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=#945DF2;gradientDirection=north;fillColor=#5A30B5;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.nat_gateway;",
    "cloudformation": "sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=#F34482;gradientDirection=north;fillColor=#BC1356;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudformation;",
    "users": "sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=#F54749;gradientDirection=north;fillColor=#C7131F;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.users;",
    "ecr": "sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=#F78E04;gradientDirection=north;fillColor=#ED7100;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ecr;",
}

K8S_SHAPES = {
    "pod": "sketch=0;html=1;dashed=0;whitespace=wrap;fillColor=#326CE5;strokeColor=none;fontColor=#ffffff;shape=mxgraph.kubernetes.icon;prIcon=pod;",
    "service": "sketch=0;html=1;dashed=0;whitespace=wrap;fillColor=#326CE5;strokeColor=none;fontColor=#ffffff;shape=mxgraph.kubernetes.icon;prIcon=svc;",
    "node": "sketch=0;html=1;dashed=0;whitespace=wrap;fillColor=#326CE5;strokeColor=none;fontColor=#ffffff;shape=mxgraph.kubernetes.icon;prIcon=node;",
}

GENERIC_SHAPES = {
    "github": "dashed=0;outlineConnect=0;html=1;align=center;labelPosition=center;verticalLabelPosition=bottom;verticalAlign=top;shape=mxgraph.weblogos.github;",
    "developer": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;",
    "box": "rounded=1;whiteSpace=wrap;html=1;",
    "group": "rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=8 8;fillColor=none;",
}

def create_cell(id, value, style, x, y, width, height, parent="1", vertex="1"):
    """Create an mxCell element."""
    cell = ET.Element("mxCell")
    cell.set("id", id)
    cell.set("value", value)
    cell.set("style", style)
    cell.set("parent", parent)
    cell.set("vertex", vertex)

    geom = ET.SubElement(cell, "mxGeometry")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", str(width))
    geom.set("height", str(height))
    geom.set("as", "geometry")

    return cell

def create_edge(id, value, source, target, style=""):
    """Create an edge mxCell element."""
    cell = ET.Element("mxCell")
    cell.set("id", id)
    cell.set("value", value)
    cell.set("style", f"edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;{style}")
    cell.set("parent", "1")
    cell.set("edge", "1")
    cell.set("source", source)
    cell.set("target", target)

    geom = ET.SubElement(cell, "mxGeometry")
    geom.set("relative", "1")
    geom.set("as", "geometry")

    return cell

def create_group(id, value, x, y, width, height, style=""):
    """Create a group/container."""
    cell = ET.Element("mxCell")
    cell.set("id", id)
    cell.set("value", value)
    cell.set("style", f"rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;{style}")
    cell.set("parent", "1")
    cell.set("vertex", "1")

    geom = ET.SubElement(cell, "mxGeometry")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", str(width))
    geom.set("height", str(height))
    geom.set("as", "geometry")

    return cell

def generate_eks_diagram():
    """Generate EKS architecture diagram."""

    # Create root structure
    mxfile = ET.Element("mxfile")
    mxfile.set("host", "app.diagrams.net")

    diagram = ET.SubElement(mxfile, "diagram")
    diagram.set("name", "EKS Architecture")
    diagram.set("id", "eks-arch")

    model = ET.SubElement(diagram, "mxGraphModel")
    model.set("dx", "1434")
    model.set("dy", "780")
    model.set("grid", "1")
    model.set("gridSize", "10")
    model.set("guides", "1")
    model.set("tooltips", "1")
    model.set("connect", "1")
    model.set("arrows", "1")
    model.set("fold", "1")
    model.set("page", "1")
    model.set("pageScale", "1")
    model.set("pageWidth", "1600")
    model.set("pageHeight", "1200")

    root = ET.SubElement(model, "root")

    # Base cells
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    # === AWS Cloud container ===
    root.append(create_group("aws-cloud", "AWS Cloud (eu-west-1)", 50, 50, 1200, 900,
                             "fillColor=#F5F5F5;strokeColor=#232F3E;strokeWidth=2;"))

    # === VPC ===
    root.append(create_cell("vpc", "VPC: 192.168.0.0/16", AWS_SHAPES["vpc"],
                           70, 100, 900, 750, parent="aws-cloud"))

    # === Public Subnets ===
    root.append(create_cell("pub-subnet", "Public Subnets (eu-west-1a, 1b, 1c)",
                           AWS_SHAPES["public_subnet"], 90, 140, 400, 200, parent="vpc"))

    # === Private Subnets ===
    root.append(create_cell("priv-subnet", "Private Subnets (eu-west-1a, 1b, 1c)",
                           AWS_SHAPES["private_subnet"], 90, 380, 600, 400, parent="vpc"))

    # === Gateways ===
    root.append(create_cell("igw", "Internet Gateway", AWS_SHAPES["igw"], 550, 160, 60, 60, parent="vpc"))
    root.append(create_cell("nat", "NAT Gateway", AWS_SHAPES["nat"], 420, 300, 60, 60, parent="vpc"))
    root.append(create_cell("elb", "Load Balancer", AWS_SHAPES["elb"], 200, 200, 60, 60, parent="pub-subnet"))

    # === EKS Control Plane ===
    root.append(create_cell("eks", "EKS Control Plane\nesade-teaching (K8s 1.32)",
                           AWS_SHAPES["eks"], 750, 200, 78, 78, parent="aws-cloud"))

    # === Node Group ===
    root.append(create_group("nodegroup", "Node Group: students (1-3 nodes)",
                            110, 420, 550, 330, "fillColor=#E2E3E5;strokeColor=#6C757D;"))

    # === EC2 Nodes ===
    root.append(create_cell("node1", "Node 1\nt3.medium", AWS_SHAPES["ec2"],
                           140, 480, 60, 60, parent="nodegroup"))
    root.append(create_cell("node2", "Node 2\nt3.medium", AWS_SHAPES["ec2"],
                           300, 480, 60, 60, parent="nodegroup"))

    # === K8s Pods ===
    root.append(create_cell("pod1", "Pod 1", K8S_SHAPES["pod"], 150, 580, 48, 48, parent="nodegroup"))
    root.append(create_cell("pod2", "Pod 2", K8S_SHAPES["pod"], 310, 580, 48, 48, parent="nodegroup"))
    root.append(create_cell("svc", "Service (LB)", K8S_SHAPES["service"], 230, 680, 48, 48, parent="nodegroup"))

    # === CloudFormation ===
    root.append(create_cell("cfn1", "eksctl-cluster", AWS_SHAPES["cloudformation"],
                           1000, 300, 60, 60, parent="aws-cloud"))
    root.append(create_cell("cfn2", "eksctl-nodegroup", AWS_SHAPES["cloudformation"],
                           1000, 450, 60, 60, parent="aws-cloud"))

    # === External actors ===
    root.append(create_cell("users", "Users", AWS_SHAPES["users"], 50, 980, 60, 60))
    root.append(create_cell("developer", "Developer", GENERIC_SHAPES["developer"], 1300, 200, 40, 80))
    root.append(create_cell("github", "GitHub Actions", GENERIC_SHAPES["github"], 1300, 400, 60, 60))
    root.append(create_cell("ecr", "ghcr.io", AWS_SHAPES["ecr"], 1300, 550, 60, 60))

    # === Edges ===
    # HTTP traffic (green)
    root.append(create_edge("e1", "HTTP", "users", "igw", "strokeColor=#22863a;strokeWidth=2;"))
    root.append(create_edge("e2", "", "igw", "elb", "strokeColor=#22863a;strokeWidth=2;"))
    root.append(create_edge("e3", "traffic", "elb", "svc", "strokeColor=#22863a;strokeWidth=2;"))
    root.append(create_edge("e4", "", "svc", "pod1", "strokeColor=#22863a;"))
    root.append(create_edge("e5", "", "svc", "pod2", "strokeColor=#22863a;"))

    # Control plane (blue dashed)
    root.append(create_edge("e6", "kubectl", "developer", "eks", "strokeColor=#0366d6;dashed=1;"))
    root.append(create_edge("e7", "kubelet", "eks", "node1", "strokeColor=#0366d6;dashed=1;"))
    root.append(create_edge("e8", "", "eks", "node2", "strokeColor=#0366d6;dashed=1;"))

    # CI/CD (purple)
    root.append(create_edge("e9", "push", "github", "ecr", "strokeColor=#6f42c1;"))
    root.append(create_edge("e10", "deploy", "github", "eks", "strokeColor=#6f42c1;dashed=1;"))

    # Image pull (orange)
    root.append(create_edge("e11", "pull", "ecr", "node1", "strokeColor=#e36209;dashed=1;"))
    root.append(create_edge("e12", "", "ecr", "node2", "strokeColor=#e36209;dashed=1;"))

    # NAT outbound (amber)
    root.append(create_edge("e13", "outbound", "node1", "nat", "strokeColor=#b08800;dashed=1;"))
    root.append(create_edge("e14", "", "node2", "nat", "strokeColor=#b08800;dashed=1;"))
    root.append(create_edge("e15", "", "nat", "igw", "strokeColor=#b08800;dashed=1;"))

    # CloudFormation creates (gray dotted)
    root.append(create_edge("e16", "creates", "cfn1", "eks", "strokeColor=#586069;dashed=1;dashPattern=1 2;"))
    root.append(create_edge("e17", "", "cfn1", "vpc", "strokeColor=#586069;dashed=1;dashPattern=1 2;"))
    root.append(create_edge("e18", "creates", "cfn2", "node1", "strokeColor=#586069;dashed=1;dashPattern=1 2;"))
    root.append(create_edge("e19", "", "cfn2", "node2", "strokeColor=#586069;dashed=1;dashPattern=1 2;"))

    # Format and save
    xml_str = ET.tostring(mxfile, encoding="unicode")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

    # Remove extra blank lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    pretty_xml = '\n'.join(lines)

    return pretty_xml

if __name__ == "__main__":
    xml = generate_eks_diagram()
    output_path = "../infra/docs/eks-architecture.drawio"
    with open(output_path, "w") as f:
        f.write(xml)
    print(f"Generated: {output_path}")

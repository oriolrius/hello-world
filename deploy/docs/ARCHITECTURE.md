# Ansible Deployment Architecture (v5.x)

## Architecture Diagram

![Ansible Deployment](deploy-architecture.png)

## Connection Color Legend

| Color | Meaning |
|-------|---------|
| Green (#48BB78) | SSH connection |
| Blue (#4299E1) | Package installation |
| Purple (#9F7AEA) | Docker Compose deployment |
| Orange (#ED8936) | Image pull from registry |

## Overview

The v5.x deployment uses Ansible to configure EC2 instances and deploy the application using Docker Compose. This approach separates infrastructure provisioning (CloudFormation) from configuration management (Ansible).

## Deployment Flow

1. **SSH Connection** - Ansible connects to EC2 via SSH
2. **Package Installation** - Installs Docker and dependencies
3. **Docker Compose** - Deploys hello-world container
4. **Health Check** - Verifies service is responding

## Playbook Tasks

### Install Required Packages

```yaml
- name: Install required packages
  apt:
    name:
      - ca-certificates
      - curl
      - gnupg
    state: present
```

### Install Docker

```yaml
- name: Install Docker
  apt:
    name:
      - docker-ce
      - docker-ce-cli
      - containerd.io
      - docker-compose-plugin
    state: present
```

### Deploy with Docker Compose

```yaml
- name: Pull and deploy with Docker Compose
  community.docker.docker_compose_v2:
    project_src: "{{ app_dir }}"
    pull: always
    state: present
```

### Health Check

```yaml
- name: Wait for service to be healthy
  uri:
    url: "http://localhost:49000/"
    status_code: 200
  retries: 10
  delay: 3
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `app_dir` | /opt/hello-world | Application directory on target |
| `image_tag` | latest | Docker image tag to deploy |

## Systemd Service

Docker Compose manages the container lifecycle. The Docker service is enabled at boot:

```yaml
- name: Start and enable Docker
  systemd:
    name: docker
    enabled: true
    state: started
```

## Manual Deployment

### Prerequisites

```bash
# Install Ansible
uv sync --dev

# Install Ansible collections
uv run ansible-galaxy collection install -r deploy/requirements.yml
```

### Create Inventory

```bash
cp deploy/inventory.ini.example deploy/inventory.ini
# Edit with your EC2 IP and SSH key path
```

### Run Playbook

```bash
cd deploy
uv run ansible-playbook -i inventory.ini playbook.yml
```

## Troubleshooting

### Check Docker Status

```bash
ssh ubuntu@<EC2_IP> "sudo systemctl status docker"
```

### Check Container Logs

```bash
ssh ubuntu@<EC2_IP> "sudo docker compose -f /opt/hello-world/docker-compose.yml logs"
```

### Restart Service

```bash
ssh ubuntu@<EC2_IP> "sudo docker compose -f /opt/hello-world/docker-compose.yml restart"
```

### Test Service

```bash
curl http://<EC2_IP>:49000/
```

## Diagram Source

The diagram is generated from `tools/generate_deploy_diagram.py`:

```bash
cd tools
source .venv/bin/activate
python generate_deploy_diagram.py
```

Editable version: [deploy-architecture.drawio](deploy-architecture.drawio)

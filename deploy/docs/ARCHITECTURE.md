# Ansible Deployment Architecture - v5.0.x

This document describes the Ansible deployment architecture for the hello-world application version 5.0.x.

## Architecture Diagram

![Deployment Architecture](deploy-architecture.png)

## Connection Color Legend

| Color | Description                        |
|-------|------------------------------------|
| Blue  | SSH connection from control node   |
| Green | Sequential task execution          |

## Overview

The deployment uses Ansible to configure EC2 instances provisioned by CloudFormation. The playbook installs Docker and deploys the hello-world application as a container using Docker Compose.

## Deployment Flow

```
┌─────────────────────┐
│   Control Node      │
│   (GitHub Actions)  │
└─────────┬───────────┘
          │ SSH
┌─────────▼───────────┐
│ 1. Install packages │
│    (apt: curl, ca)  │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│ 2. Add Docker repo  │
│    (GPG key + apt)  │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│ 3. Install Docker   │
│    (CE + Compose)   │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│ 4. Deploy container │
│    (Docker Compose) │
└─────────────────────┘
```

## Playbook Tasks

### 1. Install Required Packages

Installs system dependencies using apt:

```yaml
- name: Install required packages
  apt:
    name:
      - ca-certificates
      - curl
    state: present
    update_cache: true
```

### 2. Setup Docker Repository

Adds Docker's official GPG key and apt repository:

```yaml
- name: Create Docker keyring directory
  file:
    path: /etc/apt/keyrings
    state: directory
    mode: '0755'

- name: Download Docker GPG key
  get_url:
    url: https://download.docker.com/linux/ubuntu/gpg
    dest: /etc/apt/keyrings/docker.asc
    mode: '0644'

- name: Add Docker repository
  apt_repository:
    repo: "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
    state: present
    filename: docker
```

### 3. Install Docker

Installs Docker Engine and Compose plugin:

```yaml
- name: Install Docker packages
  apt:
    name:
      - docker-ce
      - docker-ce-cli
      - containerd.io
      - docker-compose-plugin
    state: present
    update_cache: true

- name: Start and enable Docker service
  systemd:
    name: docker
    enabled: true
    state: started
```

### 4. Deploy Application

Creates app directory and deploys via Docker Compose:

```yaml
- name: Create application directory
  file:
    path: "{{ app_dir }}"
    state: directory
    mode: '0755'

- name: Copy docker-compose.yml
  template:
    src: docker-compose.yml.j2
    dest: "{{ app_dir }}/docker-compose.yml"
    mode: '0644'
  notify: Restart hello-world

- name: Pull and start hello-world container
  community.docker.docker_compose_v2:
    project_src: "{{ app_dir }}"
    state: present
    pull: always
```

## Playbook Variables

| Variable    | Default           | Description                     |
|-------------|-------------------|---------------------------------|
| `app_dir`   | /opt/hello-world  | Installation directory          |
| `image_tag` | v5                | Docker image tag to deploy      |

## Docker Compose Configuration

The application runs as a Docker container:

| Setting        | Value                                |
|----------------|--------------------------------------|
| Image          | ghcr.io/oriolrius/hello-world:v5     |
| Port mapping   | 49000:49000                          |
| Restart policy | unless-stopped                       |
| Health check   | HTTP GET http://localhost:49000/     |

## Ansible Configuration

### ansible.cfg

| Setting            | Value                               |
|--------------------|-------------------------------------|
| inventory          | inventory.ini                       |
| host_key_checking  | False                               |
| remote_user        | ubuntu                              |
| private_key_file   | ~/.ssh/hello-world-key.pem          |

### SSH Settings

- Strict host key checking disabled for automated deployment
- Known hosts file set to /dev/null

## Handlers

### Restart hello-world

Triggered when the docker-compose.yml changes:

```yaml
- name: Restart hello-world
  community.docker.docker_compose_v2:
    project_src: "{{ app_dir }}"
    state: restarted
```

## Manual Deployment

### Prerequisites

1. EC2 instance running Ubuntu 24.04
2. SSH access with key-based authentication
3. Ansible installed on the control node

### Steps

1. Create inventory file:
   ```ini
   [hello-world]
   <ec2-public-ip> ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/your-key.pem
   ```

2. Install Ansible collection:
   ```bash
   uv run ansible-galaxy collection install -r deploy/requirements.yml
   ```

3. Run the playbook:
   ```bash
   cd deploy
   uv run ansible-playbook -i inventory.ini playbook.yml
   ```

4. Verify the service:
   ```bash
   curl http://<ec2-public-ip>:49000/
   ```

## Troubleshooting

### Check Container Status

```bash
ssh ubuntu@<ec2-ip> "sudo docker compose -f /opt/hello-world/docker-compose.yml ps"
```

### View Container Logs

```bash
ssh ubuntu@<ec2-ip> "sudo docker compose -f /opt/hello-world/docker-compose.yml logs -f"
```

### Restart Container

```bash
ssh ubuntu@<ec2-ip> "sudo docker compose -f /opt/hello-world/docker-compose.yml restart"
```

### Check Docker Service

```bash
ssh ubuntu@<ec2-ip> "sudo systemctl status docker"
```

## Diagram Source

The architecture diagram is generated using the [diagrams](https://diagrams.mingrammer.com/) library.

To regenerate the diagram:

```bash
cd tools
uv run python generate_deploy_diagram.py
```

The editable `.drawio` file is also available for manual adjustments.

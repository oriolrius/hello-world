# Ansible Deployment Architecture - v5.0.x

This document describes the Ansible deployment architecture for the hello-world application version 4.0.x.

## Architecture Diagram

![Deployment Architecture](deploy-architecture.png)

## Connection Color Legend

| Color | Description                        |
|-------|------------------------------------|
| Blue  | SSH connection from control node   |
| Green | Sequential task execution          |

## Overview

The deployment uses Ansible to configure EC2 instances provisioned by CloudFormation. The playbook installs the hello-world application and configures it as a systemd service.

## Deployment Flow

```
┌─────────────────────┐
│   Control Node      │
│   (GitHub Actions)  │
└─────────┬───────────┘
          │ SSH
┌─────────▼───────────┐
│ 1. Install curl     │
│    (apt package)    │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│ 2. Install uv       │
│    (astral.sh)      │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│ 3. Install app      │
│    (uv tool)        │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│ 4. Configure        │
│    systemd service  │
└─────────────────────┘
```

## Playbook Tasks

### 1. Install Required Packages

Installs system dependencies using apt:

```yaml
- name: Install required packages
  apt:
    name:
      - curl
    state: present
    update_cache: true
```

### 2. Install uv

Installs the uv package manager from astral.sh:

```yaml
- name: Install uv
  shell: curl -LsSf https://astral.sh/uv/install.sh | sh
  args:
    creates: /root/.local/bin/uv
```

### 3. Install hello-world

Installs the application as a uv tool from GitHub:

```yaml
- name: Install hello-world with uv
  shell: /root/.local/bin/uv tool install hello-world --from git+https://github.com/oriolrius/hello-world --force
  environment:
    PATH: "/root/.local/bin:{{ ansible_facts['env']['PATH'] }}"
```

### 4. Create systemd Service

Deploys the systemd service unit file from template:

```yaml
- name: Create systemd service
  template:
    src: hello-world.service.j2
    dest: /etc/systemd/system/hello-world.service
    mode: '0644'
  notify: Restart hello-world
```

### 5. Enable and Start Service

Enables the service to start on boot and starts it immediately:

```yaml
- name: Enable and start hello-world service
  systemd:
    name: hello-world
    enabled: true
    state: started
    daemon_reload: true
```

## Playbook Variables

| Variable   | Default   | Description                    |
|------------|-----------|--------------------------------|
| app_port   | 49000     | Port the application listens on|
| app_bind   | 0.0.0.0   | Address to bind to             |

## Systemd Service Unit

The service is configured with:

| Setting      | Value                                          |
|--------------|------------------------------------------------|
| Type         | simple                                         |
| User         | root                                           |
| ExecStart    | `/root/.local/bin/hello-world --bind 0.0.0.0 --port 49000` |
| Restart      | always                                         |
| RestartSec   | 5 seconds                                      |

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

Triggered when the service configuration changes:

```yaml
- name: Restart hello-world
  systemd:
    name: hello-world
    state: restarted
    daemon_reload: true
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

2. Run the playbook:
   ```bash
   cd deploy
   ansible-playbook -i inventory.ini playbook.yml
   ```

3. Verify the service:
   ```bash
   curl http://<ec2-public-ip>:49000/
   ```

## Troubleshooting

### Check Service Status

```bash
ssh ubuntu@<ec2-ip> "sudo systemctl status hello-world"
```

### View Service Logs

```bash
ssh ubuntu@<ec2-ip> "sudo journalctl -u hello-world -f"
```

### Restart Service

```bash
ssh ubuntu@<ec2-ip> "sudo systemctl restart hello-world"
```

## Diagram Source

The architecture diagram is generated using the [diagrams](https://diagrams.mingrammer.com/) library.

To regenerate the diagram:

```bash
cd tools
source .venv/bin/activate
python generate_deploy_diagram.py
```

The editable `.drawio` file is also available for manual adjustments.

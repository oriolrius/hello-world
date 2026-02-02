# Ansible Deployment - v5.0.x

This folder contains Ansible configuration for deploying the hello-world application to EC2 instances.

## Quick Start

### Prerequisites

- EC2 instance running Ubuntu 24.04 (provisioned via CloudFormation)
- SSH key pair for EC2 access
- Ansible installed (`uv sync --dev` installs it)

### Deploy

1. Create inventory file:
   ```bash
   cp inventory.ini.example inventory.ini
   # Edit inventory.ini with your EC2 IP
   ```

2. Run the playbook:
   ```bash
   cd deploy
   uv run ansible-playbook -i inventory.ini playbook.yml
   ```

3. Verify:
   ```bash
   curl http://<ec2-ip>:49000/
   ```

## What Gets Installed

| Component | Description |
|-----------|-------------|
| curl | Required for downloading uv |
| uv | Python package manager |
| hello-world | Application (installed as uv tool) |
| systemd service | Auto-start on boot |

## Files

| File | Description |
|------|-------------|
| `playbook.yml` | Main Ansible playbook |
| `ansible.cfg` | Ansible configuration |
| `hello-world.service.j2` | Systemd service template |
| `inventory.ini.example` | Example inventory file |
| `docs/ARCHITECTURE.md` | Detailed architecture documentation |
| `docs/deploy-architecture.png` | Architecture diagram |
| `docs/deploy-architecture.dot` | Graphviz source for diagram |
| `docs/deploy-architecture.drawio` | Editable diagram (draw.io format) |

## Variables

Configure in playbook.yml:

| Variable | Default | Description |
|----------|---------|-------------|
| app_port | 49000 | Application port |
| app_bind | 0.0.0.0 | Bind address |

## Service Management

```bash
# Check status
ssh ubuntu@<ec2-ip> "sudo systemctl status hello-world"

# View logs
ssh ubuntu@<ec2-ip> "sudo journalctl -u hello-world -f"

# Restart
ssh ubuntu@<ec2-ip> "sudo systemctl restart hello-world"
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed documentation.

![Deployment Architecture](docs/deploy-architecture.png)

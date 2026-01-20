# AWS Systems Manager (SSM) Session Manager

This guide covers using SSM Session Manager to connect to EC2 instances without SSH keys or open ports.

## Overview

SSM Session Manager provides secure shell access to EC2 instances without:
- Opening inbound ports (no port 22)
- Managing SSH keys on instances
- Using bastion hosts
- Requiring public IP addresses

All connections are encrypted and logged via AWS CloudTrail.

## Infrastructure

### Deploy the Stack

```bash
aws cloudformation create-stack \
  --stack-name SSM-Test \
  --template-body file://infra/ssm-test.yaml \
  --capabilities CAPABILITY_NAMED_IAM
```

### Stack Resources

| Resource | Description |
|----------|-------------|
| VPC | 10.0.0.0/16 with DNS enabled |
| Public Subnet | 10.0.1.0/24 with auto-assign public IP |
| Internet Gateway | For SSM agent connectivity |
| Security Group | HTTPS egress only (no inbound rules) |
| IAM Role | `AmazonSSMManagedInstanceCore` policy |
| EC2 Instance | Ubuntu 24.04 LTS on t3a.micro (AMD) |

### Delete the Stack

```bash
aws cloudformation delete-stack --stack-name SSM-Test
```

## Prerequisites

### 1. Session Manager Plugin

Install the Session Manager plugin for AWS CLI:

```bash
# Ubuntu/Debian
curl -s "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o /tmp/session-manager-plugin.deb
sudo dpkg -i /tmp/session-manager-plugin.deb

# Verify
session-manager-plugin --version
```

### 2. IAM Permissions

Your IAM user/role needs these permissions:
- `ssm:StartSession`
- `ssm:TerminateSession`
- `ssm:ResumeSession`
- `ssm:DescribeInstanceInformation`
- `ssm:GetCommandInvocation`
- `ssm:SendCommand`

The `AdministratorAccess` policy includes all of these.

## Basic Usage

### Connect via SSM

```bash
# Get instance ID
INSTANCE_ID=$(aws cloudformation describe-stacks \
  --stack-name SSM-Test \
  --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
  --output text)

# Connect
aws ssm start-session --target $INSTANCE_ID
```

### Run Commands Remotely

```bash
# Single command
aws ssm send-command \
  --instance-ids $INSTANCE_ID \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["hostname", "whoami", "df -h"]'

# Get command output
aws ssm get-command-invocation \
  --command-id <command-id> \
  --instance-id $INSTANCE_ID \
  --query 'StandardOutputContent' \
  --output text
```

### Check Instance Status

```bash
aws ssm describe-instance-information \
  --query 'InstanceInformationList[*].[InstanceId,PingStatus,PlatformName,PlatformVersion]' \
  --output table
```

## SSH over SSM

Tunnel regular SSH through SSM for tools like `scp`, `rsync`, and VSCode.

### 1. Generate SSH Key

```bash
ssh-keygen -t ed25519 -f ~/.ssh/ssm-key -N ""
```

### 2. Push Public Key to Instance

```bash
PUBKEY=$(cat ~/.ssh/ssm-key.pub)
aws ssm send-command \
  --instance-ids $INSTANCE_ID \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[
    \"mkdir -p /home/ubuntu/.ssh\",
    \"echo '$PUBKEY' >> /home/ubuntu/.ssh/authorized_keys\",
    \"chown -R ubuntu:ubuntu /home/ubuntu/.ssh\",
    \"chmod 700 /home/ubuntu/.ssh\",
    \"chmod 600 /home/ubuntu/.ssh/authorized_keys\"
  ]"
```

### 3. Configure SSH

Add to `~/.ssh/config`:

```
# SSH over SSM - specific host
Host ssm-ubuntu
    HostName i-xxxxxxxxxxxx
    User ubuntu
    ProxyCommand sh -c "aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'"
    IdentityFile ~/.ssh/ssm-key
    StrictHostKeyChecking no

# SSH over SSM - any instance by ID
Host i-* mi-*
    ProxyCommand sh -c "aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'"
    User ubuntu
    IdentityFile ~/.ssh/ssm-key
    StrictHostKeyChecking no
```

### 4. Connect

```bash
# Using alias
ssh ssm-ubuntu

# Using instance ID directly
ssh ubuntu@i-xxxxxxxxxxxx
```

## VSCode Remote SSH

### Setup

1. Install the "Remote - SSH" extension (`ms-vscode-remote.remote-ssh`)

2. Ensure `~/.ssh/config` has the SSM host configured (see above)

3. Connect:
   - Press `Ctrl+Shift+P`
   - Select "Remote-SSH: Connect to Host..."
   - Choose `ssm-ubuntu`

### Command Line

```bash
# Open VSCode connected to instance
code --remote ssh-remote+ssm-ubuntu /home/ubuntu

# Open specific folder
code --remote ssh-remote+ssm-ubuntu /home/ubuntu/project
```

## File Transfer

### SCP

```bash
# Upload
scp file.txt ssm-ubuntu:/home/ubuntu/

# Download
scp ssm-ubuntu:/home/ubuntu/file.txt ./

# Directory
scp -r ./folder ssm-ubuntu:/home/ubuntu/
```

### Rsync

```bash
# Sync local to remote
rsync -avz ./project/ ssm-ubuntu:/home/ubuntu/project/

# Sync remote to local
rsync -avz ssm-ubuntu:/home/ubuntu/project/ ./project/
```

## Troubleshooting

### Instance Not Appearing in SSM

1. Check IAM role has `AmazonSSMManagedInstanceCore` policy
2. Verify instance has internet access (for SSM endpoints)
3. Check SSM agent is running:
   ```bash
   aws ssm describe-instance-information
   ```

### SSH Connection Timeout

1. Verify Session Manager plugin is installed:
   ```bash
   session-manager-plugin --version
   ```

2. Check AWS credentials are valid:
   ```bash
   aws sts get-caller-identity
   ```

3. Verify SSH key is deployed on instance

### Permission Denied (publickey)

1. Ensure public key is in `/home/ubuntu/.ssh/authorized_keys`
2. Check file permissions:
   ```bash
   # On instance
   ls -la ~/.ssh/
   # Should be: drwx------ .ssh
   # Should be: -rw------- authorized_keys
   ```

## Security Notes

- SSM sessions are logged in CloudTrail
- No inbound security group rules needed
- Session tokens expire (typically 1-12 hours)
- Consider using VPC endpoints for private subnets (no internet required)

## References

- [AWS SSM Session Manager Documentation](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
- [Session Manager Plugin Installation](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)
- [SSH over SSM](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-enable-ssh-connections.html)

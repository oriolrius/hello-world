# hello-world

A teaching project that demonstrates the evolution of DevOps practices. The application itself is intentionally trivial — a web server that returns "hello-world" — because the focus is on **how software is built, tested, and delivered**, not the application logic.

## What This Version Demonstrates (v3.x)

This version introduces **Infrastructure as Code (IaC)** with AWS CloudFormation:

| Practice               | Implementation                                 |
| ---------------------- | ---------------------------------------------- |
| Infrastructure as Code | AWS CloudFormation templates                   |
| Cloud Deployment       | EC2 instance in custom VPC                     |
| Network Configuration  | VPC, Subnet, Internet Gateway, Security Groups |
| Application Bootstrap  | Shell script via EC2 UserData                  |
| Service Management     | systemd for process supervision                |

### Evolution from v2.x

- **v2.x**: CI/CD pipeline that builds and releases — but where does it run?
- **v3.x**: Answers "where does it run?" with **Infrastructure as Code** — the entire AWS environment is defined in `cloudformation.yml`

```
v2.x: Code → Build → Release → ???
v3.x: Code → Build → Release → CloudFormation → EC2 (running!)
```

### Architecture Overview

![Architecture Overview](assets/diagrams/architecture.png)

**Key learning**: Infrastructure can be versioned, reviewed, and automated just like application code. "Clicking in the AWS console" is replaced by `aws cloudformation deploy`.

### Limitation of This Approach

The bootstrap script runs **only on first launch**. To update the application, you must:

1. Delete the stack and recreate it, OR
2. SSH into the instance and manually update

This limitation is addressed in later versions.

## Installation

```bash
uv sync
```

## Usage

### Development mode

```bash
uv run hello-world
```

### From virtual environment

```bash
.venv/bin/hello-world
```

### With uvx (no install)

```bash
uvx --from git+https://github.com/oriolrius/hello-world hello-world
```

### From wheel

```bash
uv build
uvx --from ./dist/hello_world-*.whl hello-world
```

## Development

```bash
uv run ruff check src/ tests/   # lint
uv run ruff format src/ tests/  # format
uv run pytest -v                # test
uv build                        # build .tar.gz and .whl
```

## Parameters

| Flag           | Description  | Default     |
| -------------- | ------------ | ----------- |
| `-b, --bind` | Bind address | `0.0.0.0` |
| `-p, --port` | Port number  | `49000`   |

## Examples

```bash
hello-world                        # http://0.0.0.0:49000
hello-world -p 8080                # http://0.0.0.0:8080
hello-world -b 127.0.0.1 -p 3000   # http://127.0.0.1:3000
```

## CI/CD Pipeline

The project includes GitHub Actions workflows for automated releases and deployments.

### Release Workflow

Triggered on version tags (`v*`), the release pipeline:

1. **Lint**: Runs `ruff check` and `ruff format --check`
2. **Test**: Executes `pytest`
3. **Build**: Creates wheel and source distributions
4. **Release**: Publishes artifacts to GitHub Releases

To create a release:

```bash
git tag v3.0.0
git push origin v3.0.0
```

### Deploy Workflow

Triggered on release publish or manually via `workflow_dispatch`.

**Required GitHub Secrets:**

| Secret                    | Description                                        |
| ------------------------- | -------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | AWS access key                                     |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key                                     |
| `AWS_SESSION_TOKEN`     | AWS session token (if using temporary credentials) |

## AWS Deployment

The project includes CloudFormation templates for deploying to AWS EC2.

### Prerequisites

Install and configure the AWS CLI:

```bash
# Install AWS CLI (macOS)
brew install awscli

# Install AWS CLI (Linux)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure credentials
aws configure
```

You'll be prompted for:

| Prompt                | Description         |
| --------------------- | ------------------- |
| AWS Access Key ID     | Your IAM access key |
| AWS Secret Access Key | Your IAM secret key |
| Default region name   | e.g.,`eu-west-1`  |
| Default output format | e.g.,`json`       |

Verify your configuration:

```bash
aws sts get-caller-identity
```

### Infrastructure

The stack creates:

- VPC with public subnet
- Internet Gateway with routing
- Security Group (ports 22 and 49000)
- EC2 instance (t3.micro, Ubuntu 24.04 LTS)
- Systemd service for auto-start

### Manual Deployment

```bash
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name hello-world \
  --region eu-west-1
```

### CloudFormation Parameters

| Parameter     | Description                 | Default       |
| ------------- | --------------------------- | ------------- |
| `KeyName`   | EC2 Key Pair for SSH access | (none)        |
| `AllowedIP` | CIDR for SSH access         | `0.0.0.0/0` |

### Stack Outputs

After deployment, get all stack outputs:

```bash
aws cloudformation describe-stacks \
  --stack-name hello-world \
  --query 'Stacks[0].Outputs' \
  --output table
```

Get just the service URL:

```bash
aws cloudformation describe-stacks \
  --stack-name hello-world \
  --query 'Stacks[0].Outputs[?OutputKey==`ServiceURL`].OutputValue' \
  --output text
```

### Test Your Deployment

The EC2 instance needs 1-2 minutes to initialize after stack creation. Then test with:

```bash
# Get the URL and test
URL=$(aws cloudformation describe-stacks \
  --stack-name hello-world \
  --query 'Stacks[0].Outputs[?OutputKey==`ServiceURL`].OutputValue' \
  --output text)

curl $URL
```

Or open the URL directly in your browser:

```bash
echo $URL
# Example output: http://54.123.45.67:49000
```

### Destroy Stack

To delete all resources and avoid ongoing charges:

```bash
aws cloudformation delete-stack --stack-name hello-world
```

Monitor deletion progress:

```bash
aws cloudformation wait stack-delete-complete --stack-name hello-world
```

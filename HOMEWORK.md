# Session 4 Assignment: Containers & Docker Deployment

## Objective

In this assignment, you will deploy the **hello-world** application using GitHub Actions CI/CD pipeline and extend it by adding an additional containerized service. This exercise demonstrates the complete workflow from code to production deployment using containers.

---

## Prerequisites

Before starting this assignment, ensure you have:

- A GitHub account
- AWS Academy/Sandbox credentials configured in your forked repository
- Basic familiarity with SSH and command-line operations
- A web browser for capturing screenshots

---

## Step 1: Fork the Repository

### Task

Fork the instructor's hello-world repository to your own GitHub account.

### Instructions

1. Navigate to: `https://github.com/oriolrius/hello-world`
2. Click the **Fork** button in the top-right corner
3. Select your personal GitHub account as the destination
4. **Important:** Make sure to fork from the `v4.x` branch (this is the default branch for Session 4)

### Required Evidence

- Screenshot showing your forked repository on GitHub
- The screenshot must clearly show:
  - Your GitHub username in the repository path
  - The `v4.x` branch selected
  - The repository contents visible

---

## Step 2: Configure AWS Credentials

### Task

Set up AWS credentials as GitHub repository secrets to enable the deployment workflow.

### Instructions

1. Go to your forked repository on GitHub
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Add the following repository secrets:
   - `AWS_ACCESS_KEY_ID` - Your AWS access key
   - `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
   - `AWS_SESSION_TOKEN` - Your AWS session token (if using AWS Academy/Sandbox)

### Required Evidence

- Screenshot of the Actions secrets page showing the three secrets configured (values will be hidden, which is expected)

---

## Step 3: Run the GitHub Actions Workflow

### Task

Trigger the CI/CD pipeline and document the entire process.

### Instructions

1. Go to the **Actions** tab in your forked repository
2. Select the **Release** workflow from the left sidebar
3. Click **Run workflow** button
4. Select the `v4.x` branch
5. Click the green **Run workflow** button to start

### What Happens During Execution

The workflow executes the following jobs:

| Job         | Description                                                       | Dependencies  |
| ----------- | ----------------------------------------------------------------- | ------------- |
| `lint`    | Runs code quality checks using `ruff check` and `ruff format` | None          |
| `test`    | Executes unit tests using `pytest`                              | None          |
| `build`   | Builds the Python package using `uv build`                      | lint, test    |
| `release` | Creates a GitHub Release with the wheel artifact                  | build         |
| `docker`  | Builds and pushes the Docker image to GHCR                        | lint, test    |
| `deploy`  | Deploys infrastructure using AWS CloudFormation                   | build, docker |

### Required Evidence

Provide screenshots demonstrating successful execution:

1. **Workflow Run Overview**

   - Screenshot of the Actions tab showing the completed workflow run
   - All jobs should show green checkmarks
2. **Docker Image on GHCR**

   - Navigate to your repository's **Packages** section
   - Screenshot showing the `hello-world` container image published
   - The image tag should match the workflow run (e.g., `v4.x` or commit SHA)
3. **CloudFormation Stack**

   - Log into AWS Console
   - Navigate to **CloudFormation** > **Stacks**
   - Screenshot showing the `hello-world` stack with status `CREATE_COMPLETE`
4. **EC2 Instance Running**

   - Navigate to **EC2** > **Instances**
   - Screenshot showing the instance in `Running` state
   - Include the Public IP address in the screenshot

---

## Step 4: Document the CI/CD Process

### Task

Write a brief explanation of how the workflow operates.

### Required Documentation

In your submission, include written answers to the following:

1. **How did you trigger the workflow?**

   - Describe the steps you took to start the pipeline
2. **What is the purpose of each job?**

   - Explain what `lint`, `test`, `build`, `release`, `docker`, and `deploy` do
3. **How do the jobs depend on each other?**

   - Explain why some jobs run in parallel and others sequentially
4. **What credentials are needed and why?**

   - Explain why AWS credentials and GITHUB_TOKEN are required

---

## Step 5: Add the whoami Service

### Task

Connect to your EC2 instance and modify the Docker Compose configuration to run an additional service alongside hello-world.

### Instructions

1. **Connect to EC2 via SSH**

   ```bash
   ssh -i your-key.pem ec2-user@<EC2-PUBLIC-IP>
   ```
2. **Navigate to the application directory**

   ```bash
   cd /opt/hello-world
   ```
3. **View the current docker-compose.yml**

   ```bash
   cat docker-compose.yml
   ```
4. **Edit the docker-compose.yml file**

   ```bash
   sudo nano docker-compose.yml
   ```
5. **Add the whoami service**

   Modify the file to include both services. Your final `docker-compose.yml` should look similar to:

   ```yaml
   services:
     hello-world:
       image: ghcr.io/<YOUR-USERNAME>/hello-world:<TAG>
       ports:
         - "49000:49000"
       restart: unless-stopped

     whoami:
       image: traefik/whoami
       ports:
         - "49001:80"
       restart: unless-stopped
   ```

   **Note:** Replace `<YOUR-USERNAME>` and `<TAG>` with your actual values.
6. **Apply the changes**

   ```bash
   sudo docker compose up -d
   ```
7. **Verify both containers are running**

   ```bash
   sudo docker compose ps
   ```

### About traefik/whoami

The [traefik/whoami](https://github.com/traefik/whoami) is a tiny Go webserver that prints OS information and HTTP request details. It's commonly used for testing and debugging container deployments.

### Required Evidence

- Complete contents of your modified `docker-compose.yml` file
- Screenshot or output of `docker compose ps` showing both containers running

---

## Step 6: Verify Both Services

### Task

Confirm that both services are accessible from your browser.

### Instructions

1. Open your web browser
2. Test the hello-world service:
   ```
   http://<EC2-PUBLIC-IP>:49000
   ```
3. Test the whoami service:
   ```
   http://<EC2-PUBLIC-IP>:49001
   ```

### Required Evidence

Provide browser screenshots showing:

1. **hello-world service** (`http://<EC2-IP>:49000`)

   - The response from the hello-world application
   - URL bar must be visible showing the EC2 IP and port 49000
2. **whoami service** (`http://<EC2-IP>:49001`)

   - The whoami output displaying hostname, IP, and request headers
   - URL bar must be visible showing the EC2 IP and port 49001

---

## Submission Checklist

Before submitting, verify you have all required evidence:

| Item | Description                                    | Included? |
| ---- | ---------------------------------------------- | --------- |
| 1    | Screenshot of forked repository                | [ ]       |
| 2    | Screenshot of configured GitHub secrets        | [ ]       |
| 3    | Screenshot of completed workflow run           | [ ]       |
| 4    | Screenshot of Docker image on GHCR             | [ ]       |
| 5    | Screenshot of CloudFormation CREATE_COMPLETE   | [ ]       |
| 6    | Screenshot of EC2 instance running             | [ ]       |
| 7    | Written explanation of CI/CD process           | [ ]       |
| 8    | Modified docker-compose.yml contents           | [ ]       |
| 9    | Screenshot of docker compose ps output         | [ ]       |
| 10   | Browser screenshot of hello-world (port 49000) | [ ]       |
| 11   | Browser screenshot of whoami (port 49001)      | [ ]       |

---

## Submission Instructions

1. Compile all screenshots and written documentation into a single PDF
2. Ensure all screenshots are clearly labeled and legible
3. Upload your submission to **eCampus** under **Session 4 Assignment**
4. **Deadline:** Check eCampus for the specific due date

---

## Grading Criteria

| Criteria                                                     | Points        |
| ------------------------------------------------------------ | ------------- |
| Repository correctly forked                                  | 10            |
| Workflow executed successfully                               | 20            |
| All deployment evidence provided (GHCR, CloudFormation, EC2) | 20            |
| CI/CD process documentation quality                          | 15            |
| whoami service correctly added                               | 20            |
| Both services verified and accessible                        | 15            |
| **Total**                                              | **100** |

---

## Troubleshooting Tips

### Workflow fails at deploy job

- Verify AWS credentials are correctly set in repository secrets
- Check that your AWS session token hasn't expired (AWS Academy tokens expire after 4 hours)

### Cannot SSH to EC2

- Ensure security group allows SSH (port 22) from your IP
- Verify you're using the correct key pair

### whoami service not accessible

- Check that port 49001 is open in the EC2 security group
- Verify the container is running with `docker compose ps`
- Check container logs with `docker compose logs whoami`

### Docker compose command not found

- Use `docker compose` (with space) not `docker-compose` (with hyphen)
- The EC2 instance has Docker Compose V2 installed as a plugin

---

## Resources

- [hello-world repository](https://github.com/oriolrius/hello-world/tree/v4.x)
- [traefik/whoami documentation](https://github.com/traefik/whoami)
- [Docker Compose documentation](https://docs.docker.com/compose/)
- [GitHub Actions documentation](https://docs.github.com/en/actions)

---

**Good luck!**

If you have questions, post them in the eCampus forum or contact the instructor at joseporiol.rius@esade.edu

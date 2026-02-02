# Hello World - ECS Fargate Deployment Makefile
#
# Prerequisites:
#   - AWS CLI configured with appropriate credentials
#   - Docker installed and running
#   - CloudFormation stack deployed (run `make deploy` first)

.PHONY: help deploy delete ecr-login ecr-push redeploy status logs

# Configuration
STACK_NAME ?= hello-world
AWS_REGION ?= eu-west-1
TAG ?= latest-ecr-ecs-fargate
VERSION_SUFFIX := -ecr-ecs-fargate

help:
	@echo "Hello World ECS Fargate Deployment"
	@echo ""
	@echo "Usage: make [target] [TAG=version]"
	@echo ""
	@echo "NOTE: This branch uses version suffix: $(VERSION_SUFFIX)"
	@echo "      Example tag: v4.4.0$(VERSION_SUFFIX)"
	@echo ""
	@echo "Infrastructure:"
	@echo "  deploy      Deploy/update CloudFormation stack"
	@echo "  delete      Delete CloudFormation stack"
	@echo ""
	@echo "Docker:"
	@echo "  ecr-login   Login to ECR"
	@echo "  ecr-push    Build and push image to ECR (TAG=version)"
	@echo ""
	@echo "ECS:"
	@echo "  redeploy    Force new ECS deployment (same image)"
	@echo "  status      Show service status and task public IP"
	@echo "  logs        Tail CloudWatch logs"
	@echo ""
	@echo "Examples:"
	@echo "  make deploy"
	@echo "  make ecr-push TAG=v4.4.0$(VERSION_SUFFIX)"
	@echo "  make status"

# Get ECR URI from CloudFormation outputs
ECR_URI = $(shell aws cloudformation describe-stacks \
	--stack-name $(STACK_NAME) \
	--region $(AWS_REGION) \
	--query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryUri`].OutputValue' \
	--output text 2>/dev/null)

# Deploy CloudFormation stack
deploy:
	@echo "Deploying CloudFormation stack..."
	aws cloudformation deploy \
		--template-file infra/cloudformation.yml \
		--stack-name $(STACK_NAME) \
		--region $(AWS_REGION) \
		--capabilities CAPABILITY_NAMED_IAM \
		--parameter-overrides ImageTag=$(TAG)
	@echo "Stack deployed. ECR URI:"
	@aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME) \
		--region $(AWS_REGION) \
		--query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryUri`].OutputValue' \
		--output text

# Delete CloudFormation stack
delete:
	@echo "Deleting CloudFormation stack..."
	@echo "WARNING: This will delete all resources including the ECR repository!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	aws cloudformation delete-stack --stack-name $(STACK_NAME) --region $(AWS_REGION)
	aws cloudformation wait stack-delete-complete --stack-name $(STACK_NAME) --region $(AWS_REGION)
	@echo "Stack deleted."

# Login to ECR
ecr-login:
	@echo "Logging in to ECR..."
	aws ecr get-login-password --region $(AWS_REGION) | \
		docker login --username AWS --password-stdin $(ECR_URI)

# Build and push image to ECR
ecr-push: ecr-login
	@echo "Building and pushing image to ECR with tag: $(TAG)"
	docker build -t $(ECR_URI):$(TAG) -f docker/Dockerfile .
	docker push $(ECR_URI):$(TAG)
	@echo "Image pushed: $(ECR_URI):$(TAG)"

# Force new ECS deployment
redeploy:
	@echo "Forcing new ECS deployment..."
	aws ecs update-service \
		--cluster $(STACK_NAME) \
		--service $(STACK_NAME) \
		--region $(AWS_REGION) \
		--force-new-deployment \
		--query 'service.deployments[0].status' \
		--output text
	@echo "Deployment initiated. Run 'make status' to check progress."

# Show service status and task public IP
status:
	@echo "=== ECS Service Status ==="
	@aws ecs describe-services \
		--cluster $(STACK_NAME) \
		--services $(STACK_NAME) \
		--region $(AWS_REGION) \
		--query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount,Pending:pendingCount}' \
		--output table
	@echo ""
	@echo "=== Task Details ==="
	@TASK_ARN=$$(aws ecs list-tasks \
		--cluster $(STACK_NAME) \
		--service-name $(STACK_NAME) \
		--region $(AWS_REGION) \
		--query 'taskArns[0]' \
		--output text 2>/dev/null); \
	if [ "$$TASK_ARN" != "None" ] && [ -n "$$TASK_ARN" ]; then \
		aws ecs describe-tasks \
			--cluster $(STACK_NAME) \
			--tasks $$TASK_ARN \
			--region $(AWS_REGION) \
			--query 'tasks[0].{Status:lastStatus,Health:healthStatus,IP:attachments[0].details[?name==`privateIPv4Address`].value|[0]}' \
			--output table; \
		echo ""; \
		echo "=== Service URL ==="; \
		PUBLIC_IP=$$(aws ecs describe-tasks \
			--cluster $(STACK_NAME) \
			--tasks $$TASK_ARN \
			--region $(AWS_REGION) \
			--query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
			--output text | xargs -I {} aws ec2 describe-network-interfaces \
				--network-interface-ids {} \
				--region $(AWS_REGION) \
				--query 'NetworkInterfaces[0].Association.PublicIp' \
				--output text 2>/dev/null); \
		if [ -n "$$PUBLIC_IP" ] && [ "$$PUBLIC_IP" != "None" ]; then \
			echo "http://$$PUBLIC_IP:49000"; \
		else \
			echo "Public IP not yet assigned or task not running"; \
		fi; \
	else \
		echo "No running tasks found"; \
	fi

# Tail CloudWatch logs
logs:
	@echo "Tailing logs (Ctrl+C to stop)..."
	aws logs tail /ecs/hello-world --region $(AWS_REGION) --follow

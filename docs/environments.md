# Environments Proposal: dev, staging, production

## Real-World CD Implementation

### How Commits Flow Through Environments

In production systems, code flows through environments in a controlled pipeline:

```
Developer → PR → main branch → dev → staging → production
                     │            │        │         │
                     │            │        │         └── Manual approval + tag
                     │            │        └── Automated tests pass
                     │            └── Automated deploy on merge
                     └── CI tests (lint, unit tests)
```

### Git Branching Strategy (GitFlow/Trunk-Based)

```
main ────●────●────●────●────●────●──── (always deployable)
          \        \              \
           \        \              └── tag v1.2.0 → production
            \        └── staging deploy (after QA approval)
             └── feature/xyz → PR → merge → auto-deploy to dev
```

### How GitHub Actions Determines Target Environment

There are **three common patterns** used in real-world deployments:

---

#### Pattern 1: Branch-Based Deployment (Simple)

**Used by:** GitLab, Netlify, Vercel, Heroku, many startups

**Real-world examples:**

- **GitLab** - Their [Auto DevOps](https://docs.gitlab.com/ee/topics/autodevops/) uses branch names to determine environments
- **Netlify/Vercel** - `main` → production, PRs → preview environments
- **Heroku Pipelines** - `development` → `staging` → `production` apps linked to branches

Each branch maps to an environment automatically:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches:
      - main          # → dev (every commit)
      - release/*     # → staging (release candidates)
    tags:
      - 'v*'          # → production (releases)

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Determine environment
        id: env
        run: |
          if [[ "${{ github.ref }}" == refs/tags/v* ]]; then
            echo "environment=production" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == refs/heads/release/* ]]; then
            echo "environment=staging" >> $GITHUB_OUTPUT
          else
            echo "environment=dev" >> $GITHUB_OUTPUT
          fi

      - name: Deploy to ${{ steps.env.outputs.environment }}
        run: ./deploy.sh ${{ steps.env.outputs.environment }}
```

**Flow:**

```
git push origin main           → deploys to dev
git push origin release/1.2    → deploys to staging
git tag v1.2.0 && git push --tags → deploys to production
```

---

#### Pattern 2: Progressive Deployment (Recommended)

**Used by:** Google, Spotify, Netflix, Airbnb, most mature tech companies

**Real-world examples:**

- **Google** - [Site Reliability Engineering book](https://sre.google/sre-book/release-engineering/) describes progressive rollouts with automated canaries
- **Spotify** - Uses [Backstage](https://backstage.io/) with progressive delivery pipelines
- **Netflix** - [Spinnaker](https://spinnaker.io/) (which they created) implements progressive deployment with automated canary analysis
- **Airbnb** - Documented in their [engineering blog](https://medium.com/airbnb-engineering) - staged rollouts with feature flags
- **GitHub** - Uses [GitHub Actions environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) with protection rules (this exact pattern)

**Open Source References:**

- [Argo Rollouts](https://argoproj.github.io/rollouts/) - Kubernetes progressive delivery controller
- [Flagger](https://flagger.app/) - Progressive delivery for Kubernetes (Weaveworks)
- [Spinnaker](https://spinnaker.io/) - Multi-cloud continuous delivery (Netflix)

A single workflow deploys to **all environments sequentially**, with gates between them:

```yaml
# .github/workflows/deploy.yml
name: Progressive Deploy

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  # ─────────────────────────────────────────────────────────
  # STAGE 1: Build (runs always)
  # ─────────────────────────────────────────────────────────
  build:
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4

      - name: Build and push Docker image
        id: meta
        run: |
          docker build -t ghcr.io/org/app:${{ github.sha }} .
          docker push ghcr.io/org/app:${{ github.sha }}
          echo "tags=ghcr.io/org/app:${{ github.sha }}" >> $GITHUB_OUTPUT

  # ─────────────────────────────────────────────────────────
  # STAGE 2: Deploy to DEV (automatic on main)
  # ─────────────────────────────────────────────────────────
  deploy-dev:
    needs: build
    runs-on: ubuntu-latest
    environment: dev                    # ← GitHub Environment
    steps:
      - name: Deploy to dev
        run: |
          kubectl set image deployment/app app=${{ needs.build.outputs.image_tag }}
        env:
          KUBECONFIG: ${{ secrets.DEV_KUBECONFIG }}

      - name: Run smoke tests
        run: |
          sleep 30  # wait for rollout
          curl -f http://dev.example.com/health || exit 1

  # ─────────────────────────────────────────────────────────
  # STAGE 3: Deploy to STAGING (after dev succeeds)
  # ─────────────────────────────────────────────────────────
  deploy-staging:
    needs: [build, deploy-dev]
    runs-on: ubuntu-latest
    environment: staging                # ← Requires reviewer approval
    steps:
      - name: Deploy to staging
        run: |
          kubectl set image deployment/app app=${{ needs.build.outputs.image_tag }}
        env:
          KUBECONFIG: ${{ secrets.STAGING_KUBECONFIG }}

      - name: Run integration tests
        run: ./run-integration-tests.sh http://staging.example.com

      - name: Run performance tests
        run: ./run-perf-tests.sh http://staging.example.com

  # ─────────────────────────────────────────────────────────
  # STAGE 4: Deploy to PRODUCTION (only on tags, manual approval)
  # ─────────────────────────────────────────────────────────
  deploy-production:
    needs: [build, deploy-staging]
    if: startsWith(github.ref, 'refs/tags/v')    # ← Only on version tags
    runs-on: ubuntu-latest
    environment: production             # ← Requires approval + wait timer
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/app app=${{ needs.build.outputs.image_tag }}
        env:
          KUBECONFIG: ${{ secrets.PROD_KUBECONFIG }}

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/app --timeout=300s
          curl -f http://app.example.com/health || exit 1

      - name: Notify success
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -d '{"text": "✅ v${{ github.ref_name }} deployed to production"}'
```

**GitHub Environment Configuration:**

| Environment    | Protection Rules                              |
| -------------- | --------------------------------------------- |
| `dev`        | None - auto-deploy                            |
| `staging`    | Required reviewers: QA team                   |
| `production` | Required reviewers: DevOps + 15min wait timer |

---

#### Pattern 3: Promotion-Based Deployment (Enterprise)

**Used by:** Amazon, Microsoft, large enterprises, regulated industries (finance, healthcare)

**Real-world examples:**

- **Amazon** - Described in [AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_tracking_change_management_planned_changemgmt.html) - immutable artifacts promoted through environments
- **Microsoft Azure DevOps** - [Release pipelines](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/) with manual approvals and artifact promotion
- **JFrog Artifactory** - [Release bundles](https://jfrog.com/help/r/jfrog-distribution-documentation/release-bundles) - promote immutable artifacts between repos (dev → staging → prod)
- **Financial Services** - Required by SOX/PCI compliance - same artifact must be deployed to prod that was tested in staging

**Open Source References:**

- [JFrog Artifactory](https://jfrog.com/artifactory/) - Artifact promotion between repositories
- [Harbor](https://goharbor.io/) - Container registry with artifact promotion
- [Nexus Repository](https://www.sonatype.com/products/nexus-repository) - Artifact lifecycle management
- [AWS CodePipeline](https://aws.amazon.com/codepipeline/) - Manual approval stages between environments

**Why enterprises prefer this:**

- **Auditability** - Same SHA deployed everywhere, traceable
- **Compliance** - Proof that prod artifact was tested in staging
- **Rollback** - Simply redeploy previous artifact

Artifacts are **built once** and **promoted** through environments:

```yaml
# .github/workflows/build.yml (runs on every commit)
name: Build
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Build and test
        run: |
          docker build -t ghcr.io/org/app:${{ github.sha }} .
          docker push ghcr.io/org/app:${{ github.sha }}

      - name: Store artifact reference
        run: |
          echo "${{ github.sha }}" > artifact-version.txt
          # Store in artifact registry or database
```

```yaml
# .github/workflows/promote.yml (manual trigger)
name: Promote

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Image SHA or tag to promote'
        required: true
      from_env:
        type: choice
        options: [dev, staging]
      to_env:
        type: choice
        options: [staging, production]

jobs:
  validate-promotion:
    runs-on: ubuntu-latest
    steps:
      - name: Check version exists in source environment
        run: |
          # Verify the version was successfully deployed to from_env
          kubectl get deployment/app -n ${{ inputs.from_env }} \
            -o jsonpath='{.spec.template.spec.containers[0].image}' | \
            grep ${{ inputs.version }} || exit 1

      - name: Check test results
        run: |
          # Query test results from test management system
          ./check-test-results.sh ${{ inputs.version }} ${{ inputs.from_env }}

  promote:
    needs: validate-promotion
    runs-on: ubuntu-latest
    environment: ${{ inputs.to_env }}
    steps:
      - name: Promote to ${{ inputs.to_env }}
        run: |
          kubectl set image deployment/app \
            app=ghcr.io/org/app:${{ inputs.version }} \
            -n ${{ inputs.to_env }}
```

---

### Validation Gates Between Environments

**Industry References:**

- **Google Testing Blog** - [Testing at Google Scale](https://testing.googleblog.com/)
- **Martin Fowler** - [Deployment Pipeline](https://martinfowler.com/bliki/DeploymentPipeline.html)
- **Continuous Delivery book** - [Jez Humble &amp; David Farley](https://continuousdelivery.com/)

**Testing Tools Used:**

- **Smoke/Health:** curl, httpie, [k6](https://k6.io/)
- **Integration:** [Postman/Newman](https://www.postman.com/), [REST Assured](https://rest-assured.io/)
- **E2E:** [Playwright](https://playwright.dev/), [Cypress](https://www.cypress.io/), [Selenium](https://www.selenium.dev/)
- **Performance:** [k6](https://k6.io/), [Locust](https://locust.io/), [Gatling](https://gatling.io/)
- **Security:** [Trivy](https://trivy.dev/), [Snyk](https://snyk.io/), [OWASP ZAP](https://www.zaproxy.org/)

#### What Gets Validated at Each Stage

| Stage                     | Validation                                           | Automated? |
| ------------------------- | ---------------------------------------------------- | ---------- |
| **PR → main**      | Lint, unit tests, security scan                      | ✅ Yes     |
| **main → dev**     | Smoke tests, deployment health                       | ✅ Yes     |
| **dev → staging**  | Integration tests, E2E tests, performance            | ✅ Yes     |
| **staging → prod** | Manual QA sign-off, security review, change approval | ❌ No      |

#### Example Validation Job

```yaml
validate-before-promotion:
  runs-on: ubuntu-latest
  steps:
    # 1. Health check
    - name: Verify deployment is healthy
      run: |
        for i in {1..30}; do
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$ENV_URL/health)
          if [ "$STATUS" == "200" ]; then
            echo "✅ Health check passed"
            exit 0
          fi
          sleep 10
        done
        echo "❌ Health check failed"
        exit 1

    # 2. Smoke tests
    - name: Run smoke tests
      run: |
        npm run test:smoke -- --url=http://$ENV_URL

    # 3. Integration tests (staging only)
    - name: Run integration tests
      if: env.ENVIRONMENT == 'staging'
      run: |
        npm run test:integration -- --url=http://$ENV_URL

    # 4. Performance baseline (staging only)
    - name: Performance test
      if: env.ENVIRONMENT == 'staging'
      run: |
        k6 run --out json=perf-results.json tests/load-test.js
        ./check-perf-regression.sh perf-results.json

    # 5. Security scan
    - name: Security scan
      run: |
        trivy image ghcr.io/org/app:${{ github.sha }}
```

---

### Infrastructure Provisioning Strategies

A common question: **Do companies provision real infrastructure during CI/CD testing?** Yes — and there are several patterns depending on cost, speed, and confidence requirements.

#### The Testing Pyramid and Infrastructure

```
                    ▲
                   /│\        E2E Tests (Real Infra)
                  / │ \       - Slowest, most expensive
                 /  │  \      - Highest confidence
                /───┼───\     - Fewer tests
               /    │    \
              / Integration \  Integration Tests (Real or Mocked Infra)
             /      │       \ - Medium speed/cost
            /───────┼────────\
           /        │         \
          /    Unit Tests      \ Unit Tests (No Infra)
         /          │           \ - Fastest, cheapest
        /───────────┼────────────\ - Most tests
       ▼────────────┴─────────────▼
```

**Key insight:** Real infrastructure is typically provisioned only for the top of the pyramid (integration and E2E tests), not for unit tests.

---

#### Pattern A: Ephemeral Environments (Per PR/Branch)

**Used by:** Vercel, Netlify, Shopify, GitHub, Stripe, Airbnb

**How it works:** Spin up isolated, real infrastructure for each PR. Tear down after tests complete or PR merges.

**Real-world examples:**

- **Vercel/Netlify** - Every PR gets a unique preview URL with real deployment
- **Shopify** - Full ephemeral environments per PR using their internal "Spin" tool
- **GitHub** - Review labs create K8s namespaces per PR
- **Stripe** - Isolated test environments for payment flow integration testing
- **Airbnb** - Documented in [engineering blog](https://medium.com/airbnb-engineering) - ephemeral staging per feature branch

```yaml
# Ephemeral environment pattern
name: PR Preview Environment

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  deploy-preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create ephemeral namespace
        run: |
          kubectl create namespace pr-${{ github.event.number }} --dry-run=client -o yaml | kubectl apply -f -

      - name: Deploy to ephemeral environment
        run: |
          helm upgrade --install hello-world ./charts/hello-world \
            --namespace pr-${{ github.event.number }} \
            --set image.tag=${{ github.sha }} \
            --set ingress.host=pr-${{ github.event.number }}.preview.example.com

      - name: Run E2E tests against real infrastructure
        run: |
          npm run test:e2e -- --url=https://pr-${{ github.event.number }}.preview.example.com

      - name: Post preview URL to PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚀 Preview: https://pr-${{ github.event.number }}.preview.example.com'
            })

  cleanup-preview:
    runs-on: ubuntu-latest
    if: github.event.action == 'closed'
    steps:
      - name: Delete ephemeral namespace
        run: |
          kubectl delete namespace pr-${{ github.event.number }} --ignore-not-found
```

**Pros:**

- Complete isolation between PRs
- Tests against real infrastructure configuration
- No "works on my machine" issues
- QA can review before merge

**Cons:**

- Expensive (multiply infrastructure costs by active PRs)
- Slower CI (provisioning takes time)
- Complex cleanup logic
- Resource quotas needed to prevent runaway costs

---

#### Pattern B: Shared Test Environments (Most Common)

**Used by:** Most companies, especially cost-conscious or early-stage

**How it works:** Maintain persistent dev/staging environments. CI deploys to shared environment and runs tests.

```yaml
# Shared environment pattern
name: Integration Tests

on:
  push:
    branches: [main]

jobs:
  deploy-and-test:
    runs-on: ubuntu-latest
    environment: dev
    concurrency:
      group: dev-deployment    # ← Prevents concurrent deploys to shared env
      cancel-in-progress: false
    steps:
      - name: Deploy to shared dev
        run: |
          kubectl apply -k k8s/overlays/dev

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/hello-world -n hello-world-dev --timeout=300s

      - name: Run integration tests
        run: |
          npm run test:integration -- --url=https://dev.example.com
```

**Pros:**

- Lower cost (one environment, not N)
- Faster feedback (no provisioning)
- Simpler infrastructure

**Cons:**

- Tests can conflict if multiple PRs deploy simultaneously
- Need concurrency controls
- Environment can become "dirty" over time

**Mitigation strategies:**

- Use `concurrency` groups to serialize deployments
- Implement test isolation (unique test data per run)
- Schedule nightly environment resets

---

#### Pattern C: Hybrid Approach (Recommended)

**Used by:** Netflix, Google, Spotify, mature engineering orgs

**How it works:** Different infrastructure strategies at different pipeline stages.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HYBRID PROVISIONING STRATEGY                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Stage 1: PR Created                                                        │
│  └── Unit tests + lint (NO infrastructure)                                  │
│  └── Contract tests with mocks (NO infrastructure)                          │
│  └── Security scanning (NO infrastructure)                                  │
│  └── ⏱️ ~2 minutes                                                          │
│                                                                             │
│  Stage 2: PR Ready for Review                                               │
│  └── OPTIONAL: Spin up ephemeral preview environment                        │
│  └── Run E2E smoke tests                                                    │
│  └── ⏱️ ~5-10 minutes                                                       │
│                                                                             │
│  Stage 3: PR Merged to main                                                 │
│  └── Deploy to SHARED dev environment                                       │
│  └── Run full integration test suite                                        │
│  └── ⏱️ ~10-15 minutes                                                      │
│                                                                             │
│  Stage 4: Promote to staging                                                │
│  └── Deploy to SHARED staging environment                                   │
│  └── Run E2E + performance + security tests                                 │
│  └── ⏱️ ~20-30 minutes                                                      │
│                                                                             │
│  Stage 5: Release to production                                             │
│  └── Deploy to SHARED production (canary first)                             │
│  └── Monitor metrics, auto-rollback on errors                               │
│  └── ⏱️ ~15 minutes + monitoring window                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

```yaml
# Hybrid approach workflow
name: CI/CD Pipeline

on:
  pull_request:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  # ─────────────────────────────────────────────────────────
  # STAGE 1: No infrastructure (runs on every commit)
  # ─────────────────────────────────────────────────────────
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint
      - run: npm run test:unit
      - run: npm run test:contract  # Pact/contract tests with mocks

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'

  # ─────────────────────────────────────────────────────────
  # STAGE 2: Ephemeral preview (PRs only, on-demand)
  # ─────────────────────────────────────────────────────────
  preview-environment:
    if: github.event_name == 'pull_request' && contains(github.event.pull_request.labels.*.name, 'needs-preview')
    needs: [unit-tests, security-scan]
    runs-on: ubuntu-latest
    steps:
      - name: Deploy ephemeral environment
        run: |
          # Provision real infrastructure for this PR
          kubectl create namespace pr-${{ github.event.number }}
          kubectl apply -k k8s/overlays/preview --namespace pr-${{ github.event.number }}

      - name: Run E2E smoke tests
        run: npm run test:e2e:smoke

  # ─────────────────────────────────────────────────────────
  # STAGE 3: Shared dev (main branch only)
  # ─────────────────────────────────────────────────────────
  deploy-dev:
    if: github.ref == 'refs/heads/main'
    needs: [unit-tests, security-scan]
    runs-on: ubuntu-latest
    environment: dev
    concurrency:
      group: dev-environment
    steps:
      - name: Deploy to shared dev
        run: kubectl apply -k k8s/overlays/dev

      - name: Full integration tests
        run: npm run test:integration

  # ─────────────────────────────────────────────────────────
  # STAGE 4+: Shared staging/production (as in Pattern 2)
  # ─────────────────────────────────────────────────────────
```

---

#### Pattern D: LocalStack / Mocked Infrastructure

**Used by:** Cost-conscious teams, early-stage startups, local development

**How it works:** Use tools that emulate cloud services locally or in CI without real cloud costs.

**Tools:**

| Tool                                                 | Emulates                         | Best For               |
| ---------------------------------------------------- | -------------------------------- | ---------------------- |
| [LocalStack](https://localstack.cloud/)                 | AWS (S3, DynamoDB, Lambda, etc.) | AWS-heavy apps         |
| [MinIO](https://min.io/)                                | S3-compatible storage            | Object storage         |
| [Testcontainers](https://testcontainers.com/)           | Databases, queues, caches        | Integration tests      |
| [Kind](https://kind.sigs.k8s.io/) / [k3d](https://k3d.io/) | Kubernetes clusters              | K8s deployments        |
| [WireMock](https://wiremock.org/)                       | HTTP APIs                        | External service mocks |

```yaml
# LocalStack example for AWS testing without real AWS
integration-tests:
  runs-on: ubuntu-latest
  services:
    localstack:
      image: localstack/localstack:latest
      ports:
        - 4566:4566
      env:
        SERVICES: s3,dynamodb,sqs
  steps:
    - uses: actions/checkout@v4

    - name: Create test resources
      run: |
        aws --endpoint-url=http://localhost:4566 s3 mb s3://test-bucket
        aws --endpoint-url=http://localhost:4566 dynamodb create-table ...

    - name: Run tests against LocalStack
      env:
        AWS_ENDPOINT_URL: http://localhost:4566
      run: npm run test:integration
```

**Pros:**

- Zero cloud costs
- Fast (no network latency to cloud)
- Works offline
- Deterministic (no external state)

**Cons:**

- Not 100% feature parity with real services
- Can miss cloud-specific edge cases
- Still need real infrastructure tests before production

---

#### When to Provision Real Infrastructure: Decision Matrix

| Test Type         | Infrastructure      | When                    | Examples                       |
| ----------------- | ------------------- | ----------------------- | ------------------------------ |
| Unit tests        | None                | Always                  | Jest, pytest, go test          |
| Contract tests    | Mocked              | Always                  | Pact, Spring Cloud Contract    |
| Component tests   | Containers          | PR + main               | Testcontainers, Docker Compose |
| Integration tests | Shared dev          | main branch             | Against real dev environment   |
| E2E tests         | Shared or ephemeral | Pre-merge or post-merge | Playwright, Cypress            |
| Performance tests | Dedicated staging   | Release candidates      | k6, Gatling                    |
| Security tests    | Staging mirror      | Release candidates      | OWASP ZAP, Burp                |
| Chaos tests       | Production          | Controlled windows      | Chaos Monkey, Litmus           |

---

#### Cost vs. Confidence Trade-offs

```
High ──┬──────────────────────────────────────────────────────────────┐
       │                                          Ephemeral per PR    │
       │                                               ●              │
  C    │                                                              │
  o    │                         Shared + Ephemeral                   │
  n    │                         (Hybrid) ●                           │
  f    │                                                              │
  i    │                    Shared Staging                            │
  d    │                         ●                                    │
  e    │                                                              │
  n    │           LocalStack/Mocks                                   │
  c    │                ●                                             │
  e    │                                                              │
       │     Unit Tests Only                                          │
       │          ●                                                   │
Low ───┴──────────────────────────────────────────────────────────────┘
       Low ◄─────────────────── Cost ──────────────────────────► High
```

**Industry benchmarks (approximate):**

| Company Size          | Typical Strategy             | Monthly Infra Cost (non-prod) |
| --------------------- | ---------------------------- | ----------------------------- |
| Startup (<20 eng)     | Shared staging only          | $100-500                      |
| Growth (20-100 eng)   | Shared + on-demand ephemeral | $1,000-5,000                  |
| Enterprise (100+ eng) | Full ephemeral per PR        | $10,000-50,000+               |

---

#### Real Company Approaches

| Company           | Strategy                    | Details                                                                                                       |
| ----------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Netflix** | Hybrid + Production testing | Uses Spinnaker for progressive delivery. Tests against production with traffic shadowing and canary analysis. |
| **Spotify** | Ephemeral K8s namespaces    | Creates isolated namespaces per PR using Backstage. Auto-cleanup after 24h.                                   |
| **Shopify** | Full ephemeral (Spin)       | Internal tool "Spin" provisions complete environments per developer/PR.                                       |
| **GitHub**  | Ephemeral "Review Labs"     | K8s namespaces with real databases per PR. Uses GitHub Actions.                                               |
| **Stripe**  | Ephemeral for payments      | Critical payment flows get dedicated test infrastructure.                                                     |
| **Google**  | Mocks + shared + prod       | Heavy use of hermetic tests (mocks), shared staging, and production canaries.                                 |
| **Amazon**  | Cell-based isolation        | Each team has isolated "cells" that can be provisioned on-demand.                                             |
| **Airbnb**  | Feature-flag + staging      | Heavy use of feature flags to test in shared staging safely.                                                  |

---

#### Best Practices Summary

1. **Don't provision infrastructure for unit tests** - Use mocks, keep them fast
2. **Use containers for database/queue integration tests** - Testcontainers is your friend
3. **Shared environments are fine for most teams** - Use concurrency controls
4. **Ephemeral environments are a luxury, not a requirement** - Only if budget allows
5. **Label-triggered previews** - Don't spin up ephemeral envs for every PR, use labels like `needs-preview`
6. **Set resource quotas** - Prevent runaway costs from orphaned environments
7. **Auto-cleanup with TTL** - Delete ephemeral environments after 24-48h automatically
8. **Test in production (carefully)** - Feature flags, canaries, and traffic shadowing are production testing done right

---

### Real-World Workflow Visualization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEVELOPER WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Developer pushes to feature branch                                      │
│     └── CI runs: lint, test, build (no deploy)                             │
│                                                                             │
│  2. PR created → PR merged to main                                          │
│     └── CI runs: lint, test, build                                         │
│     └── CD auto-deploys to DEV                                             │
│         └── Smoke tests run automatically                                  │
│         └── If smoke tests fail → alert, block promotion                   │
│                                                                             │
│  3. Dev validated → Promote to STAGING (manual or scheduled)                │
│     └── Requires: QA team approval (GitHub Environment protection)         │
│     └── Integration tests run                                              │
│     └── E2E tests run                                                      │
│     └── Performance tests run                                              │
│     └── If any test fails → block promotion, notify team                   │
│                                                                             │
│  4. Staging validated → Create release tag                                  │
│     └── git tag v1.2.3 && git push --tags                                  │
│                                                                             │
│  5. Tag pushed → Promote to PRODUCTION                                      │
│     └── Requires: DevOps approval + 15min wait timer                       │
│     └── Canary deployment (10% traffic)                                    │
│     └── Monitor error rates for 10 minutes                                 │
│     └── Full rollout (100% traffic)                                        │
│     └── Post-deploy verification                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### GitHub Environment Protection Rules

Configure in: **Settings → Environments → [env name] → Protection rules**

| Rule                | Dev      | Staging                 | Production     |
| ------------------- | -------- | ----------------------- | -------------- |
| Required reviewers  | ❌       | ✅ 1 reviewer           | ✅ 2 reviewers |
| Wait timer          | ❌       | ❌                      | ✅ 15 minutes  |
| Deployment branches | `main` | `main`, `release/*` | tags only      |
| Secrets             | DEV_*    | STAGING_*               | PROD_*         |

---

### Rollback Strategy

When a deployment fails in production:

```yaml
rollback:
  runs-on: ubuntu-latest
  if: failure()
  steps:
    - name: Rollback to previous version
      run: |
        kubectl rollout undo deployment/app -n production

    - name: Notify team
      run: |
        curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
          -d '{"text": "⚠️ Production deployment failed, rolled back automatically"}'
```

---

### Summary: When Does Each Environment Get Deployed?

| Trigger               | Dev     | Staging           | Production        |
| --------------------- | ------- | ----------------- | ----------------- |
| Push to `main`      | ✅ Auto | ❌                | ❌                |
| Push to `release/*` | ❌      | ✅ After approval | ❌                |
| Push tag `v*`       | ❌      | ❌                | ✅ After approval |
| Manual dispatch       | ✅      | ✅ After approval | ✅ After approval |
| Scheduled (nightly)   | ✅      | Optional          | ❌ Never          |

---

## Overview

This proposal outlines how to introduce environment separation (dev, staging, production) across all version branches of the hello-world project.

## Environment Strategy

| Environment          | Purpose                                 | Deployment Trigger             |
| -------------------- | --------------------------------------- | ------------------------------ |
| **dev**        | Development/testing, frequent deploys   | Push to branch, manual         |
| **staging**    | Pre-production validation, mirrors prod | PR merge, manual               |
| **production** | Live traffic, stable releases           | Tag push (v*), manual approval |

---

## v1.x - Local Development Only

**Current state:** No deployment infrastructure.

**Recommendation:** Not applicable - v1.x is for local development only. Environments don't apply.

**Optional enhancement:** Add environment variable support in the application:

```python
# src/hello_world/__init__.py
import os
ENV = os.getenv("HELLO_WORLD_ENV", "development")
```

---

## v2.x - CI/CD with GitHub Actions

**Current state:** Single release workflow triggered on tags.

**Recommendation:** Use GitHub Environments with workflow inputs.

### Implementation

1. **Create GitHub Environments** (Settings → Environments):

   - `dev` - no protection rules
   - `staging` - require reviewers
   - `production` - require reviewers + wait timer
2. **Modify workflow** to accept environment input:

```yaml
# .github/workflows/release.yml
on:
  push:
    tags: ['v*']
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [dev, staging, production]
        default: dev

jobs:
  release:
    environment: ${{ inputs.environment || 'production' }}
    # ... rest of workflow
```

3. **Environment-specific artifacts:**
   - Different version suffixes: `v2.1.0-dev`, `v2.1.0-staging`, `v2.1.0`

### Files to create/modify

- `.github/workflows/release.yml` - add environment input
- No infrastructure changes needed (v2.x only builds artifacts)

---

## v3.x - CloudFormation + EC2

**Current state:** Single CloudFormation stack deploys to one EC2 instance.

**Recommendation:** Use separate CloudFormation stacks per environment with parameterized templates.

### Implementation

1. **Stack naming convention:**

   - `hello-world-dev`
   - `hello-world-staging`
   - `hello-world-production`
2. **Environment-specific parameters:**

```yaml
# infra/environments/dev.json
[
  { "ParameterKey": "InstanceType", "ParameterValue": "t3.micro" },
  { "ParameterKey": "Environment", "ParameterValue": "dev" }
]

# infra/environments/production.json
[
  { "ParameterKey": "InstanceType", "ParameterValue": "t3.small" },
  { "ParameterKey": "Environment", "ParameterValue": "production" }
]
```

3. **Add Environment parameter to CloudFormation:**

```yaml
# infra/cloudformation.yml
Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, production]
    Default: dev

Resources:
  EC2Instance:
    Properties:
      Tags:
        - Key: Environment
          Value: !Ref Environment
```

4. **Deploy commands:**

```bash
# Dev
aws cloudformation deploy \
  --stack-name hello-world-dev \
  --template-file infra/cloudformation.yml \
  --parameter-overrides file://infra/environments/dev.json

# Production
aws cloudformation deploy \
  --stack-name hello-world-production \
  --template-file infra/cloudformation.yml \
  --parameter-overrides file://infra/environments/production.json
```

### Files to create

- `infra/environments/dev.json`
- `infra/environments/staging.json`
- `infra/environments/production.json`
- Modify `infra/cloudformation.yml` - add Environment parameter
- Modify `.github/workflows/deploy.yml` - add environment matrix/input

---

## v4.x - CloudFormation + Ansible

**Current state:** CloudFormation creates EC2, Ansible configures it.

**Recommendation:** Use Ansible inventory files per environment + CloudFormation stacks.

### Implementation

1. **Ansible inventory per environment:**

```ini
# deploy/inventory/dev.ini
[hello_world]
dev-server ansible_host={{ lookup('env', 'DEV_EC2_IP') }}

[hello_world:vars]
hello_world_env=dev
hello_world_port=49000
```

```ini
# deploy/inventory/production.ini
[hello_world]
prod-server ansible_host={{ lookup('env', 'PROD_EC2_IP') }}

[hello_world:vars]
hello_world_env=production
hello_world_port=49000
hello_world_replicas=2
```

2. **Environment-specific variables:**

```yaml
# deploy/group_vars/dev.yml
hello_world_version: "latest"
hello_world_debug: true

# deploy/group_vars/production.yml
hello_world_version: "v4.1.0"
hello_world_debug: false
```

3. **Deploy commands:**

```bash
# Dev
ansible-playbook -i deploy/inventory/dev.ini deploy/playbook.yml

# Production
ansible-playbook -i deploy/inventory/production.ini deploy/playbook.yml
```

### Files to create

- `deploy/inventory/dev.ini`
- `deploy/inventory/staging.ini`
- `deploy/inventory/production.ini`
- `deploy/group_vars/dev.yml`
- `deploy/group_vars/staging.yml`
- `deploy/group_vars/production.yml`
- `infra/environments/*.json` (same as v3.x)

---

## v5.x - Docker + Docker Compose

**Current state:** Single Docker Compose deployment on EC2.

**Recommendation:** Use environment-specific compose files with variable substitution.

### Implementation

1. **Base compose + environment overrides:**

```yaml
# docker/docker-compose.yml (base)
services:
  hello-world:
    image: ghcr.io/oriolrius/hello-world:${IMAGE_TAG:-latest}
    ports:
      - "${PORT:-49000}:49000"
    environment:
      - HELLO_WORLD_ENV=${ENVIRONMENT:-dev}
```

```yaml
# docker/docker-compose.dev.yml
services:
  hello-world:
    environment:
      - DEBUG=true

# docker/docker-compose.production.yml
services:
  hello-world:
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 256M
    restart: always
```

2. **Environment files:**

```bash
# docker/.env.dev
ENVIRONMENT=dev
IMAGE_TAG=latest
PORT=49000

# docker/.env.production
ENVIRONMENT=production
IMAGE_TAG=v5.2.0
PORT=49000
```

3. **Deploy commands:**

```bash
# Dev
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml \
  --env-file docker/.env.dev up -d

# Production
docker compose -f docker/docker-compose.yml -f docker/docker-compose.production.yml \
  --env-file docker/.env.production up -d
```

### Files to create

- `docker/docker-compose.dev.yml`
- `docker/docker-compose.staging.yml`
- `docker/docker-compose.production.yml`
- `docker/.env.dev`
- `docker/.env.staging`
- `docker/.env.production`
- Ansible inventory per environment (same as v4.x)

---

## v6.x - EKS + Kubernetes

**Current state:** Single EKS cluster with one namespace.

**Recommendation:** Use Kustomize overlays for environment-specific configurations.

### Implementation Options

#### Option A: Single Cluster, Multiple Namespaces (Recommended for learning)

```
k8s/
├── base/
│   ├── kustomization.yaml
│   ├── namespace.yaml
│   ├── deployment.yaml
│   └── service.yaml
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   └── patch-replicas.yaml
    ├── staging/
    │   ├── kustomization.yaml
    │   └── patch-replicas.yaml
    └── production/
        ├── kustomization.yaml
        ├── patch-replicas.yaml
        └── patch-resources.yaml
```

**Base kustomization:**

```yaml
# k8s/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
  - deployment.yaml
  - service.yaml
```

**Dev overlay:**

```yaml
# k8s/overlays/dev/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: hello-world-dev
namePrefix: dev-
resources:
  - ../../base
patches:
  - patch-replicas.yaml
images:
  - name: ghcr.io/oriolrius/hello-world
    newTag: latest
```

```yaml
# k8s/overlays/dev/patch-replicas.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-world
spec:
  replicas: 1
```

**Production overlay:**

```yaml
# k8s/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: hello-world-production
namePrefix: prod-
resources:
  - ../../base
patches:
  - patch-replicas.yaml
  - patch-resources.yaml
images:
  - name: ghcr.io/oriolrius/hello-world
    newTag: v6.3.0
```

**Deploy commands:**

```bash
# Dev
kubectl apply -k k8s/overlays/dev

# Staging
kubectl apply -k k8s/overlays/staging

# Production
kubectl apply -k k8s/overlays/production
```

#### Option B: Separate Clusters (Production-grade)

| Cluster                    | Environments |
| -------------------------- | ------------ |
| `esade-teaching-dev`     | dev          |
| `esade-teaching-staging` | staging      |
| `esade-teaching-prod`    | production   |

More expensive but provides complete isolation.

### Files to create

- `k8s/base/` - move existing manifests here
- `k8s/overlays/dev/`
- `k8s/overlays/staging/`
- `k8s/overlays/production/`
- Modify `.github/workflows/release.yml` - add environment input and kustomize

---

## GitHub Actions Workflow Pattern (All Versions)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        description: Target environment
        options:
          - dev
          - staging
          - production
        default: dev
  push:
    branches:
      - main        # → dev
      - release/*   # → staging
    tags:
      - 'v*'        # → production

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment || (github.ref_type == 'tag' && 'production') || (startsWith(github.ref, 'refs/heads/release/') && 'staging') || 'dev' }}
    steps:
      - name: Deploy to ${{ env.ENVIRONMENT }}
        run: |
          echo "Deploying to ${{ env.ENVIRONMENT }}"
          # Environment-specific deployment logic
```

---

## Summary by Branch

| Branch | Infrastructure           | Environment Strategy                  |
| ------ | ------------------------ | ------------------------------------- |
| v1.x   | None                     | N/A (local only)                      |
| v2.x   | GitHub Actions           | GitHub Environments + workflow inputs |
| v3.x   | CloudFormation           | Separate stacks + parameter files     |
| v4.x   | CloudFormation + Ansible | Stacks + Ansible inventory per env    |
| v5.x   | Docker Compose           | Compose overrides + .env files        |
| v6.x   | EKS + Kubernetes         | ` overlays (namespaces or clusters)   |

---

## Implementation Priority

1. **Start with v6.x** - Kustomize overlays are the cleanest pattern
2. **Then v5.x** - Docker Compose overrides are straightforward
3. **Then v4.x** - Ansible inventory builds on v3.x
4. **Then v3.x** - CloudFormation parameters are simple
5. **Skip v2.x** - Just artifact builds, environments less relevant
6. **Skip v1.x** - No deployment

---

## Cost Considerations

| Environment | Resources                   | Est. Monthly Cost |
| ----------- | --------------------------- | ----------------- |
| dev         | Minimal (t3.micro, 1 pod)   | ~$20              |
| staging     | Mirror prod (reduced scale) | ~$50              |
| production  | Full scale                  | ~$184 (EKS)       |

**Tip:** Use AWS Savings Plans or Spot Instances for dev/staging to reduce costs.

---

## References & Further Reading

### Books

| Book                                                                        | Author                   | Topics                                      |
| --------------------------------------------------------------------------- | ------------------------ | ------------------------------------------- |
| [Continuous Delivery](https://continuousdelivery.com/)                         | Jez Humble, David Farley | Deployment pipelines, environments, testing |
| [Site Reliability Engineering](https://sre.google/sre-book/table-of-contents/) | Google                   | Release engineering, progressive rollouts   |
| [Accelerate](https://itrevolution.com/accelerate-book/)                        | Nicole Forsgren et al.   | DevOps metrics, deployment frequency        |
| [The Phoenix Project](https://itrevolution.com/the-phoenix-project/)           | Gene Kim et al.          | DevOps transformation (novel)               |

### Company Engineering Blogs

| Company | Blog                                                                | Notable Articles               |
| ------- | ------------------------------------------------------------------- | ------------------------------ |
| Netflix | [netflixtechblog.com](https://netflixtechblog.com/)                    | Spinnaker, canary deployments  |
| Spotify | [engineering.atspotify.com](https://engineering.atspotify.com/)        | Backstage, CI/CD               |
| Airbnb  | [medium.com/airbnb-engineering](https://medium.com/airbnb-engineering) | Feature flags, staged rollouts |
| GitHub  | [github.blog/engineering](https://github.blog/category/engineering/)   | GitHub Actions, environments   |
| Etsy    | [etsy.com/codeascraft](https://www.etsy.com/codeascraft)               | Continuous deployment pioneers |

### Open Source Tools by Category

#### CI/CD Platforms

| Tool                                               | Description             | Best For                  |
| -------------------------------------------------- | ----------------------- | ------------------------- |
| [GitHub Actions](https://github.com/features/actions) | Native GitHub CI/CD     | GitHub-hosted projects    |
| [GitLab CI](https://docs.gitlab.com/ee/ci/)           | Integrated GitLab CI/CD | GitLab users              |
| [Jenkins](https://www.jenkins.io/)                    | Self-hosted CI/CD       | Enterprise, customization |
| [CircleCI](https://circleci.com/)                     | Cloud CI/CD             | Fast builds, Docker       |
| [Tekton](https://tekton.dev/)                         | Kubernetes-native CI/CD | K8s environments          |

#### Progressive Delivery

| Tool                                               | Description              | Best For                 |
| -------------------------------------------------- | ------------------------ | ------------------------ |
| [Argo Rollouts](https://argoproj.github.io/rollouts/) | K8s progressive delivery | Canary, blue-green       |
| [Flagger](https://flagger.app/)                       | K8s progressive delivery | Service mesh integration |
| [Spinnaker](https://spinnaker.io/)                    | Multi-cloud CD           | Enterprise, multi-cloud  |
| [LaunchDarkly](https://launchdarkly.com/)             | Feature flags            | Feature-based rollouts   |

#### Artifact Management

| Tool                                                 | Description             | Best For               |
| ---------------------------------------------------- | ----------------------- | ---------------------- |
| [Harbor](https://goharbor.io/)                          | Container registry      | K8s, security scanning |
| [JFrog Artifactory](https://jfrog.com/artifactory/)     | Universal artifact repo | Enterprise, promotion  |
| [GitHub Packages](https://github.com/features/packages) | GitHub-native registry  | GitHub projects        |
| [AWS ECR](https://aws.amazon.com/ecr/)                  | AWS container registry  | AWS deployments        |

#### Infrastructure as Code

| Tool                                  | Description                    | Best For         |
| ------------------------------------- | ------------------------------ | ---------------- |
| [Terraform](https://www.terraform.io/)   | Multi-cloud IaC                | Cloud-agnostic   |
| [Pulumi](https://www.pulumi.com/)        | IaC with programming languages | Developers       |
| [AWS CDK](https://aws.amazon.com/cdk/)   | AWS IaC with code              | AWS-focused      |
| [Crossplane](https://www.crossplane.io/) | K8s-native IaC                 | K8s environments |

### GitHub Actions Specific

- [Environments documentation](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Reusable workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Required reviewers](https://docs.github.com/en/actions/managing-workflow-runs/reviewing-deployments)
- [Wait timer](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#wait-timer)

### Kubernetes Specific

- [Kustomize overlays](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
- [Helm values per environment](https://helm.sh/docs/chart_template_guide/values_files/)
- [Namespace-based multi-tenancy](https://kubernetes.io/docs/concepts/security/multi-tenancy/)
- [GitOps with ArgoCD](https://argo-cd.readthedocs.io/en/stable/)

# Specification: Git Clone Deployment Configuration

## ADDED Requirements

### Requirement: Git Repository Clone on Deployment
The Prefect deployment process SHALL clone the repository from git before executing the flow, ensuring flows run against current source code.

#### Scenario: Deploy flow from main branch
Given the prefect.yaml contains git clone configuration:
```yaml
pull:
  - prefect.deployments.steps.git_clone:
      repository: git@github.com:levyvix/scraper-filmes.git
      branch: main
```

When `prefect deploy` is executed, then:
1. Repository is cloned to the Prefect work directory
2. Flow execution uses cloned source code
3. Deployment succeeds with repository configured as pull source

#### Scenario: Clone fails with SSH permission error
Given an SSH key is not available on the worker machine
When `prefect deploy` or a flow run is attempted, then:
1. Git clone step fails with clear error message
2. Flow execution is prevented (not attempted with stale code)
3. Error message indicates SSH key setup is required
4. Documentation link provided in error or logs

### Requirement: SSH Key Setup Documentation
The deployment documentation SHALL clearly explain SSH key setup required for git clone authentication.

#### Scenario: First-time deployment setup
Given a user setting up Prefect for the first time
When they follow the deployment guide, then:
1. Step 1 explains SSH key generation: `ssh-keygen -t ed25519`
2. Step 2 explains adding public key to GitHub: Settings → Deploy Keys
3. Step 3 explains configuring ssh-agent or ssh config for automation
4. Examples provided for each step

#### Scenario: Deployment on CI/CD system
Given GitHub Actions or another CI/CD deploys the flow
When workflows execute `prefect deploy`, then:
1. Documentation explains SSH key injection via secrets
2. Examples show setup in GitHub Actions (SSH action or manual config)
3. Warning: Ensure SSH key has minimal permissions (deploy keys only)

### Requirement: Repository Configuration Validation
The deployment process SHALL validate that git repository is correctly configured and reachable.

#### Scenario: Validate repository URL before deployment
Given a `prefect.yaml` with git clone configuration
When `prefect deploy` is executed, then:
1. Git remote URL is validated as reachable
2. SSH connection to GitHub is tested (git ls-remote)
3. Deployment fails fast if repository is unreachable
4. Clear error message indicates network/auth issue

## MODIFIED Requirements

### Requirement: Deploy Flow with Git Source Configuration
The deployment `prefect.yaml` file MUST include a pull section for git clone to ensure all flow runs execute with current source code.

Previously: `prefect.yaml` had no explicit git clone configuration

Now: `prefect.yaml` MUST include:
```yaml
pull:
  - prefect.deployments.steps.git_clone:
      repository: git@github.com:levyvix/scraper-filmes.git
      branch: main
```

#### Scenario: Verify git clone configured in deployment
Given `prefect.yaml` with git clone pull step
When `prefect deploy` is executed, then:
1. Prefect recognizes and validates the pull step
2. Flow deployments reference git clone as pull source
3. Flow runs clone repository before execution
4. All runs use code from specified branch

Impact: All flow runs pull latest code from specified branch before execution.

## Summary

- Git clone configuration embedded in `prefect.yaml`
- SSH key setup is prerequisite for deployment
- Validation ensures repository is reachable before deployment
- Documentation guides SSH setup for local and CI/CD scenarios

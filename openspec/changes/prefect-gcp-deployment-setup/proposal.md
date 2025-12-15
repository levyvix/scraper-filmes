# Proposal: Prefect Deployment with Git Clone and GCP Environment Configuration

## Why

Currently, the Prefect `prefect.yaml` includes git clone configuration for deployment but lacks clear documentation and implementation guidance for:
1. Setting up Prefect to clone the repository and execute flows from git
2. Configuring GCP_PROJECT_ID and GCP credentials so that the deployed flow can authenticate with BigQuery
3. Handling environment variables and secrets securely in Prefect deployments (local server and cloud)

This causes friction during deployment setup and increases risk of misconfiguration or credential exposure.

## What Changes

- Document and validate the git clone pull step in `prefect.yaml` to ensure repository is correctly cloned
- Add configuration for environment variables (`GCP_PROJECT_ID`) passed to the deployed flow
- Document credential setup options: local service account file, workload identity, or Prefect Cloud secrets
- Update deployment documentation with step-by-step instructions for end-to-end deployment
- Validate schema for job variables and environment configuration in `prefect.yaml`

## Summary

Enable secure, reproducible Prefect deployment from git by:
1. Validating git clone configuration and repository setup
2. Documenting how to set GCP_PROJECT_ID and other environment variables for deployed flows
3. Providing clear credential management options for BigQuery access
4. Creating deployment validation and testing procedures

## Goals

1. **Git Integration**: Prefect can clone the repository and run flows from source
2. **Environment Configuration**: Environment variables passed to deployed flows reliably
3. **Credential Security**: Multiple credential options with clear security guidance
4. **Deployment Reproducibility**: Clear, documented, testable deployment process
5. **Troubleshooting**: Self-service debugging for common deployment issues

## Scope

### In Scope
- Validate and document `pull` section (git clone) in `prefect.yaml`
- Add `job_variables` configuration for environment variables (GCP_PROJECT_ID, etc.)
- Document credential options: local file, workload identity, Prefect Cloud secrets
- Add environment variable validation in flow setup
- Create deployment testing checklist
- Update `docs/PREFECT_DEPLOYMENT.md` with credential and environment setup

### Out of Scope
- Changes to flow logic or scraper implementation
- BigQuery schema or data loading changes
- Prefect flow definition structure (already defined)
- Prefect Cloud-specific features beyond credential management
- Docker image builds or container orchestration

## Approach

### Architecture

```
prefect.yaml (deployment config)
    ↓
[pull] git clone from repository
    ↓
[job_variables] Set GCP_PROJECT_ID + auth method
    ↓
Flow Execution Environment
    ├─ GCP_PROJECT_ID loaded from env vars
    ├─ GCP credentials from selected auth method
    └─ Flow runs scrapers/gratis_torrent/flow.py with BigQuery access
```

### Key Components

1. **Git Clone Configuration** (`prefect.yaml` pull section)
   - Validate repository URL (SSH or HTTPS)
   - Document branch selection
   - Test clone behavior with dummy flow runs

2. **Environment Variable Configuration** (prefect.yaml job_variables)
   - Add GCP_PROJECT_ID to job_variables
   - Support credential path configuration
   - Validate variables are passed to flow runtime

3. **Credential Options** (documented in updated guide)
   - **Option A**: Local service account JSON file on worker machine
   - **Option B**: Workload Identity / Application Default Credentials (GCP)
   - **Option C**: Prefect Cloud secrets (for cloud deployments)

4. **Flow Environment Setup** (flow.py / config.py)
   - Detect GCP_PROJECT_ID from environment
   - Load credentials based on configured method
   - Graceful fallback if credentials unavailable

5. **Validation & Testing**
   - Prefect deployment dry-run to verify git clone
   - Flow startup validation (credentials loaded)
   - BigQuery connectivity test (optional)

## Success Criteria

1. **Git Clone Integration**:
   - `prefect deploy` successfully clones repository
   - Flow runs from cloned source code
   - Branch configuration works (main, develop, etc.)

2. **Environment Configuration**:
   - GCP_PROJECT_ID passed to deployed flow
   - Other env vars (if added) also propagated
   - Variables visible in Prefect UI / API

3. **Credential Management**:
   - At least 2 of 3 credential options documented and working
   - No credentials hardcoded in code/config files
   - Clear security guidance provided

4. **Documentation**:
   - Step-by-step deployment guide with credential setup
   - Troubleshooting section for common issues
   - Examples for each credential option

5. **Testing**:
   - Deployment configuration validation passes
   - Successful flow run with BigQuery access
   - Credential loading verified in flow logs

## Related Specifications

- Related to: `integrate-loguru-prefect-logs` (logs from deployed flows)
- Complements: `add-comprehensive-test-coverage` (deployment testing)
- Depends on: Existing `flow.py` and `config.py` structure

## Timeline

Not estimated; work items detailed in `tasks.md`.

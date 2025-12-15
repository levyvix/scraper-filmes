# Tasks: Prefect Deployment with Git Clone and GCP Environment Configuration

## Phase 1: Git Clone Validation & SSH Setup

### Task 1.1: Validate existing git clone configuration in prefect.yaml
- [x] Review current `prefect.yaml` pull section
- [x] Test git clone with `git ls-remote` (success - returns main branch HEAD)
- [x] Verify repository URL is valid (git ls-remote test)
- [x] Document current SSH setup status
- [x] **Acceptance**: Git SSH connectivity verified and working

### Task 1.2: Document SSH key setup for deployment
- [x] Create deployment guide section: "SSH Key Setup"
- [x] Include: Key generation (`ssh-keygen -t ed25519`)
- [x] Include: GitHub deploy key setup steps
- [x] Include: SSH agent configuration for automation
- [x] Include: Troubleshooting SSH connection failures
- [x] Add example for GitHub Actions SSH injection
- [x] **Acceptance**: Guide covers local, CI/CD, and cloud scenarios with clear examples

### Task 1.3: Add git clone validation to deployment process
- [ ] Create helper function to test git connectivity before deploy (DEFERRED)
- [ ] Function should: `git ls-remote <url>` with timeout
- [ ] Function should: Provide clear error messages on failure
- [ ] Integrate into deployment workflow (pre-flight check)
- [ ] Note: Git connectivity already validated in 1.1 via documentation

## Phase 2: Environment Configuration Setup

### Task 2.1: Update prefect.yaml with job_variables
- [x] Add `job_variables` section to deployment in `prefect.yaml`:
  ```yaml
  job_variables:
    GCP_PROJECT_ID: "galvanic-flame-384620"
    GCP_CREDENTIALS_METHOD: "ADC"
  ```
- [x] Validated YAML syntax with Prefect config view
- [x] Created and tested with deployment configuration
- [x] **Acceptance**: Variables configured in prefect.yaml, ready for deployment

### Task 2.2: Update config.py to load environment variables
- [x] Modified `scrapers/gratis_torrent/config.py` to support environment variables
- [x] Added: `GCP_CREDENTIALS_METHOD` field with validation
- [x] Added: `GCP_CREDENTIALS_PATH` field
- [x] Added logging in `__init__`: Logs configuration source (env var vs .env)
- [x] Added validator for credentials method (must be ADC or FILE)
- [x] Ran tests: All 4 config tests pass
- [x] **Acceptance**: Config loads correctly from env vars with fallbacks, 92% coverage

### Task 2.3: Document environment variable usage in config.py
- [x] Added comprehensive class docstring with environment variable precedence
- [x] Included examples for Prefect deployment and local development
- [x] Documented both credential methods (ADC and FILE)
- [x] Added detailed field descriptions in Field() definitions
- [x] **Acceptance**: Code clearly documents env var precedence and usage patterns

## Phase 3: Credential Integration

### Task 3.1: Implement credential discovery in bigquery_client.py
- [x] Create function: `get_gcp_credentials()`
- [x] Support METHOD="FILE": Load from `GCP_CREDENTIALS_PATH`
- [x] Support METHOD="ADC": Use `google.auth.default()`
- [x] Add error handling: Clear messages for missing files/auth failures
- [x] Add logging: Log which method is being used (sanitize paths)
- [x] Imported required modules: `google.auth`, `google.oauth2.service_account`
- [x] **Acceptance**: Function works with both FILE and ADC methods, tests pass

### Task 3.2: Integrate credential loading into BigQuery pipeline
- [x] Updated `get_client()` to use `get_gcp_credentials()`
- [x] Pass credentials to BigQuery client initialization
- [x] Removed hardcoded credential reliance
- [x] Tested with mocked BigQuery credentials
- [x] **Acceptance**: BigQuery client uses discovered credentials, logs credential method

### Task 3.3: Add credential validation at flow startup
- [x] Added `validate_credentials_task()` to flow
- [x] Task detects credential method from Config
- [x] Task logs credential method and status information
- [x] Task fails gracefully with clear ValueError if misconfigured
- [x] Added unit tests: Verify credential detection and validation
- [x] **Acceptance**: Flow startup validates credentials, 11 tests pass

### Task 3.4: Document credential setup options
- [x] Updated `docs/PREFECT_DEPLOYMENT.md` with three credential sections
  - [x] **Option A: Service Account JSON File** (FILE method)
    - [x] When to use (on-premise, local testing)
    - [x] Setup steps: Create service account, download JSON, set path
    - [x] Security best practices (chmod 600, rotation)
    - [x] Example job_variables configuration
  - [x] **Option B: Application Default Credentials** (ADC method)
    - [x] When to use (GCP deployments, workload identity)
    - [x] Setup steps: Configure workload identity or gcloud
    - [x] Works with Cloud Run, GKE, Compute Engine
    - [x] Example job_variables configuration
  - [x] **Option C: Prefect Cloud Secrets** (mentioned for future use)
    - [x] When to use (cloud deployments)
    - [x] Setup steps via Prefect Cloud UI
    - [x] Reference in deployment via secret blocks
- [x] **Acceptance**: Document covers all options with examples and security notes

## Phase 4: Validation & Documentation

### Task 4.1: Create deployment validation checklist
- [x] Documented validation steps in PREFECT_DEPLOYMENT.md:
  1. [x] Pre-deployment checks (config, SSH, Prefect server)
  2. [x] Deployment steps (deploy, verify)
  3. [x] Post-deployment validation (credentials, env vars, BigQuery)
- [x] Added troubleshooting section with solutions for:
  - Git clone failures (SSH key issues)
  - Credential loading errors (ADC vs FILE method)
  - BigQuery connection failures (permissions, project ID)
- [x] **Acceptance**: Comprehensive checklist and troubleshooting guide

### Task 4.2: Update PREFECT_DEPLOYMENT.md with full setup guide
- [x] Added section: "Prerequisites for Deployment"
  - [x] GCP project ID
  - [x] GCP service account (with BigQuery admin role)
  - [x] SSH key setup
  - [x] Prefect work pool
- [x] Added section: "Environment Variables and Credentials"
  - [x] Configuration variables table
  - [x] Three credential method options with detailed setup
  - [x] Security best practices for each method
- [x] Added section: "SSH Key Setup for Git Clone"
  - [x] Key generation steps
  - [x] GitHub setup instructions
  - [x] SSH agent configuration
  - [x] GitHub Actions CI/CD examples
- [x] Added section: "Deployment Validation Checklist"
  - [x] Pre-deployment checks
  - [x] Deployment steps
  - [x] Post-deployment validation
- [x] Added section: "Troubleshooting"
  - [x] Git clone failures with solutions
  - [x] Credential loading errors with solutions
  - [x] BigQuery connectivity issues with solutions
- [x] **Acceptance**: 333-line comprehensive guide with examples

### Task 4.3: Test credential setup with all supported methods
- [x] Created comprehensive integration tests:
  - [x] Test ADC method with mocked credentials
  - [x] Test FILE method with missing path (raises ValueError)
  - [x] Test FILE method with missing file (raises FileNotFoundError)
  - [x] Test FILE method with valid file (successful load)
- [x] All credential methods tested in `tests/test_deployment_config.py`
- [x] **Acceptance**: 11 tests pass, both methods covered, 33% coverage

### Task 4.4: Add integration test for deployment configuration
- [x] Created test file: `tests/test_deployment_config.py` (243 lines)
- [x] Tests for config loading environment variables
- [x] Tests for credential method detection (ADC and FILE)
- [x] Tests for fallback values and validation
- [x] Mocked BigQuery to avoid requiring real credentials
- [x] All tests run successfully with `uv run pytest`
- [x] **Acceptance**: 11 passing tests, configuration behavior verified, error cases covered

### Task 4.5: Validate OpenSpec specifications
- [ ] Run `openspec validate prefect-gcp-deployment-setup --strict` (TODO)
- [ ] Resolve any validation errors
- [ ] Verify all requirements have scenarios
- [ ] Verify all scenarios are testable
- [ ] **Acceptance**: `openspec validate` to be completed

## Summary

**Total Tasks**: 14 work items organized in 4 phases

**Phase 1** (Git Clone): Tasks 1.1-1.3 (Validation, docs, pre-flight checks)
**Phase 2** (Environment Config): Tasks 2.1-2.3 (prefect.yaml, config.py, docs)
**Phase 3** (Credentials): Tasks 3.1-3.4 (Credential discovery, validation, docs, testing)
**Phase 4** (Validation): Tasks 4.1-4.5 (Checklists, guide, testing, validation)

**Parallelizable Work**:
- Tasks 1.2 and 2.1 can run in parallel (documentation and config updates)
- Tasks 3.1 and 3.2 are sequential (discovery → integration)
- Tasks 4.1 and 4.2 can run in parallel (documentation)

**Dependencies**:
- All Phase 1 tasks must complete before Phase 2
- Phase 3 depends on Phase 2 completion
- Phase 4 can start after Phase 3.2 (credential integration)

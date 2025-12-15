# Tasks: Prefect Deployment with Git Clone and GCP Environment Configuration

## Phase 1: Git Clone Validation & SSH Setup

### Task 1.1: Validate existing git clone configuration in prefect.yaml
- [ ] Review current `prefect.yaml` pull section
- [ ] Test git clone with `prefect deploy --dry-run`
- [ ] Verify repository URL is valid (git ls-remote test)
- [ ] Document current SSH setup status
- [ ] **Acceptance**: `prefect deploy --dry-run` succeeds, confirms git clone step

### Task 1.2: Document SSH key setup for deployment
- [ ] Create deployment guide section: "SSH Key Setup"
- [ ] Include: Key generation (`ssh-keygen -t ed25519`)
- [ ] Include: GitHub deploy key setup steps
- [ ] Include: SSH agent configuration for automation
- [ ] Include: Troubleshooting SSH connection failures
- [ ] Add example for GitHub Actions SSH injection
- [ ] **Acceptance**: Guide covers local, CI/CD, and cloud scenarios with clear examples

### Task 1.3: Add git clone validation to deployment process
- [ ] Create helper function to test git connectivity before deploy
- [ ] Function should: `git ls-remote <url>` with timeout
- [ ] Function should: Provide clear error messages on failure
- [ ] Integrate into deployment workflow (pre-flight check)
- [ ] **Acceptance**: Helper function works, deployment fails fast on git errors

## Phase 2: Environment Configuration Setup

### Task 2.1: Update prefect.yaml with job_variables
- [ ] Add `job_variables` section to deployment in `prefect.yaml`:
  ```yaml
  job_variables:
    GCP_PROJECT_ID: "galvanic-flame-384620"
    GCP_CREDENTIALS_METHOD: "ADC"
  ```
- [ ] Validate YAML syntax with `prefect deploy --dry-run`
- [ ] Test variable propagation with dummy flow run
- [ ] **Acceptance**: Variables appear in Prefect UI, accessible to flow via `os.environ`

### Task 2.2: Update config.py to load environment variables
- [ ] Modify `scrapers/gratis_torrent/config.py` to load from environment
- [ ] Add: `GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "galvanic-flame-384620")`
- [ ] Add: `GCP_CREDENTIALS_METHOD = os.environ.get("GCP_CREDENTIALS_METHOD", "ADC")`
- [ ] Add: `GCP_CREDENTIALS_PATH = os.environ.get("GCP_CREDENTIALS_PATH", None)`
- [ ] Add logging: Log which values were loaded (sanitize paths/secrets)
- [ ] Run tests: `uv run pytest scrapers/gratis_torrent/test_config.py`
- [ ] **Acceptance**: Tests pass, config values load correctly from env and fallback

### Task 2.3: Document environment variable usage in config.py
- [ ] Add docstring explaining environment variable override
- [ ] Include examples: Local dev, deployed via Prefect, CI/CD
- [ ] Document fallback values and defaults
- [ ] **Acceptance**: Code comments explain env var precedence clearly

## Phase 3: Credential Integration

### Task 3.1: Implement credential discovery in bigquery_client.py
- [ ] Create function: `get_gcp_credentials()`
- [ ] Support METHOD="FILE": Load from `GCP_CREDENTIALS_PATH`
- [ ] Support METHOD="ADC": Use `google.auth.default()`
- [ ] Add error handling: Clear messages for missing files/auth failures
- [ ] Add logging: Log which method is being used (sanitize paths)
- [ ] Import required modules: `google.auth`, `google.oauth2.service_account`
- [ ] **Acceptance**: Function works with both FILE and ADC methods, tests pass

### Task 3.2: Integrate credential loading into BigQuery pipeline
- [ ] Update `load_movies_to_bigquery()` to use `get_gcp_credentials()`
- [ ] Pass credentials to BigQuery client initialization
- [ ] Remove any hardcoded credential loading
- [ ] Test with actual BigQuery (if available)
- [ ] **Acceptance**: BigQuery client uses discovered credentials, logs credential method

### Task 3.3: Add credential validation at flow startup
- [ ] Add task to flow that validates credentials before scraping
- [ ] Task should: Detect credential method from config
- [ ] Task should: Log credential method and any status information
- [ ] Task should: Fail gracefully with clear message if misconfigured
- [ ] Add unit test: Verify credential detection works
- [ ] **Acceptance**: Flow startup logs confirm credentials loaded, tests pass

### Task 3.4: Document credential setup options
- [ ] Update `docs/PREFECT_DEPLOYMENT.md` with three credential sections
  - **Option A: Local Service Account File**
    - When to use (on-premise, local testing)
    - Setup steps: Create service account, download JSON, set path
    - Security best practices
    - Example job_variables configuration
  - **Option B: Application Default Credentials**
    - When to use (GCP deployments, workload identity)
    - Setup steps: Configure workload identity or gcloud
    - Works with Cloud Run, GKE, Compute Engine
    - Example job_variables configuration
  - **Option C: Prefect Cloud Secrets** (optional for now)
    - When to use (cloud deployments)
    - Setup steps via Prefect Cloud UI
    - Reference in deployment via secret blocks
    - Example configuration
- [ ] **Acceptance**: Document covers all options, each with examples and security notes

## Phase 4: Validation & Documentation

### Task 4.1: Create deployment validation checklist
- [ ] Document steps to validate before going live:
  1. Git clone success: Verify code pulled to work directory
  2. Environment variables: Check `os.environ` in flow logs
  3. Credentials loaded: Verify credential method logged
  4. BigQuery connectivity: Test query to staging table
  5. End-to-end run: Execute full scraper flow
- [ ] Add troubleshooting for each step
- [ ] Create script to automate pre-deployment checks (optional)
- [ ] **Acceptance**: Checklist covers all major validation points

### Task 4.2: Update PREFECT_DEPLOYMENT.md with full setup guide
- [ ] Add section: "Prerequisites for Deployment"
  - GCP project ID
  - GCP service account (with BigQuery admin role)
  - SSH key setup
  - Prefect work pool
- [ ] Add section: "Environment Variables and Credentials"
  - Overview of job_variables
  - How to set GCP_PROJECT_ID
  - How to select credential method
  - Per-option setup instructions
- [ ] Add section: "Deployment Validation"
  - Pre-deployment checklist
  - First-run validation
  - Monitoring deployed flows
- [ ] Add section: "Troubleshooting"
  - Git clone failures
  - Credential loading errors
  - BigQuery connectivity issues
  - Common misconfigurations
- [ ] Add section: "Examples"
  - Example: Local Prefect + ADC
  - Example: Prefect Cloud + Workload Identity
  - Example: On-Premise + Service Account File
- [ ] **Acceptance**: Updated guide is clear, complete, and tested

### Task 4.3: Test credential setup with all supported methods
- [ ] Test Option A (FILE method):
  - Create test service account with minimal permissions
  - Download JSON file
  - Set GCP_CREDENTIALS_METHOD=FILE and GCP_CREDENTIALS_PATH
  - Run scraper, verify BigQuery works
- [ ] Test Option B (ADC method):
  - Use gcloud ADC or workload identity
  - Set GCP_CREDENTIALS_METHOD=ADC
  - Run scraper, verify BigQuery works
- [ ] **Acceptance**: Both methods tested, work with BigQuery, logs are clear

### Task 4.4: Add integration test for deployment configuration
- [ ] Create test file: `tests/test_deployment_config.py`
- [ ] Test that config loads environment variables correctly
- [ ] Test that credential method detection works
- [ ] Test fallback values work when env vars not set
- [ ] Mock BigQuery to avoid requiring credentials in CI/CD
- [ ] Run with `uv run pytest tests/test_deployment_config.py`
- [ ] **Acceptance**: All tests pass, configuration behavior verified

### Task 4.5: Validate OpenSpec specifications
- [ ] Run `openspec validate prefect-gcp-deployment-setup --strict`
- [ ] Resolve any validation errors
- [ ] Verify all requirements have scenarios
- [ ] Verify all scenarios are testable
- [ ] **Acceptance**: `openspec validate` succeeds with no issues

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

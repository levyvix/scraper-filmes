# Design: Prefect Deployment with Git Clone and GCP Environment Configuration

## Architecture Decision Record

### 1. Git Clone Strategy

**Decision**: Use SSH-based git clone via `prefect.deployments.steps.git_clone` step (already configured).

**Rationale**:
- SSH keys are more secure than storing credentials in config
- Aligns with existing `prefect.yaml` setup (already configured)
- Works across local and cloud deployments with consistent setup

**Trade-offs**:
- Requires SSH key setup on worker machines
- Alternative: HTTPS with personal access tokens (less secure, easier setup)

**Implementation**:
- Keep existing SSH configuration: `repository: git@github.com:levyvix/scraper-filmes.git`
- Document SSH key setup in deployment guide
- Optional: Support HTTPS fallback with token in Prefect secrets

### 2. Environment Variable Injection

**Decision**: Use Prefect `job_variables` in `prefect.yaml` to pass GCP_PROJECT_ID and credential configuration.

**Rationale**:
- Native Prefect feature for injecting environment variables
- Variables propagate to flow execution environment
- Can be overridden per deployment or at runtime
- UI supports viewing/modifying variables

**Trade-offs**:
- Variables visible in Prefect UI (not secret, use Prefect secrets for sensitive values)
- Requires yaml configuration (not runtime-dynamic)

**Implementation**:
```yaml
job_variables:
  GCP_PROJECT_ID: "galvanic-flame-384620"
  GCP_CREDENTIALS_METHOD: "ADC"  # or "FILE" or "SECRETS"
  GCP_CREDENTIALS_PATH: "/etc/gcp/key.json"  # if METHOD=FILE
```

### 3. Credential Management Strategy

Three credential options to accommodate different deployment scenarios:

#### Option A: Local Service Account File (Development/On-Premise)
- Service account JSON file on worker machine
- Path passed via `GCP_CREDENTIALS_PATH` env var
- Simple for local Prefect server + worker setup
- **Security**: Protect file permissions (600), restrict access to service account
- **Deployment**: Manual setup, terraform, or image provisioning

#### Option B: Application Default Credentials (GCP Native)
- Use gcloud CLI or workload identity (GKE/Cloud Run)
- Auto-discovered credentials from environment
- No explicit credential path needed
- **Security**: Leverages GCP's native credential chain
- **Deployment**: GCP-idiomatic, best for cloud deployments

#### Option C: Prefect Cloud Secrets
- Store GCP service account JSON in Prefect Cloud Secret Block
- Reference via `prefect.context.secrets` in code
- Secure, auditable, centralized
- **Security**: Encrypted in Prefect Cloud
- **Deployment**: Cloud-only, requires Prefect Cloud setup

**Recommended Path**:
1. Development: Option A (local file)
2. On-Premise: Option A or B
3. Cloud: Option B (workload identity) or Option C (Prefect secrets)

### 4. Flow Configuration Updates

**Decision**: Update `config.py` to load GCP_PROJECT_ID from environment with fallback.

**Rationale**:
- Centralized config management
- Environment variable takes precedence (deployment override)
- Fallback to hardcoded value for local development
- No code changes required in scraper logic

**Implementation**:
```python
# config.py
import os

GCP_PROJECT_ID = os.environ.get(
    "GCP_PROJECT_ID",
    "galvanic-flame-384620"  # Fallback value
)

# Credential discovery
GCP_CREDENTIALS_METHOD = os.environ.get("GCP_CREDENTIALS_METHOD", "ADC")
GCP_CREDENTIALS_PATH = os.environ.get("GCP_CREDENTIALS_PATH", None)
```

### 5. Credential Loading Pattern

**In `bigquery_client.py`**:
```python
import google.auth
from google.auth import default as auth_default

def get_credentials():
    """Load GCP credentials based on method configuration."""
    method = os.environ.get("GCP_CREDENTIALS_METHOD", "ADC")

    if method == "FILE":
        path = os.environ.get("GCP_CREDENTIALS_PATH")
        if not path:
            raise ValueError("GCP_CREDENTIALS_PATH required for FILE method")
        return google.oauth2.service_account.Credentials.from_service_account_file(path)

    # Default: Application Default Credentials
    credentials, project = auth_default()
    return credentials
```

### 6. Deployment Validation Steps

**Before Going Live**:
1. Verify git clone: Run `prefect deployment create` with dry-run
2. Verify env vars: Check Prefect UI for job_variables
3. Verify credentials: Flow startup logs should show "GCP credentials loaded"
4. Verify BigQuery: Run scraper, check data loaded to staging table

**After Deployment**:
1. Monitor first flow run
2. Check logs in Prefect UI
3. Verify BigQuery data pipeline executed

### 7. Documentation Structure

**File**: `docs/PREFECT_DEPLOYMENT.md` (update existing)

Sections to add:
- Environment Variables & Configuration
  - GCP_PROJECT_ID setup
  - Credential method selection
  - Override examples

- Credential Setup (One subsection per option)
  - Option A: Local Service Account File
  - Option B: Application Default Credentials
  - Option C: Prefect Cloud Secrets

- Deployment Validation Checklist

- Troubleshooting
  - Git clone failures
  - Credential loading errors
  - BigQuery connectivity issues

## Implementation Sequence

1. **Phase 1: Git Clone Validation**
   - Validate existing `prefect.yaml` pull section
   - Document SSH key setup requirements
   - Test git clone with dummy run

2. **Phase 2: Environment Configuration**
   - Add `job_variables` to `prefect.yaml`
   - Update `config.py` to load GCP_PROJECT_ID from env
   - Test variable propagation

3. **Phase 3: Credential Integration**
   - Implement credential discovery in `bigquery_client.py`
   - Support Option A (file) and Option B (ADC) initially
   - Add logging for credential method used

4. **Phase 4: Documentation & Testing**
   - Update deployment guide with all options
   - Create validation checklist
   - Test each credential option
   - Add troubleshooting section

## Risk Mitigation

**Risk**: Credentials in logs
- **Mitigation**: Filter sensitive env vars from logs, use Prefect's built-in secret masking

**Risk**: SSH key on worker machine
- **Mitigation**: Use dedicated service account key, restrict permissions, rotate regularly

**Risk**: git clone fails silently
- **Mitigation**: Add validation step before flow execution, log git version and clone success

**Risk**: Flow runs with stale code
- **Mitigation**: Always use specific branch (avoid detached HEAD), validate pulled commit hash

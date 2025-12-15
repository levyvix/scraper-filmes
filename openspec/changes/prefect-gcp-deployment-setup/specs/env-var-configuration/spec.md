# Specification: Environment Variable Configuration for Deployed Flows

## ADDED Requirements

### Requirement: Pass Environment Variables to Deployed Flows
The Prefect deployment process SHALL support passing environment variables (e.g., GCP_PROJECT_ID) to flow execution environment via `job_variables` in `prefect.yaml`.

#### Scenario: Deploy flow with GCP_PROJECT_ID
Given `prefect.yaml` includes:
```yaml
deployments:
  - name: gratis-torrent
    work_pool:
      name: defaultp
      job_variables:
        GCP_PROJECT_ID: "galvanic-flame-384620"
        GCP_CREDENTIALS_METHOD: "ADC"
```

When `prefect deploy -n gratis-torrent` is executed, then:
1. job_variables are stored in deployment configuration
2. When flow runs, GCP_PROJECT_ID is available as `os.environ["GCP_PROJECT_ID"]`
3. Variable is visible in Prefect UI under deployment details
4. Variables can be overridden at runtime

#### Scenario: Override environment variable at runtime
Given a deployment with `job_variables.GCP_PROJECT_ID = "galvanic-flame-384620"`
When a user manually triggers flow run with parameter override, then:
1. User can specify alternate GCP_PROJECT_ID via CLI or API
2. Runtime-specified value takes precedence over deployment default
3. Flow logs show which value was used

### Requirement: Load Environment Variables in Flow Configuration
The flow configuration code (config.py) SHALL load environment variables with sensible fallbacks for local development.

#### Scenario: Load GCP_PROJECT_ID from deployment environment
Given a deployed flow with `job_variables.GCP_PROJECT_ID = "galvanic-flame-384620"`
When the flow executes, then:
1. `config.py` reads `os.environ.get("GCP_PROJECT_ID", fallback_value)`
2. Deployed value takes precedence
3. Local development uses fallback if env var not set
4. Config value is accessible to all modules as `config.GCP_PROJECT_ID`

#### Scenario: Detect credential method from environment
Given a deployment with `job_variables.GCP_CREDENTIALS_METHOD = "FILE"`
When the flow initializes, then:
1. `config.py` reads `os.environ.get("GCP_CREDENTIALS_METHOD", "ADC")`
2. Credential loading code respects the configured method
3. Flow logs include "Using credentials method: FILE"

### Requirement: Support Multiple Credential Methods via Configuration
The configuration system MUST allow selecting credential discovery method via environment variable.

#### Scenario: Configure local file credentials for on-premise deployment
Given deployment with:
```yaml
job_variables:
  GCP_CREDENTIALS_METHOD: "FILE"
  GCP_CREDENTIALS_PATH: "/etc/gcp/service-account.json"
```

When the flow's bigquery_client initializes, then:
1. Credential loading code detects METHOD=FILE
2. Loads credentials from GCP_CREDENTIALS_PATH
3. If file not found, flow fails with clear error message
4. Logs indicate credentials loaded from file path

#### Scenario: Configure Application Default Credentials for GCP deployment
Given deployment with:
```yaml
job_variables:
  GCP_CREDENTIALS_METHOD: "ADC"
```

When the flow's bigquery_client initializes, then:
1. Credential loading code detects METHOD=ADC
2. Uses google.auth.default() for automatic credential discovery
3. Credentials come from environment (workload identity, gcloud, etc.)
4. Logs indicate credentials loaded via ADC

### Requirement: Environment Variable Schema Validation
The deployment configuration system SHALL define and validate expected environment variables and their types.

#### Scenario: Validate job_variables in prefect.yaml
Given a developer edits `prefect.yaml` with incorrect job_variables format, then:
1. `prefect deploy --dry-run` validates the configuration
2. Clear error message if required variables missing
3. Error message if variable types incorrect (e.g., GCP_PROJECT_ID not string)
4. Suggestions for correct format

## MODIFIED Requirements

### Requirement: Config Module Supports Environment Overrides
The `config.py` module MUST prioritize environment variables over hardcoded values, enabling deployment-time configuration without code changes.

Previously:
```python
GCP_PROJECT_ID = "galvanic-flame-384620"  # Hardcoded
```

Now:
```python
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "galvanic-flame-384620")
GCP_CREDENTIALS_METHOD = os.environ.get("GCP_CREDENTIALS_METHOD", "ADC")
GCP_CREDENTIALS_PATH = os.environ.get("GCP_CREDENTIALS_PATH", None)
```

#### Scenario: Deploy to different GCP project via environment variable
Given a deployment with `job_variables.GCP_PROJECT_ID = "alternate-project-123"`
When the flow executes, then:
1. config.py loads GCP_PROJECT_ID from os.environ
2. Alternate project ID is used instead of hardcoded default
3. BigQuery pipeline references the alternate project
4. Flow logs confirm alternate project is active

Impact: Deployments can override project ID and credentials without code changes.

## Deleted Requirements

N/A - No existing environment configuration to remove.

## Summary

- `job_variables` in `prefect.yaml` passes environment variables to deployed flows
- `config.py` loads variables with fallbacks for local development
- Multiple credential methods supported: FILE, ADC, SECRETS
- Configuration validated on deployment
- Runtime overrides supported

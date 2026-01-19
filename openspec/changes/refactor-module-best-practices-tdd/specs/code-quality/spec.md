## ADDED Requirements

### Requirement: Type Safety

All code SHALL have type hints and pass MyPy strict mode.

#### Scenario: MyPy strict validation
- **WHEN** running `mypy --strict --ignore-missing-imports .`
- **THEN** zero type errors are reported
- **THEN** all functions have parameter and return type hints

### Requirement: Code Formatting

All code SHALL be formatted with Ruff at 120-character line length.

#### Scenario: Ruff formatting check
- **WHEN** running `ruff format --check --line-length 120 .`
- **THEN** all files pass formatting check
- **THEN** no formatting changes needed

#### Scenario: Ruff linting check
- **WHEN** running `ruff check .`
- **THEN** zero linting errors or warnings
- **THEN** all issues auto-fixable with `--fix`

### Requirement: Pre-commit Hooks

Pre-commit hooks SHALL enforce code quality before commits.

#### Scenario: Pre-commit validation
- **WHEN** committing code
- **THEN** Ruff, MyPy, YAML, JSON, TOML validators run
- **THEN** commit is rejected if any check fails

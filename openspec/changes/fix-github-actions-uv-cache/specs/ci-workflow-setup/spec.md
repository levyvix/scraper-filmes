# Specification: CI Workflow Setup

**Capability**: ci-workflow-setup
**Status**: Draft
**Version**: 1.0

## Overview

Correct the GitHub Actions workflow configuration to remove unsupported `uv` caching from `actions/setup-python@v4`.

## MODIFIED Requirements

### Requirement: Remove UV cache parameter from setup-python

The `actions/setup-python@v4` step SHALL NOT include `cache: "uv"` because this caching method is not supported.

#### Scenario: lint-and-type-check job removes cache parameter

Given the lint-and-type-check job in `.github/workflows/ci.yaml`
When the `Set up Python` step is configured
Then `cache: "uv"` must be removed from the setup-python action parameters
And the job must complete without "Caching for 'uv' is not supported" errors

#### Scenario: test job removes cache parameter

Given the test job in `.github/workflows/ci.yaml`
When the `Set up Python` step is configured
Then `cache: "uv"` must be removed from the setup-python action parameters
And the job must complete without "Caching for 'uv' is not supported" errors

### Requirement: Rely on astral-sh/setup-uv for caching

The system SHALL rely on `astral-sh/setup-uv@v2` action to handle UV caching implicitly, eliminating the need for explicit cache configuration in setup-python.

#### Scenario: UV caching works implicitly

Given the workflow uses `astral-sh/setup-uv@v2` before setup-python
When `uv sync` is executed to install dependencies
Then UV's package cache is automatically utilized
And no explicit caching parameter is required in the setup-python action

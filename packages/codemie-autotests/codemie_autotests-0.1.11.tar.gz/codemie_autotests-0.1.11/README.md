# CodeMie Python Autotests

End-to-end, integration, and UI test suite for CodeMie services. This repository exercises CodeMie APIs (LLM, assistants, workflows, tools) and common integrations.

The project is designed for high-parallel execution with pytest-xdist, resilient runs with pytest-rerunfailures, and optional reporting to ReportPortal.

## Table of Contents

- Overview
- Prerequisites
- Installation
- Quick start
- Configuration
  - Custom environment (direct env vars)
  - Predefined environments (PREVIEW/AZURE/GCP/AWS/PROD/LOCAL)
  - Local with custom GitLab/GitHub/Jira/Confluence tokens
- Running tests
  - Common options and markers
  - UI tests (Playwright)
  - ReportPortal integration
- Makefile targets
- Troubleshooting

## Overview

This repository contains pytest-based suites to validate CodeMie capabilities:

- Service tests for assistants, workflows, tasks, integrations, and datasources
- Workflow tests for direct and virtual assistant tools
- E2E/regression packs
- UI tests powered by Playwright

Project layout highlights:

- tests/ — test suites, fixtures, utilities, and test data
- pyproject.toml — dependencies (Poetry)
- pytest.ini — pytest configuration and ReportPortal defaults
- Makefile — helper targets for install/lint/build/publish

## Prerequisites

- Python 3.12+
- Poetry (recommended) or pip
- For UI tests: Playwright browsers installed
- Access to the required CodeMie environment and credentials

## Installation

Choose one of the following:

1) With Poetry (recommended)

```shell
poetry install
```

2) With pip

```shell
pip install codemie-autotests
```

Tip: Use a virtual environment. With Poetry, venv is created automatically per project.

## Quick start

Run a small sanity pack (smoke) against a custom environment using exported variables:

```shell
export AUTH_SERVER_URL=<auth_server_url>
export AUTH_CLIENT_ID=<client_id>
export AUTH_CLIENT_SECRET=<client_secret>
export AUTH_REALM_NAME=<realm_name>
export CODEMIE_API_DOMAIN=<codemie_api_domain_url>

pytest -n 8 -m smoke --reruns 2
```

Or pass variables inline:

```shell
AUTH_SERVER_URL=<auth_server_url> \
AUTH_CLIENT_ID=<client_id> \
AUTH_CLIENT_SECRET=<client_secret> \
AUTH_REALM_NAME=<realm_name> \
CODEMIE_API_DOMAIN=<codemie_api_domain_url> \
pytest -n 8 -m "smoke or mcp or plugin" --reruns 2
```

## Configuration

### Custom environment (direct env vars)

Provide the following environment variables for ad-hoc runs:

- AUTH_SERVER_URL, AUTH_CLIENT_ID, AUTH_CLIENT_SECRET, AUTH_REALM_NAME
- CODEMIE_API_DOMAIN

### Predefined environments (PREVIEW, AZURE, GCP, AWS, PROD, LOCAL)

For runs targeting predefined environments, create a .env file in project root. If you provide AWS credentials, the suite will fetch additional values from AWS Systems Manager Parameter Store and recreate .env accordingly.

```properties
ENV=local

AWS_ACCESS_KEY=<aws_access_token>
AWS_SECRET_KEY=<aws_secret_key>
```

Now you can run full or subset packs. Examples:

```shell
# All tests (-n controls the number of workers)
pytest -n 10 --reruns 2

# E2E + regression only
pytest -n 10 -m "e2e or regression" --reruns 2
```

Note: "--reruns 2" uses pytest-rerunfailures to improve resiliency in flaky environments.

### Local with custom GitLab, GitHub, Jira and Confluence tokens

1) Start from a .env populated via AWS (optional)
2) Replace the tokens below with your personal values
3) Important: After replacing tokens, remove AWS_ACCESS_KEY and AWS_SECRET_KEY from .env — otherwise they will overwrite your changes next time .env is regenerated

Full .env example:

```properties
ENV=local
PROJECT_NAME=codemie
GIT_ENV=gitlab # required for e2e tests only
DEFAULT_TIMEOUT=60
CLEANUP_DATA=True
LANGFUSE_TRACES_ENABLED=False

CODEMIE_API_DOMAIN=http://localhost:8080

FRONTEND_URL=https://localhost:5173/
HEADLESS=False

NATS_URL=nats://localhost:4222

TEST_USER_FULL_NAME=dev-codemie-user

GITLAB_URL=<gitlab_url>
GITLAB_TOKEN=<gitlab_token>
GITLAB_PROJECT=<gitlab_project>
GITLAB_PROJECT_ID=<gitlab_project_id>

GITHUB_URL=<github_url>
GITHUB_TOKEN=<github_token>
GITHUB_PROJECT=<github_project>

JIRA_URL=<jira_url>
JIRA_TOKEN=<jira_token>
JQL="project = 'EPMCDME' and issuetype = 'Epic' and status = 'Closed'"

CONFLUENCE_URL=<confluence_url>
CONFLUENCE_TOKEN=<confluence_token>
CQL="space = EPMCDME and type = page and title = 'AQA Backlog Estimation'"

RP_API_KEY=<report_portal_api_key>
```

## Running tests

### Common options and markers

- Parallelism: -n <workers> (pytest-xdist). Example: -n 10 or -n auto
- Reruns: --reruns <N>
- Marker selection: -m "expr"

Common markers used in this repo include:

- smoke
- mcp
- plugin
- e2e
- regression
- ui
- jira_kb, confluence_kb, code_kb
- gitlab, github, git

Examples:

```shell
# Combine markers
pytest -n 8 -m "smoke or mcp" --reruns 2

# Only mcp
pytest -n 8 -m mcp --reruns 2

# Specific integrations
pytest -n 10 -m "jira_kb or github" --reruns 2
```

### UI tests (Playwright)

Install browsers once:

```shell
playwright install
```

Then run UI pack:

```shell
pytest -n 4 -m ui --reruns 2
```

Playwright docs: https://playwright.dev/python/docs/intro

### ReportPortal integration

pytest.ini is preconfigured with rp_endpoint, rp_project, and a default rp_launch. To publish results:

1) Set RP_API_KEY in .env
2) Add the flag:

```shell
pytest -n 10 -m "e2e or regression" --reruns 2 --reportportal
```

If you need access to the ReportPortal project, contact: Anton Yeromin (anton_yeromin@epam.com).

## Makefile targets

- install — poetry install
- ruff — lint and format with Ruff
- ruff-format — format only
- ruff-fix — apply autofixes
- build — poetry build
- publish — poetry publish

Example:

```shell
make install
make ruff
```

## Troubleshooting

- Playwright not installed: Run playwright install.
- Headless issues locally: Set HEADLESS=True in .env for CI or False for local debugging.
- Env values keep reverting: Ensure AWS_ACCESS_KEY and AWS_SECRET_KEY are removed after manual edits to .env.
- Authentication failures: Verify AUTH_* variables and CODEMIE_API_DOMAIN are correct for the target environment.
- Slow or flaky runs: Reduce -n, increase timeouts, and/or use --reruns.

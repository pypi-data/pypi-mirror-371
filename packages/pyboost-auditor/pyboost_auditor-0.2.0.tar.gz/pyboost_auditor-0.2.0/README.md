# pyboost

**pyboost** is a Python CLI tool that helps you identify and quantify the financial impact of outdated Python versions in your projects. It provides a detailed report on potential cloud cost savings and offers actionable upgrade recommendations.

## Features

- **Automated Scanning:** Scans for `Dockerfile` and `environment.yaml` files to automatically detect Python versions.
- **Cost Analysis:** Estimates annual cloud savings based on your monthly bill and a hard-coded knowledge base of Python performance improvements.
- **Dependency Checks:** Runs `pip check` to find potential dependency conflicts before you upgrade.
- **CI/CD Ready:** Designed to be easily integrated into your CI/CD pipeline as a proactive guardrail.
- **Visual Reports:** Provides a clear, color-coded report in the terminal for easy reading.

## Installation

```bash
pip install pyboost
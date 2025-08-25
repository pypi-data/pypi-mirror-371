# Contributing to wspr-ai-lite

Thank you for your interest in contributing!
This project is open to contributions from the ham radio and open source community.

## Development Setup

1. Clone the repo:
   ```bash
   git clone git@github.com:KI7MT/wspr-ai-lite.git
   cd wspr-ai-lite
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install development dependencies:
   ```bash
   make setup-dev
   ```

4. Run tests:
   ```bash
   make test
   ```

## Contribution Workflow

1. **Fork** the repository.
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. **Commit your changes**:
   - Follow conventional commits when possible (`fix:`, `feat:`, `docs:`, etc.).
   - Ensure pre-commit hooks and tests pass:
     ```bash
     pre-commit run --all-files
     make test
     ```
4. **Push your branch** and open a **Pull Request**.

## Code Style & Checks

- Code is formatted with **black** and **isort**.
- **Docstrings** are required (enforced with `interrogate`).
- Pre-commit hooks run automatically:
  - Trailing whitespace
  - EOF fixes
  - YAML/JSON/TOML validation
  - Docstring coverage
  - Artifact blocking (no `site/`, DuckDB, etc. in commits)

## Smoke Tests

Before tagging a release, please run:

```bash
make smoke-test
```

This ensures the package builds, installs, ingests, and launches the UI end-to-end.

## 👥 Contributors

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for a list of people who have helped shape this project.

## 📜 License

By contributing, you agree that your contributions will be licensed under the [LICENSE](LICENSE) of this repository.

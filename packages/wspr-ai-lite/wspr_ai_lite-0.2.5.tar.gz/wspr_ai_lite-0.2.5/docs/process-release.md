# Release Process

This project uses **Semantic Versioning** and **Trusted Publishing** to PyPI via GitHub Actions.
The **smoke** workflow runs on PRs and `main`, and additionally performs a real **PyPI smoke** on tags.

---

## TL;DR

1. Bump version
2. Update changelog
3. Run smoke locally
4. Tag & push
5. CI builds + publishes
6. Verify PyPI
7. Done 🎉

---

## 0) Pre-requisites

- Push access to `main`.
- PyPI project **wspr-ai-lite** is configured with Trusted Publisher for:
  - Repo: `KI7MT/wspr-ai-lite`
  - Workflow: `publish.yml` (or `release.yml`)
- GitHub Actions enabled.

---

## 1) Choose a version

Follow **SemVer**: `MAJOR.MINOR.PATCH`.

- **Patch** = bug fixes
- **Minor** = features
- **Major** = breaking changes

---

## 2) Bump version & changelog

- Update `__version__` in `src/wspr_ai_lite/__init__.py`.
- Add new section to `CHANGELOG.md`.

---

## 3) Local checks

```bash
make test
pre-commit run -a
make smoke-test
```

## 4) Commit and Tag
```bash
git commit -am "release: v0.x.y"
git tag v0.x.y
git push origin main --tags
```

## 5) Monitor CI
- publish job should publish to PyPI.
- smoke-src and smoke-pypi should pass.

## 6) Verify PyPi Manually
```bash
python -m venv .check
.check/bin/pip install wspr-ai-lite==0.x.y
```

## 7) Draft GitHub Release Notes
Use the entry from CHANGELOG.md.


## 8) Rollback / Re-release
- PyPI versions cannot be overwritten → bump patch version.
- Yank broken releases on PyPI if necessary.


## Troubleshooting
- invalid-publisher: Ensure Trusted Publisher matches repo/workflow.
- app missing: Ensure wspr_ai_lite.py is packaged.
- Makefile errors: check for TAB indentation.
- pre-commit failures: fix docstrings, run pre-commit run -a.

```bash
make smoke-test
make smoke-test-pypi VERSION=0.x.y
git commit -am "release: v0.x.y" && git tag v0.x.y && git push origin main --tags
```

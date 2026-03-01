# OpenClaw v0.1.0 - Test PyPI Release Draft

Overview
- This draft outlines the plan to publish the first test release to PyPI Test PyPI for OpenClaw (Python-first packaging with OpenClaw UI integration).
- Target: validate packaging, metadata, dependencies, and basic installation workflow before production release.

What will be released
- Built Python wheel and sdist for v0.1.0
- Meta information: package name, version, description, license, URLs, classifiers
- CI hooks to publish to Test PyPI when a token is provided in CI Secrets

- Tokens and credentials should not be committed. Use CI Secrets: PYPI_TEST_API_TOKEN for Test PyPI uploads.
- This is a dry-run for the release process; actual deployment requires token configuration and human validation of the published artifacts.

How to test locally (manual steps)
- Build:
  - python -m pip install --upgrade pip build
  - python -m build
- Test upload (requires Test PyPI token):
  - twine upload dist/* --repository-url https://test.pypi.org/legacy/ -u __token__ -p <PYPI_TEST_API_TOKEN>
- Install from Test PyPI to verify:
  - pip install --index-url https://test.pypi.org/simple/ openclaw==<version>

Acceptance criteria
- Wheel and sdist produced without errors
- Upload to Test PyPI succeeds with provided token
- Installing from Test PyPI works and matches expected behavior

Owner notes
- Update the real Release notes with exact metadata, dependencies, and changelog once token access is confirmed.

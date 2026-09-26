# Releasing Django QueryWatch

Releases are published to PyPI through GitHub Actions Trusted Publishing. No
PyPI API token is stored in this repository.

## One-time setup

Before the first release, create a pending trusted publisher on PyPI:

1. Sign in to PyPI and open **Publishing**.
2. Choose **Add a new pending publisher**.
3. Enter these exact values:

   | Field | Value |
   | --- | --- |
   | PyPI project name | `django-querywatch` |
   | Owner | `Atiqumer` |
   | Repository name | `django-querywatch` |
   | Workflow filename | `publish.yml` |
   | Environment name | `pypi` |

4. In GitHub, create a repository environment named `pypi`. Configure
   protection rules so only intended release tags can deploy to it.

The workflow uses job-level `id-token: write` permission and PyPA's official
publishing action. Do not add a PyPI token as a GitHub secret for this flow.

## Releasing a version

1. Confirm CI is green and the version in `pyproject.toml` is new on PyPI.
2. Update `CHANGELOG.md` with the release date and final contents.
3. Commit and push the release preparation.
4. Create and push a matching version tag:

   ```powershell
   git tag v0.1.0
   git push origin v0.1.0
   ```

5. The **Publish to PyPI** workflow verifies Ruff and tests, builds the wheel
   and source distribution, then requests the `pypi` environment approval.
6. Approve the deployment only after checking the tag, version, and workflow
   run. PyPI will receive the package after approval.

Published versions cannot be replaced. If a correction is needed, publish a
new version rather than reusing the existing version number.

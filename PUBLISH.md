# Publishing PIICloak

## 📦 Publishing to PyPI

### Prerequisites

1. Create accounts:
   - PyPI: https://pypi.org/account/register/
   - TestPyPI: https://test.pypi.org/account/register/

2. Install publishing tools:
```bash
pip install --upgrade build twine
```

3. Generate API token:
   - Go to https://pypi.org/manage/account/token/
   - Create token for "Entire account" or specific project
   - Save it securely (you'll only see it once)

### Step 1: Test Build

```bash
cd /var/www/dmitry/piicloak

# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build the package
python3 -m build

# You should see:
# dist/
#   piicloak-1.0.0-py3-none-any.whl
#   piicloak-1.0.0.tar.gz
```

### Step 2: Test on TestPyPI (RECOMMENDED)

```bash
# Upload to TestPyPI first
python3 -m twine upload --repository testpypi dist/*

# Username: __token__
# Password: pypi-YOUR_TEST_TOKEN

# Test installation
pip install --index-url https://test.pypi.org/simple/ --no-deps piicloak
```

### Step 3: Publish to PyPI (PRODUCTION)

```bash
# Upload to real PyPI
python3 -m twine upload dist/*

# Username: __token__
# Password: pypi-YOUR_PROD_TOKEN
```

### Step 4: Verify

```bash
# Install from PyPI
pip install piicloak

# Test it
python3 -c "from piicloak import PIICloak; print('Success!')"
```

---

## 🐳 Publishing to Docker Hub

### Prerequisites

1. Create Docker Hub account: https://hub.docker.com/signup

2. Login:
```bash
docker login
# Username: your_dockerhub_username
# Password: your_dockerhub_password (or token)
```

### Step 1: Build Multi-Arch Images

```bash
cd /var/www/dmitry/piicloak

# Build for your platform first
docker build -t YOUR_USERNAME/piicloak:1.0.0 .
docker build -t YOUR_USERNAME/piicloak:latest .

# Test it locally
docker run -p 5050:5050 YOUR_USERNAME/piicloak:latest
```

### Step 2: Push to Docker Hub

```bash
# Push versioned image
docker push YOUR_USERNAME/piicloak:1.0.0

# Push latest tag
docker push YOUR_USERNAME/piicloak:latest
```

### Step 3: (Optional) Multi-Architecture Build

For ARM64 (Apple Silicon, Raspberry Pi, etc.) support:

```bash
# Create and use buildx builder
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap

# Build and push for multiple architectures
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t YOUR_USERNAME/piicloak:1.0.0 \
  -t YOUR_USERNAME/piicloak:latest \
  --push \
  .
```

### Step 4: Verify

```bash
# Pull and run
docker pull YOUR_USERNAME/piicloak:latest
docker run -p 5050:5050 YOUR_USERNAME/piicloak:latest

# Test
curl http://localhost:5050/health
```

---

## 🤖 Automated Publishing (GitHub Actions)

Releases are fully automated by two workflows:

- `.github/workflows/release-please.yml` — runs on every push to `main`.
  Maintains a **release PR** that bumps the version in `pyproject.toml` and
  `src/piicloak/__init__.py` and updates `docs/CHANGELOG.md` based on
  [Conventional Commits](https://www.conventionalcommits.org/) since the last
  release. Merging that PR creates the `vX.Y.Z` git tag and the GitHub release
  with auto-generated notes.
- `.github/workflows/publish.yml` — runs when a `vX.Y.Z` tag is pushed.
  Validates → lint/format/tests → builds wheel + sdist → uploads them to the
  GitHub release → publishes to PyPI via Trusted Publishing → builds multi-arch
  Docker image (`linux/amd64`, `linux/arm64`) and pushes
  `dimanjet/piicloak:<version>` + `:latest` to Docker Hub → syncs `README.md`
  to the Docker Hub repository overview.

### Release flow (for contributors)

1. Use Conventional Commit messages on PRs into `main`:
   - `feat: …` → minor version bump (`1.2.x` → `1.3.0`)
   - `fix: …` → patch bump (`1.2.0` → `1.2.1`)
   - `feat!: …` or `BREAKING CHANGE:` in body → major bump
   - `chore: …`, `docs: …`, `ci: …`, `refactor: …`, `test: …` → no release on
     their own, but show up under their category in the changelog.
2. After your PR merges, the **release-please** workflow opens or updates a PR
   titled e.g. `chore(main): release 1.3.0`. Review it like any other PR — it
   contains the proposed version bumps + `CHANGELOG.md` diff.
3. Merge the release PR. release-please creates the tag and the GitHub release,
   which triggers `publish.yml` to push the build to PyPI and Docker Hub.

No manual version edits, no `git tag` commands.

### PyPI setup (one-time)

Uses PyPI Trusted Publishing — no long-lived token:

1. At https://pypi.org/manage/project/piicloak/settings/publishing/ add a
   trusted publisher:
   - Owner: `dimanjet`
   - Repository: `piicloak`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
2. In GitHub, create the `pypi` environment at
   https://github.com/dimanjet/piicloak/settings/environments (no protection
   rules required).

### Docker Hub setup (one-time)

The `docker` job needs two repository secrets and a GitHub environment:

1. Create a Docker Hub access token:
   - https://app.docker.com/settings/personal-access-tokens → **Generate new token**
   - Scope: **Read, Write, Delete**. Name e.g. `piicloak-ci`.
   - Copy the token (shown only once).
2. Add repository secrets at
   https://github.com/dimanjet/piicloak/settings/secrets/actions :
   - `DOCKERHUB_USERNAME` → `dimanjet`
   - `DOCKERHUB_TOKEN` → the token from step 1.
3. Create the `dockerhub` environment at
   https://github.com/dimanjet/piicloak/settings/environments → **New environment**
   → name `dockerhub`. No protection rules required (optional: restrict
   deployment branches to tags matching `v*` and/or add required reviewers).

The Docker Hub repository overview (the page at
https://hub.docker.com/r/dimanjet/piicloak) is rewritten from `README.md` on
every release, so the Hub page can't drift from the repo README.

### Re-running a release manually

If a publish run fails (e.g. transient PyPI error), open the failed run on the
Actions tab and click **Re-run failed jobs** — only the failed job and its
dependants will rerun. The release tag and artifacts are already in place.

To re-publish an existing tag from scratch, trigger the `Release` workflow
manually with `workflow_dispatch` and pass the existing tag name (e.g.
`v1.2.1`); the workflow will check out that tag and run end-to-end.

---

## 📋 Release Checklist (per release)

- [ ] All PRs into `main` use Conventional Commit messages.
- [ ] release-please opened/updated a release PR.
- [ ] Review the release PR diff (version bumps + CHANGELOG entry look right).
- [ ] Merge the release PR.
- [ ] Confirm the `publish.yml` run on the new tag finishes green.
- [ ] Spot-check PyPI page, Docker Hub tags, and Docker Hub overview match the
      new version.

---

## 📊 Post-Publishing

After publishing, update README.md badges with real data:
- PyPI version badge (will show actual version)
- PyPI downloads (will show real download counts)
- Docker pulls (will show real pull counts)

Track your project:
- PyPI stats: https://pypistats.org/packages/piicloak
- Docker Hub: https://hub.docker.com/r/YOUR_USERNAME/piicloak
- GitHub stars: https://star-history.com/#YOUR_USERNAME/piicloak

---

## ⚠️ Important Notes

1. **You cannot delete/overwrite PyPI releases** - choose version numbers carefully
2. **Use semantic versioning**: MAJOR.MINOR.PATCH (e.g., 1.0.0, 1.0.1, 1.1.0)
3. **Test everything on TestPyPI first**
4. **Keep your API tokens secure** (never commit them)
5. **Create a CHANGELOG.md** to track version changes

---

## 🆘 Troubleshooting

**"Package already exists"**
- You can't re-upload the same version. Bump the version number.

**"Invalid distribution filename"**
- Clean and rebuild: `rm -rf dist/ && python3 -m build`

**Docker push denied**
- Make sure you're logged in: `docker login`
- Check the image name matches your username

**GitHub Actions failing**
- Check you've added the required secrets
- Review logs in the Actions tab

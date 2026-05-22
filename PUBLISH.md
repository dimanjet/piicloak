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

`.github/workflows/publish.yml` runs the release flow when a version tag is pushed.

### PyPI setup

Use PyPI Trusted Publishing instead of a long-lived API token:

1. Go to the PyPI project publishing settings.
2. Add a trusted publisher for this GitHub repository.
3. Use workflow name `publish.yml` and environment name `pypi`.
4. In GitHub, create the `pypi` environment under Settings → Environments.

No `PYPI_API_TOKEN` repository secret is required for this workflow.

### Release a version

```bash
# Update version in pyproject.toml and src/piicloak/__init__.py first.
git tag -a v1.1.0 -m "v1.1.0"
git push origin v1.1.0
```

The workflow will:

1. Verify the tag matches the package version.
2. Run lint, format, and tests.
3. Build and check the wheel/sdist.
4. Create the GitHub release with generated notes and distribution assets.
5. Publish the same distributions to PyPI.
6. Build a multi-arch (`linux/amd64`, `linux/arm64`) Docker image and push
   `dimanjet/piicloak:<version>` and `dimanjet/piicloak:latest` to Docker Hub.

If a tag already exists without a GitHub release, run the `Release` workflow manually from GitHub Actions and provide the existing tag name.

### Docker Hub setup (one-time)

The `docker` job in `publish.yml` needs two repository secrets and a GitHub
environment:

1. Create a Docker Hub access token:
   - Go to https://app.docker.com/settings/personal-access-tokens
   - Click **Generate new token**, scope **Read, Write, Delete**, name it e.g. `piicloak-ci`.
   - Copy the token (shown only once).
2. Add repository secrets at
   https://github.com/dimanjet/piicloak/settings/secrets/actions :
   - `DOCKERHUB_USERNAME` → your Docker Hub username (e.g. `dimanjet`).
   - `DOCKERHUB_TOKEN` → the access token from step 1.
3. Create the `dockerhub` environment at
   https://github.com/dimanjet/piicloak/settings/environments → **New environment** → name `dockerhub`. No protection rules required (optional: add a deployment branch rule restricting to tags matching `v*` and/or required reviewers).

---

## 📋 Release Checklist

Before publishing v1.0.0:

- [ ] All tests passing (`make test`)
- [ ] Version updated in `pyproject.toml` and `src/piicloak/__init__.py`
- [ ] CHANGELOG.md updated
- [ ] README.md reviewed
- [ ] GitHub repo created and code pushed
- [ ] GitHub release created with release notes
- [ ] PyPI package published
- [ ] Docker image published
- [ ] Documentation updated
- [ ] Tweet/blog post about the release

---

## 🔄 Version Bumping

For future releases:

```bash
# Update version in these files:
# - pyproject.toml (version = "1.0.1")
# - src/piicloak/__init__.py (__version__ = "1.0.1")

# Commit and tag
git add .
git commit -m "Bump version to 1.0.1"
git tag v1.0.1
git push origin main --tags

# GitHub Actions will create the GitHub release and publish to PyPI.
```

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

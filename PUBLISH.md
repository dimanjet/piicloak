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

Your `.github/workflows/publish.yml` already handles this!

**For PyPI:**
1. Go to repo Settings → Secrets → Actions
2. Add secret: `PYPI_API_TOKEN` with your PyPI token
3. Create a GitHub release or push a tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. GitHub Actions will automatically publish to PyPI

**For Docker Hub:**
1. Add secrets:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub password/token
2. Push a tag (as above)
3. GitHub Actions will automatically publish to Docker Hub

---

## 📋 Release Checklist

Before publishing v1.0.0:

- [ ] All tests passing (`make test`)
- [ ] Version updated in `setup.py`, `pyproject.toml`, `src/piicloak/__init__.py`
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
# - setup.py (version="1.0.1")
# - pyproject.toml (version = "1.0.1")
# - src/piicloak/__init__.py (__version__ = "1.0.1")

# Commit and tag
git add .
git commit -m "Bump version to 1.0.1"
git tag v1.0.1
git push origin main --tags

# GitHub Actions will handle the rest!
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

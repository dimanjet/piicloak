# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **marinovdk@gmail.com**

Please include the following information:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue (what an attacker could do)

## What to Expect

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will send you regular updates about our progress
- We will notify you when the vulnerability is fixed
- We will publicly acknowledge your responsible disclosure (unless you prefer to remain anonymous)

## Security Best Practices

When using PIICloak in production:

1. **Always use HTTPS** for API communication
2. **Enable API key authentication** (`PIICLOAK_API_KEY` environment variable)
3. **Configure CORS properly** (don't use `*` in production)
4. **Implement rate limiting** at the load balancer level
5. **Keep dependencies updated** (`pip install --upgrade piicloak`)
6. **Monitor logs** for suspicious activity
7. **Run with least privilege** (non-root user)
8. **Use secrets management** for sensitive configuration

## Known Security Considerations

- PIICloak processes sensitive data by design
- We do not store or log any input data
- The service is stateless and does not retain PII
- spaCy models are loaded from trusted sources only

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1) and announced via:

- GitHub Security Advisories
- Release notes
- Email notification to security@piicloak (if you subscribe)

## Dependency Security

We use:
- Dependabot for automated dependency updates
- CodeQL for static security analysis
- Regular security audits of dependencies

## Contact

For security concerns: marinovdk@gmail.com
For general questions: [GitHub Discussions](https://github.com/dimanjet/piicloak/discussions)

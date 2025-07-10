# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of the Recruitment Operations system seriously. If you discover a security vulnerability, please follow these steps:

1. **DO NOT** open a public GitHub issue
2. Email security details to: security@example.com
3. Include the following information:
   - Type of vulnerability
   - Component affected (CATS integration, Gemini API, etc.)
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Measures

This system implements the following security measures:

### API Security
- All API keys stored in environment variables
- HTTPS required for all external API calls
- Rate limiting on webhook endpoints

### Data Protection
- No candidate PII stored in logs
- Secure handling of resume data
- Encryption for sensitive configuration

### Access Control
- Authentication required for all endpoints
- Role-based access control
- Audit logging for sensitive operations

## Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Resolution Target**: Based on severity
  - Critical: 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: 90 days

## Disclosure Policy

- Security fixes will be released as soon as possible
- A security advisory will be published after the fix
- Credit will be given to reporters (unless anonymity requested)
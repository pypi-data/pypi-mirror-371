# certbot-dns-f5xc

A Certbot DNS plugin for F5 Distributed Cloud (F5XC) that allows you to obtain and renew Let's Encrypt certificates using DNS-01 challenges.

## Overview

This plugin enables automatic SSL/TLS certificate management through Let's Encrypt using DNS-01 challenges with F5 Distributed Cloud DNS services. It's particularly useful for wildcard certificates and domains that can't be validated through HTTP-01 challenges.

## Features

- **DNS-01 Challenge Support**: Automates Let's Encrypt DNS-01 challenges using F5XC DNS API
- **Multi-Domain Support**: Handle multiple domains and subdomains with a single configuration
- **Dynamic DNS Zone Detection**: Automatically extracts DNS zones from domain names
- **Flexible Authentication**: Supports both certificate-based authentication (recommended) and API token authentication
- **Resource Record Set (RRSet) Management**: Properly manages DNS records within F5XC's RRSet structure
- **Automatic Cleanup**: Removes TXT records after certificate validation

## Installation

### From Source

```bash
git clone https://github.com/fadlytabrani/certbot-dns-f5xc.git
cd certbot-dns-f5xc
pip install -e .
```

### Using pip

```bash
pip install certbot-dns-f5xc
```

## Configuration

**Authentication Priority**: When both certificate and API token credentials are provided, the plugin automatically uses certificate authentication and ignores the API token.

### Certificate-based Authentication (Recommended)

Create a configuration file at `~/.config/certbot/f5xc.ini`:

```ini
# F5XC DNS plugin configuration
dns_f5xc_tenant = your-tenant-id
dns_f5xc_certificate_path = /path/to/your/certificate.p12
dns_f5xc_certificate_password = your-certificate-password
dns_f5xc_propagation_seconds = 60  # Optional - DNS propagation delay in seconds
```

### API Token Authentication (Deprecated)

```ini
# F5XC DNS plugin configuration
dns_f5xc_api_token = your-api-token
dns_f5xc_propagation_seconds = 60  # Optional - DNS propagation delay in seconds
```

#### Configuration Options

- **`dns_f5xc_tenant`** (required for certificate auth): Your F5XC tenant ID
- **`dns_f5xc_certificate_path`** (required for certificate auth): Path to your P12 certificate file
- **`dns_f5xc_certificate_password`** (required for certificate auth): Password for the P12 certificate
- **`dns_f5xc_api_token`** (required for token auth): F5XC API token (deprecated)
- **`dns_f5xc_propagation_seconds`** (optional): DNS propagation delay in seconds (default: 60)
- **`dns_f5xc_rrset_identifier`** (optional): Custom identifier for RRSet naming (default: auto-detected machine hostname)

#### Authentication Priority

**Important**: The plugin uses a priority-based authentication system:

1. **Certificate Authentication (Priority 1)**: If `certificate_path`, `certificate_password`, and `tenant` are all provided, the plugin will use certificate authentication and **ignore any API token**.

2. **API Token Authentication (Priority 2)**: Only if certificate credentials are missing or incomplete will the plugin fall back to API token authentication.

**Example**: If you provide both certificate and API token credentials, the plugin will use certificate authentication and silently ignore the API token.

**Recommendation**: Use certificate authentication for production environments as it's more secure and provides better access control.

## Dynamic DNS Zone Detection

The plugin automatically extracts the DNS zone from domain names, making it perfect for multi-domain setups:

- **`example.com`** → Zone: `example.com`
- **`api.example.com`** → Zone: `example.com`
- **`sub.api.example.com`** → Zone: `example.com`
- **`www.example.com`** → Zone: `example.com`

## Resource Record Set (RRSet) Management

The plugin uses F5XC's Resource Record Set (RRSet) approach for DNS management:

- **Creates machine-specific "certbot-{identifier}" RRSets** for managing ACME challenge records
- **Configurable RRSet identifiers** via `dns_f5xc_rrset_identifier` in your INI file
- **Automatic machine identification** when no custom identifier is specified
- **Properly structures TXT records** within the RRSet for public DNS publishing
- **Ensures DNS propagation** by using F5XC's recommended API patterns
- **Automatic cleanup** of challenge records and empty RRSets after validation

### RRSet Naming Strategy

The plugin automatically creates machine-specific RRSets to prevent conflicts:

- **Default behavior**: Uses sanitized hostname (e.g., `certbot-ft-mbp1-local`)
- **Custom identifier**: Set `dns_f5xc_rrset_identifier = your_custom_name` in your INI file
- **F5XC compliance**: All names automatically follow RFC 1035 naming rules
- **Multi-device support**: Each device gets its own isolated RRSet

## Usage

### Basic Certificate Request

```bash
certbot certonly \
  --authenticator dns-f5xc \
  --dns-f5xc-credentials ~/.config/certbot/f5xc.ini \
  --dns-f5xc-propagation-seconds 60 \
  -d example.com \
  -d *.example.com
```

### Wildcard Certificate

```bash
certbot certonly \
  --authenticator dns-f5xc \
  --dns-f5xc-credentials ~/.config/certbot/f5xc.ini \
  -d *.example.com
```

### Certificate Renewal

```bash
certbot renew --authenticator dns-f5xc
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/fadlytabrani/certbot-dns-f5xc.git
cd certbot-dns-f5xc
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please:

- Open an issue on GitHub

## Acknowledgments

This plugin follows Certbot's standard DNS authenticator patterns for consistency and reliability.

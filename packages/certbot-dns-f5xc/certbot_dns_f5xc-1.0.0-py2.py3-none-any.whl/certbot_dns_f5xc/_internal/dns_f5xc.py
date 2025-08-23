"""DNS Authenticator for F5 Distributed Cloud (F5XC)."""
import logging
import time
from typing import Any, Dict, Optional

import requests
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization

from certbot import errors
from certbot.plugins import dns_common
from certbot.plugins.dns_common import CredentialsConfiguration

logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for F5 Distributed Cloud (F5XC)

    This Authenticator uses the F5XC API to fulfill a dns-01 challenge.
    """

    description = (
        'Obtain certificates using a DNS TXT record (if you are using F5XC for DNS).')
    ttl = 60

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.credentials: Optional[CredentialsConfiguration] = None
        self.f5xc_client: Optional["_F5XCClient"] = None

    @classmethod
    def add_parser_arguments(cls, add: Any, default_propagation_seconds: int = 60) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        add('credentials', help='F5XC credentials INI file.')

    def more_info(self) -> str:
        return ('This plugin configures a DNS TXT record to respond to a dns-01 challenge using '
                'the F5 Distributed Cloud (F5XC) API.')

    def _validate_credentials(self, credentials: CredentialsConfiguration) -> None:
        # Check for certificate-based authentication (recommended)
        certificate_path = credentials.conf('certificate_path')
        certificate_password = credentials.conf('certificate_password')
        tenant = credentials.conf('tenant')

        if certificate_path and certificate_password and tenant:
            # Certificate authentication is valid
            return
        else:
            # Fall back to API token authentication (deprecated)
            api_token = credentials.conf('api_token')
            if not api_token:
                raise errors.PluginError(
                    f'{credentials.confobj.filename}: Either certificate_path + certificate_password + tenant '
                    f'(recommended), or api_token is required for F5XC authentication.'
                )

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            'credentials',
            'F5XC credentials INI file',
            None,
            self._validate_credentials
        )

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        """Perform the DNS-01 challenge by creating a TXT record."""
        self._get_f5xc_client().add_txt_record(
            domain, validation_name, validation, self.ttl)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        """Clean up the DNS-01 challenge TXT record."""
        self._get_f5xc_client().delete_txt_record(domain, validation_name, validation)

    def _get_f5xc_client(self) -> "_F5XCClient":
        if not self.credentials:  # pragma: no cover
            raise errors.Error("Plugin has not been prepared.")

        # Try certificate authentication first, fall back to API token
        certificate_path = self.credentials.conf('certificate_path')
        certificate_password = self.credentials.conf('certificate_password')
        tenant = self.credentials.conf('tenant')

        # Get optional RRSet identifier
        rrset_identifier = self.credentials.conf('rrset_identifier')

        if certificate_path and certificate_password and tenant:
            return _F5XCClient(
                tenant=tenant,
                certificate_path=certificate_path,
                certificate_password=certificate_password,
                rrset_identifier=rrset_identifier
            )
        else:
            # Fall back to API token authentication
            api_token = self.credentials.conf('api_token')
            return _F5XCClient(
                tenant=tenant,  # Always pass tenant for API URL construction
                api_token=api_token,
                rrset_identifier=rrset_identifier
            )


class _F5XCClient:
    """
    Encapsulates all communication with the F5XC API.
    """

    def __init__(self, tenant: Optional[str] = None, certificate_path: Optional[str] = None,
                 certificate_password: Optional[str] = None, api_token: Optional[str] = None,
                 rrset_identifier: Optional[str] = None) -> None:
        """
        Initialize the F5XC client.

        Args:
            tenant: F5XC tenant ID
            certificate_path: Path to P12 certificate file
            certificate_password: Password for the P12 certificate
            api_token: F5XC API token (deprecated)
            rrset_identifier: Custom identifier for RRSet naming (optional)
        """
        self.tenant = tenant
        self.api_token = api_token
        self.rrset_identifier = rrset_identifier
        self.session = requests.Session()

        if certificate_path and certificate_password:
            self._setup_certificate_auth(
                certificate_path, certificate_password)
        elif api_token:
            self._setup_token_auth(api_token)
        else:
            raise ValueError(
                "Either certificate_path + certificate_password or api_token must be provided")

    def _setup_certificate_auth(self, certificate_path: str, certificate_password: str) -> None:
        """Set up certificate-based authentication."""
        try:
            # Extract PEM certificate and private key from P12
            with open(certificate_path, 'rb') as p12_file:
                p12_data = p12_file.read()

            # Extract certificate and key
            private_key, certificate, _ = pkcs12.load_key_and_certificates(
                p12_data, certificate_password.encode()
            )

            # Convert to PEM format
            cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
            key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            # Create temporary files
            import tempfile
            cert_file = tempfile.NamedTemporaryFile(
                delete=False, suffix='.crt')
            key_file = tempfile.NamedTemporaryFile(delete=False, suffix='.key')

            cert_file.write(cert_pem)
            key_file.write(key_pem)
            cert_file.close()
            key_file.close()

            # Set up session with certificate
            self.session.cert = (cert_file.name, key_file.name)
            self.session.headers.update({
                "Content-Type": "application/json",
            })

            # Store temp file paths for cleanup
            self._temp_files = [cert_file.name, key_file.name]
            logger.info("Certificate authentication configured successfully")

        except Exception as e:
            raise errors.PluginError(
                f"Failed to set up certificate authentication: {e}")

    def _setup_token_auth(self, api_token: str) -> None:
        """Set up API token-based authentication (deprecated)."""
        self.session.headers.update({
            "Authorization": f"APIToken {api_token}",
            "Content-Type": "application/json",
        })
        logger.info("API token authentication configured (deprecated)")

    def add_txt_record(self, domain: str, record_name: str, record_content: str,
                       record_ttl: int) -> None:
        """
        Add a TXT record using the supplied information.

        Args:
            domain: The domain to use to look up the F5XC zone.
            record_name: The record name (typically beginning with '_acme-challenge.').
            record_content: The record content (typically the challenge validation).
            record_ttl: The record TTL (number of seconds that the record may be cached).
        """
        zone_name = self._find_zone_name(domain)
        api_url = f"https://{self.tenant}.console.ves.volterra.io"

        # Get the current zone configuration
        zone_url = f"{api_url}/api/config/dns/namespaces/system/dns_zones/{zone_name}"

        try:
            response = self.session.get(zone_url, allow_redirects=False)
            response.raise_for_status()
            zone_data = response.json()
        except Exception as e:
            raise errors.PluginError(f"Failed to get zone configuration: {e}")

            # Create or find the machine-specific certbot RRSet
        machine_id = self._get_machine_id()
        rrset_name = f"certbot-{machine_id}"

        certbot_rrset = None
        if "rr_set_group" in zone_data["spec"]["primary"]:
            for rrset in zone_data["spec"]["primary"]["rr_set_group"]:
                if rrset["metadata"]["name"] == rrset_name:
                    certbot_rrset = rrset
                    break

        # If machine-specific RRSet doesn't exist, create it
        if not certbot_rrset:
            logger.info(
                f"Creating new {rrset_name} RRSet for machine {machine_id}...")
            certbot_rrset = {
                "metadata": {
                    "name": rrset_name,
                    "namespace": "system",
                    "description": f"Managed by certbot-dns-f5xc plugin on {machine_id}"
                },
                "rr_set": []
            }
            zone_data["spec"]["primary"]["rr_set_group"].append(
                certbot_rrset)
        else:
            logger.info(
                f"Using existing {rrset_name} RRSet for machine {machine_id}...")
            # Clean up any existing challenge records to avoid conflicts
            if "rr_set" in certbot_rrset:
                certbot_rrset["rr_set"] = [
                    record for record in certbot_rrset["rr_set"]
                    if not record.get("txt_record", {}).get("name", "").startswith("_acme-challenge")
                ]

        # Extract the subdomain from the full name
        subdomain = self._extract_subdomain(record_name, zone_name)

        # Add the TXT record to the machine-specific certbot RRSet
        # Keep original challenge names for Let's Encrypt validation
        from datetime import datetime, timezone

        txt_record = {
            "ttl": record_ttl,
            "txt_record": {
                "name": subdomain,
                "values": [record_content]
            },
            "description": f"Created {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
        }

        # Check if record already exists and update it, otherwise add new
        record_exists = False
        for record in certbot_rrset["rr_set"]:
            if (record.get("txt_record", {}).get("name") == subdomain and
                    record.get("ttl") == record_ttl):
                record.update(txt_record)
                record_exists = True
                break

        if not record_exists:
            certbot_rrset["rr_set"].append(txt_record)

        # Update the zone configuration
        try:
            response = self.session.put(
                zone_url, json=zone_data, allow_redirects=False)
            response.raise_for_status()
            logger.info(
                f"Successfully added TXT record: {record_name} to {rrset_name} RRSet")
        except Exception as e:
            # Check if this is a duplicate RR type error (conflict with existing records)
            if hasattr(e, 'response') and e.response is not None:
                error_text = e.response.text
                logger.error(f"API Error Response: {error_text}")

                # Check for duplicate RR type error
                if "duplicate RR type" in error_text and "TXT" in error_text:
                    # Extract the conflicting record name from the error
                    import re
                    match = re.search(
                        r"Record '([^']+)' contains duplicate RR type", error_text)
                    if match:
                        conflicting_record = match.group(1)
                        raise errors.PluginError(
                            f"There is an existing record '{conflicting_record}' created outside the {rrset_name} managed "
                            f"resource record group. Please remove this record manually before requesting a certificate, "
                            f"or contact your DNS administrator to resolve the conflict."
                        )
                    else:
                        raise errors.PluginError(
                            f"There is an existing TXT record that conflicts with the {rrset_name} managed "
                            f"resource record group. Please remove any existing '_acme-challenge.*' records "
                            f"before requesting a certificate."
                        )
                else:
                    # For other types of errors, show the technical details
                    raise errors.PluginError(f"Failed to add TXT record: {e}")
            else:
                raise errors.PluginError(f"Failed to add TXT record: {e}")

    def delete_txt_record(self, domain: str, record_name: str, record_content: str) -> None:
        """
        Delete a TXT record using the supplied information.

        Args:
            domain: The domain to use to look up the F5XC zone.
            record_name: The record name (typically beginning with '_acme-challenge.').
            record_content: The record content (typically the challenge validation).
        """
        try:
            zone_name = self._find_zone_name(domain)
            api_url = f"https://{self.tenant}.console.ves.volterra.io"

            # Get the current zone configuration
            zone_url = f"{api_url}/api/config/dns/namespaces/system/dns_zones/{zone_name}"

            response = self.session.get(zone_url, allow_redirects=False)
            response.raise_for_status()
            zone_data = response.json()
        except Exception as e:
            logger.debug(
                f"Encountered error getting zone during deletion: {e}")
            return

        # Extract the subdomain from the full name
        subdomain = self._extract_subdomain(record_name, zone_name)

        # Find and remove the TXT record from the machine-specific certbot RRSet
        machine_id = self._get_machine_id()
        rrset_name = f"certbot-{machine_id}"

        if "rr_set_group" in zone_data["spec"]["primary"]:
            for i, rrset in enumerate(zone_data["spec"]["primary"]["rr_set_group"]):
                if rrset["metadata"]["name"] == rrset_name:
                    if "rr_set" in rrset:
                        # Remove the TXT record by matching name and content
                        rrset["rr_set"] = [
                            record for record in rrset["rr_set"]
                            if not (record.get("txt_record", {}).get("name") == subdomain and
                                    record.get("txt_record", {}).get("values") == [record_content])
                        ]

                        # If this was the last record in the RRSet, remove the entire RRSet
                        if not rrset["rr_set"]:
                            logger.info(
                                f"Removing empty {rrset_name} RRSet after cleanup")
                            zone_data["spec"]["primary"]["rr_set_group"].pop(i)
                    break

        # Update the zone configuration
        try:
            response = self.session.put(
                zone_url, json=zone_data, allow_redirects=False)
            response.raise_for_status()
            logger.info(
                f"Successfully deleted TXT record: {record_name} from {rrset_name} RRSet")
        except Exception as e:
            logger.warning(f"Failed to delete TXT record: {e}")

    def _find_zone_name(self, domain: str) -> str:
        """
        Find the zone name for a given domain.

        Args:
            domain: The domain for which to find the zone name.

        Returns:
            The zone name, if found.

        Raises:
            certbot.errors.PluginError: if no zone name is found.
        """
        # Handle wildcard domains - strip the wildcard prefix
        if domain.startswith('*.'):
            domain = domain[2:]

        # For wildcard certificates, the zone is the domain itself (without the wildcard)
        # For regular domains, try progressively shorter parent domains until we find one that exists
        parts = domain.split('.')

        if len(parts) < 2:
            raise errors.PluginError(f"Unable to determine zone name for {domain}. "
                                     f"Please confirm that the domain name has been entered correctly "
                                     f"and is managed by F5XC.")

        # Try progressively shorter parent domains
        # e.g., for test1.int.yunohave.com, try:
        # 1. test1.int.yunohave.com
        # 2. int.yunohave.com
        # 3. yunohave.com
        for i in range(len(parts), 1, -1):
            candidate_zone = '.'.join(parts[-i:])

            # Check if this zone exists in F5XC
            try:
                api_url = f"https://{self.tenant}.console.ves.volterra.io"
                zone_url = f"{api_url}/api/config/dns/namespaces/system/dns_zones/{candidate_zone}"
                response = self.session.get(zone_url, allow_redirects=False)

                if response.status_code == 200:
                    logger.info(
                        f"Found existing zone: {candidate_zone} for domain: {domain}")
                    return candidate_zone
                elif response.status_code == 404:
                    logger.debug(
                        f"Zone {candidate_zone} does not exist, trying parent domain...")
                    continue
                else:
                    # If we get an error other than 404, log it but continue trying
                    logger.warning(
                        f"Unexpected response {response.status_code} for zone {candidate_zone}: {response.text}")
                    continue

            except Exception as e:
                logger.debug(
                    f"Error checking zone {candidate_zone}: {e}, trying parent domain...")
                continue

        # If we get here, no zone was found
        raise errors.PluginError(f"Unable to find a valid zone for {domain}. "
                                 f"Please confirm that the domain name has been entered correctly "
                                 f"and is managed by F5XC.")

    def _get_machine_id(self) -> str:
        """
        Get a unique identifier for this machine that follows F5XC naming rules.

        Priority order:
        1. Configurable rrset_identifier from INI file
        2. Hostname (sanitized)
        3. Environment variable CERTBOT_MACHINE_ID
        4. Fallback combination

        F5XC naming rules (RFC 1035):
        - Lower case alphanumeric characters or '-'
        - Start with alphabetic character
        - End with alphanumeric character
        - No dots or other special characters

        Returns:
            A unique string identifier for the current machine.
        """
        import socket
        import os
        import re

        def sanitize_name(name: str) -> str:
            """Sanitize a name to follow F5XC naming rules."""
            # Replace dots, underscores, and other invalid chars with hyphens
            sanitized = re.sub(r'[^a-z0-9-]', '-', name.lower())
            # Remove multiple consecutive hyphens
            sanitized = re.sub(r'-+', '-', sanitized)
            # Ensure it starts with a letter
            if sanitized and not sanitized[0].isalpha():
                sanitized = f"m-{sanitized}"
            # Ensure it ends with alphanumeric
            if sanitized and not sanitized[-1].isalnum():
                sanitized = sanitized.rstrip('-')
            # If empty after sanitization, use fallback
            if not sanitized:
                sanitized = "unknown"
            return sanitized

        # First priority: Check for configurable rrset_identifier
        if hasattr(self, 'rrset_identifier') and self.rrset_identifier:
            return sanitize_name(self.rrset_identifier)

        # Second priority: Try to get hostname
        try:
            hostname = socket.gethostname()
            if hostname and hostname != 'localhost':
                return sanitize_name(hostname)
        except:
            pass

        # Fallback to environment variable
        machine_id = os.environ.get('CERTBOT_MACHINE_ID')
        if machine_id:
            return sanitize_name(machine_id)

        # Final fallback to a combination of hostname and user
        try:
            username = os.environ.get('USER', 'unknown')
            hostname = socket.gethostname() or 'unknown'
            combined = f"{username}-{hostname}"
            return sanitize_name(combined)
        except:
            return "unknown-machine"

    def _extract_subdomain(self, record_name: str, zone_name: str) -> str:
        """
        Extract the subdomain from a full DNS name.

        Args:
            record_name: Full DNS name (e.g., _acme-challenge.example.com)
            zone_name: The zone name (e.g., example.com)

        Returns:
            Subdomain part (e.g., _acme-challenge)
        """
        # Remove the zone suffix
        if record_name.endswith(f".{zone_name}"):
            subdomain = record_name[:-(len(zone_name) + 1)]
        else:
            subdomain = record_name

        # Handle root domain case
        if subdomain == zone_name or not subdomain:
            return "root"

        # Return the subdomain as-is, preserving underscores
        return subdomain

    def cleanup(self) -> None:
        """Clean up temporary files."""
        if hasattr(self, '_temp_files'):
            import os
            for temp_file in self._temp_files:
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass

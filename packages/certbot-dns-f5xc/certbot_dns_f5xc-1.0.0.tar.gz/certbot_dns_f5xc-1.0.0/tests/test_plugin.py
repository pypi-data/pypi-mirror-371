#!/usr/bin/env python3
"""Simple test script for the F5XC plugin."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_import():
    """Test that we can import the plugin."""
    try:
        from certbot_dns_f5xc._internal.dns_f5xc import Authenticator, _F5XCClient
        print("✅ Plugin imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Failed to import plugin: {e}")
        return False


def test_authenticator_creation():
    """Test that we can create an authenticator instance."""
    try:
        from certbot_dns_f5xc._internal.dns_f5xc import Authenticator
        from unittest.mock import Mock

        # Create mock config and name
        mock_config = Mock()
        mock_name = "dns-f5xc"

        auth = Authenticator(mock_config, mock_name)
        print("✅ Authenticator created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create authenticator: {e}")
        return False


def test_client_creation():
    """Test that we can create a client instance."""
    try:
        from certbot_dns_f5xc._internal.dns_f5xc import _F5XCClient

        # Test with API token authentication (doesn't require files)
        client = _F5XCClient(api_token="test-token")
        print("✅ Client created successfully with API token!")
        return True
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False


def test_zone_detection():
    """Test zone detection logic."""
    try:
        from certbot_dns_f5xc._internal.dns_f5xc import _F5XCClient

        # Create a minimal client for testing (with API token to avoid file requirements)
        client = _F5XCClient(api_token="test-token")

        # Test zone detection
        test_cases = [
            ("api.example.com", "example.com"),
            ("www.example.com", "example.com"),
            ("sub.api.example.com", "example.com"),
            ("test.domain.org", "domain.org"),
        ]

        for domain, expected_zone in test_cases:
            try:
                zone = client._find_zone_name(domain)
                if zone == expected_zone:
                    print(f"✅ Zone detection correct: {domain} → {zone}")
                else:
                    print(
                        f"❌ Zone detection wrong: {domain} → {zone} (expected {expected_zone})")
                    return False
            except Exception as e:
                print(f"❌ Zone detection failed for {domain}: {e}")
                return False

        print("✅ Zone detection tests passed!")
        return True

    except Exception as e:
        print(f"❌ Zone detection test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing F5XC Plugin")
    print("=" * 30)

    tests = [
        test_import,
        test_authenticator_creation,
        test_client_creation,
        test_zone_detection,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Plugin is ready for use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

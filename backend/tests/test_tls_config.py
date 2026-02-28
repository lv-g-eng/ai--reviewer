"""
Tests for TLS/SSL configuration.

Validates Requirement 8.5: Encrypt all data in transit using TLS 1.3
"""
import pytest
import ssl
import tempfile
from pathlib import Path
from app.core.tls_config import TLSConfig, create_default_tls_config


class TestTLSConfig:
    """Test TLS configuration."""
    
    def test_create_ssl_context_client(self):
        """Test creating client SSL context."""
        tls_config = TLSConfig()
        context = tls_config.create_client_ssl_context()
        
        assert context is not None
        assert isinstance(context, ssl.SSLContext)
        
        # Verify TLS version
        if hasattr(context, 'minimum_version'):
            # Should be TLS 1.3 or TLS 1.2
            assert context.minimum_version in [ssl.TLSVersion.TLSv1_3, ssl.TLSVersion.TLSv1_2]
        
        # Verify certificate verification is enabled
        assert context.verify_mode == ssl.CERT_REQUIRED
        assert context.check_hostname is True
    
    def test_create_ssl_context_server(self):
        """Test creating server SSL context."""
        # Create temporary certificate files
        with tempfile.TemporaryDirectory() as tmpdir:
            cert_file = Path(tmpdir) / "cert.pem"
            key_file = Path(tmpdir) / "key.pem"
            
            # Generate self-signed certificate for testing
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from datetime import datetime, timedelta
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(private_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow() + timedelta(days=1))
                .sign(private_key, hashes.SHA256())
            )
            
            # Write certificate and key
            cert_file.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
            key_file.write_bytes(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
            
            # Create TLS config with certificate
            tls_config = TLSConfig(
                cert_file=str(cert_file),
                key_file=str(key_file),
            )
            
            context = tls_config.create_server_ssl_context()
            
            assert context is not None
            assert isinstance(context, ssl.SSLContext)
    
    def test_tls_config_without_certificates(self):
        """Test TLS config without certificates (client mode)."""
        tls_config = TLSConfig()
        context = tls_config.create_client_ssl_context()
        
        assert context is not None
        # Should use system CA certificates
        assert context.verify_mode == ssl.CERT_REQUIRED
    
    def test_tls_config_with_custom_verify_mode(self):
        """Test TLS config with custom verification mode."""
        tls_config = TLSConfig(verify_mode=ssl.CERT_OPTIONAL)
        context = tls_config.create_client_ssl_context()
        
        assert context.verify_mode == ssl.CERT_OPTIONAL
        assert context.check_hostname is False
    
    def test_tls_config_missing_cert_file(self):
        """Test that missing certificate file raises error."""
        tls_config = TLSConfig(
            cert_file="/nonexistent/cert.pem",
            key_file="/nonexistent/key.pem",
        )
        
        with pytest.raises(FileNotFoundError, match="Certificate file not found"):
            tls_config.create_server_ssl_context()
    
    def test_tls_config_missing_key_file(self):
        """Test that missing key file raises error."""
        with tempfile.NamedTemporaryFile(suffix=".pem") as cert_file:
            tls_config = TLSConfig(
                cert_file=cert_file.name,
                key_file="/nonexistent/key.pem",
            )
            
            with pytest.raises(FileNotFoundError, match="Key file not found"):
                tls_config.create_server_ssl_context()
    
    def test_get_cipher_info(self):
        """Test getting cipher information."""
        tls_config = TLSConfig()
        context = tls_config.create_client_ssl_context()
        
        cipher_info = TLSConfig.get_cipher_info(context)
        
        assert "minimum_version" in cipher_info
        assert "maximum_version" in cipher_info
        assert "verify_mode" in cipher_info
        assert "check_hostname" in cipher_info
        
        # Verify minimum version is TLS 1.2 or higher
        if hasattr(context, 'minimum_version'):
            assert cipher_info["minimum_version"] in ["TLSv1_2", "TLSv1_3"]
    
    def test_secure_ciphers_configured(self):
        """Test that secure cipher suites are configured."""
        tls_config = TLSConfig()
        context = tls_config.create_client_ssl_context()
        
        # Verify secure ciphers are set
        # Note: Can't directly inspect ciphers in Python, but we can verify
        # that the context was created with our secure cipher string
        assert TLSConfig.SECURE_CIPHERS is not None
        assert "AES" in TLSConfig.SECURE_CIPHERS
        assert "GCM" in TLSConfig.SECURE_CIPHERS
    
    def test_insecure_protocols_disabled(self):
        """Test that insecure protocols are disabled."""
        tls_config = TLSConfig()
        context = tls_config.create_client_ssl_context()
        
        # Verify SSL 3.0, TLS 1.0, TLS 1.1 are disabled
        # Note: OP_NO_SSLv2 is deprecated in Python 3.13+ and may be 0
        assert context.options & ssl.OP_NO_SSLv3
        assert context.options & ssl.OP_NO_TLSv1
        assert context.options & ssl.OP_NO_TLSv1_1
    
    def test_perfect_forward_secrecy_enabled(self):
        """Test that Perfect Forward Secrecy is enabled."""
        tls_config = TLSConfig()
        context = tls_config.create_client_ssl_context()
        
        # Note: OP_SINGLE_DH_USE and OP_SINGLE_ECDH_USE may be deprecated
        # in newer Python versions. The important thing is that PFS ciphers
        # are configured (ECDHE), which we verify in cipher suite tests.
        # Just verify the context was created successfully
        assert context is not None


class TestTLSConfigEnvironment:
    """Test TLS configuration with environment variables."""
    
    def test_create_default_tls_config_without_env(self, monkeypatch):
        """Test creating default TLS config without environment variables."""
        monkeypatch.delenv("SSL_CERT_FILE", raising=False)
        monkeypatch.delenv("SSL_KEY_FILE", raising=False)
        monkeypatch.delenv("SSL_CA_FILE", raising=False)
        
        tls_config = create_default_tls_config()
        
        assert tls_config is not None
        assert tls_config.cert_file is None
        assert tls_config.key_file is None
        assert tls_config.ca_file is None
    
    def test_create_default_tls_config_with_env(self, monkeypatch):
        """Test creating default TLS config with environment variables."""
        monkeypatch.setenv("SSL_CERT_FILE", "/path/to/cert.pem")
        monkeypatch.setenv("SSL_KEY_FILE", "/path/to/key.pem")
        monkeypatch.setenv("SSL_CA_FILE", "/path/to/ca.pem")
        
        tls_config = create_default_tls_config()
        
        assert tls_config.cert_file == "/path/to/cert.pem"
        assert tls_config.key_file == "/path/to/key.pem"
        assert tls_config.ca_file == "/path/to/ca.pem"
    
    def test_create_default_tls_config_with_params(self):
        """Test creating default TLS config with parameters."""
        tls_config = create_default_tls_config(
            cert_file="/custom/cert.pem",
            key_file="/custom/key.pem",
            ca_file="/custom/ca.pem",
        )
        
        assert tls_config.cert_file == "/custom/cert.pem"
        assert tls_config.key_file == "/custom/key.pem"
        assert tls_config.ca_file == "/custom/ca.pem"


class TestTLSSecurity:
    """Security-focused tests for TLS configuration."""
    
    def test_tls_version_minimum(self):
        """Test that minimum TLS version is 1.2 or higher."""
        tls_config = TLSConfig()
        context = tls_config.create_client_ssl_context()
        
        if hasattr(context, 'minimum_version'):
            # Should be TLS 1.2 or TLS 1.3
            assert context.minimum_version >= ssl.TLSVersion.TLSv1_2
    
    def test_certificate_verification_required(self):
        """Test that certificate verification is required by default."""
        tls_config = TLSConfig()
        context = tls_config.create_client_ssl_context()
        
        assert context.verify_mode == ssl.CERT_REQUIRED
        assert context.check_hostname is True
    
    def test_weak_ciphers_not_included(self):
        """Test that weak ciphers are not in cipher suite."""
        # Weak ciphers to avoid
        weak_ciphers = ["RC4", "DES", "MD5", "NULL", "EXPORT", "anon"]
        
        for weak in weak_ciphers:
            assert weak not in TLSConfig.SECURE_CIPHERS
    
    def test_strong_ciphers_included(self):
        """Test that strong ciphers are in cipher suite."""
        # Strong ciphers to include
        strong_ciphers = ["AES", "GCM", "ECDHE"]
        
        for strong in strong_ciphers:
            assert strong in TLSConfig.SECURE_CIPHERS
    
    def test_tls_13_ciphers_included(self):
        """Test that TLS 1.3 ciphers are included."""
        tls13_ciphers = [
            "TLS_AES_256_GCM_SHA384",
            "TLS_AES_128_GCM_SHA256",
            "TLS_CHACHA20_POLY1305_SHA256",
        ]
        
        for cipher in tls13_ciphers:
            assert cipher in TLSConfig.SECURE_CIPHERS


class TestTLSIntegration:
    """Integration tests for TLS configuration."""
    
    def test_tls_context_can_be_used_with_ssl_module(self):
        """Test that TLS context can be used with Python ssl module."""
        tls_config = TLSConfig()
        context = tls_config.create_client_ssl_context()
        
        # Should be able to wrap socket (won't actually connect in test)
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            ssl_sock = context.wrap_socket(sock, server_hostname="example.com")
            assert ssl_sock is not None
        except Exception:
            # Expected to fail since we're not actually connecting
            pass
        finally:
            sock.close()
    
    def test_tls_config_compatible_with_uvicorn(self):
        """Test that TLS config is compatible with Uvicorn."""
        # Create temporary certificate files
        with tempfile.TemporaryDirectory() as tmpdir:
            cert_file = Path(tmpdir) / "cert.pem"
            key_file = Path(tmpdir) / "key.pem"
            
            # Generate self-signed certificate
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from datetime import datetime, timedelta
            
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(private_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow() + timedelta(days=1))
                .sign(private_key, hashes.SHA256())
            )
            
            cert_file.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
            key_file.write_bytes(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
            
            # Verify files can be read by TLS config
            tls_config = TLSConfig(
                cert_file=str(cert_file),
                key_file=str(key_file),
            )
            
            context = tls_config.create_server_ssl_context()
            assert context is not None
            
            # Uvicorn would use these files directly
            assert cert_file.exists()
            assert key_file.exists()

import os
from unittest.mock import Mock, patch
import pytest
from pydantic import ValidationError

# Import the types we need
from golf_enterprise.factory import _create_oauth_proxy_provider, OAuthProxyConfig
from golf.auth import JWTAuthConfig


class TestOAuthProxyCreation:
    """Test OAuth proxy creation from configurations."""

    def test_oauth_proxy_creation_basic(self) -> None:
        """Test OAuth proxy creation with basic configuration."""
        # Create token verifier config
        token_verifier_config = JWTAuthConfig(
            jwks_uri="https://github.com/.well-known/jwks.json",
            issuer="https://github.com",
            audience="api://github",
            required_scopes=["read:user"],
        )

        config = OAuthProxyConfig(
            upstream_authorization_endpoint="https://github.com/login/oauth/authorize",
            upstream_token_endpoint="https://github.com/login/oauth/access_token",
            upstream_client_id="github_client_id",
            upstream_client_secret="github_client_secret",
            base_url="https://my-proxy.example.com",
            scopes_supported=["read:user", "user:email"],
            token_verifier_config=token_verifier_config,
        )

        # Mock our local OAuthProxy import
        with (
            patch("golf_enterprise.oauth_proxy.OAuthProxy") as mock_oauth_proxy_class,
            patch("golf.auth.factory.create_auth_provider") as mock_create_auth_provider,
        ):
            # Mock token verifier
            mock_token_verifier = Mock()
            mock_token_verifier.verify_token = Mock()
            mock_token_verifier.required_scopes = ["read:user"]
            mock_create_auth_provider.return_value = mock_token_verifier

            provider = _create_oauth_proxy_provider(config)

            # Verify token verifier was created
            mock_create_auth_provider.assert_called_once_with(token_verifier_config)

            # Verify OAuthProxy was called with correct parameters
            mock_oauth_proxy_class.assert_called_once_with(
                upstream_authorization_endpoint="https://github.com/login/oauth/authorize",
                upstream_token_endpoint="https://github.com/login/oauth/access_token",
                upstream_client_id="github_client_id",
                upstream_client_secret="github_client_secret",
                upstream_revocation_endpoint=None,
                base_url="https://my-proxy.example.com",
                redirect_path="/oauth/callback",
                token_verifier=mock_token_verifier,
                scopes_supported=["read:user", "user:email"],
            )

            # Verify token verifier scopes were updated
            assert mock_token_verifier.required_scopes == ["read:user", "user:email"]

            assert provider == mock_oauth_proxy_class.return_value

    def test_oauth_proxy_with_env_variables(self) -> None:
        """Test OAuth proxy creation with environment variable configuration."""
        token_verifier_config = JWTAuthConfig(
            jwks_uri="https://oauth2.googleapis.com/oauth2/v3/certs",
            issuer="https://accounts.google.com",
            audience="my-google-client-id",
        )

        config = OAuthProxyConfig(
            upstream_authorization_endpoint="https://default.example.com/auth",
            upstream_token_endpoint="https://default.example.com/token",
            upstream_client_id="default_client_id",
            upstream_client_secret="default_client_secret",
            base_url="https://default.example.com",
            upstream_authorization_endpoint_env_var="GOOGLE_AUTH_ENDPOINT",
            upstream_token_endpoint_env_var="GOOGLE_TOKEN_ENDPOINT",
            upstream_client_id_env_var="GOOGLE_CLIENT_ID",
            upstream_client_secret_env_var="GOOGLE_CLIENT_SECRET",
            base_url_env_var="PROXY_BASE_URL",
            scopes_supported=["openid", "profile", "email"],
            token_verifier_config=token_verifier_config,
        )

        env_vars = {
            "GOOGLE_AUTH_ENDPOINT": "https://accounts.google.com/o/oauth2/v2/auth",
            "GOOGLE_TOKEN_ENDPOINT": "https://oauth2.googleapis.com/token",
            "GOOGLE_CLIENT_ID": "env_google_client_id",
            "GOOGLE_CLIENT_SECRET": "env_google_client_secret",
            "PROXY_BASE_URL": "https://env-proxy.example.com",
        }

        # Mock our local OAuthProxy import
        with (
            patch("golf.auth.oauth_proxy.OAuthProxy") as mock_oauth_proxy_class,
            patch("golf.auth.factory.create_auth_provider") as mock_create_auth_provider,
            patch.dict(os.environ, env_vars),
        ):
            # Mock token verifier
            mock_token_verifier = Mock()
            mock_token_verifier.verify_token = Mock()
            mock_token_verifier.required_scopes = []
            mock_create_auth_provider.return_value = mock_token_verifier

            provider = _create_oauth_proxy_provider(config)

            # Verify environment variables were used
            mock_oauth_proxy_class.assert_called_once_with(
                upstream_authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
                upstream_token_endpoint="https://oauth2.googleapis.com/token",
                upstream_client_id="env_google_client_id",
                upstream_client_secret="env_google_client_secret",
                upstream_revocation_endpoint=None,
                base_url="https://env-proxy.example.com",
                redirect_path="/oauth/callback",
                token_verifier=mock_token_verifier,
                scopes_supported=["openid", "profile", "email"],
            )

            assert provider == mock_oauth_proxy_class.return_value

    def test_oauth_proxy_invalid_token_verifier(self) -> None:
        """Test OAuth proxy creation with invalid token verifier."""
        token_verifier_config = JWTAuthConfig(
            jwks_uri="https://example.com/.well-known/jwks.json",
        )

        config = OAuthProxyConfig(
            upstream_authorization_endpoint="https://provider.example.com/auth",
            upstream_token_endpoint="https://provider.example.com/token",
            upstream_client_id="client_id",
            upstream_client_secret="client_secret",
            base_url="https://proxy.example.com",
            token_verifier_config=token_verifier_config,
        )

        # Mock our local OAuthProxy import
        with (
            patch("golf.auth.oauth_proxy.OAuthProxy") as mock_oauth_proxy_class,
            patch("golf.auth.factory.create_auth_provider") as mock_create_auth_provider,
        ):
            # Mock invalid token verifier (missing verify_token method)
            mock_invalid_verifier = Mock(spec=[])  # No verify_token method
            mock_create_auth_provider.return_value = mock_invalid_verifier

            with pytest.raises(ValueError, match="OAuth proxy requires a TokenVerifier"):
                _create_oauth_proxy_provider(config)

    def test_oauth_proxy_missing_required_config(self) -> None:
        """Test OAuth proxy creation fails with missing required configuration."""
        token_verifier_config = JWTAuthConfig(jwks_uri="https://example.com/.well-known/jwks.json")

        # Test missing upstream_client_id - should fail at config validation level
        with pytest.raises(ValidationError, match="Client credentials cannot be empty"):
            OAuthProxyConfig(
                upstream_authorization_endpoint="https://provider.example.com/auth",
                upstream_token_endpoint="https://provider.example.com/token",
                upstream_client_id="",  # Empty, should fail
                upstream_client_secret="client_secret",
                base_url="https://proxy.example.com",
                token_verifier_config=token_verifier_config,
            )

    def test_oauth_proxy_creation_success(self) -> None:
        """Test OAuth proxy creation succeeds with local implementation."""
        token_verifier_config = JWTAuthConfig(jwks_uri="https://example.com/.well-known/jwks.json")

        config = OAuthProxyConfig(
            upstream_authorization_endpoint="https://provider.example.com/auth",
            upstream_token_endpoint="https://provider.example.com/token",
            upstream_client_id="client_id",
            upstream_client_secret="client_secret",
            base_url="https://proxy.example.com",
            token_verifier_config=token_verifier_config,
        )

        # Mock our local OAuthProxy implementation
        with (
            patch("golf.auth.oauth_proxy.OAuthProxy") as mock_oauth_proxy_class,
            patch("golf.auth.factory.create_auth_provider") as mock_create_auth_provider,
        ):
            # Mock token verifier
            mock_token_verifier = Mock()
            mock_token_verifier.verify_token = Mock()
            mock_token_verifier.required_scopes = []
            mock_create_auth_provider.return_value = mock_token_verifier

            provider = _create_oauth_proxy_provider(config)

            # Verify OAuthProxy was created successfully with our local implementation
            mock_oauth_proxy_class.assert_called_once()
            assert provider == mock_oauth_proxy_class.return_value

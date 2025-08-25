"""Factory functions for creating OAuth proxy providers."""

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp.server.auth.auth import AuthProvider

from .oauth_proxy import OAuthProxy


def create_oauth_proxy_provider(config) -> "AuthProvider":
    """Create OAuth proxy provider from Golf configuration.
    
    Args:
        config: OAuthProxyConfig instance from Golf
        
    Returns:
        Configured OAuthProxy instance
        
    Raises:
        ValueError: If configuration is invalid
        ImportError: If required dependencies are missing
    """
    # Import OAuthProxyConfig from Golf
    try:
        from golf.auth.providers import OAuthProxyConfig
        from golf.auth.factory import create_auth_provider
    except ImportError as e:
        raise ImportError("Golf MCP framework is required") from e
    
    if not isinstance(config, OAuthProxyConfig):
        raise ValueError(f"Expected OAuthProxyConfig, got {type(config).__name__}")
    
    # Resolve runtime values from environment variables
    upstream_authorization_endpoint = config.upstream_authorization_endpoint
    if config.upstream_authorization_endpoint_env_var:
        env_value = os.environ.get(config.upstream_authorization_endpoint_env_var)
        if env_value:
            upstream_authorization_endpoint = env_value.strip()

    upstream_token_endpoint = config.upstream_token_endpoint
    if config.upstream_token_endpoint_env_var:
        env_value = os.environ.get(config.upstream_token_endpoint_env_var)
        if env_value:
            upstream_token_endpoint = env_value.strip()

    upstream_client_id = config.upstream_client_id
    if config.upstream_client_id_env_var:
        env_value = os.environ.get(config.upstream_client_id_env_var)
        if env_value:
            upstream_client_id = env_value.strip()

    upstream_client_secret = config.upstream_client_secret
    if config.upstream_client_secret_env_var:
        env_value = os.environ.get(config.upstream_client_secret_env_var)
        if env_value:
            upstream_client_secret = env_value.strip()

    upstream_revocation_endpoint = config.upstream_revocation_endpoint
    if config.upstream_revocation_endpoint_env_var:
        env_value = os.environ.get(config.upstream_revocation_endpoint_env_var)
        if env_value:
            upstream_revocation_endpoint = env_value.strip()

    base_url = config.base_url
    if config.base_url_env_var:
        env_value = os.environ.get(config.base_url_env_var)
        if env_value:
            base_url = env_value.strip()

    # Validate resolved configuration
    if not upstream_authorization_endpoint:
        raise ValueError("upstream_authorization_endpoint is required")
    if not upstream_token_endpoint:
        raise ValueError("upstream_token_endpoint is required")
    if not upstream_client_id:
        raise ValueError("upstream_client_id is required")
    if not upstream_client_secret:
        raise ValueError("upstream_client_secret is required")
    if not base_url:
        raise ValueError("base_url is required")

    # Create the underlying token verifier using Golf's factory
    token_verifier = create_auth_provider(config.token_verifier_config)

    # Ensure it's actually a TokenVerifier
    if not hasattr(token_verifier, "verify_token"):
        raise ValueError(f"OAuth proxy requires a TokenVerifier, got {type(token_verifier).__name__}")

    # Update token verifier's required_scopes to match our scopes_supported for consistency
    # This ensures that token validation uses the same scopes as advertised
    if config.scopes_supported and hasattr(token_verifier, "required_scopes"):
        token_verifier.required_scopes = list(config.scopes_supported)

    return OAuthProxy(
        upstream_authorization_endpoint=upstream_authorization_endpoint,
        upstream_token_endpoint=upstream_token_endpoint,
        upstream_client_id=upstream_client_id,
        upstream_client_secret=upstream_client_secret,
        upstream_revocation_endpoint=upstream_revocation_endpoint,
        base_url=base_url,
        redirect_path=config.redirect_path,
        token_verifier=token_verifier,
        scopes_supported=config.scopes_supported,
    )
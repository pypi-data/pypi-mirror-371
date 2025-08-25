"""Golf MCP Enterprise - OAuth Proxy for Non-DCR Providers

This package provides OAuth proxy functionality for Golf MCP servers,
enabling integration with OAuth providers that don't support Dynamic
Client Registration (DCR) like GitHub, Google, Okta Web Applications.

The proxy acts as a DCR-capable authorization server to MCP clients
while using fixed upstream client credentials.
"""

__version__ = "0.1.0"

from .oauth_proxy import OAuthProxy
from .factory import create_oauth_proxy_provider

# Integration with Golf's plugin system
def register_golf_enterprise_providers():
    """Register enterprise providers with Golf's auth system."""
    try:
        from golf.auth.registry import get_provider_registry
        registry = get_provider_registry()
        registry.register_factory("oauth_proxy", create_oauth_proxy_provider)
    except ImportError:
        # Golf not available, skip registration
        pass

# Auto-register when imported
register_golf_enterprise_providers()

__all__ = [
    "OAuthProxy",
    "create_oauth_proxy_provider", 
    "register_golf_enterprise_providers",
]
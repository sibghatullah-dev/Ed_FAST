"""
PeerHub module initialization.
Provides unified interface for both JSON and database backends.
"""

from config.app_config import USE_DATABASE

if USE_DATABASE:
    # Use database-backed service
    from peerhub.db_service import PeerHubDBService as PeerHubService
else:
    # Use legacy JSON-backed service
    from peerhub.service import PeerHubService

__all__ = ['PeerHubService']

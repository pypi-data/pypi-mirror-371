# File: packages/cli/udicti_cli/commands/__init__.py

"""
This __init__.py file makes the 'commands' directory a Python package
and serves to expose individual command modules so they can be imported
by the main application.
"""


from .onboarding import onboarding_app
from .show import show_app
from .github_auth import github_auth_app
from .dashboard import dashboard_app
from .welcome import app

__all__ = [
    "onboarding_app",
    "show_app",
    "github_auth_app",
    "dashboard_app",
    "app",
]

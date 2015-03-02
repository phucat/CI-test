"""
Central place to store event listeners for your application,
automatically imported at run time.
"""
import logging
from ferris.core.events import on
from app.etc.auth import require_domain


# example
@on('controller_before_authorization')
def inject_authorization_chains(controller, authorizations):
    authorizations.insert(0, require_domain)

# Step 4: serve Django on 127.0.0.1:$PORT (default 8765) with Keycloak validation mocked.
# The seeded staff user is logged in whenever the request carries an `access_token` cookie (any value).
# Nothing in the repo is modified. Not auto-reloading: restart after changing Python code.
import os
import sys

sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
os.environ.setdefault("DATABASE_NAME", "crm_preview")

import django

django.setup()

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model, login
from django.core.management import call_command

staff = get_user_model().objects.get(email="preview-staff@nalo.fr")


def fake_validate(request, access_token, client_type="admin"):
    # Two authentication backends are configured, so `backend` is mandatory.
    login(request, staff, backend="django.contrib.auth.backends.ModelBackend")
    return True


with (
    patch("security.keycloak.decorators.validate_access_token", side_effect=fake_validate),
    patch("security.keycloak.mixins.validate_access_token", side_effect=fake_validate),
    patch("security.keycloak.clients.get_keycloak_openid", return_value=MagicMock()),
):
    call_command("runserver", f"127.0.0.1:{os.environ.get('PORT', '8765')}", noreload=True)

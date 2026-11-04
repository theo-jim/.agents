# Step 2: base data for the CRM preview (one client with a contract, one staff account).
# Run ONCE and alone: two parallel runs collide on james.bond+test1@nalo.fr.
import os
import sys

sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
os.environ.setdefault("DATABASE_NAME", "crm_preview")

import django

django.setup()

from evest.models.profile import Profile
from evest.tests.libs.mockup_nalo import create_complete_user, initialize_global_project_values

user, profile, contract, project = create_complete_user()
staff, _ = Profile.objects.create_user(email="preview-staff@nalo.fr", password="1234", is_staff=True)
initialize_global_project_values(profile)
print("PROFILE_ID", profile.pk, "CONTRACT_ID", contract.pk, "STAFF", staff.pk, flush=True)

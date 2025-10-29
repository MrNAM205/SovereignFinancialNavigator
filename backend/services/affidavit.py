import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from typing import List

from models import RemedyEvent, Creditor, UserProfile, DispatchEvent, Notice

# Build a robust path to the templates directory
# This assumes this service file is in backend/services/
# and the templates are in shared/constants/templates/
# relative to the project root.
TEMPLATE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "shared", "constants", "templates")
)

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def generate_affidavit(user: UserProfile, creditor: Creditor, events: List[RemedyEvent]) -> str:
    """Renders the affidavit using a Jinja2 template."""
    template = env.get_template("affidavit_template.j2")
    context = {
        "user_name": user.full_name,
        "user_address": user.address,
        "creditor_name": creditor.name,
        "creditor_address": creditor.address,
        "events": events,
        "date": datetime.utcnow().strftime("%B %d, %Y"),
    }
    return template.render(context)

def generate_affidavit_of_mailing(user: UserProfile, creditor: Creditor, dispatch: DispatchEvent, notice: Notice) -> str:
    """Renders the affidavit of mailing using a Jinja2 template."""
    template = env.get_template("affidavit_of_mailing.j2")
    context = {
        "user_name": user.full_name,
        "user_address": user.address,
        "dispatch_date": dispatch.sent_at.strftime("%B %d, %Y"),
        "document_title": f"Notice of {notice.template_name.replace('.j2', '').replace('_', ' ').title()}",
        "dispatch_method": dispatch.dispatch_method,
        "creditor_name": creditor.name,
        "creditor_address": creditor.address,
        "today": datetime.utcnow().strftime("%B %d, %Y"),
    }
    return template.render(context)

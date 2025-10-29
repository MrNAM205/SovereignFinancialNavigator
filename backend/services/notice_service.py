import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

from models import UserProfile, Creditor

# Build a robust path to the notices directory
TEMPLATE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "shared", "constants", "notices")
)

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def generate_notice(template_name: str, user: UserProfile, creditor: Creditor) -> str:
    """Renders a notice using a Jinja2 template."""
    try:
        template = env.get_template(template_name)
    except Exception as e:
        # In a real app, you'd have more robust error logging
        raise FileNotFoundError(f"Notice template '{template_name}' not found.") from e

    context = {
        "user": user,
        "creditor": creditor,
        "date": datetime.utcnow().strftime("%B %d, %Y"),
    }
    return template.render(context)

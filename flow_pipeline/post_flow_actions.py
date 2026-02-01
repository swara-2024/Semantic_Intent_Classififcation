import yaml
from services.email_service import send_email


# 🔧 fix filename mismatch here
with open("config/department_routes.yml") as f:
    ROUTES = yaml.safe_load(f)


def handle_post_flow(intent: str, slots: dict):

    route = ROUTES.get(intent)

    if not route:
        print("⚠️ No route configured for intent:", intent)
        return False

    to_email = route.get("email")
    subject = route.get("subject", f"New request: {intent}")

    body_lines = [
        f"New request received",
        f"Intent: {intent}",
        "",
        "Collected details:"
    ]

    for k, v in slots.items():
        body_lines.append(f"- {k}: {v}")

    body = "\n".join(body_lines)

    return send_email(to_email, subject, body)

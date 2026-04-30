import requests
import json
import time
import logging
from typing import Dict, Any, List

# ==========================
# CONFIG
# ==========================
API_TOKEN = "YOUR_API_TOKEN"
ZONE_ID = "YOUR_ZONE_ID"

OUTPUT_TF = "cloudflare_page_rules.tf"
OUTPUT_JSON = "cloudflare_page_rules.json"

BASE_URL = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/pagerules"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# ==========================
# LOGGING
# ==========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ==========================
# FETCH PAGE RULES
# ==========================
def fetch_page_rules() -> List[Dict[str, Any]]:
    page = 1
    per_page = 50
    all_rules = []

    while True:
        url = f"{BASE_URL}?page={page}&per_page={per_page}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            raise Exception(f"API error {response.status_code}: {response.text}")

        data = response.json()

        if not data.get("success"):
            raise Exception(f"Cloudflare API error: {data}")

        rules = data.get("result", [])
        all_rules.extend(rules)

        total_pages = data.get("result_info", {}).get("total_pages", 1)
        if page >= total_pages:
            break

        page += 1
        time.sleep(0.2)

    logging.info(f"Fetched {len(all_rules)} page rules")
    return all_rules


# ==========================
# HELPERS
# ==========================
def sanitize_name(name: str) -> str:
    return (
        name.replace("*", "wildcard")
        .replace(".", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


def format_value(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return f'"{value}"'


# ==========================
# ACTION HANDLERS
# ==========================
def handle_forwarding_url(value):
    return [
        "    forwarding_url {",
        f'      url         = "{value["url"]}"',
        f'      status_code = {value["status_code"]}',
        "    }"
    ]


def handle_generic(action_id, value):
    return [f"    {action_id} = {format_value(value)}"]


def handle_security_level(value):
    return [f'    security_level = "{value}"']


def handle_cache_level(value):
    return [f'    cache_level = "{value}"']


def handle_ssl(value):
    return [f'    ssl = "{value}"']


def handle_always_use_https(value):
    return [f"    always_use_https = {format_value(value)}"]


# Registry of supported handlers
ACTION_HANDLERS = {
    "forwarding_url": handle_forwarding_url,
    "security_level": handle_security_level,
    "cache_level": handle_cache_level,
    "ssl": handle_ssl,
    "always_use_https": handle_always_use_https,
}


# ==========================
# ACTION MAPPER
# ==========================
def map_actions(actions: List[Dict[str, Any]]) -> List[str]:
    tf_lines = []

    for action in actions:
        action_id = action.get("id")
        value = action.get("value")

        if not action_id:
            continue

        handler = ACTION_HANDLERS.get(action_id)

        try:
            if handler:
                tf_lines.extend(handler(value))
            else:
                logging.warning(f"Unsupported action: {action_id}, using fallback")
                tf_lines.extend(handle_generic(action_id, value))
        except Exception as e:
            logging.error(f"Failed to process action {action_id}: {e}")

    return tf_lines


# ==========================
# TERRAFORM GENERATION
# ==========================
def generate_terraform(rules: List[Dict[str, Any]]) -> str:
    tf_blocks = []

    for i, rule in enumerate(rules, start=1):
        try:
            target = rule["targets"][0]["constraint"]["value"]
        except Exception:
            logging.warning(f"Skipping malformed rule #{i}")
            continue

        priority = rule.get("priority", 1)
        status = rule.get("status", "active")

        resource_name = f"rule_{i}_{sanitize_name(target)}"

        block = []
        block.append(f'resource "cloudflare_page_rule" "{resource_name}" {{')
        block.append(f'  zone_id  = "{ZONE_ID}"')
        block.append(f'  target   = "{target}"')
        block.append(f'  priority = {priority}')
        block.append(f'  status   = "{status}"\n')

        block.append("  actions {")

        action_lines = map_actions(rule.get("actions", []))
        if action_lines:
            block.extend(action_lines)
        else:
            block.append("    # No valid/supported actions")

        block.append("  }")
        block.append("}\n")

        tf_blocks.append("\n".join(block))

    return "\n".join(tf_blocks)


# ==========================
# SAVE FILES
# ==========================
def save_json(rules):
    with open(OUTPUT_JSON, "w") as f:
        json.dump(rules, f, indent=2)
    logging.info(f"Saved raw JSON → {OUTPUT_JSON}")


def save_tf(tf_content):
    with open(OUTPUT_TF, "w") as f:
        f.write(tf_content)
    logging.info(f"Saved Terraform → {OUTPUT_TF}")


# ==========================
# MAIN
# ==========================
def main():
    logging.info("Starting Cloudflare export...")

    rules = fetch_page_rules()

    save_json(rules)

    logging.info("Converting to Terraform...")
    tf_content = generate_terraform(rules)

    save_tf(tf_content)

    logging.info("Done ✔")


if __name__ == "__main__":
    main()
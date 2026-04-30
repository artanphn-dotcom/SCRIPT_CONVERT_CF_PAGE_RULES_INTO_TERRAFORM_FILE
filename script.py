import requests
import json
import time

# ==========================
# CONFIG
# ==========================
API_TOKEN = "Cloudflare API token with read permissions for page rules and zones"
ZONE_ID = "domain zone id from cloudflare dashboard"
OUTPUT_TF = "cloudflare_page_rules.tf"

BASE_URL = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/pagerules"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}


# ==========================
# FETCH PAGE RULES
# ==========================
def fetch_page_rules():
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

        result = data.get("result", [])
        all_rules.extend(result)

        total_pages = data.get("result_info", {}).get("total_pages", 1)
        if page >= total_pages:
            break

        page += 1
        time.sleep(0.2)  # avoid rate limits

    print(f"[INFO] Fetched {len(all_rules)} page rules")
    return all_rules


# ==========================
# HELPERS
# ==========================
def sanitize_name(name):
    return (
        name.replace("*", "wildcard")
        .replace(".", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


def map_actions(actions):
    tf_lines = []

    for action in actions:
        action_id = action["id"]
        value = action.get("value")

        # Special handling
        if action_id == "forwarding_url":
            tf_lines.append("    forwarding_url {")
            tf_lines.append(f'      url         = "{value["url"]}"')
            tf_lines.append(f'      status_code = {value["status_code"]}')
            tf_lines.append("    }")

        elif action_id == "cache_ttl_by_status":
            # Example of complex structure
            continue  # skip or implement later

        else:
            if isinstance(value, bool):
                tf_lines.append(f'    {action_id} = {str(value).lower()}')
            elif isinstance(value, (int, float)):
                tf_lines.append(f'    {action_id} = {value}')
            elif value is None:
                continue
            else:
                tf_lines.append(f'    {action_id} = "{value}"')

    return tf_lines


# ==========================
# GENERATE TERRAFORM
# ==========================
def generate_terraform(rules):
    tf_blocks = []

    for i, rule in enumerate(rules, start=1):
        try:
            target = rule["targets"][0]["constraint"]["value"]
        except Exception:
            print(f"[WARN] Skipping malformed rule #{i}")
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
        if not action_lines:
            block.append("    # No supported actions found")
        else:
            block.extend(action_lines)

        block.append("  }")
        block.append("}\n")

        tf_blocks.append("\n".join(block))

    return "\n".join(tf_blocks)


# ==========================
# MAIN
# ==========================
def main():
    print("[INFO] Starting export from Cloudflare...")

    rules = fetch_page_rules()

    print("[INFO] Converting to Terraform format...")
    tf_content = generate_terraform(rules)

    with open(OUTPUT_TF, "w") as f:
        f.write(tf_content)

    print(f"[SUCCESS] Terraform file generated: {OUTPUT_TF}")


if __name__ == "__main__":
    main()

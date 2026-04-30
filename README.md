# Cloudflare Page Rules to Terraform Exporter

This project provides a Python script (`script1.py`) to export all Cloudflare Page Rules for a given zone and automatically generate both a Terraform configuration file (`cloudflare_page_rules.tf`) and a raw JSON export (`cloudflare_page_rules.json`). This enables you to migrate, back up, or version-control your Cloudflare Page Rules using Infrastructure as Code (IaC).

## Features

- Fetches all Page Rules from a Cloudflare zone using the Cloudflare API
- Converts Page Rules into Terraform resources (`cloudflare_page_rule`)
- Handles forwarding URLs and several other actions (security level, cache level, SSL, always use HTTPS, and more)
- Outputs both a ready-to-use `cloudflare_page_rules.tf` and a raw JSON export for auditing
- Includes logging for progress and warnings

## Files

- `script1.py` — Main Python script to fetch and export Cloudflare Page Rules
- `cloudflare_page_rules.tf` — Generated Terraform file containing all exported rules
- `cloudflare_page_rules.json` — Raw JSON export of all fetched Page Rules

## Prerequisites

- Python 3.7+
- `requests` library (`pip install requests`)
- A Cloudflare API Token with **read permissions** for Page Rules and Zones

## Usage

1. **Configure the Script**
	 - Open `script1.py` and set the following variables at the top:
		 - `API_TOKEN`: Your Cloudflare API token
		 - `ZONE_ID`: The Zone ID of your domain (find in Cloudflare dashboard)

2. **Install Dependencies**
	 ```bash
	 pip install requests
	 ```

3. **Run the Export Script**
	 ```bash
	 python script1.py
	 ```
	 This will generate or overwrite `cloudflare_page_rules.tf` and `cloudflare_page_rules.json` in the current directory.

4. **Review and Use the Terraform File**
	 - The generated `cloudflare_page_rules.tf` contains all your Page Rules as Terraform resources.
	 - Integrate this file into your Terraform workflow as needed.
	 - The JSON file can be used for auditing or further processing.

## Example Output

```hcl
resource "cloudflare_page_rule" "rule_1_example_com" {
	zone_id  = "YOUR_ZONE_ID"
	target   = "example.com/path"
	priority = 1
	status   = "active"
	actions {
		forwarding_url {
			url         = "https://destination.com/"
			status_code = 301
		}
		always_use_https = true
		security_level = "high"
	}
}
```

## Notes

- The script supports several common Page Rule actions. Unsupported actions are included as generic assignments with a warning in the logs.
- The script avoids Cloudflare API rate limits with a short delay between requests.
- Always review the generated Terraform file before applying changes to production.

---
**Author:** Artan Vitija

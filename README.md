# Cloudflare Page Rules to Terraform Exporter

This project provides a Python script to export all Cloudflare Page Rules for a given zone and automatically generate a Terraform configuration file (`cloudflare_page_rules.tf`). This enables you to migrate, back up, or version-control your Cloudflare Page Rules using Infrastructure as Code (IaC).

## Features

- Fetches all Page Rules from a Cloudflare zone using the Cloudflare API
- Converts Page Rules into Terraform resources (`cloudflare_page_rule`)
- Handles forwarding URLs and other supported actions
- Outputs a ready-to-use `cloudflare_page_rules.tf` file

## Files

- `script.py` — Main Python script to fetch and export Cloudflare Page Rules
- `cloudflare_page_rules.tf` — Generated Terraform file containing all exported rules

## Prerequisites

- Python 3.7+
- `requests` library (`pip install requests`)
- A Cloudflare API Token with **read permissions** for Page Rules and Zones

## Usage

1. **Configure the Script**
	 - Open `script.py` and set the following variables at the top:
		 - `API_TOKEN`: Your Cloudflare API token
		 - `ZONE_ID`: The Zone ID of your domain (find in Cloudflare dashboard)

2. **Install Dependencies**
	 ```bash
	 pip install requests
	 ```

3. **Run the Export Script**
	 ```bash
	 python script.py
	 ```
	 This will generate or overwrite `cloudflare_page_rules.tf` in the current directory.

4. **Review and Use the Terraform File**
	 - The generated `cloudflare_page_rules.tf` contains all your Page Rules as Terraform resources.
	 - Integrate this file into your Terraform workflow as needed.

## Example Output

```hcl
resource "cloudflare_page_rule" "rule_1_abcdef.de_expense" {
	zone_id  = "xxxxxxxxx6e9c3737fc5a92cc5919"
	target   = "abcdef.de/expense"
	priority = 3
	status   = "active"
	actions {
		forwarding_url {
			url         = "https://expense-lumina.preview.emergentagent.com/"
			status_code = 301
		}
	}
}
```

## Notes

- Only supported actions (e.g., `forwarding_url`) are exported. Extend `script.py` to handle more actions as needed.
- The script avoids Cloudflare API rate limits with a short delay between requests.
- Always review the generated Terraform file before applying changes to production.

---
**Author:** Artan Vitija

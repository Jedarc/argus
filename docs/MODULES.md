# Argus — Modules

Each module accepts one or more target types and returns a normalized `ModuleResult`.
Modules marked with 🔑 require an API key to operate.

---

## hudsonrock

**Target:** `username`, `email`
**Source:** cavalier.hudsonrock.com (free public API)
**Cache TTL:** 7 days

Searches the target against HudsonRock's database of machines compromised by infostealers
(Lumma, RedLine, Raccoon, Vidar, etc.).

Returns per infection:
- Date of compromise
- Stealer family
- Computer name
- IP address (masked in the free tier)
- Total number of compromised services
- Top exposed logins (masked in the free tier)

---

## sherlock

**Target:** `username`
**Source:** subprocess — `sherlock <username> --print-found --no-color`
**Cache TTL:** 1 day
**Dependency:** `pip install sherlock-project`

Searches the username across 400+ platforms.

Returns:
- List of profile URLs found
- Total hit count

---

## whatsmyname

**Target:** `username`
**Source:** local JSON database from WebBreacher/WhatsMyName (cloned during setup)
**Cache TTL:** 1 day

Alternative and complement to Sherlock. Uses the same data backing whatsmyname.app.

Returns:
- Profile URLs grouped by category (social, gaming, coding, etc.)
- Hit count per category

---

## holehe

**Target:** `email`
**Source:** subprocess — `holehe <email> --only-used --no-color`
**Cache TTL:** 1 day
**Dependency:** `pip install holehe`

Checks which services have an account registered under the email address,
without triggering verification emails.

Returns:
- Services where the email exists
- Services where it does not

---

## ipinfo

**Target:** `ip`
**Source:** ipinfo.io (free tier — 50k requests/month, no key required)
**Cache TTL:** 30 days

Geolocation and metadata for an IP address.

Returns:
- Country, region, city
- ASN and carrier name
- Coordinates
- Reverse hostname

---

## whois

**Target:** `domain`
**Source:** python-whois (local library)
**Cache TTL:** 3 days
**Dependency:** `pip install python-whois`

Queries domain registration data.

Returns:
- Registrant (when not private)
- Creation and expiration dates
- Nameservers
- Registrar

---

## subfinder

**Target:** `domain`
**Source:** subprocess — `subfinder -d <domain> -silent`
**Cache TTL:** 3 days
**Dependency:** `subfinder` binary from projectdiscovery/subfinder

Passive subdomain enumeration via multiple public sources (crt.sh, VirusTotal free, Shodan free, etc.).

Returns:
- List of discovered subdomains
- Total count

---

## hibp 🔑

**Target:** `email`
**Key:** `HIBP_API_KEY`
**Source:** haveibeenpwned.com/api/v3
**Cache TTL:** 7 days

Checks whether the email appeared in any known data breach.

Returns:
- List of breaches (name, breach date, exposed data types)
- Total breach count

---

## shodan 🔑

**Target:** `ip`, `domain`
**Key:** `SHODAN_API_KEY`
**Source:** api.shodan.io
**Cache TTL:** 7 days

Internet-exposed service data for the target.

Returns:
- Open ports and service banners
- Associated CVEs
- Hostnames
- Last scan date

---

## hunter_io 🔑

**Target:** `domain`
**Key:** `HUNTER_API_KEY`
**Source:** api.hunter.io/v2
**Cache TTL:** 7 days

Discovers email addresses associated with a corporate domain.

Returns:
- List of found emails
- Domain email format pattern (e.g. `{first}.{last}@company.com`)
- Sources where each email was found

---

## virustotal 🔑

**Target:** `ip`, `domain`
**Key:** `VT_API_KEY`
**Source:** virustotal.com/api/v3
**Cache TTL:** 3 days

Threat intelligence and reputation analysis.

Returns:
- Detection score (malicious engines / total)
- Assigned categories
- Latest analysis results
- Related samples (for file hashes)

---

## Adding a New Module

1. Create `src/api/modules/<module_name>.py` extending `BaseModule`
2. Implement `run(target_value: str, api_key: str | None) -> ModuleResult`
3. Declare `name`, `accepted_target_types`, and `requires_api_key`
4. Register it in `src/api/modules/__init__.py`

The system auto-discovers all registered modules and exposes them in the settings panel
without any additional wiring.

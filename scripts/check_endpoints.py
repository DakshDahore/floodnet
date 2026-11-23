#!/usr/bin/env python3
"""
scripts/check_endpoints.py
Verifies consistency of worker backend endpoint URLs across frontend config.js and README.md.
Prints 'all consistent' when endpoints match.
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def extract_config_urls():
    config_file = PROJECT_ROOT / "floodlock_frontend" / "js" / "config.js"
    content = config_file.read_text(encoding="utf-8")
    match = re.search(r"const\s+WORKER_ENDPOINTS\s*=\s*\[(.*?)\];", content, re.DOTALL)
    if not match:
        raise ValueError("Could not find WORKER_ENDPOINTS array in config.js")
    array_body = match.group(1)
    urls = [url.strip().strip('"').strip("'") for url in re.findall(r'["\'](https://[^"\']+)["\']', array_body)]
    return urls

def extract_readme_urls():
    readme_file = PROJECT_ROOT / "README.md"
    content = readme_file.read_text(encoding="utf-8")
    urls = re.findall(r"https://floodlock-backend[a-z0-9\.\-]*\.workers\.dev", content)
    # Deduplicate preserving order
    seen = set()
    dedup = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            dedup.append(u)
    return dedup

def main():
    config_urls = extract_config_urls()
    readme_urls = extract_readme_urls()

    if not config_urls:
        print("[FAIL] No URLs found in config.js WORKER_ENDPOINTS")
        sys.exit(1)

    if not readme_urls:
        print("[FAIL] No URLs found in README.md")
        sys.exit(1)

    differ = False
    if len(config_urls) != len(readme_urls):
        print(f"[FAIL] Count mismatch: config.js has {len(config_urls)}, README.md has {len(readme_urls)}")
        differ = True
    else:
        for idx, (cu, ru) in enumerate(zip(config_urls, readme_urls)):
            if cu != ru:
                print(f"[FAIL] Slot {idx + 1} mismatch: config='{cu}' vs readme='{ru}'")
                differ = True

    if differ:
        sys.exit(1)

    print("all consistent")

if __name__ == "__main__":
    main()

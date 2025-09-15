#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random
import time

def collect_links(seed_url, target_count=500, timeout=5, output_file="collected_uris.txt"):
    visited = set()
    to_visit = [seed_url]

    while len(visited) < target_count and to_visit:
        url = to_visit.pop(0)

        try:
            response = requests.get(url, timeout=timeout, headers={"User-Agent": "CS432/532"}, allow_redirects=True)
        except requests.RequestException as e:
            print(f"Failed: {url} ({e})")
            continue

        final_url = response.url  # after redirects
        if final_url in visited:
            continue

        ctype = response.headers.get("Content-Type", "")
        clen = response.headers.get("Content-Length")

        # Check if it's HTML and large enough
        if "text/html" in ctype:
            length_ok = False
            if clen is not None:
                length_ok = int(clen) > 1000
            else:
                length_ok = len(response.content) > 1000

            if length_ok:
                print(final_url)
                visited.add(final_url)

                # Extract new links
                soup = BeautifulSoup(response.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    new_url = urljoin(final_url, link["href"])
                    if new_url not in visited:
                        to_visit.append(new_url)

        # Pick a random already-collected URI if we run out of frontier
        if not to_visit and len(visited) < target_count:
            new_seed = random.choice(list(visited))
            print(f"Need to collect {target_count - len(visited)} more URIs...")
            print(f" random seed: {new_seed}")
            to_visit.append(new_seed)
            time.sleep(1)

    # Save results
    with open(output_file, "w") as f:
        for u in visited:
            f.write(u + "\n")

    print(f"\nCollected {len(visited)} unique URIs")
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 collect-webpages.py <seed_url> [target_count]")
        sys.exit(1)

    seed = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 500

    collect_links(seed, target_count=count)

#!/usr/bin/env python3.12
"""test_scrape_poc.py — Fase 5.1 POC (TDD: roept social_api aan, FAALT zonder key).

Volgt de GSD-plan-phase werkwijze: eerst failing test, dan implementatie.
Bewijst dat de data-shape (caption + posted_at + metrics) dekt wat de user vraagt.
"""
import os, sys, json
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import social_api

def main():
    key = os.environ.get("SCRAPECREATORS_API_KEY")
    if not key:
        print("FAIL: SCRAPECREATORS_API_KEY niet gezet (verwacht in POC-fase zonder key)")
        return 1
    # Roep LinkedIn + IG aan voor reeload
    for platform in ("linkedin", "instagram"):
        posts = social_api.fetch("reeload", platform)
        if not posts:
            print(f"FAIL: geen posts voor reeload/{platform}")
            return 1
        p = posts[0]
        for field in ("caption", "posted_at", "metrics"):
            if field not in p:
                print(f"FAIL: post mist veld '{field}' op {platform}")
                return 1
        print(f"OK: reeload/{platform} -> {len(posts)} post(s), eerste heeft caption+posted_at+metrics")
    return 0

if __name__ == "__main__":
    sys.exit(main())

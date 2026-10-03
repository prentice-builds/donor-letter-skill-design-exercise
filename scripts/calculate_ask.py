#!/usr/bin/env python3
"""Assign donor tiers and calculate ask amounts for a donor file.

Usage:
    python calculate_ask.py donors.csv --campaign-year 2026 [--emergency] -o asks.csv

Reads a donor CSV, writes the same rows plus `tier`, `ask_amount`, and
`flags` columns. Every rule lives in this file so the same input always
produces the same output. No model judgment is involved.

The constants below are fundraising strategy, not code plumbing. They belong
to the development team; review and adjust them before each campaign.
"""

import argparse
import csv
import sys

# ---------------------------------------------------------------------------
# Strategy constants (owned by fundraising staff; edit these, not the logic)
# ---------------------------------------------------------------------------

TIER_THRESHOLDS = [          # (minimum lifetime total, tier name)
    (50_000, "Platinum"),
    (10_000, "Gold"),
    (1_000, "Silver"),
    (0, "Bronze"),
]
LAPSED_AFTER_YEARS = 3       # no gift in > this many years => Lapsed

ASK_PERCENT = {              # ask as a share of largest single gift
    "Platinum": 0.40,
    "Gold": 0.25,
    "Silver": 0.15,
}
FLAT_ASK = {                 # flat asks; uplifts below do NOT apply to these.
    "Bronze": 150,           # Over-asking small or lapsed donors risks losing
    "Lapsed": 50,            # them entirely, so their ask stays predictable.
}

LAPSED_MAJOR_THRESHOLD = 10_000  # lapsed donors above this lifetime total
                                 # get flagged for personal outreach. A
                                 # major donor who stopped giving deserves a
                                 # gift officer's call, not a form letter

LOYALTY_UPLIFT = 0.10        # if donor gave in the year before the campaign
VOLUNTEER_BONUS = 100        # flat, if donor volunteers
EMERGENCY_MULTIPLIER = 1.2   # if the campaign is an emergency appeal
ROUND_TO = 50                # rounding happens LAST, after all uplifts

REQUIRED = ["first_name", "last_name", "largest_gift", "lifetime_total",
            "last_gift_year", "volunteer"]


def parse_money(value):
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def assign_tier(lifetime_total, last_gift_year, campaign_year):
    if campaign_year - last_gift_year > LAPSED_AFTER_YEARS:
        return "Lapsed"
    for minimum, tier in TIER_THRESHOLDS:
        if lifetime_total >= minimum:
            return tier
    return "Bronze"


def calculate_ask(tier, largest_gift, last_gift_year, volunteer,
                  campaign_year, emergency):
    """Order of operations is fixed: percent -> loyalty -> volunteer ->
    emergency -> round. Flat tiers skip everything and round only."""
    if tier in FLAT_ASK:
        return FLAT_ASK[tier]
    ask = largest_gift * ASK_PERCENT[tier]
    if last_gift_year == campaign_year - 1:
        ask *= 1 + LOYALTY_UPLIFT
    if volunteer:
        ask += VOLUNTEER_BONUS
    if emergency:
        ask *= EMERGENCY_MULTIPLIER
    return int(round(ask / ROUND_TO) * ROUND_TO)


def process(path, campaign_year, emergency, out_path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames or []

    missing_cols = [c for c in REQUIRED if c not in columns]
    if missing_cols:
        sys.exit(f"ERROR: donor file is missing required columns: "
                 f"{', '.join(missing_cols)}. Fix the export and rerun.")

    seen_names = set()
    for row in rows:
        flags = []
        largest = parse_money(row.get("largest_gift"))
        lifetime = parse_money(row.get("lifetime_total"))
        try:
            last_year = int(str(row.get("last_gift_year", "")).strip())
        except ValueError:
            last_year = None
        vol_raw = str(row.get("volunteer", "")).strip().lower()
        volunteer = vol_raw in ("yes", "y", "true", "1")
        if not volunteer and vol_raw not in ("no", "n", "false", "0", ""):
            flags.append(f"unrecognized volunteer value '{vol_raw}', "
                         f"treated as no")

        name_key = (row.get("first_name", "").strip().lower(),
                    row.get("last_name", "").strip().lower())
        if name_key in seen_names:
            flags.append("possible duplicate donor")
        seen_names.add(name_key)

        if None in (largest, lifetime) or last_year is None:
            row["tier"] = ""
            row["ask_amount"] = ""
            flags.append("SKIP: missing or unparseable required data")
            row["flags"] = "; ".join(flags)
            continue

        tier = assign_tier(lifetime, last_year, campaign_year)
        ask = calculate_ask(tier, largest, last_year, volunteer,
                            campaign_year, emergency)
        if ask > largest:
            flags.append("ask exceeds donor's largest-ever gift; "
                         "review before sending")
        if tier == "Lapsed" and lifetime >= LAPSED_MAJOR_THRESHOLD:
            flags.append("lapsed major donor; consider personal outreach "
                         "by a gift officer instead of a letter")

        row["tier"] = tier
        row["ask_amount"] = ask
        row["flags"] = "; ".join(flags)

    out_columns = columns + ["tier", "ask_amount", "flags"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    skipped = sum(1 for r in rows if "SKIP" in r["flags"])
    flagged = sum(1 for r in rows if r["flags"] and "SKIP" not in r["flags"])
    print(f"Processed {len(rows)} donors -> {out_path} "
          f"({skipped} skipped, {flagged} flagged for review)")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("donor_file")
    p.add_argument("--campaign-year", type=int, required=True)
    p.add_argument("--emergency", action="store_true",
                   help="campaign is an emergency appeal")
    p.add_argument("-o", "--output", default="asks.csv")
    args = p.parse_args()
    process(args.donor_file, args.campaign_year, args.emergency, args.output)

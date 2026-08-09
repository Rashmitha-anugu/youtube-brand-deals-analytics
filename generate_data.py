"""
generate_data.py
----------------
Generates a SYNTHETIC, clearly-labeled dataset that mimics the shape of a
YouTube "Brand Deals" go-to-market analytics problem: creators, brand-deal
campaigns, and per-campaign performance.

IMPORTANT: This is *synthetic* data produced by a seeded random generator.
It contains no real creators, brands, or proprietary YouTube data. It exists
so the analysis and dashboard in this repo are fully reproducible. To use real
data, replace these CSVs with exports from the YouTube Data API / YouTube
Analytics API or a public dataset that shares the same columns.

Run:  python data/generate_data.py
Out:  data/creators.csv, data/brand_deals.csv, data/deal_performance.csv
"""

import csv
import os
import random

SEED = 42
random.seed(SEED)

HERE = os.path.dirname(os.path.abspath(__file__))

# --- Reference dimensions -------------------------------------------------

# Category profiles: (base engagement rate, base conversion rate, avg order value $)
# Loosely modeled on how verticals differ; NOT calibrated to any real source.
CATEGORIES = {
    "Gaming":    {"eng": 0.045, "cvr": 0.016, "aov": 40},
    "Beauty":    {"eng": 0.060, "cvr": 0.028, "aov": 36},
    "Tech":      {"eng": 0.038, "cvr": 0.022, "aov": 90},
    "Fitness":   {"eng": 0.052, "cvr": 0.022, "aov": 55},
    "Food":      {"eng": 0.048, "cvr": 0.018, "aov": 28},
    "Finance":   {"eng": 0.030, "cvr": 0.026, "aov": 140},
    "Lifestyle": {"eng": 0.050, "cvr": 0.020, "aov": 48},
}

FORMATS = {
    # format -> (relative reach multiplier, relative CPM the brand pays)
    "Dedicated Video":  {"reach": 1.00, "cpm": 30},
    "Integration":      {"reach": 0.85, "cpm": 18},
    "Short":            {"reach": 1.40, "cpm": 8},
    "Livestream":       {"reach": 0.55, "cpm": 22},
}

COUNTRIES = ["US", "US", "US", "UK", "CA", "IN", "AU", "DE", "BR"]

BRANDS = [
    "NovaTech", "GlowLab", "PeakFuel", "ByteBank", "UrbanEats", "AeroFit",
    "PixelPlay", "PureSkin", "CoinFlow", "TrailGear", "LumaBeauty", "MetaMart",
    "SnackHouse", "VoltEnergy", "ZenLiving", "CloudNest", "FitForge", "PayPilot",
]

FIRST = ["Aria", "Leo", "Maya", "Ravi", "Sofia", "Kai", "Nina", "Diego", "Zoe",
         "Omar", "Lena", "Theo", "Priya", "Marco", "Ivy", "Noah", "Sana", "Eli"]
LAST = ["Chen", "Patel", "Rivera", "Okafor", "Kim", "Silva", "Nguyen", "Brooks",
        "Haddad", "Rossi", "Larsen", "Mensah", "Cohen", "Wang", "Costa", "Ali"]


def make_creators(n=60):
    rows = []
    for i in range(1, n + 1):
        cat = random.choice(list(CATEGORIES.keys()))
        # subscribers follow a rough log-normal-ish spread (10k .. 8M)
        subs = int(10_000 * (10 ** random.uniform(0, 2.9)))
        name = f"{random.choice(FIRST)} {random.choice(LAST)}"
        rows.append({
            "creator_id": f"C{i:03d}",
            "creator_name": name,
            "category": cat,
            "subscribers": subs,
            "country": random.choice(COUNTRIES),
            # tier used later for deal pricing
        })
    return rows


def month_seasonality(month):
    # 1.0 baseline, Q4 (Oct-Dec) uplift for brand spend, small summer dip.
    m = int(month.split("-")[1])
    if m in (10, 11, 12):
        return 1.35
    if m in (6, 7):
        return 0.90
    return 1.0


def make_deals_and_perf(creators, n_deals=520):
    months = [f"{y}-{m:02d}" for y in (2024, 2025) for m in range(1, 13)]
    deals, perf = [], []
    for i in range(1, n_deals + 1):
        cr = random.choice(creators)
        cat = cr["category"]
        prof = CATEGORIES[cat]
        fmt = random.choice(list(FORMATS.keys()))
        fmeta = FORMATS[fmt]
        month = random.choice(months)
        seas = month_seasonality(month)

        # --- Deal value (what the brand pays the creator) ---
        # priced off audience size, format CPM, and category demand, with noise
        cat_demand = {"Finance": 1.4, "Tech": 1.3, "Beauty": 1.1}.get(cat, 1.0)
        # 2.2x list-rate factor: agencies/creators price above raw media CPM
        base_cpm = fmeta["cpm"] * cat_demand * 2.2
        # assume the deal is priced against ~1 sponsored video's expected views
        expected_views = cr["subscribers"] * random.uniform(0.10, 0.35) * fmeta["reach"]
        deal_value = (expected_views / 1000) * base_cpm * random.uniform(0.8, 1.2)
        deal_value = round(max(500, deal_value), 2)

        # --- Realized performance ---
        actual_views = int(expected_views * seas * random.uniform(0.6, 1.4))
        eng_rate = max(0.005, random.gauss(prof["eng"], prof["eng"] * 0.25))
        likes = int(actual_views * eng_rate)
        comments = int(likes * random.uniform(0.03, 0.10))
        avg_view_pct = round(min(0.95, max(0.15, random.gauss(0.42, 0.12))), 3)

        # conversions from a UTM/promo-code style attribution
        cvr = max(0.002, random.gauss(prof["cvr"], prof["cvr"] * 0.3))
        # shorts convert worse (less link real estate)
        if fmt == "Short":
            cvr *= 0.5
        # attribution_rate: only a fraction of sales are trackable to the deal
        # (promo code / UTM leakage), which keeps measured ROI realistic.
        attribution_rate = 0.22
        conversions = int(actual_views * avg_view_pct * cvr * attribution_rate)
        revenue = round(conversions * prof["aov"] * random.uniform(0.9, 1.1), 2)
        roi = round(revenue / deal_value, 3) if deal_value else 0.0

        deals.append({
            "deal_id": f"D{i:04d}",
            "creator_id": cr["creator_id"],
            "brand": random.choice(BRANDS),
            "category": cat,
            "format": fmt,
            "campaign_month": month,
            "deal_value_usd": deal_value,
        })
        perf.append({
            "deal_id": f"D{i:04d}",
            "views": actual_views,
            "likes": likes,
            "comments": comments,
            "avg_view_pct": avg_view_pct,
            "conversions": conversions,
            "revenue_usd": revenue,
            "roi": roi,
        })
    return deals, perf


def write_csv(path, rows, fields):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})


def main():
    creators = make_creators()
    deals, perf = make_deals_and_perf(creators)

    write_csv(os.path.join(HERE, "creators.csv"), creators,
              ["creator_id", "creator_name", "category", "subscribers", "country"])
    write_csv(os.path.join(HERE, "brand_deals.csv"), deals,
              ["deal_id", "creator_id", "brand", "category", "format",
               "campaign_month", "deal_value_usd"])
    write_csv(os.path.join(HERE, "deal_performance.csv"), perf,
              ["deal_id", "views", "likes", "comments", "avg_view_pct",
               "conversions", "revenue_usd", "roi"])

    print(f"Wrote {len(creators)} creators, {len(deals)} deals, {len(perf)} performance rows.")


if __name__ == "__main__":
    main()

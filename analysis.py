"""
analysis.py
-----------
Loads the synthetic Brand Deals CSVs into an in-memory SQLite database, runs the
SQL analysis (star-schema joins + aggregation), computes the headline KPIs, and
emits:
  - analysis/results.json         (all computed aggregates)
  - dashboard/dashboard.html      (self-contained interactive dashboard)
  - analysis/queries.sql          (the exact SQL used, for review)

Run:  python analysis/analysis.py
"""

import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

# --------------------------------------------------------------------------
# SQL is the single source of truth. Each query is also dumped to queries.sql.
# --------------------------------------------------------------------------
QUERIES = {
    "kpis": """
        SELECT
          COUNT(*)                              AS campaigns,
          COUNT(DISTINCT d.creator_id)          AS creators,
          ROUND(SUM(d.deal_value_usd), 0)       AS spend,
          ROUND(SUM(p.revenue_usd), 0)          AS revenue,
          ROUND(SUM(p.revenue_usd) * 1.0
                / SUM(d.deal_value_usd), 2)     AS blended_roi,
          ROUND(AVG(p.roi), 2)                  AS avg_roi,
          SUM(p.views)                          AS views,
          SUM(p.conversions)                    AS conversions,
          ROUND(100.0 * SUM(CASE WHEN p.roi < 1 THEN 1 ELSE 0 END)
                / COUNT(*), 1)                  AS pct_at_risk
        FROM brand_deals d
        JOIN deal_performance p ON p.deal_id = d.deal_id
    """,
    "roi_by_category": """
        SELECT d.category,
               COUNT(*)                                AS campaigns,
               ROUND(SUM(d.deal_value_usd), 0)         AS spend,
               ROUND(SUM(p.revenue_usd), 0)            AS revenue,
               ROUND(SUM(p.revenue_usd) * 1.0
                     / SUM(d.deal_value_usd), 2)       AS roi
        FROM brand_deals d
        JOIN deal_performance p ON p.deal_id = d.deal_id
        GROUP BY d.category
        ORDER BY roi DESC
    """,
    "roi_by_format": """
        SELECT d.format,
               COUNT(*)                                AS campaigns,
               ROUND(AVG(p.avg_view_pct) * 100, 1)     AS avg_view_pct,
               ROUND(SUM(p.revenue_usd) * 1.0
                     / SUM(d.deal_value_usd), 2)       AS roi
        FROM brand_deals d
        JOIN deal_performance p ON p.deal_id = d.deal_id
        GROUP BY d.format
        ORDER BY roi DESC
    """,
    "revenue_by_month": """
        SELECT d.campaign_month                        AS month,
               ROUND(SUM(d.deal_value_usd), 0)         AS spend,
               ROUND(SUM(p.revenue_usd), 0)            AS revenue
        FROM brand_deals d
        JOIN deal_performance p ON p.deal_id = d.deal_id
        GROUP BY d.campaign_month
        ORDER BY d.campaign_month
    """,
    "top_creators": """
        SELECT c.creator_name,
               c.category,
               c.subscribers,
               COUNT(*)                                AS campaigns,
               ROUND(SUM(p.revenue_usd), 0)            AS revenue,
               ROUND(SUM(p.revenue_usd) * 1.0
                     / SUM(d.deal_value_usd), 2)       AS roi
        FROM brand_deals d
        JOIN deal_performance p ON p.deal_id = d.deal_id
        JOIN creators c        ON c.creator_id = d.creator_id
        GROUP BY c.creator_id
        HAVING campaigns >= 3
        ORDER BY revenue DESC
        LIMIT 10
    """,
    "at_risk": """
        SELECT d.category,
               d.format,
               COUNT(*)                                AS campaigns,
               ROUND(SUM(d.deal_value_usd), 0)         AS spend_at_risk
        FROM brand_deals d
        JOIN deal_performance p ON p.deal_id = d.deal_id
        WHERE p.roi < 1
        GROUP BY d.category, d.format
        ORDER BY spend_at_risk DESC
        LIMIT 8
    """,
}


def load_db():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("""CREATE TABLE creators(creator_id TEXT, creator_name TEXT,
                   category TEXT, subscribers INTEGER, country TEXT)""")
    cur.execute("""CREATE TABLE brand_deals(deal_id TEXT, creator_id TEXT,
                   brand TEXT, category TEXT, format TEXT, campaign_month TEXT,
                   deal_value_usd REAL)""")
    cur.execute("""CREATE TABLE deal_performance(deal_id TEXT, views INTEGER,
                   likes INTEGER, comments INTEGER, avg_view_pct REAL,
                   conversions INTEGER, revenue_usd REAL, roi REAL)""")
    import csv
    for tbl, fields in [
        ("creators", ["creator_id", "creator_name", "category", "subscribers", "country"]),
        ("brand_deals", ["deal_id", "creator_id", "brand", "category", "format",
                         "campaign_month", "deal_value_usd"]),
        ("deal_performance", ["deal_id", "views", "likes", "comments", "avg_view_pct",
                              "conversions", "revenue_usd", "roi"]),
    ]:
        rows = list(csv.DictReader(open(os.path.join(DATA, tbl + ".csv"))))
        placeholders = ",".join("?" * len(fields))
        cur.executemany(
            f"INSERT INTO {tbl} VALUES ({placeholders})",
            [[r[f] for f in fields] for r in rows],
        )
    con.commit()
    return con


def run(con, sql):
    return [dict(r) for r in con.execute(sql).fetchall()]


def main():
    con = load_db()
    results = {name: run(con, sql) for name, sql in QUERIES.items()}
    results["kpis"] = results["kpis"][0]  # single row

    # write queries.sql for reviewers
    with open(os.path.join(HERE, "queries.sql"), "w") as f:
        for name, sql in QUERIES.items():
            f.write(f"-- {name}\n{sql.strip()}\n;\n\n")

    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    build_dashboard(results)

    k = results["kpis"]
    print("KPIs:")
    print(f"  Campaigns: {k['campaigns']}  Creators: {k['creators']}")
    print(f"  Spend: ${k['spend']:,.0f}  Revenue: ${k['revenue']:,.0f}  Blended ROI: {k['blended_roi']}x")
    print(f"  At-risk (ROI<1): {k['pct_at_risk']}%")
    print("\nROI by category:")
    for r in results["roi_by_category"]:
        print(f"  {r['category']:<10} ROI {r['roi']}x  (${r['spend']:,.0f} spend)")
    print("\nWrote analysis/results.json, analysis/queries.sql, dashboard/dashboard.html")


# --------------------------------------------------------------------------
# Dashboard builder — writes a single self-contained HTML file.
# --------------------------------------------------------------------------
def build_dashboard(results):
    from dashboard_template import render
    html = render(results)
    out = os.path.join(ROOT, "dashboard", "dashboard.html")
    with open(out, "w") as f:
        f.write(html)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, HERE)
    main()

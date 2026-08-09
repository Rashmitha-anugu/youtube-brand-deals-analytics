# YouTube Brand Deals — GTM Insight Narrative

> **Note on data:** This analysis runs on a *synthetic, reproducible* dataset
> (`data/generate_data.py`), built to demonstrate go-to-market analytics
> methodology for a YouTube Brand Deals–style business. It contains no real or
> proprietary data. All figures below are computed by `analysis/analysis.py`.

## Executive summary

Across **520 campaigns** with **60 creators**, the Brand Deals portfolio
converted **$6.7M in media spend** into **$18.7M in attributed revenue** — a
**blended 2.8x ROAS**. That headline is healthy, but it masks wide dispersion:
**35.8% of campaigns returned below 1.0x** (i.e., lost money on a directly
attributed basis). The opportunity is not to spend more — it is to **move spend
from consistently unprofitable pockets into proven ones**, which the data
locates precisely.

## What's working

**Finance is the standout vertical at 4.89x ROAS**, nearly double the portfolio
blend, driven by high average order value and strong intent-to-purchase from
finance audiences. **Tech, Beauty, and Fitness** all clear ~2.3x. Two creators
alone — both in Finance — account for over **$8.2M** of attributed revenue, a
concentration worth protecting with priority inventory and renewal terms.

On **format efficiency**, **Shorts return the most per dollar (4.02x)** because
placement cost is low and reach is high — but their *absolute* revenue
contribution is modest. **Dedicated videos** are the opposite: the **lowest ROI
(2.16x)** yet the largest driver of scale. The read is not "kill dedicated
videos" but "**price them more aggressively and reserve them for high-AOV
verticals**," while using Shorts to extend efficient reach.

## Where the money is leaking

**Food returns 0.88x — below break-even** — on **$779K of spend across 76
campaigns**. Combined with under-performing dedicated-video and livestream
placements, the top eight at-risk segments concentrate **~$1.05M of spend
returning under 1.0x**. Food + Dedicated Video alone is **$200K** at a loss.

## The recommendation (what I'd tell stakeholders)

1. **Reallocate ~$0.8M–$1.0M** out of below-break-even Food and low-ROI
   dedicated-video placements into **Finance and Tech**, and into **Shorts** for
   efficient reach. At the current spread, shifting even $500K from ~0.9x to the
   ~2.8x blend implies **~$1M in incremental attributed revenue**.
2. **Renegotiate dedicated-video rate cards** — they carry the lowest ROI; a
   10–15% price reduction or performance clause materially changes their return.
3. **Lock renewal terms with the top two Finance creators** before competitors
   do; they are single points of both revenue and risk.
4. **Instrument attribution more tightly.** A third of campaigns reading below
   1.0x may partly reflect *attribution leakage* (promo-code/UTM gaps), not true
   loss — closing that gap is itself a data-quality project with revenue upside.

## Method

Star-schema SQL joins across `creators`, `brand_deals`, and `deal_performance`
(SQLite), aggregated in `analysis/analysis.py`; ROI defined as attributed
revenue ÷ media spend. Robust framing (median campaign ROI, at-risk share)
is preferred over the mean, which a small number of viral overperformers skews.
The interactive dashboard is in `dashboard/dashboard.html`.

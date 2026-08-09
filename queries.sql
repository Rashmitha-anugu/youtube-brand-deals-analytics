-- kpis
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
;

-- roi_by_category
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
;

-- roi_by_format
SELECT d.format,
               COUNT(*)                                AS campaigns,
               ROUND(AVG(p.avg_view_pct) * 100, 1)     AS avg_view_pct,
               ROUND(SUM(p.revenue_usd) * 1.0
                     / SUM(d.deal_value_usd), 2)       AS roi
        FROM brand_deals d
        JOIN deal_performance p ON p.deal_id = d.deal_id
        GROUP BY d.format
        ORDER BY roi DESC
;

-- revenue_by_month
SELECT d.campaign_month                        AS month,
               ROUND(SUM(d.deal_value_usd), 0)         AS spend,
               ROUND(SUM(p.revenue_usd), 0)            AS revenue
        FROM brand_deals d
        JOIN deal_performance p ON p.deal_id = d.deal_id
        GROUP BY d.campaign_month
        ORDER BY d.campaign_month
;

-- top_creators
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
;

-- at_risk
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
;


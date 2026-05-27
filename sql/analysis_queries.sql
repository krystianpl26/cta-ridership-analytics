-- Annual ridership totals
SELECT
  EXTRACT(YEAR FROM service_date) AS year,
  SUM(total_rides) AS total_annual_rides,
  AVG(total_rides) AS average_daily_rides
FROM cta_ridership
GROUP BY 1
ORDER BY 1;

-- Monthly ridership trends
SELECT
  EXTRACT(YEAR FROM service_date) AS year,
  EXTRACT(MONTH FROM service_date) AS month,
  SUM(total_rides) AS monthly_total_rides,
  SUM(bus) AS monthly_bus_rides,
  SUM(rail_boardings) AS monthly_rail_rides
FROM cta_ridership
GROUP BY 1, 2
ORDER BY 1, 2;

-- Bus vs rail totals by year
SELECT
  EXTRACT(YEAR FROM service_date) AS year,
  SUM(bus) AS total_bus_rides,
  SUM(rail_boardings) AS total_rail_rides,
  SUM(bus) / NULLIF(SUM(total_rides), 0) AS bus_share,
  SUM(rail_boardings) / NULLIF(SUM(total_rides), 0) AS rail_share
FROM cta_ridership
GROUP BY 1
ORDER BY 1;

-- Day type comparison: 2019 vs 2025
SELECT
  EXTRACT(YEAR FROM service_date) AS year,
  CASE day_type
    WHEN 'W' THEN 'Weekday'
    WHEN 'A' THEN 'Saturday'
    WHEN 'U' THEN 'Sunday/Holiday'
    ELSE 'Unknown'
  END AS day_type_label,
  AVG(total_rides) AS avg_rides
FROM cta_ridership
WHERE EXTRACT(YEAR FROM service_date) IN (2019, 2025)
GROUP BY 1, 2
ORDER BY 1, 2;

-- Pandemic recovery vs 2019 baseline
WITH annual AS (
  SELECT
    EXTRACT(YEAR FROM service_date) AS year,
    SUM(total_rides) AS total_annual_rides
  FROM cta_ridership
  GROUP BY 1
), baseline AS (
  SELECT total_annual_rides AS baseline_2019
  FROM annual
  WHERE year = 2019
)
SELECT
  a.year,
  a.total_annual_rides,
  100.0 * a.total_annual_rides / b.baseline_2019 AS pct_of_2019,
  100.0 * (a.total_annual_rides - b.baseline_2019) / b.baseline_2019 AS pct_change_from_2019
FROM annual a
CROSS JOIN baseline b
WHERE a.year >= 2020
ORDER BY a.year;

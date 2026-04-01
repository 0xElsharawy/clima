SELECT
  DATE_TRUNC ('day', event_time) AS date,
  COUNT(*) AS total_records
FROM
  weather_readings
GROUP BY
  1
ORDER BY
  1 DESC;

SELECT
  CASE
    WHEN weathercode = 0 THEN 'Clear Sky'
    WHEN weathercode BETWEEN 1 AND 3  THEN 'Partly Cloudy'
    WHEN weathercode IN (45, 48) THEN 'Foggy'
    WHEN weathercode BETWEEN 51 AND 67  THEN 'Rainy'
    WHEN weathercode BETWEEN 71 AND 77  THEN 'Snowy'
    WHEN weathercode BETWEEN 80 AND 99  THEN 'Stormy'
    ELSE 'Other'
  END AS condition_label,
  COUNT(*) AS city_count
FROM
  weather_readings
WHERE
  event_time >= NOW () - INTERVAL '24 hours'
GROUP BY
  1
ORDER BY
  2 DESC;

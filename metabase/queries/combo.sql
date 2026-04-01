SELECT
  DATE_TRUNC ('hour', event_time) AS time,
  AVG(temperature_2m) AS temp,
  SUM(precipitation) AS rain_intensity
FROM
  weather_readings
GROUP BY
  1
ORDER BY
  1 DESC;

SELECT
  AVG(temperature_2m) AS avg_temp
FROM
  weather_readings
WHERE
  event_time > NOW () - INTERVAL '1 hour';

-- Add Ranges: Create a "Cold" range (Blue) from -10 to 15, "Moderate" (Green) from 15 to 30, and "Hot" (Red) from 30 to 50.

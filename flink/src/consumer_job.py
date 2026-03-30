import os
import logging

from pyflink.table import EnvironmentSettings, StreamTableEnvironment
from pyflink.datastream import StreamExecutionEnvironment

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "weather-topic")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "password")
PG_DB = os.getenv("POSTGRES_DB", "weather_db")


def create_postgres_sink(t_env):
    table_name = "weather_readings"
    sink_ddl = f"""
        CREATE TABLE {table_name} (
            city TEXT,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            generationtime_ms DOUBLE PRECISION,
            utc_offset_seconds INT,
            timezone TEXT,
            timezone_abbreviation TEXT,
            elevation DOUBLE PRECISION,

            time TIMESTAMP,
            interval_sec INT,

            temperature_2m DOUBLE PRECISION,
            apparent_temperature DOUBLE PRECISION,
            relative_humidity_2m DOUBLE PRECISION,
            is_day INT,
            precipitation DOUBLE PRECISION,
            rain DOUBLE PRECISION,
            showers DOUBLE PRECISION,
            snowfall DOUBLE PRECISION,
            weathercode INT,
            cloud_cover INT,
            pressure_msl DOUBLE PRECISION,
            surface_pressure DOUBLE PRECISION,
            wind_speed_10m DOUBLE PRECISION,
            wind_direction_10m INT,
            wind_gusts_10m DOUBLE PRECISION,

            temperature_unit TEXT,
            wind_speed_unit TEXT
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://{PG_HOST}:{PG_PORT}/{PG_DB}',
            'driver' = 'org.postgresql.Driver',
            'username' = '{PG_USER}',
            'password' = '{PG_PASS}',
            'table-name' = '{table_name}'
        )
    """
    t_env.execute_sql(sink_ddl)
    return table_name


def create_kafka_source(t_env):
    source_ddl = f"""
        CREATE TABLE kafka_weather_source (
            latitude DOUBLE,
            longitude DOUBLE,
            generationtime_ms DOUBLE,
            utc_offset_seconds INT,
            timezone STRING,
            timezone_abbreviation STRING,
            elevation DOUBLE,

            `current_units` ROW<
                temperature_2m STRING,
                wind_speed_10m STRING
            >,

            `current` ROW<
                `time` STRING,
                `interval` INT,
                temperature_2m DOUBLE,
                apparent_temperature DOUBLE,
                relative_humidity_2m DOUBLE,
                is_day INT,
                precipitation DOUBLE,
                rain DOUBLE,
                showers DOUBLE,
                snowfall DOUBLE,
                weathercode INT,
                cloud_cover INT,
                pressure_msl DOUBLE,
                surface_pressure DOUBLE,
                wind_speed_10m DOUBLE,
                wind_direction_10m INT,
                wind_gusts_10m DOUBLE
            >,

            city STRING
        ) WITH (
            'connector' = 'kafka',
            'topic' = '{KAFKA_TOPIC}',
            'properties.bootstrap.servers' = '{KAFKA_BOOTSTRAP}',
            'properties.group.id' = 'weather_consumer_group',
            'scan.startup.mode' = 'earliest-offset',
            'value.format' = 'avro-confluent',
            'value.avro-confluent.schema-registry.url' = 'http://schema-registry:8081'
        )
    """
    t_env.execute_sql(source_ddl)
    return "kafka_weather_source"


def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(10 * 1000)

    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    try:
        source_table = create_kafka_source(t_env)
        sink_table = create_postgres_sink(t_env)

        t_env.execute_sql(f"""
            INSERT INTO {sink_table}
            SELECT
                city,
                latitude,
                longitude,
                generationtime_ms,
                utc_offset_seconds,
                timezone,
                timezone_abbreviation,
                elevation,

                TO_TIMESTAMP(`current`.`time`, 'yyyy-MM-dd''T''HH:mm') AS time,
                `current`.`interval` AS interval_sec,

                `current`.temperature_2m,
                `current`.apparent_temperature,
                `current`.relative_humidity_2m,
                `current`.is_day,
                `current`.precipitation,
                `current`.rain,
                `current`.showers,
                `current`.snowfall,
                `current`.weathercode,
                `current`.cloud_cover,
                `current`.pressure_msl,
                `current`.surface_pressure,
                `current`.wind_speed_10m,
                `current`.wind_direction_10m,
                `current`.wind_gusts_10m,

                current_units.temperature_2m AS temperature_unit,
                current_units.wind_speed_10m AS wind_speed_unit
            FROM {source_table}
        """).wait()

    except Exception as e:
        logger.error("Error writing messages to Postgres: %s", e)


if __name__ == "__main__":
    main()

import json
import os
import requests
import psycopg2
from datetime import datetime, timedelta, timezone
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from confluent_kafka import Producer


default_args = {"owner": "batman", "retries": 5, "retry_delay": timedelta(minutes=1)}

dag = DAG(
    dag_id="streaming_dag",
    default_args=default_args,
    description="A DAG for streaming to kafka topic and storing API response in MinIO bucket",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
)

BASE_URL = "https://api.open-meteo.com/v1/forecast"
BUCKET_NAME = os.getenv("BUCKET_NAME", "weather-bucket")
TOPIC = os.getenv("KAFKA_TOPIC")

DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "database": "weather_db",
    "user": "postgres",
    "password": "password",
}


def fetch_weather_to_minio(**kwargs):
    ti = kwargs["ti"]

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT city, lat, lng FROM cities;")
    cities = [
        {"city": row[0], "latitude": row[1], "longitude": row[2]}
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()

    hook = S3Hook(aws_conn_id="minio_conn")
    if hook.check_for_bucket(bucket_name=BUCKET_NAME):
        print("Successfully connected to MinIO!")

    keys = []

    for city in cities:
        response = requests.get(
            BASE_URL,
            params={
                "latitude": city["latitude"],
                "longitude": city["longitude"],
                "current": ",".join(
                    [
                        "temperature_2m",
                        "apparent_temperature",
                        "relative_humidity_2m",
                        "is_day",
                        "precipitation",
                        "rain",
                        "showers",
                        "snowfall",
                        "weathercode",
                        "cloud_cover",
                        "pressure_msl",
                        "surface_pressure",
                        "wind_speed_10m",
                        "wind_direction_10m",
                        "wind_gusts_10m",
                    ]
                ),
                "timezone": "auto",
            },
        )

        response.raise_for_status()
        data = response.json()
        data["city"] = city["city"]

        ts = data["current"]["time"].replace(":", "-")
        key = f"landing/{city['city']}/{ts}.json"

        hook.load_string(
            json.dumps(data),
            key=key,
            bucket_name=BUCKET_NAME,
            replace=True,
        )

        keys.append(key)

    return keys


def delivery_report(err, msg):
    if err:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered to {msg.topic()} [Partition: {msg.partition()}]")


def stream_to_kafka(ti):
    producer_conf = {
        "bootstrap.servers": "kafka:29092",
    }
    producer = Producer(producer_conf)

    object_keys = ti.xcom_pull(task_ids="fetch_weather_to_minio")
    if not object_keys:
        raise ValueError("No object keys received from previous task")

    hook = S3Hook(aws_conn_id="minio_conn")
    try:
        for key in object_keys:
            data_str = hook.read_key(key=key, bucket_name=BUCKET_NAME)
            weather_data = json.loads(data_str)
            if not weather_data:
                continue
            producer.produce(
                topic=TOPIC,
                key=weather_data["city"].encode("utf-8"),
                value=json.dumps(weather_data).encode("utf-8"),
                on_delivery=delivery_report,
            )
        producer.flush()
    except Exception as e:
        print(f"❌ Error in Kafka streaming: {e}")
        raise


with dag:
    task1 = PythonOperator(
        task_id="fetch_weather_to_minio",
        python_callable=fetch_weather_to_minio,
        op_kwargs={
            "city": {"city": "Cairo", "latitude": 30.0444, "longitude": 31.2357}
        },
    )

    task2 = PythonOperator(task_id="stream_to_kafka", python_callable=stream_to_kafka)

    task1 >> task2

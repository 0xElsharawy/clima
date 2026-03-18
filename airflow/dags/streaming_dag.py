import json
from datetime import datetime, timedelta, timezone
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringSerializer,
)

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
BUCKET_NAME = "weather-archive"
TOPIC = "weather_raw"


def fetch_weather_to_minio(city, **kwargs):
    import requests

    response = requests.get(
        BASE_URL,
        params={
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "current": ["temperature_2m", "wind_speed_10m"],
            "timezone": "auto",
        },
    )
    response.raise_for_status()
    data = response.json()
    data["city"] = city["city"]

    ts = data["current"]["time"].replace(":", "-")
    key = f"landing/{city['city']}/{ts}.json"

    hook = S3Hook(aws_conn_id="minio_conn")
    hook.load_string(json.dumps(data), key=key, bucket_name=BUCKET_NAME, replace=True)

    return key


def delivery_report(err, msg):
    if err:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered to {msg.topic()} [Partition: {msg.partition()}]")


def weather_to_dict(weather_data, ctx):
    return {"city": weather_data["city"]}


def stream_to_kafka(ti):
    object_key = ti.xcom_pull(task_ids="fetch_weather_to_minio")
    hook = S3Hook(aws_conn_id="minio_conn")
    data_str = hook.read_key(key=object_key, bucket_name=BUCKET_NAME)
    weather_data = json.loads(data_str)

    producer_conf = {
        "bootstrap.servers": "kafka:29092",
    }

    producer = Producer(dict(producer_conf))


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

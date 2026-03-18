from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


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


def upload_to_minio(ti):
    import json
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook

    hook = S3Hook(aws_conn_id="minio_conn")

    weather_data = ti.xcom_pull(task_ids="fetch_weather")
    data_str = json.dumps(weather_data)

    timestamp = weather_data["current"]["time"].replace(":", "-")
    city = weather_data["city"]
    object_key = f"landing/{city}/{timestamp}.json"

    hook.load_string(
        string_data=data_str,
        key=object_key,
        bucket_name="weather-archive",
        replace=True,
    )


def fetch_weather(city):
    import requests

    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "current": ["temperature_2m", "wind_speed_10m"],
        "timezone": "auto",
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        weather_data = response.json()
        weather_data["city"] = city["city"]
        return weather_data
    else:
        print(f"Error fetching weather data for {city['city']}: {response.status_code}")
        return None


def kafka_stream():
    pass


with dag:
    task1 = PythonOperator(
        task_id="fetch_weather",
        python_callable=fetch_weather,
        op_kwargs={
            "city": {"city": "Cairo", "latitude": 30.0444, "longitude": 31.2357}
        },
    )

    task2 = PythonOperator(task_id="upload_to_minio", python_callable=upload_to_minio)

    task1 >> task2

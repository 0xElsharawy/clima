import os
import requests
import psycopg2
import pandas as pd
from datetime import datetime, timedelta, timezone
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator

default_args = {"owner": "batman", "retries": 5, "retry_delay": timedelta(minutes=1)}

dag = DAG(
    dag_id="ingest_cities_dag",
    default_args=default_args,
    description="A DAG for downloading and ingesting Spanish cities data into Postgres",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
)

PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_PORT = int(os.getenv("POSTGRES_PORT", 5432))
PG_DB = os.getenv("POSTGRES_DB", "weather_db")
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")

CSV_URL = "https://simplemaps.com/static/data/country-cities/es/es.csv"
CSV_FILE = "/tmp/es.csv"

DB_CONFIG = {
    "host": PG_HOST,
    "port": PG_PORT,
    "database": PG_DB,
    "user": PG_USER,
    "password": PG_PASSWORD,
}


def download_csv():
    r = requests.get(CSV_URL)
    r.raise_for_status()
    with open(CSV_FILE, "wb") as f:
        f.write(r.content)


def ingest_csv():
    df = pd.read_csv(CSV_FILE)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            city VARCHAR(100),
            lat DECIMAL(9,6),
            lng DECIMAL(9,6),
            country VARCHAR(50),
            iso2 CHAR(2),
            admin_name VARCHAR(100),
            capital VARCHAR(20),
            population BIGINT,
            population_proper BIGINT,
            PRIMARY KEY(city, country)
        );
    """)
    conn.commit()

    for row in df.itertuples(index=False):
        cur.execute(
            """
            INSERT INTO cities (city, lat, lng, country, iso2, admin_name, capital, population, population_proper)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (city, country) DO NOTHING;
        """,
            tuple(row),
        )
    conn.commit()
    cur.close()
    conn.close()


with dag:
    task1 = BashOperator(
        task_id="cleanup_tmp",
        bash_command="rm -rf /tmp/* /tmp/.[!.]* 2>/dev/null || true",
    )

    task2 = PythonOperator(task_id="download_csv", python_callable=download_csv)

    task3 = PythonOperator(task_id="ingest_csv", python_callable=ingest_csv)

    task1 >> task2 >> task3

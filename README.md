# Real-Time Weather Pipeline

A real-time weather data pipeline that fetches weather data from Open-Meteo API, stores raw data in MinIO, streams through Kafka, and processes with Apache Flink into ClickHouse for analytics.

## Architecture

```
Open-Meteo API
      ↓
Apache Airflow (orchestration)
      ↓
MinIO (raw data landing zone)
      ↓
Apache Kafka (streaming)
      ↓
Apache Flink (stream processing)
      ↓
ClickHouse (analytics database)
      ↓
Metabase (visualization)
```

## Tech Stack

| Component         | Technology                     |
| ----------------- | ------------------------------ |
| Orchestration     | Apache Airflow                 |
| Message Broker    | Apache Kafka + Schema Registry |
| Stream Processing | Apache Flink (PyFlink)         |
| Object Storage    | MinIO (S3-compatible)          |
| Analytics DB      | ClickHouse                     |
| Visualization     | Metabase                       |
| Infrastructure    | Terraform                      |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- `just` command runner (optional)
- Terraform

### Start all services

```bash
# Using just (recommended)
just up

# Or using docker compose directly
docker compose up -d
```

### Useful Commands

```bash
just ps        # Check service status
just logs <service>  # View logs (airflow, kafka, flink, etc.)
just shell <service> # Open shell in container
just down      # Stop all services
just rebuild   # Rebuild and restart
```

## Services & Ports

| Service       | Port | URL                   |
| ------------- | ---- | --------------------- |
| Airflow       | 8080 | http://localhost:8080 |
| Kafka UI      | 8083 | http://localhost:8083 |
| Flink UI      | 8082 | http://localhost:8082 |
| ClickHouse    | 8123 | http://localhost:8123 |
| Metabase      | 3000 | http://localhost:3000 |
| MinIO Console | 9001 | http://localhost:9001 |

## Default Credentials

| Service    | Username | Password            |
| ---------- | -------- | ------------------- |
| Airflow    | admin    | `just airflow-cred` |
| MinIO      | mioadmin | mioadmin            |
| ClickHouse | chadmin  | chadmin             |

## Project Structure

```
├── airflow/           # Airflow DAGs and config
│   └── dags/
│       ├── streaming_dag.py   # Main pipeline DAG
│       └── cities.json        # 30 Spanish cities
├── kafka/             # Kafka + Schema Registry
├── flink/             # PyFlink jobs
├── clickhouse/        # ClickHouse setup
├── metabase/          # BI dashboards
├── minio/             # Object storage
├── postgres/          # Metadata storage
└── terraform/         # Infrastructure as code
```

## Pipeline Flow

1. **Airflow DAG** fetches weather data from Open-Meteo API for configured cities
2. Raw JSON is stored in **MinIO** (weather-archive bucket, landing/ prefix)
3. Data is serialized with Avro schema and produced to **Kafka** (weather_raw topic)
4. **Flink** consumes from Kafka, transforms, and writes to **ClickHouse**
5. **Metabase** provides visualization dashboards

## Terraform (MinIO)

```bash
just init    # Initialize terraform
just apply   # Create MinIO bucket
just destroy # Remove resources
```

## Environment Variables

Copy `.env.example` to `.env` and configure as needed:

```bash
cp .env.example .env
```

Key variables:

- `KAFKA_TOPIC` - Kafka topic name
- `CLICKHOUSE_DB` - ClickHouse database name
- `MINIO_BUCKET` - MinIO bucket name

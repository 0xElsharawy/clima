# Real-Time Weather Pipeline

A real-time weather data pipeline that fetches weather data from Open-Meteo API, stores raw data in MinIO, and streams through Kafka for downstream processing.

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
[Downstream consumers]
```

## Tech Stack

| Component      | Technology                |
| -------------- | ------------------------- |
| Orchestration  | Apache Airflow            |
| Message Broker | Apache Kafka              |
| Object Storage | MinIO (S3-compatible)     |
| Metadata DB    | PostgreSQL                |
| Infrastructure | Terraform                 |

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
| MinIO Console | 9001 | http://localhost:9001 |
| PostgreSQL    | 5432 | localhost:5432        |

### 🛠 MinIO Setup for Airflow

To enable Airflow to communicate with your local MinIO instance, follow these steps:

1.  Navigate to your Airflow web UI (typically `http://localhost:8080`).
2.  In the top menu, go to **Admin** -> **Connections**.
3.  Click the **+ (plus)** icon to add a new connection.
4.  Fill in the following details:
    - **Connection Id:** `minio_conn`
    - **Connection Type:** `Amazon Web Services`
    - **Extra Fields JSON:** copy and paste the following JSON configuration:

    ```json
    {
      "aws_access_key_id": "mioadmin",
      "aws_secret_access_key": "mioadmin",
      "endpoint_url": "http://minio:9000"
    }
    ```

    - **Save** the connection.

## Default Credentials

| Service    | Username | Password            |
| ---------- | -------- | ------------------- |
| Airflow    | admin    | `just airflow-cred` |
| MinIO      | mioadmin | mioadmin            |
| PostgreSQL | airflow  | airflow             |

## Project Structure

```
├── airflow/           # Airflow DAGs and config
│   └── dags/
│       ├── streaming_dag.py   # Main pipeline DAG
│       └── cities.json        # 30 Spanish cities
├── kafka/             # Kafka configuration
├── minio/             # Object storage
├── postgres/          # Metadata storage
└── terraform/         # Infrastructure as code
```

## Pipeline Flow

1. **Airflow DAG** fetches weather data from Open-Meteo API for configured cities
2. Raw JSON is stored in **MinIO** (weather-archive bucket, landing/ prefix)
3. Data is serialized and produced to **Kafka** (weather_raw topic)
4. **Kafka** streams data for downstream consumers

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
- `MINIO_BUCKET` - MinIO bucket name

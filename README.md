# Real-Time Weather Pipeline

A real-time weather data pipeline that fetches weather data from Open-Meteo API, stores raw data in MinIO, and streams through Kafka for downstream processing.

## Architecture

![Pipeline Diagram](assets/pipeline.png)

## Tech Stack

| Component              | Technology              |
| ---------------------- | ----------------------- |
| Orchestration          | Apache Airflow          |
| Message Broker         | Apache Kafka            |
| Stream Processing      | Apache Flink            |
| Object Storage         | MinIO (S3-compatible)   |
| Metadata DB & OLAP     | PostgreSQL              |
| Infrastructure as Code | Terraform               |
| Visualization          | Metabase                |
| Containerization       | Docker & Docker Compose |

## Quick Start

### Prerequisites

- Git
- Docker & Docker Compose
- `just` command runner (A better `make`)
- Terraform

### Setup

1. Clone the repository and navigate to the project directory:

```bash
git clone <repository-url>
cd real-time-weather-pipeline
```

2. Start the services using `just`:

```bash
# Using just (recommended)
just up

# Or using docker compose directly
docker compose up -d
```

> [!NOTE]
> I will be using `just` for all commands in this README, but you can achieve the same results by looking in `justfile` to see the equivalent commands.

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
| Airflow UI    | 8080 | http://localhost:8080 |
| Flink UI      | 5432 | http://localhost:8082 |
| Kafka UI      | 8083 | http://localhost:8083 |
| MinIO Console | 9001 | http://localhost:9001 |
| Metabase      | 3000 | http://localhost:3000 |

### MinIO Setup for Airflow

To enable Airflow to communicate with MinIO instance, follow these steps:

1.  Navigate to your Airflow web UI (typically `http://localhost:8080`).
2.  In the side menu, go to **Admin** -> **Connections**.
3.  Click the **+ (plus)** icon to add a new connection.
4.  Fill in the following details:
    - **Connection Id:** `minio_conn`
    - **Connection Type:** `Amazon Web Services`
    - Access Key: `mioadmin`
    - Secret Key: `mioadmin`
    - **Extra Fields JSON:** add `{ "endpoint_url": "http://minio:9000" }`
    - **Save** the connection.

## Default Credentials

| Service    | Username | Password |
| ---------- | -------- | -------- |
| Airflow    | admin    | -        |
| MinIO      | mioadmin | mioadmin |
| PostgreSQL | airflow  | airflow  |

To get the Airflow admin password, you can run:

```bash
# Password is frequently changed for security, so check the generated file
docker exec airflow cat simple_auth_manager_passwords.json.generated
```

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

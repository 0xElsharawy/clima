FROM flink:2.2.0-scala_2.12-java17

# UV setup for PyFlink
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /opt/pyflink

COPY pyproject.flink.toml pyproject.toml

RUN uv python install 3.11 && uv sync

ENV PATH="/opt/pyflink/.venv/bin:$PATH"

# Flink libraries for connectors
WORKDIR /opt/flink/lib

# Base URLs
ARG MAVEN_REPO=https://repo.maven.apache.org/maven2
ARG CONFLUENT_REPO=https://packages.confluent.io/maven

RUN wget -q ${MAVEN_REPO}/org/apache/flink/flink-sql-connector-kafka/4.0.1-2.0/flink-sql-connector-kafka-4.0.1-2.0.jar && \
    wget -q ${MAVEN_REPO}/org/apache/flink/flink-connector-jdbc-core/4.0.0-2.0/flink-connector-jdbc-core-4.0.0-2.0.jar && \
    wget -q ${MAVEN_REPO}/com/clickhouse/clickhouse-jdbc-all/0.9.7/clickhouse-jdbc-all-0.9.7.jar && \
    wget -q ${MAVEN_REPO}/org/apache/avro/avro/1.11.2/avro-1.11.2.jar && \
    wget -q ${MAVEN_REPO}/org/apache/flink/flink-avro/2.2.0/flink-avro-2.2.0.jar && \
    wget -q ${CONFLUENT_REPO}/io/confluent/kafka-schema-registry-client/7.7.7/kafka-schema-registry-client-7.7.7.jar && \
    wget -q ${CONFLUENT_REPO}/io/confluent/kafka-avro-serializer/7.6.1/kafka-avro-serializer-7.6.1.jar

# Copy custom Flink config
COPY flink-config.yaml /opt/flink/conf/config.yaml

WORKDIR /opt/flink

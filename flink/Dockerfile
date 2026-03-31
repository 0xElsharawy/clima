FROM flink:2.2.0-scala_2.12-java17

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /opt/pyflink

COPY pyproject.flink.toml pyproject.toml

RUN uv python install 3.11 && uv sync

ENV PATH="/opt/pyflink/.venv/bin:$PATH"

WORKDIR /opt/flink/lib

ARG MAVEN_REPO=https://repo.maven.apache.org/maven2

RUN wget -q ${MAVEN_REPO}/org/apache/flink/flink-json/2.2.0/flink-json-2.2.0.jar
RUN wget -q ${MAVEN_REPO}/org/apache/flink/flink-sql-connector-kafka/4.0.1-2.0/flink-sql-connector-kafka-4.0.1-2.0.jar
RUN wget -q ${MAVEN_REPO}/org/apache/flink/flink-connector-jdbc-core/4.0.0-2.0/flink-connector-jdbc-core-4.0.0-2.0.jar
RUN wget -q ${MAVEN_REPO}/org/apache/flink/flink-connector-jdbc-postgres/4.0.0-2.0/flink-connector-jdbc-postgres-4.0.0-2.0.jar
RUN wget -q ${MAVEN_REPO}/org/postgresql/postgresql/42.7.10/postgresql-42.7.10.jar

COPY flink-config.yaml /opt/flink/conf/config.yaml

WORKDIR /opt/flink

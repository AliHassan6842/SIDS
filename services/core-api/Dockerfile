FROM eclipse-temurin:21-jdk AS build
WORKDIR /workspace
COPY .mvn .mvn
COPY mvnw pom.xml ./
RUN chmod +x mvnw && ./mvnw -q -DskipTests dependency:go-offline
COPY src src
RUN ./mvnw -q -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY --from=build /workspace/target/core-api-*.jar /app/core-api.jar
RUN mkdir -p /data/private-images && chown -R 65532:65532 /app /data
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/core-api.jar"]

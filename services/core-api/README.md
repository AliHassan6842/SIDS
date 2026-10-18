# SIDS Core API

Java 21/Spring Boot service for identity, authorization, crop/pest catalog, scan ownership, bounded AI orchestration, PostgreSQL persistence, Flyway migrations, and private local image storage.

From this directory on Windows:

```powershell
$env:JAVA_HOME = 'C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot'
Get-Content ..\..\.env | Where-Object { $_ -and -not $_.StartsWith('#') } | ForEach-Object {
    $name, $value = $_.Split('=', 2)
    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
}
.\mvnw.cmd clean test
.\mvnw.cmd package
.\mvnw.cmd spring-boot:run
```

On Linux/macOS, export the values from the ignored root `.env`, run `chmod +x mvnw`, and use the equivalent `./mvnw` commands. A running PostgreSQL instance is required for the application. `DATABASE_PASSWORD`, `AUTH_JWT_SECRET`, and `AI_SERVICE_TOKEN` have no source-code defaults; startup fails when they are missing, too short, or still contain a published placeholder. Tests use Testcontainers for the real PostgreSQL Flyway compatibility gate, so Docker must be available.

Uploaded images are stored below `STORAGE_LOCAL_ROOT`; in Compose this is the private `sids_private_images` named volume. The API never serves that directory as a public static path.

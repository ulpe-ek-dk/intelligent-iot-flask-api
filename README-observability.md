# Grafana Observability — branch: grafana-integration

Denne branch tilføjer full-stack observability til Intelligent IoT Flask API'en
med Prometheus, Grafana og MySQL Exporter.

## Arkitektur

```
Flask API  ──/metrics──►  Prometheus  ──query──►  Grafana
MySQL DB   ◄── mysqld-exporter ──►  Prometheus
```

## Kom i gang

### 1. Byg image lokalt (første gang)
```bash
docker build -t intelligent-iot-flask-api:latest .
```

### 2. Start hele stacken
```bash
docker compose up -d
```

### 3. Åbn services
| Service    | URL                          |
|------------|------------------------------|
| Flask API  | http://localhost:5005        |
| Grafana    | http://localhost:3000        |
| Prometheus | http://localhost:9090        |
| /metrics   | http://localhost:5005/metrics|

### 4. Log ind i Grafana
- Brugernavn: `admin`
- Adgangskode: `admin`

Dashboardet **"Intelligent IoT API — Observability"** er automatisk
klar under Dashboards → IoT.

## Custom metrics i appen

| Metric | Type | Beskrivelse |
|--------|------|-------------|
| `iot_devices_online_total` | Gauge | Antal devices med status=online |
| `iot_db_errors_total` | Counter | Fejlede DB-kald (label: operation) |
| `iot_device_not_found_total` | Counter | Antal 404-svar på device endpoints |

## Mappestruktur

```
grafana/
  provisioning/
    datasources/prometheus.yml   # Auto-konfigurerer Prometheus datasource
    dashboards/dashboards.yml    # Fortæller Grafana hvor dashboards ligger
  dashboards/
    iot-dashboard.json           # Færdigt IoT dashboard
prometheus.yml                   # Scrape config for Flask + MySQL
docker-compose.yml               # Udvider original med obs-stack
app.py                           # Flask app med metrics tilføjet
requirements.txt                 # prometheus-flask-exporter tilføjet
```
# =============================================================
# Makefile – genvejskommandoer til iot-flask-api
# Brug: make <kommando>
# =============================================================

# Kør ikke som targets, men som kommandoer
.PHONY: dev devobs devobs-bg obs-check obs-check-devices down clean push remote-up remote-down status logs

LOCAL := docker compose -f docker-compose.yml -f docker-compose.local.yml --env-file .env.local
OBS   := docker compose -f docker-compose.yml -f docker-compose.local.yml -f docker-compose.observability.yml --env-file .env.local

# Lokalt: byg og kør med hot-reload (genstarter ved kodeændringer)
dev:
	$(LOCAL) up --build

# Lokalt med Prometheus og Grafana (i forgrunden, viser logs)
devobs:
	$(OBS) up --build

# Lokalt med Prometheus og Grafana (i baggrunden)
devobs-bg:
	$(OBS) up --build -d

# Er observability grøn? API, metrics, Prometheus og Grafana
obs-check:
	curl -fsS http://localhost:5005/health
	curl -fsS http://localhost:5005/metrics | grep -q flask_http_request_total
	curl -fsS http://localhost:9090/api/v1/targets | grep -q '"health":"up"'
	curl -fsS http://localhost:3000/api/health

obs-check-devices:
	@n=$$(curl -fsS 'http://localhost:9090/api/v1/query' --data-urlencode 'query=changes(iot_devices_online_total[2m])' | grep -o '"value":\[[^]]*\]' | grep -o '"[0-9.]*"]' | tr -d '"]'); \
	echo "Antal ændringer de seneste 2 min: $$n"; \
	if [ "$$n" != "0" ]; then echo "FEJL: iot_devices_online_total skifter værdi"; exit 1; fi; \
	echo "OK: iot_devices_online_total er stabil"

# Stop alle containere (også observability)
down:
	$(OBS) down

# Stop og slet volumes (rydder DB og Grafana)
clean:
	$(OBS) down -v

# Byg og push image til ghcr.io
push:
	docker build -t ghcr.io/ulpe-ek-dk/intelligent-iot-flask-api:latest .
	docker push ghcr.io/ulpe-ek-dk/intelligent-iot-flask-api:latest

# Deploy til remote maskine / Azure VM
remote-up:
	docker compose -f docker-compose.yml -f docker-compose.remote.yml --env-file .env.remote up -d

# Stop remote deployment
remote-down:
	docker compose -f docker-compose.yml -f docker-compose.remote.yml --env-file .env.remote down

# Vis kørende containere
status:
	$(OBS) ps

logs:
	$(LOCAL) logs -f api
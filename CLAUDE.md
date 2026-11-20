# Regler for AI-agenter i dette projekt

## Om projektet
Flask-API til IoT-enheder med MySQL, kørt med Docker Compose.
Observability med Prometheus og Grafana (docker-compose.observability.yml).

## Kommandoer
- Stakken kører allerede (startet med `make devobs` i et andet vindue).
- Brug kun disse make-targets:
  - `make obs-check` – tjekker API, metrics, Prometheus og Grafana
  - `make obs-check-devices` – tjekker at iot_devices_online_total er stabil
  - `make status` – viser kørende containere
  - `make logs` – viser API'ets logs
- Kald ikke docker compose direkte, når der findes et target.
- Kør ALDRIG `make push`, `make remote-up`, `make remote-down` eller `make clean`.
- Hvis en service skal genstartes, så spørg først.

## Arbejdsgang
- Forklar først din hypotese, og hvilke filer du vil ændre, før du ændrer noget.
- Lav den mindste ændring, der løser problemet, og vis diffen.
- Ændr ikke Makefile.
- Tilføj ingen nye afhængigheder uden at spørge.

## Sikkerhed
- Læs, vis eller commit aldrig .env, .env.local, .env.remote eller andre hemmeligheder.
- Commit og push ikke. Jeg reviewer og committer selv.

## Definition of done
- `make obs-check-devices` og `make obs-check` er grønne.
- Efter en ændring skal du vente mindst 2 minutter, før `make obs-check-devices` kan blive grøn.
- Rapportér kommandoerne og deres output. Påstå ikke, at noget virker, uden at have kørt det.
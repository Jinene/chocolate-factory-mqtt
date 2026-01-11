# Chocolate Factory MQTT (Factory → Data Center) Reference Project

This repository demonstrates a professional MQTT topic/QoS design for an industrial chocolate factory
producing **white**, **milk**, and **dark** chocolate across an **8-step production process**.

## Architecture
- Factory machines publish telemetry, state, alarms, batch events, and quality results via MQTT.
- A data center consumer subscribes and stores messages in SQLite for traceability and monitoring.

## Topic Namespace
`factory/<site>/<line>/<step>/<machine>/<message_type>`

Example:
- `factory/tunis-01/line-a/s5_tempering/temper-01/telemetry`
- `factory/tunis-01/line-a/s8_packaging/packer-03/quality`

## QoS Policy
- telemetry: QoS 0
- state: QoS 1 (retained)
- alarm: QoS 1
- quality: QoS 1
- batch: QoS 1

## Quick Start

### 1) Start MQTT broker
```bash
docker compose up -d
2) Create a Python venv + install deps
bash
Copier le code
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
3) Run data center subscriber (stores into SQLite)
bash
Copier le code
python -m src.datacenter.subscriber
4) Run factory simulation (publishes 8-step production)
bash
Copier le code
python -m src.factory_sim.simulate_line
Output
Console logs show ingested topics.

SQLite DB: datacenter_messages.db with table mqtt_messages.

Next Improvements (Production)
TLS + client certificates

per-machine ACLs

bridge local broker → cloud broker

schema validation + message versioning

metrics/exporter (Prometheus/Grafana)

yaml
Copier le code

---

## How this looks “industry professional”
- Clean topic hierarchy, consistent naming, minimal “magic”
- QoS is chosen by message criticality
- Uses retained state + LWT (classic industrial requirements)
- Data center side persists to a database (traceability)

If you want, I can also generate:
- an **EMQX** version (MQTT 5 features: user properties, session expiry, reason codes)
- a **Node-RED** flow for the data center dashboard
- a **bridge** example (factory broker → cloud broker) and security hardening (TLS + ACL)
::contentReference[oaicite:0]{index=0}

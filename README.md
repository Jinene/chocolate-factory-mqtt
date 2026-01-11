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

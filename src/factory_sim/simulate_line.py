from __future__ import annotations
import random
import time

from src.common.settings import SITE, LINE, STEPS, CHOCOLATE_TYPES, QOS_BY_TYPE, RETAIN_BY_TYPE
from src.common.topics import topic
from src.common.payloads import BatchContext, make_batch_id, telemetry_payload, state_payload, alarm_payload, quality_payload
from src.factory_sim.publisher import MqttPublisher

MACHINES_BY_STEP = {
    "s1_dosing":    ["weigher-01"],
    "s2_mixing":    ["mixer-02"],
    "s3_refining":  ["refiner-01"],
    "s4_conching":  ["conche-01"],
    "s5_tempering": ["temper-01"],
    "s6_molding":   ["molder-01"],
    "s7_cooling":   ["cooltunnel-01"],
    "s8_packaging": ["packer-03"],
}

def simulate_tags(step: str) -> dict:
    # A few realistic examples (extend as needed)
    if step == "s1_dosing":
        return {"weight_kg": round(random.uniform(10.0, 50.0), 2), "scale_status": "OK"}
    if step == "s2_mixing":
        return {"rpm": round(random.uniform(40, 120), 1), "motor_current_a": round(random.uniform(5, 20), 2)}
    if step == "s3_refining":
        return {"particle_size_um": round(random.uniform(15, 35), 1), "roller_temp_c": round(random.uniform(30, 55), 1)}
    if step == "s4_conching":
        return {"temp_c": round(random.uniform(45, 80), 1), "humidity_pct": round(random.uniform(20, 45), 1)}
    if step == "s5_tempering":
        return {"temp_c": round(random.uniform(30, 33.5), 2), "viscosity_cP": round(random.uniform(3500, 5200), 0)}
    if step == "s6_molding":
        return {"deposit_g": round(random.uniform(95, 105), 2), "nozzle_pressure_bar": round(random.uniform(1.0, 2.5), 2)}
    if step == "s7_cooling":
        return {"tunnel_temp_c": round(random.uniform(6, 12), 1), "belt_speed_mpm": round(random.uniform(4, 9), 2)}
    if step == "s8_packaging":
        return {"packs_per_min": int(random.uniform(40, 120)), "reject_rate_pct": round(random.uniform(0.0, 1.5), 2)}
    return {}

def main() -> None:
    product_type = random.choice(CHOCOLATE_TYPES)
    ctx = BatchContext(product_type=product_type, batch_id=make_batch_id(product_type))

    machine_for_lwt = "edge-gw-01"
    lwt_topic = topic(SITE, LINE, "s0_edge", machine_for_lwt, "state")
    publisher = MqttPublisher(
        client_id=f"factory-sim-{SITE}-{LINE}",
        lwt_topic=lwt_topic,
        lwt_payload={"ts": "unknown", "state": "OFFLINE"},
    )
    publisher.connect()

    # Publish ONLINE state (retained)
    publisher.publish(
        lwt_topic,
        {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "state": "ONLINE"},
        qos=QOS_BY_TYPE["state"],
        retain=True,
    )

    # Batch start event (QoS 1)
    batch_topic = topic(SITE, LINE, "s0_batch", "line-controller", "batch")
    publisher.publish(
        batch_topic,
        {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": "BATCH_START", "product_type": ctx.product_type, "batch_id": ctx.batch_id},
        qos=QOS_BY_TYPE["batch"],
        retain=RETAIN_BY_TYPE["batch"],
    )

    # Run through 8 steps
    for step in STEPS:
        for machine in MACHINES_BY_STEP[step]:
            # State = RUNNING (retained)
            st_topic = topic(SITE, LINE, step, machine, "state")
            publisher.publish(
                st_topic,
                state_payload(ctx, state="RUNNING"),
                qos=QOS_BY_TYPE["state"],
                retain=RETAIN_BY_TYPE["state"],
            )

            # Telemetry burst (QoS 0)
            tel_topic = topic(SITE, LINE, step, machine, "telemetry")
            for _ in range(5):
                publisher.publish(
                    tel_topic,
                    telemetry_payload(ctx, simulate_tags(step)),
                    qos=QOS_BY_TYPE["telemetry"],
                    retain=RETAIN_BY_TYPE["telemetry"],
                )
                time.sleep(0.3)

            # Example: tempering alarm condition sometimes
            if step == "s5_tempering":
                last_temp = simulate_tags(step)["temp_c"]
                if last_temp > 33.0:
                    al_topic = topic(SITE, LINE, step, machine, "alarm")
                    publisher.publish(
                        al_topic,
                        alarm_payload(ctx, severity="HIGH", code="TEMP_OUT_OF_RANGE",
                                     message="Tempering temperature exceeded max limit",
                                     value=last_temp, limit=33.0),
                        qos=QOS_BY_TYPE["alarm"],
                        retain=RETAIN_BY_TYPE["alarm"],
                    )

            # Packaging quality message (QoS 1)
            if step == "s8_packaging":
                q_topic = topic(SITE, LINE, step, machine, "quality")
                publisher.publish(
                    q_topic,
                    quality_payload(ctx, results={
                        "weight_g": round(random.uniform(98.5, 101.5), 2),
                        "seal_integrity": "PASS",
                        "label_check": "PASS",
                        "defect_rate_pct": round(random.uniform(0.0, 1.0), 2),
                    }),
                    qos=QOS_BY_TYPE["quality"],
                    retain=RETAIN_BY_TYPE["quality"],
                )

            # State = IDLE (retained)
            publisher.publish(
                st_topic,
                state_payload(ctx, state="IDLE"),
                qos=QOS_BY_TYPE["state"],
                retain=RETAIN_BY_TYPE["state"],
            )

    # Batch end event
    publisher.publish(
        batch_topic,
        {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": "BATCH_END", "product_type": ctx.product_type, "batch_id": ctx.batch_id},
        qos=QOS_BY_TYPE["batch"],
        retain=False,
    )

    publisher.close()

if __name__ == "__main__":
    main()


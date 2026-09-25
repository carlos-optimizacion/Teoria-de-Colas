"""Simulación de eventos discretos para Decision Lab.

El motor trabaja en minutos y complementa, no reemplaza, los modelos analíticos.
Permite colas M/M/s, capacidad total finita y una aproximación Gamma para M/G/1
calibrada con media y coeficiente de variación.
"""

from collections import deque
from heapq import heappop, heappush
from random import Random
from statistics import mean


def _sample(rng, mean_value, distribution="exponential", cv=1.0):
    if distribution == "deterministic":
        return mean_value
    if distribution == "gamma":
        if cv <= 0:
            return mean_value
        shape = 1.0 / (cv * cv)
        scale = mean_value / shape
        return rng.gammavariate(shape, scale)
    return rng.expovariate(1.0 / mean_value)


def _single_queue(
    t_llegada_min,
    t_atencion_min,
    servers,
    horizon_min,
    seed,
    capacity=None,
    arrival_distribution="exponential",
    service_distribution="exponential",
    service_cv=1.0,
):
    if t_llegada_min <= 0 or t_atencion_min <= 0 or servers < 1 or horizon_min <= 0:
        raise ValueError("Parámetros de simulación inválidos.")
    if capacity is not None and capacity < servers:
        raise ValueError("La capacidad total K debe ser mayor o igual a s.")

    rng = Random(seed)
    events = []
    first = _sample(rng, t_llegada_min, arrival_distribution)
    heappush(events, (first, 0, "arrival", None))

    queue = deque()
    busy = 0
    arrivals = admitted = blocked = started = waited = completed = 0
    total_wait = total_system = 0.0
    area_queue = area_busy = 0.0
    last_area_time = 0.0
    sequence = 1
    series = [(0.0, 0)]

    while events:
        time, _, kind, customer_arrival = heappop(events)
        clipped = min(time, horizon_min)
        if clipped > last_area_time:
            dt = clipped - last_area_time
            area_queue += len(queue) * dt
            area_busy += busy * dt
            last_area_time = clipped

        if kind == "arrival":
            if time > horizon_min:
                continue
            arrivals += 1
            next_arrival = time + _sample(rng, t_llegada_min, arrival_distribution)
            if next_arrival <= horizon_min:
                sequence += 1
                heappush(events, (next_arrival, sequence, "arrival", None))

            system_count = busy + len(queue)
            if capacity is not None and system_count >= capacity:
                blocked += 1
                series.append((time, len(queue)))
                continue

            admitted += 1
            if busy < servers:
                busy += 1
                started += 1
                service = _sample(rng, t_atencion_min, service_distribution, service_cv)
                sequence += 1
                heappush(events, (time + service, sequence, "departure", time))
            else:
                queue.append(time)
            series.append((time, len(queue)))

        else:
            completed += 1
            total_system += time - customer_arrival
            if queue:
                queued_arrival = queue.popleft()
                wait = time - queued_arrival
                total_wait += wait
                waited += 1
                started += 1
                service = _sample(rng, t_atencion_min, service_distribution, service_cv)
                sequence += 1
                heappush(events, (time + service, sequence, "departure", queued_arrival))
            else:
                busy -= 1
            if time <= horizon_min:
                series.append((time, len(queue)))

    if last_area_time < horizon_min:
        dt = horizon_min - last_area_time
        area_queue += len(queue) * dt
        area_busy += busy * dt

    started_den = max(started, 1)
    completed_den = max(completed, 1)
    admitted_den = max(admitted, 1)
    arrivals_den = max(arrivals, 1)
    return {
        "arrivals": arrivals,
        "admitted": admitted,
        "blocked": blocked,
        "completed": completed,
        "wq_min": total_wait / started_den,
        "w_min": total_system / completed_den,
        "lq": area_queue / horizon_min,
        "utilization": area_busy / (servers * horizon_min),
        "p_wait": waited / admitted_den,
        "p_block": blocked / arrivals_den,
        "effective_rate": admitted / (horizon_min / 60.0),
        "queue_series": [{"t": round(t, 3), "q": q} for t, q in series if t <= horizon_min],
    }


def simulate_queue(
    t_llegada_min,
    t_atencion_min,
    servers,
    horizon_min=480.0,
    replications=30,
    seed=2026,
    capacity=None,
    arrival_distribution="exponential",
    service_distribution="exponential",
    service_cv=1.0,
):
    replications = max(1, min(int(replications), 200))
    runs = [
        _single_queue(
            t_llegada_min,
            t_atencion_min,
            servers,
            horizon_min,
            seed + i,
            capacity=capacity,
            arrival_distribution=arrival_distribution,
            service_distribution=service_distribution,
            service_cv=service_cv,
        )
        for i in range(replications)
    ]
    return {
        "replications": replications,
        "horizon_min": horizon_min,
        "arrivals": round(mean(r["arrivals"] for r in runs), 2),
        "admitted": round(mean(r["admitted"] for r in runs), 2),
        "blocked": round(mean(r["blocked"] for r in runs), 2),
        "completed": round(mean(r["completed"] for r in runs), 2),
        "wq_min": mean(r["wq_min"] for r in runs),
        "w_min": mean(r["w_min"] for r in runs),
        "lq": mean(r["lq"] for r in runs),
        "utilization": mean(r["utilization"] for r in runs),
        "p_wait": mean(r["p_wait"] for r in runs),
        "p_block": mean(r["p_block"] for r in runs),
        "effective_rate": mean(r["effective_rate"] for r in runs),
        "queue_series": runs[0]["queue_series"],
    }


def simulate_mms(t_llegada_min, t_atencion_min, servers, horizon_min=480.0, replications=30, seed=2026):
    return simulate_queue(
        t_llegada_min,
        t_atencion_min,
        servers,
        horizon_min=horizon_min,
        replications=replications,
        seed=seed,
    )

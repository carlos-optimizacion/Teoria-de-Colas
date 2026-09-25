"""Motor de simulación de eventos discretos para Decision Lab.

La simulación complementa, no reemplaza, el modelo analítico. Trabaja en minutos.
"""

from collections import deque
from heapq import heappop, heappush
from random import Random
from statistics import mean


def _single_mm_s(t_llegada_min, t_atencion_min, servers, horizon_min, seed):
    if t_llegada_min <= 0 or t_atencion_min <= 0 or servers < 1 or horizon_min <= 0:
        raise ValueError("Parámetros de simulación inválidos.")

    rng = Random(seed)
    events = []
    first = rng.expovariate(1.0 / t_llegada_min)
    heappush(events, (first, 0, "arrival", None))

    queue = deque()
    busy = 0
    arrivals = waited = completed = 0
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
            next_arrival = time + rng.expovariate(1.0 / t_llegada_min)
            if next_arrival <= horizon_min:
                sequence += 1
                heappush(events, (next_arrival, sequence, "arrival", None))

            if busy < servers:
                busy += 1
                service = rng.expovariate(1.0 / t_atencion_min)
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
                service = rng.expovariate(1.0 / t_atencion_min)
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

    denominator = max(arrivals, 1)
    return {
        "arrivals": arrivals,
        "completed": completed,
        "wq_min": total_wait / denominator,
        "w_min": total_system / denominator,
        "lq": area_queue / horizon_min,
        "utilization": area_busy / (servers * horizon_min),
        "p_wait": waited / denominator,
        "queue_series": [{"t": round(t, 3), "q": q} for t, q in series if t <= horizon_min],
    }


def simulate_mms(t_llegada_min, t_atencion_min, servers, horizon_min=480.0, replications=30, seed=2026):
    replications = max(1, min(int(replications), 200))
    runs = [
        _single_mm_s(t_llegada_min, t_atencion_min, servers, horizon_min, seed + i)
        for i in range(replications)
    ]
    return {
        "replications": replications,
        "horizon_min": horizon_min,
        "arrivals": round(mean(r["arrivals"] for r in runs), 2),
        "completed": round(mean(r["completed"] for r in runs), 2),
        "wq_min": mean(r["wq_min"] for r in runs),
        "w_min": mean(r["w_min"] for r in runs),
        "lq": mean(r["lq"] for r in runs),
        "utilization": mean(r["utilization"] for r in runs),
        "p_wait": mean(r["p_wait"] for r in runs),
        "queue_series": runs[0]["queue_series"],
    }

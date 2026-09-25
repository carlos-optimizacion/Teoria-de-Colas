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


def simulate_visual_mms(
    t_llegada_min,
    t_atencion_min,
    servers,
    horizon_min=60.0,
    seed=2026,
    max_frames=1200,
):
    """Genera una línea de tiempo visual reproducible para un sistema M/M/s.

    La llegada y el tiempo de servicio de cada cliente se generan con flujos
    aleatorios separados. Así dos configuraciones con distinto número de
    servidores pueden compararse usando la misma secuencia base de clientes y
    servicios, lo que hace la animación actual vs. propuesta más consistente.
    """
    if t_llegada_min <= 0 or t_atencion_min <= 0 or servers < 1 or horizon_min <= 0:
        raise ValueError("Parámetros de simulación visual inválidos.")

    arrivals_rng = Random(seed)
    service_rng = Random(seed + 100_003)
    event_heap = []
    order = 0
    next_customer = 0
    first_arrival = arrivals_rng.expovariate(1.0 / t_llegada_min)
    heappush(event_heap, (first_arrival, order, "arrival", None, None))

    queue = deque()
    server_customer = [None] * servers
    customer_service = {}
    customer_arrival = {}
    frames = []
    arrivals = completed = waited = 0
    max_queue = 0
    total_wait = 0.0
    busy_area = 0.0
    queue_area = 0.0
    last_time = 0.0
    truncated = False

    def snapshot(time, kind, customer=None, server=None, started_customer=None):
        nonlocal truncated
        if len(frames) >= max_frames:
            truncated = True
            return
        frames.append({
            "time": round(time, 3),
            "kind": kind,
            "customer": customer,
            "server": server,
            "started_customer": started_customer,
            "queue": list(queue),
            "servers": list(server_customer),
            "arrivals": arrivals,
            "completed": completed,
            "queue_length": len(queue),
            "max_queue": max_queue,
        })

    snapshot(0.0, "start")

    while event_heap:
        time, _, kind, customer, server_idx = heappop(event_heap)
        if time > horizon_min:
            break

        dt = time - last_time
        if dt > 0:
            queue_area += len(queue) * dt
            busy_area += sum(c is not None for c in server_customer) * dt
            last_time = time

        if kind == "arrival":
            next_customer += 1
            customer = next_customer
            arrivals += 1
            customer_arrival[customer] = time
            customer_service[customer] = service_rng.expovariate(1.0 / t_atencion_min)

            next_arrival = time + arrivals_rng.expovariate(1.0 / t_llegada_min)
            if next_arrival <= horizon_min:
                order += 1
                heappush(event_heap, (next_arrival, order, "arrival", None, None))

            try:
                free_idx = server_customer.index(None)
            except ValueError:
                free_idx = None

            if free_idx is None:
                queue.append(customer)
                waited += 1
                max_queue = max(max_queue, len(queue))
                snapshot(time, "arrival_queue", customer=customer)
            else:
                server_customer[free_idx] = customer
                order += 1
                heappush(
                    event_heap,
                    (time + customer_service[customer], order, "departure", customer, free_idx),
                )
                snapshot(time, "arrival_service", customer=customer, server=free_idx + 1)

        else:
            completed += 1
            server_customer[server_idx] = None
            started_customer = None
            if queue:
                started_customer = queue.popleft()
                wait = time - customer_arrival[started_customer]
                total_wait += wait
                server_customer[server_idx] = started_customer
                order += 1
                heappush(
                    event_heap,
                    (
                        time + customer_service[started_customer],
                        order,
                        "departure",
                        started_customer,
                        server_idx,
                    ),
                )
            snapshot(
                time,
                "departure",
                customer=customer,
                server=server_idx + 1,
                started_customer=started_customer,
            )

    if last_time < horizon_min:
        dt = horizon_min - last_time
        queue_area += len(queue) * dt
        busy_area += sum(c is not None for c in server_customer) * dt

    snapshot(horizon_min, "end")
    return {
        "servers_count": servers,
        "horizon_min": horizon_min,
        "seed": seed,
        "arrivals": arrivals,
        "completed": completed,
        "waiting_customers": waited,
        "max_queue": max_queue,
        "avg_queue": queue_area / horizon_min,
        "utilization": busy_area / (servers * horizon_min),
        "avg_wait_started": total_wait / max(waited, 1),
        "frames": frames,
        "truncated": truncated,
    }

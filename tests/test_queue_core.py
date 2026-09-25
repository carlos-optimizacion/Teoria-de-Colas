import math

import pytest

from queue_core import (
    dd1_sequence,
    economic_cost,
    evaluate_mms_capacity,
    mg1_from_minutes,
    mms,
    mms_from_minutes,
    mmsk,
    probability_wait_over,
    rates_from_minutes,
    recommend_mms_capacity,
)


def test_rates_from_minutes():
    lam, mu = rates_from_minutes(30, 20)
    assert lam == pytest.approx(2.0)
    assert mu == pytest.approx(3.0)


def test_mm1_known_case():
    # λ=2/h, μ=3/h -> ρ=2/3, L=2, Lq=4/3, W=1 h, Wq=2/3 h
    r = mms(2.0, 3.0, 1)
    assert r["estable"] is True
    assert r["rho"] == pytest.approx(2 / 3)
    assert r["L"] == pytest.approx(2.0)
    assert r["Lq"] == pytest.approx(4 / 3)
    assert r["W"] == pytest.approx(1.0)
    assert r["Wq"] == pytest.approx(2 / 3)
    assert r["P_espera"] == pytest.approx(2 / 3)


def test_mms_erlang_c_known_case():
    # λ=4/h, μ=3/h, s=2
    r = mms(4.0, 3.0, 2)
    assert r["estable"] is True
    assert r["rho"] == pytest.approx(2 / 3)
    assert r["P_espera"] == pytest.approx(0.5333333333)
    assert r["Lq"] == pytest.approx(1.0666666667)
    assert r["Wq"] == pytest.approx(0.2666666667)
    assert r["W"] == pytest.approx(0.6)


def test_mms_unstable_case_reports_infinite_congestion():
    r = mms(6.0, 3.0, 2)
    assert r["estable"] is False
    assert r["rho"] == pytest.approx(1.0)
    assert math.isinf(r["Lq"])
    assert math.isinf(r["Wq"])


def test_probability_wait_over_zero_equals_erlang_c():
    r = mms(4.0, 3.0, 2)
    assert probability_wait_over(r, 0) == pytest.approx(r["P_espera"])


def test_probability_wait_over_decreases_with_threshold():
    r = mms_from_minutes(15, 20, 2)
    p0 = probability_wait_over(r, 0)
    p5 = probability_wait_over(r, 5)
    p10 = probability_wait_over(r, 10)
    assert p0 > p5 > p10 >= 0


def test_mmsk_probabilities_sum_to_one_and_flow_is_consistent():
    r = mmsk(8.0, 5.0, 2, 5)
    assert sum(r["probs"]) == pytest.approx(1.0)
    assert 0 <= r["P_bloqueo"] <= 1
    assert r["lambda_efectiva"] == pytest.approx(8.0 * (1 - r["P_bloqueo"]))
    assert r["L"] == pytest.approx(r["lambda_efectiva"] * r["W"])


def test_mg1_reduces_wait_when_service_variability_falls():
    alto = mg1_from_minutes(6, 4, 1.0)
    bajo = mg1_from_minutes(6, 4, 0.5)
    assert alto["estable"] and bajo["estable"]
    assert bajo["Wq"] < alto["Wq"]
    assert bajo["rho"] == pytest.approx(alto["rho"])


def test_economic_cost_unstable_is_not_zero_waiting_cost():
    r = mms(6.0, 3.0, 2)
    c = economic_cost(r, 2, 20.0, 12.0)
    assert math.isinf(c["espera"])
    assert math.isinf(c["total"])


def test_dd1_without_queue_when_service_is_faster_than_arrivals():
    rows = dd1_sequence(10, 8, n=8)
    assert all(row["Espera (min)"] == pytest.approx(0.0) for row in rows)


def test_capacity_evaluation_and_recommendation():
    escenarios = evaluate_mms_capacity(
        t_llegada_min=4,
        t_atencion_min=6,
        max_servers=8,
        costo_operador_h=20,
        costo_espera_cliente_h=12,
        meta_wq_min=5,
    )
    assert len(escenarios) == 8
    assert any(e["meets_service"] for e in escenarios)

    escenarios2, rec = recommend_mms_capacity(
        t_llegada_min=4,
        t_atencion_min=6,
        max_servers=8,
        costo_operador_h=20,
        costo_espera_cliente_h=12,
        meta_wq_min=5,
    )
    assert escenarios2 == escenarios
    assert rec["meets_service"] is True
    assert rec["cost_total"] == min(
        e["cost_total"] for e in escenarios if e["meets_service"]
    )


@pytest.mark.parametrize(
    "args",
    [
        (0, 5),
        (-1, 5),
        (5, 0),
    ],
)
def test_invalid_times_raise(args):
    with pytest.raises(ValueError):
        rates_from_minutes(*args)

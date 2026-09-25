import math

from interpretation_core import (
    interpret_dd1,
    interpret_economic,
    interpret_erlang_b,
    interpret_mg1,
    interpret_mm1,
    interpret_mms,
    interpret_mmsk,
    to_markdown,
)
from queue_core import mms, mms_from_minutes, mmsk


def test_mm1_interpretation_stable_contains_operational_language():
    r = mms(10.0, 15.0, 1)
    lectura = interpret_mm1(r)
    assert "cada 100" in lectura["que_pasa"]
    assert "holgura" in lectura["por_que"]
    assert "promedio" in lectura["operacion"]


def test_mm1_interpretation_unstable_prioritizes_capacity():
    r = mms(15.0, 10.0, 1)
    lectura = interpret_mm1(r)
    assert "no alcanza un estado estable" in lectura["que_pasa"]
    assert "capacidad insuficiente" in lectura["operacion"]


def test_mms_interpretation_reads_probability_and_wait_jointly():
    r = mms_from_minutes(10.0, 15.0, 2)
    lectura = interpret_mms(r, 2)
    assert "todos los servidores ocupados" in lectura["que_pasa"]
    assert "P(espera)" in lectura["operacion"]


def test_mmsk_interpretation_explains_space_vs_service_capacity():
    r = mmsk(10.0, 6.0, 2, 5)
    lectura = interpret_mmsk(r)
    assert "no ingresan" in lectura["que_pasa"]
    assert "Aumentar K agrega espacio" in lectura["accion"]


def test_erlang_b_interpretation_has_no_queue_message():
    r = {"B": 0.08, "lambda_eff": 9.2, "ocupacion": 0.72}
    lectura = interpret_erlang_b(r, 4)
    assert "No existe cola" in lectura["que_pasa"]
    assert "pérdida de demanda" in lectura["aprendizaje"]


def test_mg1_interpretation_accepts_minutes_explicitly():
    r = {"estable": True, "rho": 0.7, "Wq": 6.5}
    lectura = interpret_mg1(r, 1.4, time_unit="minutes")
    assert "6.5 min" in lectura["que_pasa"]
    assert "variabilidad" in lectura["operacion"]


def test_dd1_interpretation_distinguishes_balanced_and_overloaded():
    ok = interpret_dd1(5.0, 4.0, 0.0, 0.0)
    bad = interpret_dd1(5.0, 6.0, 3.0, 6.0)
    assert "no se acumula cola" in ok["que_pasa"]
    assert "crece de forma acumulativa" in bad["por_que"]


def test_economic_interpretation_explains_marginal_tradeoff():
    lectura = interpret_economic(60.0, 20.0, 80.0, 3, 4.0)
    assert "S/ 80.00/h" in lectura["que_pasa"]
    assert "mínimo económico" in lectura["operacion"]


def test_markdown_contains_five_learning_questions():
    lectura = {
        "que_pasa": "a",
        "por_que": "b",
        "operacion": "c",
        "accion": "d",
        "aprendizaje": "e",
    }
    text = to_markdown(lectura)
    assert "¿Qué está pasando?" in text
    assert "¿Por qué ocurre?" in text
    assert "¿Qué significa operativamente?" in text
    assert "¿Qué podrías cambiar?" in text
    assert "¿Qué debes aprender" in text

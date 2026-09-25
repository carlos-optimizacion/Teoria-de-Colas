from interpretation_core import marginal_mms_analysis, marginal_mms_markdown


def test_marginal_detects_instability_with_one_less_server():
    data = marginal_mms_analysis(4.0, 6.0, 2)
    rows = {row["s"]: row for row in data["rows"]}

    assert rows[1]["estable"] is False
    assert rows[2]["estable"] is True
    assert rows[3]["estable"] is True
    assert "inestable" in data["insight"].lower()


def test_marginal_extra_server_reduces_wait():
    data = marginal_mms_analysis(6.0, 4.0, 2)
    rows = {row["s"]: row for row in data["rows"]}

    assert rows[3]["wq_min"] < rows[2]["wq_min"]
    assert "ganancia marginal" in data["insight"].lower()


def test_marginal_markdown_keeps_technical_metrics_visible():
    text = marginal_mms_markdown(6.0, 4.0, 2)

    assert "Utilización" in text
    assert "P(espera)" in text
    assert "Wq" in text
    assert "Lq" in text
    assert "Lectura marginal" in text

"""Topes y registro anónimo (backend/registro.py). Sin modelos: corre en segundos.

Uso: .venv/bin/python -m pytest tests/
"""

import sqlite3

import pytest

from backend import registro
from backend.registro import Registro, limpiar


@pytest.fixture
def reg(tmp_path, monkeypatch):
    monkeypatch.setitem(registro.CONF, "preguntas_por_persona_por_dia", 3)
    monkeypatch.setitem(registro.CONF, "usd_por_dia", 0.05)
    return Registro(tmp_path / "a.sqlite3")


def test_tope_por_persona_no_afecta_a_otra(reg):
    assert [reg.admitir("1.1.1.1") for _ in range(4)] == [None, None, None, "persona"]
    assert reg.admitir("2.2.2.2") is None


def test_tope_global_por_gasto(reg, capsys):
    reg.anotar("¿Cuánto cuesta?", 1, ["S1"], respuesta="Cuesta X [S1].", uso={"usd": 0.06})
    assert reg.admitir("3.3.3.3") == "global"
    assert reg.admitir("4.4.4.4") == "global"
    assert capsys.readouterr().out.count("AVISO") == 1      # el aviso sale una sola vez por día


def test_no_guarda_la_direccion_ni_datos_personales(reg, tmp_path):
    reg.admitir("10.20.30.40")
    reg.anotar("Soy ana@mail.com, DNI 30.123.456, cel +54 11 2345-6789", 1, [])
    db = sqlite3.connect(tmp_path / "a.sqlite3")
    volcado = "\n".join(db.iterdump())
    assert "10.20.30.40" not in volcado
    assert "ana@mail.com" not in volcado and "30.123.456" not in volcado and "2345-6789" not in volcado


def test_limpiar_respeta_montos_cortos_y_anios():
    assert limpiar("¿Sale 2026 o 2027? ¿Son 8 cuotas?") == "¿Sale 2026 o 2027? ¿Son 8 cuotas?"
    assert limpiar("mi tel 1123953895") == "mi tel [número]"


def test_marca_cuando_deriva_al_contacto(reg, tmp_path):
    reg.anotar("¿Hay becas?", 1, [], respuesta="Ese dato no lo tengo a mano: escribinos a licdia@unlu.edu.ar.")
    reg.anotar("¿Cuánto dura?", 1, [], respuesta="Dura un año [S3].")
    db = sqlite3.connect(tmp_path / "a.sqlite3")
    assert db.execute("SELECT deriva FROM preguntas ORDER BY id").fetchall() == [(1,), (0,)]


def test_opinion_se_liga_a_la_pregunta_y_limpia_el_comentario(reg, tmp_path):
    reg.anotar("¿Hay becas?", 1, [], respuesta="No lo tengo a mano.", clave="clave-de-prueba")
    assert reg.opinar("clave-de-prueba", -1, "faltaba lo de becas, llamame al 1123456789")
    assert reg.opinar("clave-de-prueba", 1)                  # se puede cambiar de opinión
    assert not reg.opinar("otra-clave-cualquiera", 1)
    reg.opinar("clave-de-prueba", -1, "faltaba lo de becas, llamame al 1123456789")
    db = sqlite3.connect(tmp_path / "a.sqlite3")
    voto, comentario = db.execute("SELECT voto, comentario FROM preguntas").fetchone()
    assert (voto, comentario) == (-1, "faltaba lo de becas, llamame al [número]")

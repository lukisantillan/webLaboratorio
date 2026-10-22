"""Qué le preguntan al asistente: resumen del registro anónimo de preguntas (backend/registro.py).

Uso, en la VM (o en local, con la base de ../datos/):
    .venv/bin/python -m backend.consultas [--dias 7] [--db RUTA]
    .venv/bin/python -m backend.consultas --csv > preguntas.csv
Desde la Mac, con la VPN: bash despliegue/preguntas.sh [--dias 30] [--csv]

Muestra, por día, preguntas, bloqueos por tope, errores, gasto y aprovechamiento de la caché; las opiniones (las
respuestas que no sirvieron, con su comentario); las preguntas en las que el asistente derivó al contacto (indicio de
que el sitio no tenía el dato), las secciones más usadas y las últimas preguntas. Abre la base en solo lectura.
"""

import argparse
import collections
import csv
import json
import os
import pathlib
import sqlite3
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    carpeta = pathlib.Path(os.environ.get("STATE_DIRECTORY") or RAIZ / "datos")
    ap.add_argument("--db", default=carpeta / "asistente.sqlite3")
    ap.add_argument("--dias", type=int, default=7)
    ap.add_argument("--csv", action="store_true", help="todas las preguntas del período en CSV, por la salida estándar")
    a = ap.parse_args()
    db = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    filas = db.execute("SELECT * FROM preguntas WHERE momento >= date('now', 'localtime', ?) ORDER BY id",
                       (f"-{a.dias - 1} days",)).fetchall()

    if a.csv:
        w = csv.writer(sys.stdout)
        w.writerow(filas[0].keys() if filas else ["momento", "pregunta"])
        w.writerows([tuple(f) for f in filas])
        return

    print(f"Últimos {a.dias} días: {len(filas)} preguntas\n")
    print(f"{'día':<11}{'preg.':>6}{'topes':>6}{'error':>6}{'deriva':>7}{'USD':>8}{'caché':>7}")
    por_dia = collections.defaultdict(list)
    for f in filas:
        por_dia[f["momento"][:10]].append(f)
    for dia, fs in sorted(por_dia.items()):
        entrada = sum((f["tokens_entrada"] or 0) + (f["tokens_cache_escritura"] or 0) for f in fs)
        cache = sum(f["tokens_cache_lectura"] or 0 for f in fs)
        print(f"{dia:<11}{len(fs):>6}{sum(bool(f['bloqueo']) for f in fs):>6}{sum(bool(f['error']) for f in fs):>6}"
              f"{sum(f['deriva'] or 0 for f in fs):>7}{sum(f['usd'] or 0 for f in fs):>8.3f}"
              f"{cache / (entrada + cache) if entrada + cache else 0:>7.0%}")

    votos = [f for f in filas if f["voto"]]
    if votos:
        utiles = sum(f["voto"] > 0 for f in votos)
        print(f"\nOpiniones: {utiles} útiles, {len(votos) - utiles} no sirvieron")
        for f in [f for f in votos if f["voto"] < 0][-25:]:
            print(f"  👎 {f['momento']}  {f['pregunta']}" + (f"  → {f['comentario']}" if f["comentario"] else ""))

    derivadas = collections.Counter(f["pregunta"].strip().lower() for f in filas if f["deriva"])
    if derivadas:
        print("\nDerivó al contacto (¿falta el dato en el sitio?), de la más repetida a la menos:")
        for q, n in derivadas.most_common(25):
            print(f"  {n:>3} × {q}")

    usos = collections.Counter(s for f in filas for s in json.loads(f["secciones"]))
    if usos:
        print("\nSecciones más recuperadas: " + ", ".join(f"{s} ({n})" for s, n in usos.most_common(10)))

    print("\nÚltimas preguntas:")
    for f in filas[-20:]:
        marca = f" [{f['bloqueo'] or f['error']}]" if f["bloqueo"] or f["error"] else ""
        print(f"  {f['momento']}  {f['pregunta']}{marca}")


if __name__ == "__main__":
    main()

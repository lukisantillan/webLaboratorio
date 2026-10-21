"""Evaluación de la recuperación: para cada pregunta de prueba, si las secciones esperadas quedan entre las K que
recibe el modelo (con la misma lógica del backend: casi duplicados y cupos por parte en preguntas compuestas).

Uso: .venv/bin/python ingesta/evaluar.py
"""

import json
import pathlib
import re

import numpy as np
from sentence_transformers import SentenceTransformer

RAIZ = pathlib.Path(__file__).resolve().parents[1]
K, POR_PARTE, CASI_IGUAL = 6, 2, 0.92
COMPUESTA = re.compile(r"\s+y\s+(?=(?:c[oó]mo|cu[aá]nto|cu[aá]ndo|d[oó]nde|qu[eé]|qui[eé]n|cu[aá]l|hay|puedo|necesito|se)\b)",
                       re.IGNORECASE)
# (pregunta, requisitos): cada requisito es una lista de alternativas de título; tienen que cumplirse todos
PRUEBAS = [
    ("¿Cuánto cuesta?", [["Estructura de aranceles"]]),
    ("¿Necesito saber programar?", [["conocimientos previos", "Sirve si no vengo", "pre-requisitos"]]),
    ("¿Qué voy a construir?", [["Lo que vas a construir"]]),
    ("¿Cuándo empieza la próxima cohorte?", [["Cuándo empieza", "Cohorte 2027"]]),
    ("¿Quiénes son los docentes?", [["Quiénes son los docentes", "Cuerpo docente"]]),
    ("¿Qué título otorga?", [["Qué título otorga"]]),
    ("¿El título tiene validez nacional?", [["validez nacional"]]),
    ("¿Cuántas horas por semana hay que dedicarle?", [["carga horaria", "pre-requisitos"]]),
    ("¿Necesito una GPU?", [["computadora especial"]]),
    ("¿Cómo se paga?", [["Cómo pagar", "formas de pago"]]),
    ("¿Puedo cursar un módulo suelto?", [["módulos sueltos"]]),
    ("¿Hay un trabajo final?", [["trabajo final"]]),
    ("¿Cómo es la evaluación?", [["evaluación", "Evaluación"]]),
    ("¿Hay examen de ingreso?", [["examen de admisión"]]),
    ("¿Qué se ve en el módulo de IA generativa?", [["4 Inteligencia Artificial Generativa"]]),
    ("¿Qué herramientas y tecnologías usan?", [["Stack tecnologico"]]),
    ("¿Qué salida laboral tiene?", [["salida laboral", "Para qué te prepara"]]),
    ("¿Las clases quedan grabadas?", [["100% virtual"]]),
    ("¿Qué clases hay en octubre?", [["Cronograma clase por clase"]]),
    ("¿Qué requisitos de admisión piden?", [["Requisitos de admisión", "pre-requisitos"]]),
    ("¿Cuánto cuesta la diplomatura y cómo se paga?", [["Estructura de aranceles"], ["Cómo pagar", "formas de pago"]]),
    ("¿Cuál es el precio de la diplomatura?", [["Estructura de aranceles"]]),
    ("¿Cuánto sale?", [["Estructura de aranceles"]]),
    ("¿Me puedo inscribir ahora y cuándo empieza la próxima cohorte?", [["Cómo me inscribo", "Inscripción", "Cohorte 2027"], ["Cuándo empieza", "Cohorte 2027"]]),
    ("¿Qué título otorga y tiene validez nacional?", [["Qué título otorga"], ["validez nacional"]]),
    ("¿Qué voy a aprender y quiénes dan las clases?", [["Plan de estudios", "Lo que vas a construir", "Enfoque"], ["docentes", "Cuerpo docente"]]),
    ("¿Qué días y en qué horario son las clases?", [["Dias y Horarios", "100% virtual"]]),
    ("¿Cuánto dura la diplomatura?", [["Duración", "carga horaria"]]),
]


def main():
    S = json.loads((RAIZ / "indice" / "secciones.json").read_text(encoding="utf-8"))["secciones"]
    E = np.load(RAIZ / "indice" / "embeddings.npy")
    conf = json.loads((RAIZ / "indice" / "modelo.json").read_text(encoding="utf-8"))
    m = SentenceTransformer(conf["modelo"], device="cpu")

    def recuperar(q):
        partes = [x.strip(" ¿?") for x in COMPUESTA.split(q) if len(x.strip(" ¿?").split()) >= 2]
        cs = [q] + (partes if len(partes) > 1 else [])
        Sm = E @ m.encode([conf["prefijo_consulta"] + c for c in cs], normalize_embeddings=True).T
        top = []

        def sumar(orden, cupo):
            n = 0
            for i in orden:
                if len(top) >= K or n >= cupo:
                    return
                if all(float(E[i] @ E[j]) < CASI_IGUAL for j in top):
                    top.append(int(i))
                    n += 1
        for c in range(1, Sm.shape[1]):
            sumar(np.argsort(-Sm[:, c]), POR_PARTE)
        sumar(np.argsort(-Sm[:, 0]), K)
        return top

    fallos = []
    for q, reqs in PRUEBAS:
        titulos = [S[i]["titulo"] for i in recuperar(q)]
        if not all(any(any(a in t for a in alt) for t in titulos) for alt in reqs):
            fallos.append((q, [t[:34] for t in titulos]))
    print(f"{len(PRUEBAS) - len(fallos)}/{len(PRUEBAS)} preguntas con todas sus secciones entre las {K} recuperadas")
    for f in fallos:
        print("  falla:", f)


if __name__ == "__main__":
    main()

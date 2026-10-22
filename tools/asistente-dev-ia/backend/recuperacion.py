"""Recuperación de secciones: la usan el backend (backend/app.py) y la evaluación (ingesta/evaluar.py).

Vive en un solo lugar para que la evaluación mida exactamente lo que corre en producción. No calcula embeddings:
recibe los vectores ya normalizados, así cada lado usa su propia instancia del modelo.
"""

import re

import numpy as np

K = 6                      # secciones que recibe el modelo
CASI_IGUAL = 0.92          # dos secciones más parecidas que esto entre sí cuentan como una (portada y subpágina)
POR_PARTE = 2              # lugares garantizados para cada parte de una pregunta compuesta

# " y " seguido de otra pregunta: "… y cómo …", "… y cuándo …", "… y hay …"
COMPUESTA = re.compile(r"\s+y\s+(?=(?:c[oó]mo|cu[aá]nto|cu[aá]ndo|d[oó]nde|qu[eé]|qui[eé]n|cu[aá]l|hay|puedo|necesito|se)\b)",  # noqa: E501
                       re.IGNORECASE)


def consultas_de(consulta: str) -> list[str]:
    """La consulta entera y, si es compuesta ("¿cuánto cuesta y cómo se paga?"), cada una de sus partes."""
    partes = [x.strip(" ¿?") for x in COMPUESTA.split(consulta) if len(x.strip(" ¿?").split()) >= 2]
    return [consulta] + (partes if len(partes) > 1 else [])


def recuperar(E: np.ndarray, V: np.ndarray) -> tuple[list[int], np.ndarray]:
    """Índices de las K secciones para el modelo y la similitud máxima de cada sección con las consultas.

    E: embeddings de las secciones (n × d); V: embeddings de consultas_de(...) en el mismo orden (m × d).
    Cada parte de una pregunta compuesta tiene sus mejores secciones garantizadas (con 26 preguntas de prueba,
    quedarse con la similitud máxima o fusionar rankings dejaba afuera la segunda parte); el resto se completa
    por la pregunta entera. Las casi duplicadas cuentan una sola vez.
    """
    Sm = E @ V.T                          # similitud de cada sección con cada consulta
    top: list[int] = []

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
    return top, Sm.max(axis=1)

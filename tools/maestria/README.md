# Herramientas de la Maestría en Ciencia de Datos

| Archivo | Que es |
|---|---|
| `contenidos_minimos.json` | **El dataset.** Contenidos minimos textuales del Anexo III de la Res. HCS 789/23: los 8 cursos obligatorios, las optativas (parrafo y 20 cursos previstos, con su carrera de origen) y los 3 cursos de nivelacion. Es la fuente del dorso de las tarjetas de la portada y del acordeon del plan de estudios. |
| `terminos.py` | Arma el bloque "La maestria en cuarenta terminos" de la portada, entre los marcadores `<!-- terminos:inicio -->` y `<!-- terminos:fin -->`: la lista de terminos con su peso (`data-p`), el curso (`data-c`, 0 = varios) y la leyenda. `js/mcd-terminos.js` dibuja la nube a partir de esa lista. |
| `terminos.json` | Salida de `terminos.py`: N y df de cada termino candidato en el digesto, y los 40 elegidos con su peso. Permite volver a renderizar sin el digesto. |

## Metodo de `terminos.py`

Peso = TF x IDF. TF es la cantidad de cursos obligatorios en cuyos contenidos minimos aparece el termino;
IDF = log((1 + N) / (1 + df)) + 1, con df = documentos del digesto de la UNLu (indice de rag-unlu,
21.364 documentos normativos) que lo contienen. Los terminos son palabras sueltas y segmentos cortos
delimitados por la puntuacion del texto. En la nube, el tamano es lineal con el peso normalizado y el color
indica el curso donde aparece el termino (blanco si aparece en mas de uno).

## Uso

    python3 tools/maestria/terminos.py --digesto ../rag-unlu/indice/chunks.jsonl   # recalcula df (unos 20 s)
    python3 tools/maestria/terminos.py                                             # solo renderiza

Esta carpeta no se despliega: en la VM solo van los archivos del sitio.

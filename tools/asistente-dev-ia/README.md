# Asistente de la Diplomatura en IA Generativa (dev-ia)

Backend del asistente conversacional de la portada de https://licdia.unlu.edu.ar/dev-ia/. Vive en `tools/` del
repositorio del sitio, que no se publica; la interfaz es `js/devia-asistente.js` y `css/devia-asistente.css`.

Es un RAG chico de punta a punta: el texto del sitio estático se parte en secciones citables, cada sección tiene su
embedding, y ante cada pregunta se calcula el embedding de la pregunta, se recuperan las 6 secciones más parecidas
(sin repetir casi duplicados) y un modelo de lenguaje responde solo con ellas, citándolas. La respuesta llega en
streaming (Server-Sent Events) con las etapas que muestra la interfaz: embedding, secciones recuperadas, texto y uso.
No se guardan conversaciones.

## Estructura

- `ingesta/extraer_sitio.py`: extrae las secciones del sitio (portada, preguntas frecuentes, módulos del plan y
  subpáginas) a `indice/secciones.json`.
- `ingesta/indexar.py`: embeddings de las secciones (`intfloat/multilingual-e5-base`), `indice/modelo.json` y la
  proyección 3D por PCA que dibuja la interfaz.
- `backend/app.py`: FastAPI con `/dev-ia/api/mapa` y `/dev-ia/api/chat`. Llama a Claude con el SDK oficial de
  Anthropic, con prompt caching sobre la parte fija del prompt (reglas + ficha de datos clave); la fecha y las secciones
  de cada consulta van en un bloque aparte, después del punto de caché.
- `backend/recuperacion.py`: la recuperación (cupos por parte en preguntas compuestas, casi duplicados). La usan el
  backend y `ingesta/evaluar.py`, así la evaluación mide lo mismo que corre en producción.
- `despliegue/`: servicio de systemd, snippet y zonas de nginx, e `instalar.sh` para la VM.

## Configuración

Modelo, modo de pensamiento y precios en `backend/llm.json` (en el repo: se cambia con un despliegue común; si se
cambia de modelo, actualizar los precios). La clave va en `.env` (`LLM_API_KEY`, ver
`.env.example`), que no se versiona ni se copia en las actualizaciones.

## Desarrollo

```
python3 -m venv .venv && .venv/bin/pip install torch -r requirements.txt
SITIO_DIR=../.. .venv/bin/python -m uvicorn backend.app:app --port 8020
```

Con `SITIO_DIR` el backend sirve también el sitio estático: la portada queda en http://localhost:8020/dev-ia/.

## Cuando cambia el contenido del sitio

```
.venv/bin/python ingesta/extraer_sitio.py ../../dev-ia
.venv/bin/python ingesta/indexar.py
```

y volver a desplegar (`indice/` viaja con el código).

## Despliegue en la VM

Primera instalación, o cambios de dependencias o de la unidad de systemd (por ejemplo, el paso al SDK de Anthropic): copiar el proyecto (sin `.venv`, `.env` ni
cachés) a `~/asistente-dev-ia` en la VM y correr `sudo bash ~/asistente-dev-ia/despliegue/instalar.sh`. Código e
índice, sin sudo: `bash despliegue/actualizar.sh` desde la Mac con la VPN conectada. El servicio queda en `/opt/asistente-dev-ia` con usuario
propio, en el puerto 8030 local, detrás de nginx en `/dev-ia/api/`, con límite de tasa y tope de memoria de 2 GB.

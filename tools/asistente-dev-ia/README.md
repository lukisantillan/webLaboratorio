# Asistente de la Diplomatura en IA Generativa (dev-ia)

Backend del asistente conversacional de la portada de https://licdia.unlu.edu.ar/dev-ia/. Vive en `tools/` del
repositorio del sitio, que no se publica; la interfaz es `js/devia-asistente.js` y `css/devia-asistente.css`.

Es un RAG chico de punta a punta: el texto del sitio estático se parte en secciones citables, cada sección tiene su
embedding, y ante cada pregunta se calcula el embedding de la pregunta, se recuperan las 6 secciones más parecidas
(sin repetir casi duplicados) y un modelo de lenguaje responde solo con ellas, citándolas. La respuesta llega en
streaming (Server-Sent Events) con las etapas que muestra la interfaz: embedding, secciones recuperadas, texto y uso.
No se guardan conversaciones: solo cada pregunta suelta, anónima (ver "Topes y registro").

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
- `backend/registro.py` y `backend/topes.json`: topes de uso y registro anónimo de preguntas (SQLite).
- `backend/consultas.py` y `despliegue/preguntas.sh`: resumen de lo que se pregunta.
- `tests/`: pruebas de topes y registro (`.venv/bin/python -m pytest tests/`).
- `despliegue/`: servicio de systemd, snippet y zonas de nginx, e `instalar.sh` para la VM.

## Configuración

Modelo, modo de pensamiento y precios en `backend/llm.json` (en el repo: se cambia con un despliegue común; si se
cambia de modelo, actualizar los precios, que alimentan el tope de gasto). La clave va en `.env` (`LLM_API_KEY`, ver
`.env.example`), que no se versiona ni se copia en las actualizaciones.

## Topes y registro

- Tope por persona: `preguntas_por_persona_por_dia` por dirección de origen (la que pasa nginx en `X-Real-IP`).
- Tope global: `usd_por_dia` de gasto en el modelo, calculado con el uso que informa la API. Al llegar, el servicio deja
  una línea `AVISO:` en `journalctl -u asistente-dev-ia` y hasta el día siguiente responde con el contacto.
- Registro: cada pregunta con fecha, secciones recuperadas, si la respuesta derivó al contacto (indicio de un dato que
  falta en el sitio), tokens, costo y tiempos. Sin la dirección de origen (el contador usa un hash con sal diaria) y
  con correos y números de 7 dígitos o más reemplazados. Se borra a los `dias_registro` días. En la VM está en
  `/var/lib/asistente-dev-ia/asistente.sqlite3` (grupo del servicio); en desarrollo, en `datos/`.

```
bash despliegue/preguntas.sh --dias 30          # resumen: por día, derivadas, secciones más usadas, últimas
bash despliegue/preguntas.sh --csv > preguntas.csv
```

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

Primera instalación, o cambios de dependencias o de la unidad de systemd (por ejemplo, el paso al SDK de Anthropic y
la carpeta de datos de los topes y el registro): copiar el proyecto (sin `.venv`, `.env` ni
cachés) a `~/asistente-dev-ia` en la VM y correr `sudo bash ~/asistente-dev-ia/despliegue/instalar.sh`. Código e
índice, sin sudo: `bash despliegue/actualizar.sh` desde la Mac con la VPN conectada. El servicio queda en `/opt/asistente-dev-ia` con usuario
propio, en el puerto 8030 local, detrás de nginx en `/dev-ia/api/`, con límite de tasa y tope de memoria de 2 GB.

#!/bin/bash
# Resumen de lo que le preguntan al asistente, leído en la VM (backend/consultas.py). Desde la Mac, con la VPN:
#   bash despliegue/preguntas.sh                 # últimos 7 días
#   bash despliegue/preguntas.sh --dias 30
#   bash despliegue/preguntas.sh --csv > preguntas.csv
# administrador lee la base por el grupo del servicio (instalar.sh lo suma al grupo).
set -euo pipefail
ssh licdia "cd /opt/asistente-dev-ia && .venv/bin/python -m backend.consultas --db /var/lib/asistente-dev-ia/asistente.sqlite3 $*"

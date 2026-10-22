#!/bin/bash
# Actualiza código e índice del asistente en la VM sin sudo. Requiere haber corrido instalar.sh (que deja el código
# de administrador con el grupo del servicio y la regla para reiniciar solo este servicio). Desde la Mac, con la VPN:
#   bash despliegue/actualizar.sh
# Si cambian requirements.txt o la unidad de systemd, usar instalar.sh. Los permisos los da la VM: la carpeta raíz es
# 750 y las carpetas de código heredan el grupo del servicio (setgid).
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
rsync -rlt \
    --exclude .venv --exclude .env --exclude .cache --exclude datos --exclude __pycache__ --exclude .DS_Store \
    "$RAIZ"/ licdia:/opt/asistente-dev-ia/
ssh licdia 'sudo -n /usr/bin/systemctl restart asistente-dev-ia && for _ in $(seq 1 60); do curl -sf -o /dev/null http://127.0.0.1:8030/dev-ia/api/mapa && break; sleep 2; done; curl -s -o /dev/null -w "servicio: %{http_code}\n" http://127.0.0.1:8030/dev-ia/api/mapa'

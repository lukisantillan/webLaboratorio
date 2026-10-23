/* LICDIA, portada: la red de nodos del fondo de Contacto (el sitio original de Lucas Santillán), animada en el encabezado.
   Los nodos con nombre son las líneas de trabajo de "¿Qué hacemos?", leídas de la misma página; el resto es la red que
   las une. Canvas liviano: se pausa fuera de pantalla y queda quieto con "reducir movimiento". */
(function () {
    'use strict';
    var header = document.querySelector('header.masthead');
    var capa = header && header.querySelector('.lv-red');
    if (!capa) return;
    var reducir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var cv = document.createElement('canvas');
    capa.appendChild(cv);
    var ctx = cv.getContext('2d'), W = 0, H = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);
    var semilla = 13, nodos = [], visible = true, corriendo = false;
    function azar() { semilla = (semilla * 16807) % 2147483647; return (semilla - 1) / 2147483646; }
    var lineas = Array.prototype.map.call(document.querySelectorAll('#portfolio .portfolio-caption-heading'), function (e) {
        return e.textContent.replace(/\s+/g, ' ').trim();
    }).filter(function (t) { return t && t.length < 60; });

    function medir() {
        W = header.offsetWidth; H = header.offsetHeight;
        cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function crear() {
        medir();
        nodos = [];
        var n = Math.max(40, Math.min(90, Math.round(W * H / 16000)));
        for (var i = 0; i < n; i++) {
            nodos.push({ x: azar() * W, y: azar() * H, vx: (azar() - 0.5) * 0.25, vy: (azar() - 0.5) * 0.25,
                         r: 1 + azar() * 1.6, c: azar() < 0.6 ? '63,210,242' : '138,109,255', nombre: null });
        }
        // las líneas de trabajo, repartidas por los bordes para no tapar el título
        lineas.forEach(function (t, k) {
            var a = (k / Math.max(lineas.length, 1)) * 6.283 + 0.4, rx = W * (0.36 + azar() * 0.1), ry = H * (0.34 + azar() * 0.1);
            nodos.push({ x: Math.min(W * 0.86, Math.max(W * 0.14, W / 2 + Math.cos(a) * rx)), y: Math.min(H * 0.88, Math.max(H * 0.26, H * 0.55 + Math.sin(a) * ry)), vx: (azar() - 0.5) * 0.12, vy: (azar() - 0.5) * 0.12,
                         r: 2.6, c: '63,210,242', nombre: t });
        });
    }
    // más tenue detrás del texto central
    function velo(x, y) {
        var dx = (x - W / 2) / (W * 0.32), dy = (y - H * 0.5) / (H * 0.4);
        return Math.min(1, 0.2 + 0.8 * Math.max(0, Math.sqrt(dx * dx + dy * dy) - 0.35));
    }
    function cuadro() {
        ctx.clearRect(0, 0, W, H);
        var lim = Math.min(170, W * 0.14);
        if (!reducir) {
            nodos.forEach(function (n) {
                n.x += n.vx; n.y += n.vy;
                // los nodos con nombre no salen de la zona visible (arriba está el menú)
                var x0 = n.nombre ? W * 0.12 : -20, x1 = n.nombre ? W * 0.88 : W + 20, y0 = n.nombre ? H * 0.24 : -20, y1 = n.nombre ? H * 0.9 : H + 20;
                if (n.x < x0 || n.x > x1) n.vx *= -1;
                if (n.y < y0 || n.y > y1) n.vy *= -1;
            });
        }
        for (var i = 0; i < nodos.length; i++) {
            for (var j = i + 1; j < nodos.length; j++) {
                var a = nodos[i], b = nodos[j], dx = a.x - b.x, dy = a.y - b.y, d = Math.sqrt(dx * dx + dy * dy);
                if (d > lim) continue;
                var al = (1 - d / lim) * 0.28 * velo((a.x + b.x) / 2, (a.y + b.y) / 2);
                ctx.strokeStyle = 'rgba(120,170,255,' + al.toFixed(3) + ')';
                ctx.lineWidth = 0.8;
                ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
            }
        }
        ctx.font = '500 11px "DM Mono", ui-monospace, monospace';
        nodos.forEach(function (n) {
            var v = velo(n.x, n.y);
            ctx.fillStyle = 'rgba(' + n.c + ',' + (0.35 + 0.55 * v).toFixed(3) + ')';
            ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, 6.283); ctx.fill();
            if (n.nombre && W > 760) {
                ctx.fillStyle = 'rgba(200,230,255,' + (0.5 * v).toFixed(3) + ')';
                ctx.textAlign = n.x > W / 2 ? 'left' : 'right';
                ctx.fillText(n.nombre, n.x + (n.x > W / 2 ? 9 : -9), n.y + 4);
            }
        });
        if (visible && !reducir) requestAnimationFrame(cuadro); else corriendo = false;
    }
    function arrancar() { if (!corriendo) { corriendo = true; requestAnimationFrame(cuadro); } }
    crear();
    if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) arrancar(); }).observe(header);
    }
    var espera;
    window.addEventListener('resize', function () { clearTimeout(espera); espera = setTimeout(function () { crear(); if (reducir) cuadro(); }, 200); });
    if (reducir) cuadro(); else arrancar();
})();

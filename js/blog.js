/* Blog del LICDIA: filtros del índice y mapa de entradas del encabezado.
   El mapa dibuja cada entrada como un nodo ubicado por su huella (los primeros bytes del SHA-256 de su texto), del color de
   su categoría y unido a las entradas del mismo tema; al pasar por una tarjeta se enciende su nodo. Se pausa fuera de
   pantalla y queda quieto con "reducir movimiento". */
(function () {
    'use strict';
    var reducir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var COLORES = { novedades: '63,210,242', publicaciones: '138,125,255', tesis: '63,207,142', tecnicos: '245,185,66' };

    // ---------- Filtros ----------
    var tarjetas = Array.prototype.slice.call(document.querySelectorAll('.bl-item'));
    var botones = Array.prototype.slice.call(document.querySelectorAll('.bl-filtro'));
    var vacio = document.querySelector('.bl-vacio');
    var filtro = { cat: '', tema: '' };
    function aplicar() {
        var n = 0;
        tarjetas.forEach(function (t) {
            var ok = (!filtro.cat || t.getAttribute('data-cat') === filtro.cat) && (!filtro.tema || t.getAttribute('data-tema') === filtro.tema);
            t.hidden = !ok;
            if (ok) n++;
        });
        botones.forEach(function (b) {
            var tipo = b.getAttribute('data-tipo'), v = b.getAttribute('data-valor');
            b.setAttribute('aria-pressed', String(tipo === 'cat' ? filtro.cat === v : !!filtro.tema));
        });
        var tema = document.querySelector('.bl-filtro-tema');
        if (tema) {
            tema.classList.toggle('visible', !!filtro.tema);
            var et = tema.querySelector('.bl-tema-nombre');
            if (et) et.textContent = filtro.tema ? (tema.getAttribute('data-' + filtro.tema) || filtro.tema) : '';
        }
        if (vacio) vacio.style.display = n ? 'none' : 'block';
    }
    if (botones.length) {
        // por defecto, solo Novedades (los artículos técnicos son otra cosa); desde una diplomatura (?tema=) se ve todo el tema
        var q = new URLSearchParams(location.search);
        filtro.tema = q.get('tema') || '';
        var c = q.get('categoria');
        filtro.cat = c === 'todo' ? '' : (c || (filtro.tema ? '' : 'novedades'));
        botones.forEach(function (b) {
            b.addEventListener('click', function () {
                var tipo = b.getAttribute('data-tipo'), v = b.getAttribute('data-valor');
                if (tipo === 'cat') filtro.cat = v; else filtro.tema = '';
                var u = new URLSearchParams();
                u.set('categoria', filtro.cat || 'todo');
                if (filtro.tema) u.set('tema', filtro.tema);
                history.replaceState(null, '', location.pathname + (u.toString() ? '?' + u : ''));
                aplicar();
            });
        });
        aplicar();
    }

    // ---------- Mapa de entradas ----------
    var capa = document.querySelector('.bl-mapa');
    var datos = document.getElementById('bl-datos');
    if (!capa || !datos) return;
    var entradas = JSON.parse(datos.textContent);
    var cabecera = capa.parentElement;
    var cv = document.createElement('canvas');
    capa.appendChild(cv);
    var ctx = cv.getContext('2d'), W = 0, H = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);
    var activo = null, visible = true, corriendo = false;
    var nodos = entradas.map(function (e, i) {
        var b = function (k) { return parseInt(e.h.slice(k * 2, k * 2 + 2), 16) / 255; };
        return { e: e, x: 0.08 + 0.84 * b(0), y: 0.12 + 0.76 * b(1), f: b(2) * 6.283, r: 2.6 + 3 * b(3), c: COLORES[e.cat] || COLORES.novedades };
    });
    // polvo de fondo: puntos tenues fijos (posiciones pseudoaleatorias reproducibles)
    var semilla = 7, polvo = [];
    function azar() { semilla = (semilla * 16807) % 2147483647; return (semilla - 1) / 2147483646; }
    for (var k = 0; k < 70; k++) polvo.push({ x: azar(), y: azar(), r: 0.6 + azar() * 1.1, f: azar() * 6.283 });
    function medir() {
        W = cabecera.offsetWidth; H = cabecera.offsetHeight;
        cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    // más tenue detrás del texto, que está a la izquierda
    function velo(x) { return Math.min(1, 0.25 + 0.75 * Math.max(0, (x / W - 0.25) / 0.5)); }
    function cuadro(ahora) {
        var t = (ahora || 0) / 1000;
        ctx.clearRect(0, 0, W, H);
        polvo.forEach(function (d) {
            var x = d.x * W, a = (0.18 + 0.12 * Math.sin(t * 0.6 + d.f)) * velo(x);
            ctx.fillStyle = 'rgba(150,200,255,' + a.toFixed(3) + ')';
            ctx.beginPath(); ctx.arc(x, d.y * H, d.r, 0, 6.283); ctx.fill();
        });
        var P = nodos.map(function (n) {
            var dx = reducir ? 0 : Math.sin(t * 0.25 + n.f) * 10, dy = reducir ? 0 : Math.cos(t * 0.2 + n.f) * 8;
            return { x: n.x * W + dx, y: n.y * H + dy, n: n };
        });
        for (var i = 0; i < P.length; i++) {
            for (var j = i + 1; j < P.length; j++) {
                if (P[i].n.e.tema !== P[j].n.e.tema) continue;
                var enc = activo && (P[i].n.e.slug === activo || P[j].n.e.slug === activo);
                ctx.strokeStyle = 'rgba(140,200,255,' + (enc ? 0.35 : 0.07) * velo((P[i].x + P[j].x) / 2) + ')';
                ctx.lineWidth = enc ? 1.2 : 0.8;
                ctx.beginPath(); ctx.moveTo(P[i].x, P[i].y); ctx.lineTo(P[j].x, P[j].y); ctx.stroke();
            }
        }
        P.forEach(function (p) {
            var on = p.n.e.slug === activo, a = velo(p.x);
            var r = p.n.r * (on ? 1.8 : 1);
            var g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r * 5);
            g.addColorStop(0, 'rgba(' + p.n.c + ',' + (on ? 0.5 : 0.22) * a + ')');
            g.addColorStop(1, 'rgba(' + p.n.c + ',0)');
            ctx.fillStyle = g; ctx.beginPath(); ctx.arc(p.x, p.y, r * 5, 0, 6.283); ctx.fill();
            ctx.fillStyle = 'rgba(' + p.n.c + ',' + (on ? 1 : 0.75 * a) + ')';
            ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, 6.283); ctx.fill();
            if (on) {
                ctx.font = '500 11px "DM Mono", ui-monospace, monospace';
                ctx.fillStyle = 'rgba(220,235,255,.85)';
                ctx.textAlign = p.x > W * 0.7 ? 'right' : 'left';
                ctx.fillText('0x' + p.n.e.h.slice(0, 8), p.x + (p.x > W * 0.7 ? -12 : 12), p.y - 10);
            }
        });
        if (visible && !reducir) requestAnimationFrame(cuadro); else corriendo = false;
    }
    function arrancar() { if (!corriendo) { corriendo = true; requestAnimationFrame(cuadro); } }
    medir();
    tarjetas.forEach(function (t) {
        t.addEventListener('mouseenter', function () { activo = t.getAttribute('data-slug'); if (reducir) cuadro(); });
        t.addEventListener('mouseleave', function () { activo = null; if (reducir) cuadro(); });
    });
    if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) arrancar(); }).observe(cabecera);
    }
    var espera;
    window.addEventListener('resize', function () { clearTimeout(espera); espera = setTimeout(function () { medir(); if (reducir) cuadro(); }, 200); });
    if (reducir) cuadro(); else arrancar();
})();

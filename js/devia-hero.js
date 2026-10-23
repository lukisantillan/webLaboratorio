/* Diplomatura en IA Generativa: escena del encabezado del sitio convencional, de la familia del asistente
   (js/devia-asistente.js). Números flotantes que son valores reales de los embeddings de las secciones del sitio
   (BGE-M3, muestreados por asistente-dev-ia/ingesta), una constelación tenue y un orbe que respira detrás del título.
   Canvas liviano: se pausa fuera de pantalla y queda quieto con "reducir movimiento". */
(function () {
    var header = document.querySelector('header.fondoDiplomatura');
    if (!header) return;
    var capa = header.querySelector('.dv-hero-fondo');
    if (!capa) {   // subpáginas: el encabezado no trae la capa
        capa = document.createElement('div');
        capa.className = 'dv-hero-fondo';
        capa.setAttribute('aria-hidden', 'true');
        header.insertBefore(capa, header.firstChild);
    }
    var cont = header.querySelector('.container');
    if (cont && !header.querySelector('.dv-hero-rotulo')) {
        var rotulo = document.createElement('p');
        rotulo.className = 'dv-hero-rotulo';
        rotulo.textContent = 'Diplomatura de posgrado · LICDIA · UNLu';
        cont.insertBefore(rotulo, cont.firstChild);
    }
    var VALORES = [0.0136, -0.0154, 0.0496, -0.035, -0.0207, 0.0115, -0.0155, 0.005, -0.0036, 0.035, 0.0348, -0.0195, 0.0083, -0.0066, 0.0105, -0.0159, -0.014, -0.0488, 0.004, -0.0549, 0.0104, -0.0051, -0.0572, 0.0262, 0.2591, -0.0097, -0.0188, 0.0053, -0.0491, -0.034, -0.0244, -0.0315, 0.0029, 0.0179, 0.027, -0.0197, 0.0189, 0.0266, -0.0046, -0.0136, 0.0016, -0.0083, -0.0151, 0.0188, 0.041, -0.0039, -0.0053, -0.0796, 0.0154, 0.0494, 0.0384, -0.0503, -0.0282, 0.0255, -0.0305, -0.0138, -0.0157, 0.032, -0.0309, 0.001, -0.0012, 0.007, 0.0013, -0.0263, -0.0255, 0.0114, -0.0375, 0.0469, -0.0169, 0.0289, 0.0102, -0.0346, 0.0056, 0.0181, 0.0376, 0.0129, 0.0251, 0.0205, -0.008, -0.0115, 0.0367, 0.0823, 0.0176, -0.014, -0.0204, 0.0197, -0.0238, 0.0146, 0.0005, 0.0178, -0.0357, 0.0075, -0.0129, 0.0154, -0.0442, 0.0451, 0.0191, -0.0199, 0.0473, -0.0388, 0.0372, -0.0354, 0.0263, -0.0311, 0.0118, 0.0116, 0.0082, -0.0198, -0.0367, 0.0002, 0.0061, -0.0421, 0.0206, -0.0827, -0.0105, -0.0131, -0.006, -0.0333, -0.0303, -0.028, -0.014, -0.0027, 0.0392, -0.0005, -0.0256, -0.0079, 0.0405, -0.0213, -0.0416, -0.0433, 0.0498, 0.0033, 0.0094, -0.024, 0.0148, 0.0056, 0.0115, 0.0268, -0.0057, 0.0171];
    var cv = document.createElement('canvas');
    capa.appendChild(cv);
    var ctx = cv.getContext('2d'), W = 0, H = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);
    var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var semilla = 11;
    function azar() { semilla = (semilla * 16807) % 2147483647; return (semilla - 1) / 2147483646; }
    var nums = [], nodos = [], orbe = [], visible = true, corriendo = false;

    function medir() {
        // offsetWidth/offsetHeight: tamaño real, sin la rotación de la animación de entrada de AOS
        W = header.offsetWidth; H = header.offsetHeight;
        cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function crear() {
        medir();
        nums = [];
        var n = Math.max(26, Math.min(70, Math.round(W * H / 14000)));
        for (var i = 0; i < n; i++) {
            var v = VALORES[i % VALORES.length];
            nums.push({ t: (v >= 0 ? '+' : '') + v.toFixed(4), x: azar() * W, y: azar() * H, z: azar(),
                        vy: -(0.08 + azar() * 0.22), vx: (azar() - 0.5) * 0.08 });
        }
        nodos = [];
        for (var k = 0; k < 46; k++) {
            var u = azar() * 2 - 1, th = azar() * 6.283, r = Math.sqrt(1 - u * u), d = 0.55 + azar() * 0.45;
            nodos.push({ x: Math.cos(th) * r * d, y: u * d, z: Math.sin(th) * r * d, c: azar() < 0.5 ? '77,226,255' : '138,125,255' });
        }
        orbe = [];
        var N = 260, oro = Math.PI * (3 - Math.sqrt(5));
        for (var j = 0; j < N; j++) {
            var y = 1 - (j / (N - 1)) * 2, rr = Math.sqrt(1 - y * y), a = j * oro;
            orbe.push({ x: Math.cos(a) * rr, y: y, z: Math.sin(a) * rr });
        }
    }
    function rot(p, a, b) {
        var ca = Math.cos(a), sa = Math.sin(a), cb = Math.cos(b), sb = Math.sin(b);
        var x = p.x * ca - p.z * sa, z = p.x * sa + p.z * ca;
        return { x: x, y: p.y * cb - z * sb, z: p.y * sb + z * cb };
    }
    // Más tenue detrás del título para que se lea
    function velo(x, y) {
        var dx = (x - W / 2) / (W * 0.36), dy = (y - H * 0.5) / (H * 0.36);
        return Math.min(1, 0.3 + 0.7 * Math.max(0, Math.sqrt(dx * dx + dy * dy) - 0.3));
    }
    function cuadro(ahora) {
        var t = (ahora || 0) / 1000;
        ctx.clearRect(0, 0, W, H);
        var cx = W / 2, cy = H * 0.5, R = Math.min(W, H) * 0.62, Ro = Math.min(W, H) * 0.16;
        // Constelación
        var P = nodos.map(function (n) { var q = rot(n, t * 0.05, 0.35), s = 3 / (3 + q.z); return { x: cx + q.x * R * 1.6 * s, y: cy + q.y * R * s, s: s, c: n.c }; });
        ctx.lineWidth = 1;
        for (var i = 0; i < P.length; i++) {
            for (var j = i + 1; j < P.length; j++) {
                var dx = P[i].x - P[j].x, dy = P[i].y - P[j].y, d = Math.sqrt(dx * dx + dy * dy);
                if (d < R * 0.32) {
                    ctx.strokeStyle = 'rgba(140,180,255,' + (0.09 * (1 - d / (R * 0.32)) * velo((P[i].x + P[j].x) / 2, (P[i].y + P[j].y) / 2)).toFixed(3) + ')';
                    ctx.beginPath(); ctx.moveTo(P[i].x, P[i].y); ctx.lineTo(P[j].x, P[j].y); ctx.stroke();
                }
            }
        }
        P.forEach(function (p) {
            ctx.fillStyle = 'rgba(' + p.c + ',' + (0.55 * velo(p.x, p.y)).toFixed(3) + ')';
            ctx.beginPath(); ctx.arc(p.x, p.y, 1.2 + 1.4 * p.s, 0, 6.283); ctx.fill();
        });
        // Orbe que respira detrás del título
        var halo = ctx.createRadialGradient(cx, cy, 0, cx, cy, Ro * 3);
        halo.addColorStop(0, 'rgba(77,226,255,.13)'); halo.addColorStop(1, 'rgba(138,125,255,0)');
        ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(cx, cy, Ro * 3, 0, 6.283); ctx.fill();
        var amp = 1 + 0.03 * Math.sin(t * 1.3);
        orbe.forEach(function (o) {
            var q = rot({ x: o.x * amp, y: o.y * amp, z: o.z * amp }, t * 0.25, 0.4), s = 3 / (3 + q.z), prof = (1 - q.z) / 2;
            ctx.fillStyle = 'rgba(' + Math.round(77 + 61 * (o.y + 1) / 2) + ',' + Math.round(226 - 101 * (o.y + 1) / 2) + ',255,' + (0.05 + 0.2 * prof).toFixed(3) + ')';
            ctx.beginPath(); ctx.arc(cx + q.x * Ro * s, cy + q.y * Ro * s, 0.6 + 1.1 * prof, 0, 6.283); ctx.fill();
        });
        // Números de embedding que suben
        ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        nums.forEach(function (n) {
            if (!quieto) { n.y += n.vy * (0.6 + n.z); n.x += n.vx; }
            if (n.y < -12) { n.y = H + 12; n.x = Math.random() * W; }
            ctx.font = '400 ' + (9 + n.z * 6).toFixed(1) + 'px "DM Mono", ui-monospace, monospace';
            ctx.fillStyle = 'rgba(150,200,255,' + ((0.06 + n.z * 0.24) * velo(n.x, n.y)).toFixed(3) + ')';
            ctx.fillText(n.t, n.x, n.y);
        });
        if (visible && !quieto) requestAnimationFrame(cuadro); else corriendo = false;
    }
    function arrancar() { if (!corriendo && !quieto) { corriendo = true; requestAnimationFrame(cuadro); } }

    crear();
    if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) arrancar(); }).observe(header);
    }
    var espera;
    window.addEventListener('resize', function () { clearTimeout(espera); espera = setTimeout(function () { crear(); if (quieto) cuadro(0); }, 200); });
    if (quieto) cuadro(0); else arrancar();
})();

/* Maestría en Ciencia de Datos: fondo en movimiento del encabezado de la portada.
   Puntos dispersos, como ruido, que cada 12 s se agrupan en cuatro grupos a los costados del texto (asignación al
   centro más cercano, como en k-medias), toman el color de su grupo con la paleta de la nube de términos y vuelven
   a dispersarse. Canvas liviano: se pausa fuera de pantalla y queda quieto con "reducir movimiento". */
(function () {
    var header = document.querySelector('#masthead');
    var capa = header && header.querySelector('.mcd-hero-fondo');
    if (!capa) return;
    var cv = document.createElement('canvas');
    cv.className = 'mcd-hero-canvas';
    capa.appendChild(cv);
    var ctx = cv.getContext('2d'), W = 0, H = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);
    var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var semilla = 7;
    function azar() { semilla = (semilla * 16807) % 2147483647; return (semilla - 1) / 2147483646; }
    var COLORES = ['255,201,214', '187,168,247', '127,220,201', '242,196,109'];  // rosa, lavanda, aguamarina, ámbar
    var puntos = [], centros = [], t0 = performance.now(), ultimoT = 0, visible = true;

    function medir() {
        // offsetWidth/offsetHeight: el tamaño real, sin la rotación de la animación de entrada de AOS
        W = header.offsetWidth; H = header.offsetHeight;
        cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    // Más tenue detrás del bloque de texto centrado
    function velo(x, y) {
        var dx = (x - W / 2) / (W * 0.32), dy = (y - H * 0.55) / (H * 0.42);
        return Math.min(1, 0.25 + 0.75 * Math.max(0, Math.sqrt(dx * dx + dy * dy) - 0.35));
    }
    // Centros a los costados del texto: dos a la izquierda y dos a la derecha
    function centroNuevo(k) {
        var izq = k % 2 === 0;
        return { x: W * (izq ? 0.06 + 0.22 * azar() : 0.72 + 0.22 * azar()), y: H * (0.2 + 0.65 * azar()) };
    }
    function crear() {
        medir();
        var n = Math.max(30, Math.min(70, Math.round(W * H / 9000)));
        puntos = [];
        for (var i = 0; i < n; i++) {
            puntos.push({ x: azar() * W, y: azar() * H, vx: (azar() - 0.5) * 0.36, vy: (azar() - 0.5) * 0.36,
                          r: 1.4 + azar() * 1.4, g: 0, col: 0,
                          // lugar propio dentro del grupo: los grupos se ven como nubes y no como un punto
                          ang: azar() * 6.2832, rad: Math.sqrt(azar()) * Math.min(70, W * 0.06) });
        }
        centros = [0, 1, 2, 3].map(centroNuevo);
    }

    // Ciclo de 12 s: dispersión (0-4 s), agrupamiento (4-9 s) y vuelta a la dispersión (9-12 s)
    function cuadro(ahora) {
        ctx.clearRect(0, 0, W, H);
        var t = ((ahora - t0) / 1000) % 12;
        if (t < ultimoT) centros = centros.map(function (c, k) { return centroNuevo(k); });
        ultimoT = t;
        var fuerza = t < 4 ? 0 : t < 9 ? Math.min(1, (t - 4) / 2.5) : Math.max(0, 1 - (t - 9) / 2.2);
        puntos.forEach(function (p) {
            var mejor = 0, dm = 1e9;
            centros.forEach(function (c, k) { var d = (p.x - c.x) * (p.x - c.x) + (p.y - c.y) * (p.y - c.y); if (d < dm) { dm = d; mejor = k; } });
            p.col = mejor;
            var c = centros[mejor], tx = c.x + Math.cos(p.ang) * p.rad, ty = c.y + Math.sin(p.ang) * p.rad;
            p.vx += (tx - p.x) * 0.0016 * fuerza + (azar() - 0.5) * 0.04;
            p.vy += (ty - p.y) * 0.0016 * fuerza + (azar() - 0.5) * 0.04;
            p.vx *= 0.96; p.vy *= 0.96;
            var v = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
            if (v > 0.9) { p.vx *= 0.9 / v; p.vy *= 0.9 / v; }
            if (fuerza === 0 && v < 0.15) { p.vx += (azar() - 0.5) * 0.12; p.vy += (azar() - 0.5) * 0.12; }
            p.x += p.vx; p.y += p.vy;
            if (p.x < 0 || p.x > W) p.vx *= -1;
            if (p.y < 0 || p.y > H) p.vy *= -1;
            p.g += ((fuerza > 0.3 ? 1 : 0) - p.g) * 0.05;   // cuánto se ve el color del grupo
        });
        puntos.forEach(function (p) {
            var base = 0.7 * velo(p.x, p.y);
            ctx.fillStyle = 'rgba(255,201,214,' + (base * (1 - p.g)).toFixed(3) + ')';
            ctx.beginPath(); ctx.arc(p.x, p.y, p.r + 0.4, 0, 6.2832); ctx.fill();
            if (p.g > 0.02) {
                ctx.fillStyle = 'rgba(' + COLORES[p.col] + ',' + Math.min(1, base * p.g * 1.25).toFixed(3) + ')';
                ctx.beginPath(); ctx.arc(p.x, p.y, p.r + 0.4 + 0.5 * p.g, 0, 6.2832); ctx.fill();
            }
        });
        if (visible && !quieto) requestAnimationFrame(cuadro);
    }

    crear();
    if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (es) {
            var antes = visible; visible = es[0].isIntersecting;
            if (visible && !antes && !quieto) requestAnimationFrame(cuadro);
        }).observe(header);
    }
    var espera;
    window.addEventListener('resize', function () {
        clearTimeout(espera);
        espera = setTimeout(function () { crear(); if (quieto) cuadro(performance.now()); }, 200);
    });
    requestAnimationFrame(cuadro);
})();

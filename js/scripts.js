/*!
* Start Bootstrap - Agency v7.0.12 (https://startbootstrap.com/theme/agency)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-agency/blob/master/LICENSE)
*/
//
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Navbar shrink function
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink')
        } else {
            navbarCollapsible.classList.add('navbar-shrink')
        }

    };

    // Shrink the navbar 
    navbarShrink();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);

    //  Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            rootMargin: '0px 0px -40%',
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

});

function initMap() {
    // Coordenadas de tu ubicación
    var location = { lat: -34.57916, lng: -59.08685}; // Ejemplo para Buenos Aires

    // Crear el mapa
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 15,
        center: location
    });

    // Marcador en el mapa
    var marker = new google.maps.Marker({
        position: location,
        map: map
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const elementos = document.querySelectorAll('.oculto');

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('aparecer'); // Agregar la clase 'aparecer' cuando se haga visible
                observer.unobserve(entry.target); // Deja de observar después de que aparece
            }
        });
    }, {
        threshold: 0.1 // El 10% del elemento debe ser visible para activar la animación
    });

    elementos.forEach(elemento => {
        observer.observe(elemento); // Observar cada elemento con la clase 'oculto'
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const elementos = document.querySelectorAll('.der');

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('.derecha');
                observer.unobserve(entry.target); // Deja de observar después de que aparece
            }
        });
    }, {
        threshold: 0.1 // El 10% del elemento debe ser visible para activar la animación
    });

    elementos.forEach(elemento => {
        observer.observe(elemento); // Observar cada elemento con la clase 'oculto'
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const elementos = document.querySelectorAll('.izq');

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('.izquierda');
                observer.unobserve(entry.target); // Deja de observar después de que aparece
            }
        });
    }, {
        threshold: 0.1 // El 10% del elemento debe ser visible para activar la animación
    });

    elementos.forEach(elemento => {
        observer.observe(elemento); // Observar cada elemento con la clase 'oculto'
    });
});

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-inscripcion");
  const msg  = document.getElementById("insc-msg");
  const checks = document.querySelectorAll(".ingreso-check");
  const exp   = document.getElementById("ing4"); // experiencia laboral
  const imgTitulo = document.getElementById("imagen_titulo");
  const flag  = document.getElementById("titulo-req-flag");
  const emailHidden = document.getElementById("email-hidden");
  const correoVisible = document.querySelector("[name='postulante_email']");

  // regla: si experiencia laboral está marcada, no pedimos título
  function reglaTitulo(){
    if (exp && exp.checked) {
      imgTitulo?.removeAttribute("required");
      flag.textContent = "";
    } else {
      imgTitulo?.setAttribute("required","required");
      flag.textContent = "*";
    }
  }
  checks.forEach(c => c.addEventListener("change", reglaTitulo));
  reglaTitulo();

  form.addEventListener("submit", (e) => {
    // validar al menos un check
    if (!Array.from(checks).some(c => c.checked)) {
      e.preventDefault();
      msg.innerHTML = '<span class="text-danger">Seleccioná al menos una forma de ingreso.</span>';
      return;
    }
    // copiar el correo al campo hidden "email"
    if (correoVisible && emailHidden) {
      emailHidden.value = correoVisible.value;
    }
    msg.textContent = "Enviando...";
    // FormSubmit procesa y redirige
  });
});

(function () {
  const btn = document.getElementById('btnCopyCBU');
  if (!btn) return;

  async function copyText(text) {
    // usa Clipboard API si hay contexto seguro (https/localhost)
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    // fallback clásico
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); }
    finally { document.body.removeChild(ta); }
  }

  btn.addEventListener('click', async (e) => {
    const targetSel = e.currentTarget.dataset.target;
    const el = document.querySelector(targetSel);
    const text = (el?.dataset.copy || el?.textContent || '').trim();

    try {
      await copyText(text);
      btn.textContent = 'Copiado ✓';
      setTimeout(() => (btn.textContent = 'Copiar CBU'), 1500);
    } catch (err) {
      console.error(err);
      alert('No se pudo copiar automáticamente. Seleccioná y copiá manualmente.');
    }
  });
})();



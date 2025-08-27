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

// ===== Config =====
const FORM_ENDPOINT = "https://formsubmit.co/licdia@unlu.edu.ar"; // destino principal
const CC_EMAIL      = "licdia.unlu@gmail.com";                    // copia
const SUBJECT       = "Nueva inscripción / consulta desde el sitio";
const REDIRECT_TO   = ""; // opcional: ej. "https://tu-dominio.com/gracias.html"

// ===== Lógica =====
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-inscripcion");    // id de tu <form>
  const msg  = document.getElementById("insc-msg");            // contenedor de mensajes
  const checks = document.querySelectorAll(".ingreso-check");  // checkboxes forma de ingreso
  const expCheck = document.getElementById("ing4");            // "Experiencia laboral..."
  const imgTitulo = document.getElementById("imagen_titulo");
  const flag = document.getElementById("titulo-req-flag");     // el asterisco del label

  function syncTituloRequirement(){
    const exp = expCheck && expCheck.checked;
    if (exp) {
      imgTitulo && imgTitulo.removeAttribute("required");
      flag && (flag.textContent = "");
    } else {
      imgTitulo && imgTitulo.setAttribute("required","required");
      flag && (flag.textContent = "*");
    }
  }
  checks.forEach(c => c.addEventListener("change", syncTituloRequirement));
  syncTituloRequirement();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    msg.textContent = "";

    // Validar al menos un check
    const alguno = Array.from(checks).some(c => c.checked);
    if (!alguno) {
      msg.innerHTML = '<span class="text-danger">Seleccioná al menos una forma de ingreso.</span>';
      return;
    }
    // Revalidar regla del título
    syncTituloRequirement();

    // Armar FormData (incluye archivos)
    const fd = new FormData(form);

    // Config de FormSubmit
    fd.append("_subject", SUBJECT);
    fd.append("_cc", CC_EMAIL);
    fd.append("_captcha", "false");              // opcional
    if (REDIRECT_TO) fd.append("_next", REDIRECT_TO);

    // Requisito: asegurarte de tener un campo de email (FormSubmit lo prefiere)
    // Supongo que tu input de correo se llama "postulante_email"; si no, adaptá:
    if (!fd.get("postulante_email")) {
      // Si tu input se llama "Correo" o "email", duplicalo a "email"
      const fallbackEmail = fd.get("Correo") || fd.get("email") || "";
      fd.append("email", fallbackEmail);
    }

    // Enviar
    try {
      msg.textContent = "Enviando...";
      const r = await fetch(FORM_ENDPOINT, {
        method: "POST",
        body: fd
        // NO pongas Content-Type; fetch lo define con boundary del FormData
      });
      if (!r.ok) throw new Error("Error de red");
      // FormSubmit puede redirigir; si usamos fetch, mostramos feedback manual
      msg.innerHTML = '<span class="text-success">¡Enviado correctamente! Revisá tu correo.</span>';
      form.reset();
      syncTituloRequirement();
    } catch (err) {
      console.error(err);
      msg.innerHTML = '<span class="text-danger">No se pudo enviar. Probá nuevamente.</span>';
    }
  });
});

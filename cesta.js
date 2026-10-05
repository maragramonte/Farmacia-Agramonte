/* ---------------------------------------------------------------
   Farmàcia Agramonte — la cesta

   Una lista de lo que alguien quiere encargar, que se guarda en su propio
   navegador y acaba en un mensaje de WhatsApp. NO es una tienda: aquí no se
   cobra, no se piden datos y nada de esto sale del ordenador de quien mira la
   web hasta que pulsa «Enviar el encargo» y el mensaje se escribe solo en su
   WhatsApp. Eso es a propósito, y es lo que mantiene la web fuera del régimen
   de venta a distancia: el encargo se confirma y se paga en el mostrador.

   Por qué esto no es React: lo único que hace falta es guardar una lista y
   volver a pintarla. Son estas cuatrocientas líneas, sin dependencias, sin
   compilar nada y sin que los testers instalen Node: siguen abriendo
   servir.bat y ya está.

   IDIOMAS. Los textos están abajo, en TEXTOS, y se elige por el lang del
   <html>, que lo pone el generador. Un idioma que no esté en la tabla cae en
   español, igual que en catalogo.py. Es el único fichero del sitio cuyos
   textos NO están en herramientas/textos.json, y es por una razón: aquí se
   escriben mientras alguien pulsa botones, no al generar las páginas.

   El contrato con el HTML son atributos data-*, y lo pone el generador
   (herramientas/catalogo.py). Si cambias un nombre aquí, cámbialo allí:

     [data-cesta-contador]   El enlace de la cabecera. Nace con hidden; esto se
                             lo quita, que un enlace a la cesta sin JavaScript
                             no llevaría a nada que funcione.
     [data-cesta-cuenta]     Dentro del anterior: cuántas unidades hay.
     [data-cesta-anade]      Botón de añadir. Nace con hidden, por lo mismo.
                             Lleva data-id, data-nombre, data-formato y
                             data-url.
     [data-cesta-estado]     Línea junto al botón de la ficha: «ya tienes 2».
                             El valor del atributo es el id del producto.
     [data-cesta-sinjs]      El aviso de que esto necesita JavaScript. Nace
                             visible y lo escondemos: si este fichero no carga,
                             es lo único que se ve, y dice la verdad.
     [data-cesta-vacia]      En cesta.html, el bloque de «no has apuntado nada».
     [data-cesta-llena]      En cesta.html, el bloque con la lista y los botones.
     [data-cesta-lista]      El <ul> donde se pinta la lista.
     [data-cesta-avisos]     Región aria-live: lo que se le dice a un lector de
                             pantalla al añadir o quitar.
     [data-cesta-total]      Cuántas unidades hay, en el resumen de la cesta.
     [data-cesta-recorte]    El aviso de que la cesta no cabe en un WhatsApp.
     [data-cesta-whatsapp]   El enlace de enviar; le ponemos el href al pintar.
     [data-cesta-correo]     Lo mismo, por correo, para quien no use WhatsApp.
     [data-cesta-copia]      Copiar la lista al portapapeles.
     [data-cesta-vaciar]     Vaciar la cesta.
   --------------------------------------------------------------- */
(function () {
  "use strict";

  var CLAVE = "agramonte-cesta-1";
  var WHATSAPP = "34661192472";
  var CORREO = "farmacia.lallana@gmail.com";

  /* Un wa.me con un texto larguísimo deja de funcionar, y falla callando: se
     abre WhatsApp con el mensaje cortado o sin mensaje. Antes de llegar ahí
     recortamos la lista nosotros y lo decimos en el propio mensaje. */
  var TOPE_URL = 1800;
  var TOPE_UNIDADES = 99;

  /* ---------- Los textos ----------
     Los %s se rellenan en orden. Al añadir un idioma, se añade su bloque; lo
     que falte sale en español. */
  var TEXTOS = {
    es: {
      cesta_con: "Tu cesta: %s",
      cesta_vacia: "Tu cesta, vacía",
      uno: "1 producto",
      varios: "%s productos",
      anadido: "Añadido a la cesta: %s. Ahora tienes %s.",
      quitado: "Quitado de la cesta. Quedan %s.",
      vaciada: "Cesta vacía.",
      quitar_una: "Quitar una unidad de %s",
      anadir_una: "Añadir una unidad de %s",
      quitar_esto: "Quitar %s de la cesta",
      quitar: "Quitar",
      ya_tienes: "Ya tienes <strong>%s</strong> en la cesta. <a href=\"cesta.html\">Ver la cesta</a>",
      copiar: "Copiar la lista",
      copiada: "Copiada",
      no_copiada: "No se ha podido copiar",
      copiada_aviso: "Lista copiada al portapapeles.",
      no_copiada_aviso: "No se ha podido copiar la lista.",
      mensaje_cabeza: "Hola, quería encargar:\n\n",
      mensaje_pie: "\n\n¿Me decís el precio y cuándo lo puedo recoger? Gracias.",
      mensaje_resto_uno: "\n- ...y 1 producto más.",
      mensaje_resto: "\n- ...y %s productos más.",
      correo_asunto: "Encargo desde la web",
      recorte: "La cesta es tan larga que en WhatsApp no cabe de una vez: el " +
               "mensaje llevará los primeros y dirá que faltan <strong>%s</strong>. " +
               "Para mandarla entera, usa <strong>Copiar la lista</strong> o el correo."
    },
    ca: {
      cesta_con: "La teva cistella: %s",
      cesta_vacia: "La teva cistella, buida",
      uno: "1 producte",
      varios: "%s productes",
      anadido: "Afegit a la cistella: %s. Ara tens %s.",
      quitado: "Tret de la cistella. Queden %s.",
      vaciada: "Cistella buida.",
      quitar_una: "Treure una unitat de %s",
      anadir_una: "Afegir una unitat de %s",
      quitar_esto: "Treure %s de la cistella",
      quitar: "Treure",
      ya_tienes: "Ja en tens <strong>%s</strong> a la cistella. <a href=\"cesta.html\">Veure la cistella</a>",
      copiar: "Copiar la llista",
      copiada: "Copiada",
      no_copiada: "No s'ha pogut copiar",
      copiada_aviso: "Llista copiada al porta-retalls.",
      no_copiada_aviso: "No s'ha pogut copiar la llista.",
      mensaje_cabeza: "Hola, volia encarregar:\n\n",
      mensaje_pie: "\n\nEm dieu el preu i quan ho puc recollir? Gràcies.",
      mensaje_resto_uno: "\n- ...i 1 producte més.",
      mensaje_resto: "\n- ...i %s productes més.",
      correo_asunto: "Encàrrec des del web",
      recorte: "La cistella és tan llarga que a WhatsApp no hi cap d'un cop: el " +
               "missatge portarà els primers i dirà que en falten <strong>%s</strong>. " +
               "Per enviar-la sencera, fes servir <strong>Copiar la llista</strong> o el correu."
    },
    en: {
      cesta_con: "Your basket: %s",
      cesta_vacia: "Your basket, empty",
      uno: "1 product",
      varios: "%s products",
      anadido: "Added to the basket: %s. You now have %s.",
      quitado: "Removed from the basket. %s left.",
      vaciada: "Basket empty.",
      quitar_una: "Remove one unit of %s",
      anadir_una: "Add one unit of %s",
      quitar_esto: "Remove %s from the basket",
      quitar: "Remove",
      ya_tienes: "You already have <strong>%s</strong> in the basket. <a href=\"cesta.html\">See the basket</a>",
      copiar: "Copy the list",
      copiada: "Copied",
      no_copiada: "Could not copy",
      copiada_aviso: "List copied to the clipboard.",
      no_copiada_aviso: "The list could not be copied.",
      mensaje_cabeza: "Hello, I would like to order:\n\n",
      mensaje_pie: "\n\nCould you tell me the price and when I can collect it? Thank you.",
      mensaje_resto_uno: "\n- ...and 1 more product.",
      mensaje_resto: "\n- ...and %s more products.",
      correo_asunto: "Order from the website",
      recorte: "The basket is so long that it will not fit in WhatsApp in one go: the " +
               "message will carry the first ones and say that <strong>%s</strong> are missing. " +
               "To send it whole, use <strong>Copy the list</strong> or email."
    }
  };

  var IDIOMA = (function () {
    var l = (document.documentElement.getAttribute("lang") || "es").slice(0, 2);
    return TEXTOS[l] ? l : "es";
  })();

  function t(clave) {
    var cadena = TEXTOS[IDIOMA][clave];
    if (cadena === undefined) cadena = TEXTOS.es[clave];
    /* Los huecos se rellenan en orden con el resto de los argumentos. Se hace
       a mano y no con una librería porque es lo único que hace falta. */
    for (var i = 1; i < arguments.length; i++) {
      cadena = cadena.replace("%s", arguments[i]);
    }
    return cadena;
  }

  /* ---------- Dónde se guarda ----------
     En localStorage, que es del navegador de quien mira la web: la farmacia no
     ve nada de esto. Puede fallar —ventana privada, almacenamiento bloqueado—
     y entonces no hay que romperse: se tira de esta copia en memoria y la cesta
     dura lo que dure la pestaña. Es peor, pero funciona.

     La clave no lleva el idioma a propósito: quien añade algo en español y
     luego cambia a catalán tiene que encontrar su cesta, no otra vacía. */
  var memoria = null;

  function acota(n) {
    n = parseInt(n, 10);
    if (isNaN(n) || n < 1) return 1;
    return n > TOPE_UNIDADES ? TOPE_UNIDADES : n;
  }

  function leer() {
    var crudo = null;
    try {
      crudo = window.localStorage.getItem(CLAVE);
    } catch (e) {
      return memoria || [];
    }
    if (!crudo) return [];
    var datos;
    try {
      datos = JSON.parse(crudo);
    } catch (e) {
      return [];
    }
    if (!Array.isArray(datos)) return [];
    /* Lo que sale de localStorage es texto que alguien ha podido tocar, y va a
       parar a un mensaje y a la pantalla: se valida como se validaría lo que
       llega de fuera. Una línea rota se cae, no se pinta a medias. */
    return datos.filter(function (it) {
      return it && typeof it.id === "string" && typeof it.nombre === "string";
    }).map(function (it) {
      return {
        id: it.id,
        nombre: it.nombre,
        formato: typeof it.formato === "string" ? it.formato : "",
        url: typeof it.url === "string" ? it.url : "",
        cantidad: acota(it.cantidad)
      };
    });
  }

  function guardar(items) {
    memoria = items;
    try {
      window.localStorage.setItem(CLAVE, JSON.stringify(items));
    } catch (e) {
      /* Sin sitio o sin permiso. La copia en memoria ya está puesta. */
    }
  }

  function unidades(items) {
    return items.reduce(function (t, it) { return t + it.cantidad; }, 0);
  }

  /* ---------- Las cuatro cosas que se pueden hacer ---------- */
  function anade(datos) {
    var items = leer();
    for (var i = 0; i < items.length; i++) {
      if (items[i].id === datos.id) {
        items[i].cantidad = acota(items[i].cantidad + 1);
        guardar(items);
        return items[i].cantidad;
      }
    }
    items.push({
      id: datos.id,
      nombre: datos.nombre,
      formato: datos.formato || "",
      url: datos.url || "",
      cantidad: 1
    });
    guardar(items);
    return 1;
  }

  function cambia(id, delta) {
    guardar(leer().map(function (it) {
      if (it.id !== id) return it;
      it.cantidad = acota(it.cantidad + delta);
      return it;
    }));
  }

  function quita(id) {
    guardar(leer().filter(function (it) { return it.id !== id; }));
  }

  function vacia() {
    guardar([]);
  }

  /* ---------- El mensaje ----------
     Se escribe solo, pero lo manda la persona desde su WhatsApp: puede leerlo y
     cambiarlo antes de darle a enviar, que para eso wa.me deja el texto
     preparado en lugar de mandarlo. */
  function lineas(items) {
    return items.map(function (it) {
      return "- " + it.cantidad + " x " + it.nombre +
        (it.formato ? " (" + it.formato + ")" : "");
    });
  }

  function mensaje(items, tope) {
    var puestas = lineas(items);
    var fuera = 0;

    /* Recortar por el final hasta que el enlace quepa. Mejor un mensaje que
       dice «y 25 más» que un enlace que no abre. */
    while (true) {
      var cola = "";
      if (fuera === 1) cola = t("mensaje_resto_uno");
      else if (fuera > 1) cola = t("mensaje_resto", fuera);
      var texto = t("mensaje_cabeza") + puestas.join("\n") + cola + t("mensaje_pie");
      /* Devuelve {texto, fuera}, no sólo la cadena: quien pinta la página
         necesita saber cuántas líneas se han quedado fuera para avisarlo. */
      if (!tope || encodeURIComponent(texto).length <= tope ||
          puestas.length <= 1) {
        return { texto: texto, fuera: fuera };
      }
      puestas.pop();
      fuera++;
    }
  }

  function topeDelTexto() {
    /* El tope es de la URL entera, así que se descuenta lo que ocupa la base. */
    return TOPE_URL - ("https://wa.me/" + WHATSAPP + "?text=").length;
  }

  function enlaceWhatsapp(items) {
    return "https://wa.me/" + WHATSAPP + "?text=" +
      encodeURIComponent(mensaje(items, topeDelTexto()).texto);
  }

  function enlaceCorreo(items) {
    return "mailto:" + CORREO +
      "?subject=" + encodeURIComponent(t("correo_asunto")) +
      "&body=" + encodeURIComponent(mensaje(items, null).texto);
  }

  /* ---------- Pintar ---------- */
  function escribe(el, s) {
    if (el) el.textContent = s;
  }

  function escapa(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function plural(n) {
    return n === 1 ? t("uno") : t("varios", n);
  }

  function avisa(s) {
    var zona = document.querySelector("[data-cesta-avisos]");
    if (!zona) return;
    /* Vaciar y volver a escribir: si el texto fuese idéntico al anterior
       —añadir dos veces el mismo producto— un lector de pantalla no lo
       anunciaría otra vez. */
    zona.textContent = "";
    window.setTimeout(function () { zona.textContent = s; }, 60);
  }

  function pintaContador(items) {
    var n = unidades(items);
    var enlaces = document.querySelectorAll("[data-cesta-contador]");
    for (var i = 0; i < enlaces.length; i++) {
      enlaces[i].hidden = false;
      escribe(enlaces[i].querySelector("[data-cesta-cuenta]"), String(n));
      enlaces[i].setAttribute("aria-label",
        n ? t("cesta_con", plural(n)) : t("cesta_vacia"));
      enlaces[i].classList.toggle("cesta-enlace-vacio", n === 0);
    }
  }

  function pintaBotones(items) {
    var botones = document.querySelectorAll("[data-cesta-anade]");
    for (var i = 0; i < botones.length; i++) botones[i].hidden = false;

    /* La línea de «ya tienes 2 en la cesta» que va junto al botón de la ficha. */
    var estados = document.querySelectorAll("[data-cesta-estado]");
    for (var j = 0; j < estados.length; j++) {
      var id = estados[j].getAttribute("data-cesta-estado");
      var cuantos = 0;
      for (var k = 0; k < items.length; k++) {
        if (items[k].id === id) cuantos = items[k].cantidad;
      }
      if (!cuantos) {
        estados[j].hidden = true;
        estados[j].innerHTML = "";
        continue;
      }
      estados[j].hidden = false;
      estados[j].innerHTML = t("ya_tienes", cuantos);
    }
  }

  function pintaPagina(items) {
    var lista = document.querySelector("[data-cesta-lista]");
    if (!lista) return;

    var sinNada = document.querySelector("[data-cesta-vacia]");
    var conAlgo = document.querySelector("[data-cesta-llena]");
    if (sinNada) sinNada.hidden = items.length > 0;
    if (conAlgo) conAlgo.hidden = items.length === 0;

    lista.innerHTML = items.map(function (it) {
      var nombre = it.url
        ? '<a href="' + escapa(it.url) + '">' + escapa(it.nombre) + "</a>"
        : escapa(it.nombre);
      return '<li class="cesta-linea">' +
        '<div class="cesta-que"><strong>' + nombre + "</strong>" +
          (it.formato ? "<small>" + escapa(it.formato) + "</small>" : "") +
        "</div>" +
        '<div class="cesta-cantidad">' +
          '<button type="button" data-cesta-menos="' + escapa(it.id) + '"' +
            ' aria-label="' + escapa(t("quitar_una", it.nombre)) + '"' +
            (it.cantidad <= 1 ? " disabled" : "") + ">&minus;</button>" +
          '<span aria-hidden="true">' + it.cantidad + "</span>" +
          '<button type="button" data-cesta-mas="' + escapa(it.id) + '"' +
            ' aria-label="' + escapa(t("anadir_una", it.nombre)) + '"' +
            (it.cantidad >= TOPE_UNIDADES ? " disabled" : "") + ">+</button>" +
        "</div>" +
        '<button type="button" class="cesta-quitar" data-cesta-quita="' +
          escapa(it.id) + '" aria-label="' +
          escapa(t("quitar_esto", it.nombre)) + '">' + escapa(t("quitar")) +
        "</button></li>";
    }).join("");

    var wa = document.querySelector("[data-cesta-whatsapp]");
    if (wa) wa.href = enlaceWhatsapp(items);
    var correo = document.querySelector("[data-cesta-correo]");
    if (correo) correo.href = enlaceCorreo(items);
    escribe(document.querySelector("[data-cesta-total]"), plural(unidades(items)));

    /* Si el mensaje de WhatsApp no cabe entero hay que decirlo aquí: enviar un
       encargo recortado creyendo que iba completo es el peor fallo que puede
       tener esta página. Por correo y copiando la lista sí va todo. */
    var recorte = document.querySelector("[data-cesta-recorte]");
    if (recorte) {
      var fuera = mensaje(items, topeDelTexto()).fuera;
      recorte.hidden = fuera === 0;
      if (fuera) recorte.innerHTML = t("recorte", fuera);
    }
  }

  function pinta() {
    var items = leer();
    pintaContador(items);
    pintaBotones(items);
    pintaPagina(items);
  }

  /* Tras quitar una línea, el foco se queda en un botón que ya no existe. Lo
     llevamos al primer «Quitar» que siga habiendo, y si no queda ninguno al
     título, que es donde está la explicación de que la cesta está vacía. */
  function enfoca() {
    var primero = document.querySelector("[data-cesta-quita]");
    if (primero) {
      primero.focus();
      return;
    }
    var titulo = document.querySelector("[data-cesta-vacia] h2") ||
                 document.querySelector("h1");
    if (titulo) {
      titulo.setAttribute("tabindex", "-1");
      titulo.focus();
    }
  }

  function aPelo(s) {
    var area = document.createElement("textarea");
    area.value = s;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    var ok = false;
    try {
      ok = document.execCommand("copy");
    } catch (e) {
      ok = false;
    }
    document.body.removeChild(area);
    return ok;
  }

  function copia(b) {
    var items = leer();
    if (!items.length) return;
    var s = mensaje(items, null).texto;
    var dicho = function (ok) {
      escribe(b, ok ? t("copiada") : t("no_copiada"));
      avisa(ok ? t("copiada_aviso") : t("no_copiada_aviso"));
      window.setTimeout(function () { escribe(b, t("copiar")); }, 2000);
    };
    /* El portapapeles moderno no existe en file:// ni en http sin cifrar, que
       es justo como se abre esto al probarlo en local. De ahí la copia de
       seguridad con un textarea, que funciona en los dos sitios. */
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(s).then(
        function () { dicho(true); },
        function () { dicho(aPelo(s)); });
      return;
    }
    dicho(aPelo(s));
  }

  function cosa(b) {
    return {
      id: b.getAttribute("data-id"),
      nombre: b.getAttribute("data-nombre"),
      formato: b.getAttribute("data-formato"),
      url: b.getAttribute("data-url")
    };
  }

  /* ---------- Los clics ----------
     Uno solo, delegado en el documento: la lista de la cesta se vuelve a pintar
     entera en cada cambio, así que un escuchador por botón habría que volver a
     ponerlo cada vez. */
  function haz(e) {
    if (!e.target || !e.target.closest) return;
    var b = e.target.closest("button, a");
    if (!b) return;

    if (b.hasAttribute("data-cesta-anade")) {
      e.preventDefault();
      if (!b.getAttribute("data-id")) return;
      anade(cosa(b));
      pinta();
      avisa(t("anadido", b.getAttribute("data-nombre"),
              plural(unidades(leer()))));
      b.classList.add("anadido");
      window.setTimeout(function () { b.classList.remove("anadido"); }, 1200);
      return;
    }

    var mas = b.getAttribute("data-cesta-mas");
    var menos = b.getAttribute("data-cesta-menos");
    if (mas || menos) {
      var id = mas || menos;
      cambia(id, mas ? 1 : -1);
      pinta();
      /* Volver a dar el foco al mismo botón: sin esto se pierde al repintar y
         quien use el teclado se queda en el cuerpo de la página. */
      var sigue = document.querySelector(
        "[" + (mas ? "data-cesta-mas" : "data-cesta-menos") +
        '="' + id.replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"]');
      if (sigue && !sigue.disabled) sigue.focus();
      else enfoca();
      return;
    }

    var fuera = b.getAttribute("data-cesta-quita");
    if (fuera) {
      quita(fuera);
      pinta();
      avisa(t("quitado", plural(unidades(leer()))));
      enfoca();
      return;
    }

    if (b.hasAttribute("data-cesta-vaciar")) {
      vacia();
      pinta();
      avisa(t("vaciada"));
      enfoca();
      return;
    }

    if (b.hasAttribute("data-cesta-copia")) copia(b);
  }

  /* ---------- Arranque ---------- */
  function arranca() {
    var avisos = document.querySelectorAll("[data-cesta-sinjs]");
    for (var i = 0; i < avisos.length; i++) avisos[i].hidden = true;
    document.addEventListener("click", haz);
    /* Dos pestañas abiertas son la misma cesta: si se añade en una, la otra se
       entera y no se queda enseñando una cuenta que ya no es. Vale también si
       las dos pestañas están en idiomas distintos. */
    window.addEventListener("storage", function (e) {
      if (!e.key || e.key === CLAVE) pinta();
    });
    pinta();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", arranca);
  } else {
    arranca();
  }
})();

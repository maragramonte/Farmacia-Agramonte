#!/usr/bin/env python3
"""
Escribe las páginas del catálogo a partir de herramientas/catalogo-datos.json.

    python herramientas/catalogo.py

Genera dos cosas por cada categoría del JSON:

    catalogo-<id>.html              la rejilla de tarjetas de la categoría.
    catalogo-<id>-<producto>.html   la ficha de cada uno de sus productos.

Y dos más, que no dependen del JSON pero comparten con ellas cabecera y pie:

    historia.html                   quiénes somos y de dónde viene la farmacia.
                                    El texto se edita EN ESTE FICHERO, en
                                    pagina_historia().
    cesta.html                      la lista de lo que alguien quiere encargar.
                                    Lo que la rellena es cesta.js, en el
                                    navegador; aquí sólo se escribe el molde.

Existe por una razón muy concreta: la tira de categorías que va arriba de cada
página tiene que listarlas todas, así que añadir una obligaba a tocar las diez a
mano. Ahora que además hay una ficha por producto, escribir esto a mano sería
una errata esperando a ocurrir.

La web sigue siendo estática: esto no se ejecuta al visitarla, sólo cuando
cambian los productos. Igual que herramientas/tarjeta-social.py con og.png.

Para cambiar productos o precios se edita el JSON, no este fichero ni el HTML.
El HTML generado NO se edita a mano: se pierde al volver a ejecutar esto.
"""

import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent.parent
DATOS = Path(__file__).resolve().parent / "catalogo-datos.json"
CARPETA_FOTOS = RAIZ / "fotos"

# En orden de preferencia: si un producto tiene la foto en dos formatos, gana el
# primero de la lista.
EXTENSIONES_FOTO = (".webp", ".avif", ".jpg", ".jpeg", ".png")

BASE = "https://maragramonte.github.io/Farmacia-Agramonte/"
WHATSAPP = "34661192472"
TELEFONO_ENLACE = "+34933195921"
TELEFONO_VISIBLE = "933 19 59 21"
WHATSAPP_VISIBLE = "661 192 472"
CORREO = "farmacia.lallana@gmail.com"

# Los iconos, en la misma línea que los del resto del sitio: trazo, sin relleno.
ICONOS = {
    "capsula": '<rect x="3" y="8" width="18" height="8" rx="4"/><line x1="12" y1="8" x2="12" y2="16"/>',
    "espejo":  '<circle cx="12" cy="9" r="6"/><path d="M12 15v6"/><path d="M9 21h6"/>',
    "bote":    '<path d="M10 2h4v4l2 3v11H8V9l2-3Z"/><line x1="8" y1="13" x2="16" y2="13"/>',
    "sol":     '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.4 1.4M17.6 17.6 19 19M19 5l-1.4 1.4M6.4 17.6 5 19"/>',
    "peine":   '<path d="M4 9h16v3a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4V9Z"/><path d="M8 9V5M12 9V5M16 9V5"/>',
    "cara":    '<circle cx="12" cy="12" r="9"/><circle cx="9" cy="10" r="1"/><circle cx="15" cy="10" r="1"/><path d="M9 15c1.8 1.4 4.2 1.4 6 0"/>',
    "corazon": '<path d="M12 20s-7-4.4-7-9a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 4.6-7 9-7 9Z"/>',
    "manzana": '<path d="M12 8c-3 0-5 2.4-5 5.8S9.5 21 12 21s5-3.8 5-7.2S15 8 12 8Z"/><path d="M12 8V5"/><path d="M12 6c1.6 0 3-1.2 3-3-1.6 0-3 1.2-3 3Z"/>',
    "hoja":    '<path d="M20 4C10 4 4 9 4 16c0 2 1 4 1 4s6-1 9-4c3-3 6-8 6-12Z"/><path d="M5 20c3-6 7-9 11-11"/>',
    "cruz":    '<line x1="12" y1="4" x2="12" y2="20"/><line x1="4" y1="12" x2="20" y2="12"/>',
}

# Las secciones de la ficha, en el orden en que se leen, y con qué se pinta
# cada una. Todas son opcionales: si el producto no trae la clave en el JSON, la
# sección no aparece. Una ficha corta es mejor que un epígrafe vacío, y mucho
# mejor que un epígrafe inventado, que aquí además sería un consejo de salud.
SECCIONES = [
    ("descripcion",  "Para qué es",    "p"),
    ("modo_empleo",  "Modo de empleo", "ol"),
    ("composicion",  "Composición",    "p"),
    ("advertencias", "Advertencias",   "ul"),
]

ICONO_WHATSAPP = (
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 '
    '15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm5.6 14.1c-.2.7-1.4 1.3-1.9 1.3-.5 0-1.1.2-3.6-.8-3-1.3-4.9-4.4'
    '-5-4.6-.2-.2-1.2-1.6-1.2-3s.7-2.1 1-2.4c.3-.3.6-.4.8-.4h.6c.2 0 .4 0 .7.5l1 2.3c0 .2 0 .4-.1.6l'
    '-.4.5c-.2.2-.4.3-.2.7.2.3.9 1.4 1.9 2.3 1.3 1.1 2.3 1.5 2.7 1.6.2 0 .4 0 .6-.2l.9-1c.2-.2.4-.2.7'
    '-.1l2.2 1c.3.2.4.3.5.4.1.2.1.7-.2 1.3Z"/></svg>'
)

ICONO_CESTA = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h16l-1.4 11a2 2 0 0 1-2 1.8H7.4a2 2 0 0 1-2-1.8L4 8Z"/>'
    '<path d="M9 8V5.5a3 3 0 0 1 6 0V8"/></svg>'
)

ICONO_MAS = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><line x1="12" y1="5" x2="12" y2="19"/>'
    '<line x1="5" y1="12" x2="19" y2="12"/></svg>'
)

ICONO_AVISO = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2 20h20L12 3Z"/>'
    '<line x1="12" y1="10" x2="12" y2="14"/><circle cx="12" cy="17" r=".6" fill="currentColor" stroke="none"/></svg>'
)


def escapa(t):
    """Lo que venga del JSON va a parar dentro del HTML, así que se escapa."""
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def enlace_whatsapp(consulta):
    texto = "Hola, quería preguntar por %s." % consulta
    return "https://wa.me/%s?text=%s" % (WHATSAPP, quote(texto, safe=""))


def slug_producto(p):
    """La parte de la URL que identifica al producto dentro de su categoría.

    Se saca del nombre, pero el JSON puede fijarla con "id". Hace falta poder:
    renombrar un producto le cambiaría la URL, y una URL que ya está en Google
    no se cambia a la ligera."""
    if p.get("id"):
        return p["id"]
    t = unicodedata.normalize("NFKD", p["nombre"])
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def ruta_producto(c, p):
    return "catalogo-%s-%s.html" % (c["id"], slug_producto(p))


def id_cesta(c, p):
    """Cómo se llama el producto dentro de la cesta de quien mira la web.

    Es la categoría y el slug, que juntos ya son únicos —lo comprueba
    comprueba_urls_unicas— y no cambian al renombrar un producto si lleva su
    clave "id". Eso importa más de lo que parece: la cesta vive en el navegador
    de la persona, así que un id que cambie le deja dentro una línea huérfana
    que ya no enlaza a ninguna ficha."""
    return "%s-%s" % (c["id"], slug_producto(p))


def boton_anadir(c, p):
    """El botón de añadir a la cesta.

    Nace con hidden y lo destapa cesta.js. Sin JavaScript no hay cesta, y un
    botón que no hace nada es peor que no tenerlo: el de WhatsApp, que es un
    enlace de verdad, sigue ahí al lado y funciona siempre.

    El formato va sin la marca amarilla de «pendiente»: esto no se lee, se
    copia a un mensaje de WhatsApp, y «(Formato pendiente)» ahí no se entiende."""
    return ('<button type="button" class="anadir" data-cesta-anade hidden'
            ' data-id="%s" data-nombre="%s" data-formato="%s" data-url="%s">%s Añadir</button>'
            % (escapa(id_cesta(c, p)), escapa(p["nombre"]),
               escapa(p.get("formato") or ""), escapa(ruta_producto(c, p)),
               ICONO_MAS))


def precio_html(p, sangria):
    """El precio, o nada en absoluto.

    La farmacia ha decidido no publicar precios: el catálogo enseña lo que hay y
    el precio se pregunta. Un precio expuesto al público es una oferta, y
    mantener decenas al día en una web estática es de esas cosas que se quedan
    viejas sin que nadie se entere.

    Ojo con lo que NO se hace aquí: no se deja el hueco amarillo de .pendiente.
    Ese amarillo quiere decir «esto falta», y esto no falta, es que no va. Si
    algún día se quiere publicar el de un producto concreto, basta con ponerle
    "precio" en el JSON y sale sólo en ese."""
    if not p.get("precio"):
        return ""
    return '\n%s<p class="precio">%s</p>' % (sangria, escapa(p["precio"]))


def formato_html(p):
    """El envase y el contenido, o la marca amarilla si todavía no se saben.

    Aquí el amarillo sí toca, al revés que con el precio: todo producto tiene un
    formato, así que no tenerlo es una ficha a medias y hay que verlo. El precio
    no lleva marca porque no falta, es que no se publica."""
    if not p.get("formato"):
        return '<span class="pendiente">Formato pendiente</span>'
    return escapa(p["formato"])


def resumen_html(p):
    """La línea que explica el producto, o la marca amarilla si no está.

    Un export del programa de gestión trae nombres y formatos, no frases: por
    eso esto puede faltar y hay que verlo. Igual que el formato."""
    if not p.get("resumen"):
        return '<span class="pendiente">Resumen pendiente</span>'
    return escapa(p["resumen"])


def consulta_de(p):
    """Lo que se escribe solo en el WhatsApp al pulsar Preguntar.

    Si el JSON no la trae, se saca del nombre. Sale un poco más seca que una
    escrita a mano —«el La Roche-Posay Anthelios...»— pero un mensaje algo tieso
    es mejor que cuarenta productos sin botón que funcione."""
    return p.get("consulta") or p["nombre"]


def descripcion_meta(p):
    """La meta description de la ficha. Se salta lo que falte, que si no queda
    un doble espacio o una frase que empieza por la nada."""
    trozos = [t for t in (p.get("resumen"), p.get("formato")) if t]
    return "%s en la Farmàcia Agramonte, Plaça de la Llana 11, El Born (Barcelona)." % (
        " ".join(trozos) if trozos else p["nombre"])


def foto_de(c, p):
    """La foto del producto dentro de fotos/, o None si todavía no la hay.

    Dos maneras. Si el JSON trae "foto", manda ésa. Si no, se busca en fotos/ un
    fichero que se llame igual que la página del producto, y ésa es la buena el
    día que lleguen las 54: basta con dejar el fichero bien nombrado y aparece
    sola. Escribir a mano 54 claves "foto" es una errata esperando a ocurrir, que
    es la misma razón por la que existe este script."""
    if p.get("foto"):
        return "fotos/%s" % p["foto"]
    base = "%s-%s" % (c["id"], slug_producto(p))
    for ext in EXTENSIONES_FOTO:
        if (CARPETA_FOTOS / (base + ext)).exists():
            return "fotos/%s%s" % (base, ext)
    return None


def foto_html(c, p, icono):
    ruta = foto_de(c, p)
    if ruta:
        return ('<div class="foto foto-real"><img src="%s" alt="%s" loading="lazy"></div>'
                % (escapa(ruta), escapa(p["nombre"])))
    return '<div class="foto"><svg viewBox="0 0 24 24" aria-hidden="true">%s</svg></div>' % icono


def tira(categorias, actual):
    """La tira de arriba. Con página propia van como enlace; el resto, en texto."""
    filas = []
    for c in categorias:
        nombre = escapa(c["nombre"])
        if c["id"] == actual:
            filas.append('    <a href="catalogo-%s.html" aria-current="page">%s</a>' % (c["id"], nombre))
        else:
            filas.append('    <a href="catalogo-%s.html">%s</a>' % (c["id"], nombre))
    # La actual va primera, que es donde el ojo la busca.
    orden = [f for f in filas if 'aria-current' in f] + [f for f in filas if 'aria-current' not in f]
    return "\n".join(orden)


def ficha(c, p, icono):
    """Una tarjeta de la rejilla.

    El título lleva a la ficha del producto. Debajo, las dos maneras de pedirlo:
    «Añadir», que lo apunta en la cesta para encargar varias cosas de una vez, y
    «Preguntar», que sigue yendo directo a WhatsApp, porque quien ya sabe lo que
    quiere no tiene por qué dar un rodeo por la cesta.

    Las dos van dentro de .acciones, y es ese bloque el que se pega al fondo de
    la tarjeta. Antes el margen automático vivía en el botón de WhatsApp; con dos
    botones eso habría dejado un hueco distinto en cada tarjeta."""
    return """    <article class="producto">
      %s
      <div class="cuerpo">
        <h2><a href="%s">%s</a></h2>
        <p class="resumen">%s</p>
        <p class="formato">%s</p>%s
        <div class="acciones">
          %s
          <a class="boton" href="%s" target="_blank" rel="noopener" aria-label="Preguntar por %s por WhatsApp">Preguntar</a>
        </div>
      </div>
    </article>""" % (
        foto_html(c, p, icono), escapa(ruta_producto(c, p)), escapa(p["nombre"]),
        resumen_html(p), formato_html(p), precio_html(p, " " * 8),
        boton_anadir(c, p),
        escapa(enlace_whatsapp(consulta_de(p))), escapa(consulta_de(p)))


def aviso_plantilla():
    return """
<div class="aviso-plantilla">
  <div class="contenedor">
    %s
    <div>
      <strong class="rotulo">Plantilla de ejemplo</strong>
      <p>
        Los productos y los formatos de esta página <strong>son
        inventados</strong> y están aquí sólo para ver la maquetación. Nada de lo
        que se lee abajo es el catálogo de la farmacia. No enlazar esta página ni
        darla por buena hasta sustituirlo por productos reales.
      </p>
    </div>
  </div>
</div>
""" % ICONO_AVISO


CIERRE_PEDIDO = """  <div class="cierre">
    <h2>Cómo se pide</h2>
    <p>
      Con «Añadir» vas apuntando lo que quieras en <a href="cesta.html">tu
      cesta</a>, que se queda guardada en este navegador y puedes cambiar cuando
      quieras. Al acabar, la cesta escribe sola el mensaje y nos lo mandas por
      WhatsApp: lo preparamos, te confirmamos el precio y lo recoges en el
      mostrador.
    </p>
    <p>
      <strong>Aquí no se paga nada</strong> y no te pedimos ningún dato: esto no
      es una tienda en línea, es la manera de encargar sin tener que escribirnos
      los productos uno a uno. El mostrador es además donde podemos aconsejarte.
    </p>
    <p>
      Si prefieres llamar, el número es el
      <a href="tel:%s">%s</a>, de lunes a sábado de 9:00 a
      14:30 y de 16:00 a 20:30.
    </p>
  </div>
""" % (TELEFONO_ENLACE, TELEFONO_VISIBLE)


def cuerpo_categoria(c, icono):
    """Las fichas, o —si la categoría no lleva lista— la explicación de por qué.

    En ese segundo caso no se añade además el cierre de «cómo se pide»: diría
    lo mismo dos veces seguidas. El teléfono se mete aquí en su lugar."""
    if c["productos"]:
        fichas = "\n\n".join(ficha(c, p, icono) for p in c["productos"])
        return ('  <div class="productos">\n\n%s\n\n  </div>\n' % fichas) + "\n" + CIERRE_PEDIDO

    sp = c["sin_productos"]
    parrafos = "\n".join("    <p>%s</p>" % escapa(t) for t in sp["parrafos"])
    return """  <div class="cierre">
    <h2>%s</h2>
%s
    <p>
      Para encargar: <a href="https://wa.me/%s" target="_blank" rel="noopener">WhatsApp</a>
      o <a href="tel:%s">%s</a>, de lunes a sábado de 9:00 a 14:30 y de 16:00 a 20:30.
    </p>
  </div>
""" % (escapa(sp["titulo"]), parrafos, WHATSAPP, TELEFONO_ENLACE, TELEFONO_VISIBLE)


def seccion(p, clave, titulo, envoltura):
    """Un epígrafe de la ficha, o nada si el producto no trae ese dato."""
    textos = p.get(clave)
    if not textos:
        return ""
    if envoltura == "p":
        interior = "\n".join("    <p>%s</p>" % escapa(t) for t in textos)
    else:
        puntos = "\n".join("      <li>%s</li>" % escapa(t) for t in textos)
        interior = "    <%s>\n%s\n    </%s>" % (envoltura, puntos, envoltura)
    # Las advertencias se marcan aparte: es lo único de la ficha que hay que
    # leer sí o sí, y no debe leerse como un párrafo más.
    extra = " detalle-advertencias" if clave == "advertencias" else ""
    return '  <section class="detalle%s">\n    <h2>%s</h2>\n%s\n  </section>\n\n' % (
        extra, escapa(titulo), interior)


def otros_de(c, actual):
    """El resto de la categoría, al pie de la ficha. Sin foto y sin precio: es
    un índice para seguir mirando, no otra rejilla de tarjetas."""
    resto = [p for p in c["productos"] if slug_producto(p) != slug_producto(actual)]
    if not resto:
        return ""
    puntos = "\n".join(
        '      <li><a href="%s"><strong>%s</strong><small>%s</small></a></li>'
        % (escapa(ruta_producto(c, p)), escapa(p["nombre"]), formato_html(p))
        for p in resto)
    return """  <section class="otros">
    <h2>Más de %s</h2>
    <ul>
%s
    </ul>
    <a class="volver" href="catalogo-%s.html">Ver toda la categoría</a>
  </section>
""" % (escapa(c["nombre"]), puntos, c["id"])


def documento(titulo, descripcion, ruta, contenido, es_plantilla,
              noindex=False, aqui=None):
    """El esqueleto que comparten la página de categoría, la ficha de producto,
    la historia y la cesta: cabeza, cabecera, aviso, <main> y pie. Lo de dentro
    de <main> lo pone quien llama. Nació al montar las fichas, para no tener dos
    copias de la cabecera que se separasen a la primera de cambio.

    "aqui" dice en qué entrada del menú estamos, para marcarla con aria-current:
    "historia", "cesta" o nada."""
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    aqui_historia = ' aria-current="page"' if aqui == "historia" else ""
    aqui_cesta = ' aria-current="page"' if aqui == "cesta" else ""
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- ESTE FICHERO SE GENERA. No lo edites a mano: se pierde al ejecutar
     python herramientas/catalogo.py. Los productos están en
     herramientas/catalogo-datos.json. -->
%s<link rel="canonical" href="%s%s">
<meta name="description" content="%s">
<title>%s</title>
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#2a1d12">
<!-- Tipografías propias, servidas desde este mismo repositorio. -->
<link rel="preload" href="tipografias/playfair-display-variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="tipografias/karla-variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="tipografias.css">
<link rel="stylesheet" href="marca.css">
<link rel="stylesheet" href="catalogo.css">
<link rel="stylesheet" href="cesta.css">
<!-- La cesta es lo único de la web que se ejecuta en el navegador. Con defer
     para que no frene el pintado: lo que depende de ella nace con hidden y se
     destapa al cargar, así que nada parpadea ni se ve a medias. -->
<script src="cesta.js" defer></script>
</head>
<body>

<!-- Lo que se le dice a un lector de pantalla al añadir o quitar de la cesta.
     Está en todas las páginas porque desde todas se puede añadir. -->
<div class="solo-lectores" role="status" aria-live="polite" data-cesta-avisos></div>

<header class="cabecera">
  <div class="contenedor">
    <a class="marca" href="index.html">Farmàcia Agramonte</a>
    <nav class="nav" aria-label="Principal">
      <a href="index.html">Inicio</a>
      <a href="index.html#categorias">Categorías</a>
      <a href="historia.html"%s>Historia</a>
      <a href="index.html#contacto">Contacto</a>
    </nav>
    <a class="cesta-enlace" href="cesta.html" data-cesta-contador hidden%s>
      %s
      <span class="cesta-rotulo">Cesta</span>
      <span class="cesta-cuenta" data-cesta-cuenta>0</span>
    </a>
    <a class="boton" href="https://wa.me/%s" target="_blank" rel="noopener">
      %s
      Pedir
    </a>
  </div>
</header>
%s
<main class="contenedor">
%s
</main>

<footer class="pie">
  <div class="contenedor">
    <p>© 2026 Farmàcia Agramonte</p>
    <p>
      <a href="aviso-legal.html">Aviso legal</a> ·
      <a href="privacidad.html">Privacidad</a> ·
      <a href="cookies.html">Cookies</a>
    </p>
  </div>
</footer>

</body>
</html>
""" % (robots, BASE, ruta, escapa(descripcion), escapa(titulo),
       aqui_historia, aqui_cesta, ICONO_CESTA,
       WHATSAPP, ICONO_WHATSAPP,
       aviso_plantilla() if es_plantilla else "",
       contenido)


def pagina(c, categorias):
    """La página de una categoría: portada, tira y rejilla."""
    icono = ICONOS[c["icono"]]
    es_plantilla = c.get("plantilla", False)
    coletilla = " (plantilla)" if es_plantilla else ""

    contenido = """
  <p class="migas"><a href="index.html">Inicio</a> › <a href="index.html#categorias">Categorías</a> › %s</p>

  <div class="portada-categoria">
    <h1>%s</h1>
    <p>%s</p>
  </div>

  <nav class="tira" aria-label="Categorías del catálogo">
%s
  </nav>

%s""" % (escapa(c["nombre"]), escapa(c["nombre"]), escapa(c["intro"]),
         tira(categorias, c["id"]), cuerpo_categoria(c, icono))

    # Sin noindex: las diez se indexan. Decisión de la farmacia, tomada sabiendo
    # que lo que Google recoge son los precios de ejemplo y que un precio
    # expuesto al público es una oferta. Al poner los reales esto no cambia.
    return documento(
        titulo="%s%s — Farmàcia Agramonte" % (c["nombre"], coletilla),
        descripcion="%s en la Farmàcia Agramonte, Plaça de la Llana 11, El Born (Barcelona)." % c["nombre"],
        ruta="catalogo-%s.html" % c["id"],
        contenido=contenido,
        es_plantilla=es_plantilla)


def pagina_producto(c, p):
    """La ficha de un producto: foto, datos, epígrafes y el resto de la categoría."""
    icono = ICONOS[c["icono"]]
    es_plantilla = c.get("plantilla", False)
    coletilla = " (plantilla)" if es_plantilla else ""

    secciones = "".join(seccion(p, clave, titulo, env) for clave, titulo, env in SECCIONES)

    contenido = """
  <p class="migas"><a href="index.html">Inicio</a> › <a href="index.html#categorias">Categorías</a> › <a href="catalogo-%s.html">%s</a> › %s</p>

  <div class="ficha-producto">
    %s
    <div class="datos">
      <h1>%s</h1>
      <p class="formato">%s</p>
      <p class="resumen">%s</p>%s
      <div class="acciones">
        %s
        <a class="boton" href="%s" target="_blank" rel="noopener" aria-label="Preguntar por %s por WhatsApp">
          %s
          Preguntar por WhatsApp
        </a>
      </div>
      <p class="cesta-estado" data-cesta-estado="%s" hidden></p>
      <p class="nota-consejo">
        Desde aquí no se paga nada: «Añadir» lo apunta en tu cesta y, cuando
        acabes de mirar, nos la mandas de una vez por WhatsApp. Lo preparamos,
        te confirmamos el precio y lo recoges en el mostrador, que es donde
        además podemos aconsejarte. Si lo prefieres, llámanos al
        <a href="tel:%s">%s</a>.
      </p>
    </div>
  </div>

%s%s""" % (
        c["id"], escapa(c["nombre"]), escapa(p["nombre"]),
        foto_html(c, p, icono), escapa(p["nombre"]), formato_html(p),
        resumen_html(p), precio_html(p, " " * 6),
        boton_anadir(c, p),
        escapa(enlace_whatsapp(consulta_de(p))), escapa(consulta_de(p)), ICONO_WHATSAPP,
        escapa(id_cesta(c, p)),
        TELEFONO_ENLACE, TELEFONO_VISIBLE,
        secciones, otros_de(c, p))

    # Mientras la categoría sea plantilla, sus fichas van con noindex y fuera del
    # sitemap. Que las diez páginas de categoría se indexen fue una decisión
    # tomada a sabiendas; una ficha inventada por producto es otra cosa: son
    # decenas de páginas flacas, con un precio de ejemplo que se lee como gratis
    # y —en cuanto se rellenen los epígrafes— con texto de salud que no ha
    # firmado nadie. Al quitar "plantilla": true del JSON se indexan solas.
    return documento(
        titulo="%s%s — %s — Farmàcia Agramonte" % (p["nombre"], coletilla, c["nombre"]),
        descripcion=descripcion_meta(p),
        ruta=ruta_producto(c, p),
        contenido=contenido,
        es_plantilla=es_plantilla,
        noindex=es_plantilla)


def pagina_cesta():
    """cesta.html: la lista de lo que alguien quiere encargar.

    La pinta cesta.js leyendo el localStorage de quien la abre, así que lo que
    se escribe aquí son los tres estados posibles, los tres ya en el HTML y dos
    de ellos con hidden:

      sin JavaScript   lo único que se ve si cesta.js no carga. Nace visible a
                       propósito: es el único estado honesto cuando la cesta no
                       puede funcionar, y dice cómo pedir de todas formas.
      cesta vacía      no ha añadido nada.
      cesta con cosas  la lista, con las cantidades y los botones.

    Va con noindex y fuera del sitemap.xml, y no por prudencia: es una página
    distinta para cada visitante y vacía para Google, que no tiene cesta. Que
    salga en los resultados de búsqueda no le sirve a nadie."""
    contenido = """
  <p class="migas"><a href="index.html">Inicio</a> › <a href="index.html#categorias">Categorías</a> › Tu cesta</p>

  <div class="portada-categoria">
    <h1>Tu cesta</h1>
    <p>
      Lo que has apuntado para encargar. Se guarda <strong>sólo en este
      navegador</strong>: no nos llega nada, ni lo vemos, hasta que nos mandes
      el mensaje tú.
    </p>
  </div>

  <div class="cesta-sinjs" data-cesta-sinjs>
    <p>
      <strong>La cesta necesita JavaScript</strong>, y en este navegador está
      desactivado o no ha llegado a cargarse. El resto del catálogo funciona
      igual: puedes verlo todo y pedirnos lo que quieras por WhatsApp.
    </p>
    <p>
      Escríbenos al <a href="https://wa.me/%s" target="_blank" rel="noopener">%s</a>
      o llama al <a href="tel:%s">%s</a>, de lunes a sábado de 9:00 a 14:30 y de
      16:00 a 20:30.
    </p>
  </div>

  <div class="cesta-vacia" data-cesta-vacia hidden>
    <h2>Todavía no has apuntado nada</h2>
    <p>
      Entra en una categoría y pulsa «Añadir» en lo que te interese. Puedes
      juntar cosas de categorías distintas: la cesta es una sola.
    </p>
    <p><a href="index.html#categorias">Ver las categorías</a></p>
  </div>

  <div data-cesta-llena hidden>
    <ul class="cesta-lista" data-cesta-lista></ul>

    <p class="cesta-resumen">
      En la cesta: <strong data-cesta-total>0 productos</strong>
      <span>Sin precios: te los confirmamos al contestarte.</span>
    </p>

    <p class="cesta-recorte" data-cesta-recorte hidden></p>

    <div class="cesta-acciones">
      <a class="boton" href="https://wa.me/%s" target="_blank" rel="noopener" data-cesta-whatsapp>
        %s
        Enviar el encargo
      </a>
      <button type="button" class="cesta-secundario" data-cesta-copia>Copiar la lista</button>
      <a class="cesta-secundario" href="mailto:%s" data-cesta-correo>Enviarlo por correo</a>
      <button type="button" class="cesta-secundario cesta-vaciar" data-cesta-vaciar>Vaciar la cesta</button>
    </div>
  </div>

  <div class="cierre">
    <h2>Qué pasa al enviarlo</h2>
    <p>
      Se abre tu WhatsApp con el mensaje escrito: puedes leerlo, cambiar lo que
      quieras y enviarlo tú. <strong>Aquí no se cobra nada y no te pedimos
      ningún dato</strong>; esto no es una tienda en línea, es la manera de
      encargar sin escribirnos los productos uno a uno.
    </p>
    <p>
      Te contestamos con el precio y cuándo lo tienes listo, y se paga al
      recogerlo en el mostrador, que es donde además podemos aconsejarte. Si
      prefieres llamar, el número es el <a href="tel:%s">%s</a>.
    </p>
    <p>
      De <strong>medicamentos</strong> no hay catálogo y no entran en la cesta:
      <a href="catalogo-medicamentos.html">ahí se explica</a> cómo se encarga
      una receta.
    </p>
  </div>
""" % (WHATSAPP, WHATSAPP_VISIBLE, TELEFONO_ENLACE, TELEFONO_VISIBLE,
       WHATSAPP, ICONO_WHATSAPP, CORREO,
       TELEFONO_ENLACE, TELEFONO_VISIBLE)

    return documento(
        titulo="Tu cesta — Farmàcia Agramonte",
        descripcion="Lo que has apuntado para encargar en la Farmàcia Agramonte, "
                    "Plaça de la Llana 11, El Born (Barcelona).",
        ruta="cesta.html",
        contenido=contenido,
        es_plantilla=False,
        noindex=True,
        aqui="cesta")


# El reportaje de prensa. Es el único enlace a un sitio ajeno que hay en la web
# aparte de WhatsApp, y va aquí arriba para que se vea de un vistazo que existe.
PRENSA_URL = "https://www.larepublica.cat/coronavirus/reportatge-la-barcelona-que-no-es-resigna/"
PRENSA_TITULO = "Coronavirus: La Barcelona que no se resigna"
PRENSA_MEDIO = "La República"


def pagina_historia():
    """historia.html: quiénes somos y de dónde viene la farmacia.

    El texto lo escribe la farmacia y se edita AQUÍ, en este fichero, no en el
    HTML, que se pierde al regenerar. Está en el generador y no en
    catalogo-datos.json porque ese JSON es de productos; esto es prosa, como el
    CIERRE_PEDIDO de arriba.

    Se genera en vez de escribirse a mano por una razón concreta: es una página
    del menú principal, así que comparte cabecera, menú y contador de la cesta
    con las cincuenta y ocho de catálogo. Escrita a mano habría una tercera
    copia de esa cabecera —ya hay dos, aquí y en index.html— y el día que el
    menú cambie se quedaría atrás sin que nadie lo note."""
    contenido = """
  <p class="migas"><a href="index.html">Inicio</a> › Quiénes somos</p>

  <div class="portada-categoria">
    <h1>Quiénes somos</h1>
    <p>
      En la Farmàcia Agramonte nos esforzamos todos los días para que nuestros
      clientes reciban el mejor servicio posible.
    </p>
  </div>

  <div class="historia">
    <section class="detalle">
      <h2>Pasión por la salud</h2>
      <p>
        En la Farmàcia Agramonte tenemos pasión por la salud, y por eso nuestro
        objetivo es proporcionar el mejor consejo farmacéutico con el trato más
        humano y profesional posible. Te acompañamos y te asesoramos en todas y
        cada una de tus consultas y tratamientos.
      </p>
      <p>
        La farmacia la regenta <strong>Zoila Agramonte Bucho</strong>, licenciada
        en Farmacia por la Universidad de La Habana, farmacéutica y dietista
        titulada, con más de treinta años de experiencia en el sector
        farmacéutico.
      </p>
    </section>

    <section class="detalle">
      <h2>Una tienda modernista protegida</h2>
      <p>
        La Farmàcia Agramonte, antigua <strong>Farmàcia Joaquim Cases</strong>,
        es una tienda modernista protegida como <strong>Bien Cultural de
        Interés Local</strong> y catalogada como comercio emblemático de gran
        interés.
      </p>
      <p>
        La decoración actual del local viene de una reforma modernista de 1880,
        la época en la que la familia Cases creó una fórmula magistral que se
        popularizó por toda España e incluso en América, la «Solución Cases»,
        famosa por su capacidad de paliar múltiples enfermedades y dolores.
      </p>
      <p>
        Por fuera, en la fachada destaca un mueble de madera aplacada que ocupa
        toda su superficie. Por dentro, los acabados modernistas propios de la
        época: cristales con motivos florales grabados al ácido, pavimento de
        mosaico hidráulico y muebles con acabados de ebanistería de líneas
        curvas y motivos florales.
      </p>
      <p>
        Esos motivos modernistas conviven con restos de arquitectura medieval,
        como el arco de piedra de carga del interior. Está datado en el
        <strong>siglo XIII</strong>, de los que se construían para hacer
        posibles espacios flexibles donde ubicar talleres, comercios y demás.
      </p>
    </section>

    <section class="detalle">
      <h2>Cuatro siglos de boticarios</h2>
      <p>
        Las primeras referencias históricas de la farmacia datan de
        <strong>1600</strong>, y hablan de un espacio regentado por una larga
        estirpe de boticarios.
      </p>
      <ul class="cronologia">
        <li><strong>Hasta 1747</strong><span>Los Saurina, los primeros en
          regentarla.</span></li>
        <li><strong>1864 – 2014</strong><span>La familia Cases, propietaria
          durante siglo y medio.</span></li>
        <li><strong>Desde 2019</strong><span>Zoila Agramonte Bucho, nueva
          titular.</span></li>
      </ul>
      <p>
        En 2019 Zoila decide poner en valor el inmenso patrimonio histórico y
        artístico que tiene la farmacia y, al mismo tiempo, dotarla de
        dinamismo y modernidad.
      </p>
    </section>

    <section class="detalle">
      <h2>Reportajes de prensa</h2>
      <p>
        La revista digital %s nos contactó para hacer un reportaje sobre la
        farmacia y sobre cómo había repercutido el impacto de la pandemia de
        covid-19 en el barrio de Santa Caterina.
      </p>
      <a class="prensa" href="%s" target="_blank" rel="noopener">
        <span class="prensa-medio">%s · Reportaje</span>
        <strong>%s</strong>
        <span class="prensa-pie">Se abre en una pestaña nueva, en su web</span>
      </a>
    </section>
  </div>

  <div class="cierre">
    <h2>Ven a verla</h2>
    <p>
      Estamos en la Plaça de la Llana, 11, en El Born, de lunes a sábado de 9:00
      a 14:30 y de 16:00 a 20:30. Si quieres preguntar algo antes de venir,
      escríbenos por <a href="https://wa.me/%s" target="_blank" rel="noopener">WhatsApp</a>
      o llama al <a href="tel:%s">%s</a>.
    </p>
  </div>
""" % (PRENSA_MEDIO, PRENSA_URL, PRENSA_MEDIO, PRENSA_TITULO,
       WHATSAPP, TELEFONO_ENLACE, TELEFONO_VISIBLE)

    return documento(
        titulo="Quiénes somos — Farmàcia Agramonte",
        descripcion="La Farmàcia Agramonte, antigua Farmàcia Joaquim Cases: "
                    "tienda modernista protegida en la Plaça de la Llana, El Born "
                    "(Barcelona), con referencias desde 1600.",
        ruta="historia.html",
        contenido=contenido,
        es_plantilla=False,
        aqui="historia")


def comprueba_portada(categorias):
    """La portada enlaza las categorías a mano, así que aquí se comprueba que no
    se hayan descuadrado: una categoría nueva en el JSON que nadie enlace, o un
    enlace de la portada a una página que ya no se genera."""
    portada = (RAIZ / "index.html").read_text(encoding="utf-8")
    enlazadas = set(re.findall(r'href="catalogo-([a-z0-9-]+)\.html"', portada))
    definidas = {c["id"] for c in categorias}
    if definidas - enlazadas:
        print("  AVISO: sin enlazar desde la portada: %s" % sorted(definidas - enlazadas))
    if enlazadas - definidas:
        print("  AVISO: la portada enlaza páginas que no se generan: %s" % sorted(enlazadas - definidas))


def comprueba_sitemap(indexables):
    """El sitemap está escrito a mano. Mientras una categoría sea plantilla sus
    fichas llevan noindex y no pintan nada ahí; en cuanto deje de serlo sí, y son
    decenas. Mejor que avise el script a descubrirlo tarde."""
    mapa = (RAIZ / "sitemap.xml").read_text(encoding="utf-8")
    faltan = sorted(r for r in indexables if (BASE + r) not in mapa)
    if faltan:
        print("  AVISO: %d fichas indexables que no están en sitemap.xml: %s%s"
              % (len(faltan), ", ".join(faltan[:4]), " …" if len(faltan) > 4 else ""))


def comprueba_fotos(categorias):
    """Cuenta las fotos puestas y avisa de las que el JSON nombra y no están.

    Una clave "foto" con una errata no se nota al generar: se nota en el
    navegador, como una imagen rota, y sólo si alguien abre esa ficha."""
    rotas, puestas, total = [], 0, 0
    for c in categorias:
        for p in c["productos"]:
            total += 1
            ruta = foto_de(c, p)
            if ruta and not (RAIZ / ruta).exists():
                rotas.append("%s → %s" % (p["nombre"], ruta))
            elif ruta:
                puestas += 1
    if rotas:
        print("  AVISO: el JSON nombra fotos que no están en fotos/: %s" % "; ".join(rotas))
    print("  fotos puestas: %d de %d productos" % (puestas, total))


def comprueba_huerfanas(escritas):
    """Avisa de las catalogo-*.html que este script ya no genera.

    Al quitar un producto del JSON, su página se queda en el disco: nadie la
    enlaza, pero sigue publicada, sigue en Google si llegó a entrar y sigue
    diciendo lo que decía. No las borro solo —un borrado en cadena por una
    errata en el JSON sería peor— pero hay que verlas."""
    hay = {p.name for p in RAIZ.glob("catalogo-*.html")}
    sobran = sorted(hay - set(escritas))
    if sobran:
        print("  AVISO: %d páginas que ya no se generan y siguen en el disco."
              % len(sobran))
        print("         Bórralas con: git rm %s" % " ".join(sobran))


def comprueba_urls_unicas(categorias):
    """Dos productos que den la misma URL se pisarían el fichero en silencio."""
    for c in categorias:
        vistos = {}
        for p in c["productos"]:
            s = slug_producto(p)
            if s in vistos:
                raise SystemExit(
                    'En %s, «%s» y «%s» dan la misma URL (%s). Ponle una clave "id" '
                    "distinta a uno de los dos en el JSON."
                    % (c["id"], vistos[s], p["nombre"], ruta_producto(c, p)))
            vistos[s] = p["nombre"]


def main():
    datos = json.loads(DATOS.read_text(encoding="utf-8"))
    categorias = datos["categorias"]

    faltan = [c["icono"] for c in categorias if c["icono"] not in ICONOS]
    if faltan:
        raise SystemExit("Iconos que no existen en ICONOS: %s" % faltan)

    comprueba_urls_unicas(categorias)
    comprueba_portada(categorias)
    comprueba_fotos(categorias)

    paginas, fichas, indexables, escritas = 0, 0, [], []
    for c in categorias:
        destino = RAIZ / ("catalogo-%s.html" % c["id"])
        destino.write_text(pagina(c, categorias), encoding="utf-8")
        escritas.append(destino.name)
        paginas += 1

        for p in c["productos"]:
            ruta = ruta_producto(c, p)
            (RAIZ / ruta).write_text(pagina_producto(c, p), encoding="utf-8")
            escritas.append(ruta)
            fichas += 1
            if not c.get("plantilla", False):
                indexables.append(ruta)

        cuantos = len(c["productos"])
        print("  %-38s %s" % (destino.name,
                              "%d fichas" % cuantos if cuantos else "sin lista de productos"))

    (RAIZ / "historia.html").write_text(pagina_historia(), encoding="utf-8")
    print("  %-38s %s" % ("historia.html", "quiénes somos"))
    indexables.append("historia.html")

    (RAIZ / "cesta.html").write_text(pagina_cesta(), encoding="utf-8")
    print("  %-38s %s" % ("cesta.html", "la cesta (noindex)"))

    comprueba_huerfanas(escritas)
    comprueba_sitemap(indexables)
    print("\n%d páginas de categoría, %d fichas de producto, la historia y la cesta, escritas desde %s"
          % (paginas, fichas, DATOS.name))


if __name__ == "__main__":
    main()

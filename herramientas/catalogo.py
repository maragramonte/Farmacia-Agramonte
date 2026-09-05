#!/usr/bin/env python3
"""
Escribe las páginas del catálogo a partir de herramientas/catalogo-datos.json.

    python herramientas/catalogo.py

Genera dos cosas por cada categoría del JSON:

    catalogo-<id>.html              la rejilla de tarjetas de la categoría.
    catalogo-<id>-<producto>.html   la ficha de cada uno de sus productos.

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


def precio_html(p):
    return ('<span class="pendiente">00,00 €</span>' if not p.get("precio")
            else escapa(p["precio"]))


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

    El título lleva a la ficha del producto. El botón sigue yendo a WhatsApp,
    que es como se pide de verdad: quien ya sabe lo que quiere no tiene por qué
    dar un rodeo por la ficha."""
    return """    <article class="producto">
      %s
      <div class="cuerpo">
        <h2><a href="%s">%s</a></h2>
        <p class="resumen">%s</p>
        <p class="formato">%s</p>
        <p class="precio">%s</p>
        <a class="boton" href="%s" target="_blank" rel="noopener" aria-label="Preguntar por %s por WhatsApp">Preguntar</a>
      </div>
    </article>""" % (
        foto_html(c, p, icono), escapa(ruta_producto(c, p)), escapa(p["nombre"]),
        escapa(p["resumen"]), escapa(p["formato"]), precio_html(p),
        escapa(enlace_whatsapp(p["consulta"])), escapa(p["consulta"]))


def aviso_plantilla():
    return """
<div class="aviso-plantilla">
  <div class="contenedor">
    %s
    <div>
      <strong class="rotulo">Plantilla de ejemplo</strong>
      <p>
        Los productos, los formatos y los precios de esta página <strong>son
        inventados</strong> y están aquí sólo para ver la maquetación. Nada de lo
        que se lee abajo es el catálogo de la farmacia. No enlazar esta página ni
        darla por buena hasta sustituirlo por productos reales.
      </p>
    </div>
  </div>
</div>
""" % ICONO_AVISO


CIERRE_PEDIDO = """  <div class="cierre">
    <h2>Cómo se pide, de momento</h2>
    <p>
      Esta página es un escaparate: enseña lo que tenemos, pero no es una tienda
      en línea. Se pregunta por WhatsApp o por teléfono, lo preparamos y se
      recoge en el mostrador, que es donde además podemos aconsejarte.
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
        % (escapa(ruta_producto(c, p)), escapa(p["nombre"]), escapa(p["formato"]))
        for p in resto)
    return """  <section class="otros">
    <h2>Más de %s</h2>
    <ul>
%s
    </ul>
    <a class="volver" href="catalogo-%s.html">Ver toda la categoría</a>
  </section>
""" % (escapa(c["nombre"]), puntos, c["id"])


def documento(titulo, descripcion, ruta, contenido, es_plantilla, noindex=False):
    """El esqueleto que comparten la página de categoría y la ficha de producto:
    cabeza, cabecera, aviso, <main> y pie. Lo de dentro de <main> lo pone quien
    llama. Nació al montar las fichas, para no tener dos copias de la cabecera
    que se separasen a la primera de cambio."""
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
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
</head>
<body>

<header class="cabecera">
  <div class="contenedor">
    <a class="marca" href="index.html">Farmàcia Agramonte</a>
    <nav class="nav" aria-label="Principal">
      <a href="index.html">Inicio</a>
      <a href="index.html#categorias">Categorías</a>
      <a href="index.html#contacto">Contacto</a>
    </nav>
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
      <p class="resumen">%s</p>
      <p class="precio">%s</p>
      <a class="boton" href="%s" target="_blank" rel="noopener" aria-label="Preguntar por %s por WhatsApp">
        %s
        Preguntar por WhatsApp
      </a>
      <p class="nota-consejo">
        Esto es un escaparate, no una tienda: no se compra desde aquí. Nos
        preguntas por WhatsApp o al <a href="tel:%s">%s</a>, lo preparamos y lo
        recoges en el mostrador, que es donde además podemos aconsejarte.
      </p>
    </div>
  </div>

%s%s""" % (
        c["id"], escapa(c["nombre"]), escapa(p["nombre"]),
        foto_html(c, p, icono), escapa(p["nombre"]), escapa(p["formato"]),
        escapa(p["resumen"]), precio_html(p),
        escapa(enlace_whatsapp(p["consulta"])), escapa(p["consulta"]), ICONO_WHATSAPP,
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
        descripcion="%s %s en la Farmàcia Agramonte, Plaça de la Llana 11, El Born (Barcelona)." % (
            p["resumen"], p["formato"]),
        ruta=ruta_producto(c, p),
        contenido=contenido,
        es_plantilla=es_plantilla,
        noindex=es_plantilla)


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

    paginas, fichas, indexables = 0, 0, []
    for c in categorias:
        destino = RAIZ / ("catalogo-%s.html" % c["id"])
        destino.write_text(pagina(c, categorias), encoding="utf-8")
        paginas += 1

        for p in c["productos"]:
            ruta = ruta_producto(c, p)
            (RAIZ / ruta).write_text(pagina_producto(c, p), encoding="utf-8")
            fichas += 1
            if not c.get("plantilla", False):
                indexables.append(ruta)

        cuantos = len(c["productos"])
        print("  %-38s %s" % (destino.name,
                              "%d fichas" % cuantos if cuantos else "sin lista de productos"))

    comprueba_sitemap(indexables)
    print("\n%d páginas de categoría y %d fichas de producto escritas desde %s"
          % (paginas, fichas, DATOS.name))


if __name__ == "__main__":
    main()

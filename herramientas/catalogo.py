#!/usr/bin/env python3
"""
Escribe las páginas del catálogo a partir de herramientas/catalogo-datos.json.

    python herramientas/catalogo.py

Genera un catalogo-<id>.html por cada categoría del JSON. Existe por una razón
muy concreta: la tira de categorías que va arriba de cada página tiene que
listarlas todas, así que añadir una obligaba a tocar las diez a mano. Con diez
páginas eso es una errata esperando a ocurrir.

La web sigue siendo estática: esto no se ejecuta al visitarla, sólo cuando
cambian los productos. Igual que herramientas/tarjeta-social.py con og.png.

Para cambiar productos o precios se edita el JSON, no este fichero ni el HTML.
El HTML generado NO se edita a mano: se pierde al volver a ejecutar esto.
"""

import json
import re
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent.parent
DATOS = Path(__file__).resolve().parent / "catalogo-datos.json"

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


def ficha(p, icono):
    precio = ('<span class="pendiente">00,00 €</span>' if not p.get("precio")
              else escapa(p["precio"]))
    if p.get("foto"):
        foto = ('<div class="foto foto-real"><img src="fotos/%s" alt="%s" loading="lazy"></div>'
                % (escapa(p["foto"]), escapa(p["nombre"])))
    else:
        foto = '<div class="foto"><svg viewBox="0 0 24 24" aria-hidden="true">%s</svg></div>' % icono
    return """    <article class="producto">
      %s
      <div class="cuerpo">
        <h2>%s</h2>
        <p class="resumen">%s</p>
        <p class="formato">%s</p>
        <p class="precio">%s</p>
        <a class="boton" href="%s" target="_blank" rel="noopener" aria-label="Preguntar por %s por WhatsApp">Preguntar</a>
      </div>
    </article>""" % (
        foto, escapa(p["nombre"]), escapa(p["resumen"]), escapa(p["formato"]), precio,
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
        fichas = "\n\n".join(ficha(p, icono) for p in c["productos"])
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


def pagina(c, categorias):
    icono = ICONOS[c["icono"]]
    es_plantilla = c.get("plantilla", False)
    # Sin noindex: las diez se indexan. Decisión de la farmacia, tomada sabiendo
    # que lo que Google recoge son los precios de ejemplo y que un precio
    # expuesto al público es una oferta. Al poner los reales esto no cambia.
    canonical = '<link rel="canonical" href="%scatalogo-%s.html">' % (BASE, c["id"])

    coletilla = " (plantilla)" if es_plantilla else ""

    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- ESTE FICHERO SE GENERA. No lo edites a mano: se pierde al ejecutar
     python herramientas/catalogo.py. Los productos están en
     herramientas/catalogo-datos.json. -->
%s
<meta name="description" content="%s en la Farmàcia Agramonte, Plaça de la Llana 11, El Born (Barcelona).">
<title>%s%s — Farmàcia Agramonte</title>
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

  <p class="migas"><a href="index.html">Inicio</a> › <a href="index.html#categorias">Categorías</a> › %s</p>

  <div class="portada-categoria">
    <h1>%s</h1>
    <p>%s</p>
  </div>

  <nav class="tira" aria-label="Categorías del catálogo">
%s
  </nav>

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
""" % (canonical, escapa(c["nombre"]), escapa(c["nombre"]), coletilla,
       WHATSAPP, ICONO_WHATSAPP,
       aviso_plantilla() if es_plantilla else "",
       escapa(c["nombre"]), escapa(c["nombre"]), escapa(c["intro"]),
       tira(categorias, c["id"]),
       cuerpo_categoria(c, icono))


def main():
    datos = json.loads(DATOS.read_text(encoding="utf-8"))
    categorias = datos["categorias"]

    faltan = [c["icono"] for c in categorias if c["icono"] not in ICONOS]
    if faltan:
        raise SystemExit("Iconos que no existen en ICONOS: %s" % faltan)

    # La portada enlaza las categorías a mano, así que aquí se comprueba que no
    # se hayan descuadrado: una categoría nueva en el JSON que nadie enlace, o
    # un enlace de la portada a una página que ya no se genera.
    portada = (RAIZ / "index.html").read_text(encoding="utf-8")
    enlazadas = set(re.findall(r'href="catalogo-([a-z0-9-]+)\.html"', portada))
    definidas = {c["id"] for c in categorias}
    if definidas - enlazadas:
        print("  AVISO: sin enlazar desde la portada: %s" % sorted(definidas - enlazadas))
    if enlazadas - definidas:
        print("  AVISO: la portada enlaza páginas que no se generan: %s" % sorted(enlazadas - definidas))

    escritas = 0
    for c in categorias:
        destino = RAIZ / ("catalogo-%s.html" % c["id"])
        destino.write_text(pagina(c, categorias), encoding="utf-8")
        cuantos = len(c["productos"])
        print("  %-38s %s" % (destino.name,
                              "%d productos" % cuantos if cuantos else "sin lista de productos"))
        escritas += 1
    print("\n%d páginas escritas desde %s" % (escritas, DATOS.name))


if __name__ == "__main__":
    main()

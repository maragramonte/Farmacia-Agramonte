#!/usr/bin/env python3
"""
Escribe las páginas del catálogo a partir de herramientas/catalogo-datos.json.

    python herramientas/catalogo.py

Genera dos cosas por cada categoría del JSON y por cada idioma:

    catalogo-<id>.html              la rejilla de tarjetas de la categoría.
    catalogo-<id>-<producto>.html   la ficha de cada uno de sus productos.

Y dos más, que no dependen del JSON pero comparten con ellas cabecera y pie:

    historia.html                   quiénes somos y de dónde viene la farmacia.
                                    El texto está en herramientas/textos.json.
    cesta.html                      la lista de lo que alguien quiere encargar.
                                    Lo que la rellena es cesta.js, en el
                                    navegador; aquí sólo se escribe el molde.

IDIOMAS. El español se escribe en la raíz y cada idioma más en su carpeta
(ca/, y en/ el día que se añada). Eso es deliberado: las URL en español llevan
tiempo publicadas y están en Google y en el sitemap, así que mover el español a
/es/ las rompería todas. Los idiomas se declaran en textos.json, y lo que no
esté traducido sale en español avisando al ejecutar esto.

Existe por una razón muy concreta: la tira de categorías que va arriba de cada
página tiene que listarlas todas, así que añadir una obligaba a tocar las diez a
mano. Ahora que además hay una ficha por producto y dos idiomas, escribir esto a
mano sería una errata esperando a ocurrir.

La web sigue siendo estática: esto no se ejecuta al visitarla, sólo cuando
cambian los productos. Igual que herramientas/tarjeta-social.py con og.png.

Para cambiar productos se edita catalogo-datos.json y para cambiar cualquier
texto de la interfaz, textos.json. El HTML generado NO se edita a mano: se
pierde al volver a ejecutar esto.
"""

import datetime
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent.parent
DATOS = Path(__file__).resolve().parent / "catalogo-datos.json"
TEXTOS = Path(__file__).resolve().parent / "textos.json"
CARPETA_FOTOS = RAIZ / "fotos"

# En orden de preferencia: si un producto tiene la foto en dos formatos, gana el
# primero de la lista.
EXTENSIONES_FOTO = (".webp", ".avif", ".jpg", ".jpeg", ".png")

BASE = "https://maragramonte.github.io/Farmacia-Agramonte/"
WHATSAPP = "34661192472"
TELEFONO_ENLACE = "+34933195921"
TELEFONO_VISIBLE = "933 19 59 21"
WHATSAPP_VISIBLE = "661 192 472"
# El perfil de Instagram. Va en el pie de todas las páginas: en la portada
# como icono de .sociales, aquí como icono más arroba, que así es un dato
# de contacto y no sólo un adorno. La portada lo lleva escrito a mano en
# index.html; si cambia la cuenta, hay que tocar los dos sitios.
# El aria-label del enlace repite la arroba que se ve a propósito: un nombre
# accesible que no contenga el texto visible rompe el «Label in Name» de la
# WCAG. Lo que añade es la palabra Instagram, que el icono dice de un vistazo
# y un lector de pantalla no.
INSTAGRAM = "https://www.instagram.com/farmacia.agramonte/"
INSTAGRAM_VISIBLE = "@farmacia.agramonte"
CORREO = "farmacia.lallana@gmail.com"

# El idioma que vive en la raíz y al que se recurre cuando falta una traducción.
BASICO = "es"

# Se rellenan al arrancar, desde textos.json.
CADENAS = {}
IDIOMAS = {}
# Los pares [espanol, traduccion] con que se traduce index.html.
PORTADA = {}
# Lo que se ha tenido que servir en español por no estar traducido. Se avisa al
# final, junto, en lugar de una línea por cada hueco: con doscientas páginas
# serían cientos de líneas iguales.
SIN_TRADUCIR = set()


def carga_textos():
    datos = json.loads(TEXTOS.read_text(encoding="utf-8"))
    CADENAS.update(datos["textos"])
    IDIOMAS.update(datos["idiomas"])
    PORTADA.update(datos.get("portada", {}))
    if BASICO not in IDIOMAS:
        raise SystemExit("textos.json no declara el idioma «%s»" % BASICO)
    if IDIOMAS[BASICO]["carpeta"]:
        raise SystemExit(
            "El idioma «%s» tiene que ir en la raíz (carpeta vacía): sus URL ya "
            "están publicadas y moverlas las rompería." % BASICO)


def T(clave, idioma):
    """Una cadena de textos.json, en el idioma pedido.

    Si falta la traducción, devuelve la española y lo anota para avisar al
    final. Es lo que permite añadir un idioma e ir traduciéndolo poco a poco sin
    que la web se quede con huecos en blanco por el camino.

    Devuelve lo que haya en el JSON: una cadena o una lista de párrafos. Los %s
    los rellena quien llama, que es quien sabe con qué."""
    entrada = CADENAS.get(clave)
    if entrada is None:
        raise SystemExit('Falta la clave «%s» en textos.json' % clave)
    if idioma in entrada:
        return entrada[idioma]
    SIN_TRADUCIR.add((idioma, clave))
    return entrada[BASICO]


def texto_de(valor, idioma, clave=None):
    """Un campo de catalogo-datos.json, que puede venir en uno o en varios idiomas.

        "resumen": "Hidratante en gel..."                   vale para todos
        "resumen": {"es": "Hidratante...", "ca": "Hidra..."} uno por idioma

    Las dos formas conviven a propósito: así se puede traducir producto a
    producto sin tocar los cuarenta de golpe, y lo que ya estaba escrito sigue
    valiendo tal cual. Vale igual para las listas de los epígrafes.

    El "clave" es para avisar. Una cadena suelta en un campo que se traduce
    —un resumen, una intro— no es que valga para todos: es que está sin
    traducir, y hay que verlo. En los que NO se traducen —el nombre de un
    producto, que es una marca— se llama sin clave y no se avisa de nada."""
    if isinstance(valor, dict):
        if idioma in valor:
            return valor[idioma]
        if clave:
            SIN_TRADUCIR.add((idioma, "datos: %s" % clave))
        return valor.get(BASICO, "")
    if clave and valor and idioma != BASICO:
        SIN_TRADUCIR.add((idioma, "datos: %s" % clave))
    return valor


def carpeta(idioma):
    """La subcarpeta del idioma: "" para el español, "ca" para el catalán."""
    return IDIOMAS[idioma]["carpeta"]


def prefijo(idioma):
    """Lo que hay que poner delante para llegar a la raíz desde ese idioma.

    El CSS, las tipografías, cesta.js y las fotos viven en la raíz y no se
    duplican por idioma, así que desde ca/ se piden con ../. Se calcula en vez
    de usar rutas absolutas (/Farmacia-Agramonte/...) porque esas llevan dentro
    el nombre del repositorio y se romperían al renombrarlo o al poner un
    dominio propio."""
    return "../" if carpeta(idioma) else ""


def ruta_publica(idioma, fichero):
    """La ruta del fichero contando desde la raíz del sitio: lo que va en el
    canonical, en los hreflang y en el sitemap."""
    car = carpeta(idioma)
    return "%s/%s" % (car, fichero) if car else fichero


def destino(idioma, fichero):
    """Dónde se escribe en el disco."""
    car = carpeta(idioma)
    return (RAIZ / car / fichero) if car else (RAIZ / fichero)


def enlace_idioma(desde, hacia, fichero):
    """El enlace del selector de idioma, de una versión de la página a la otra."""
    car = IDIOMAS[hacia]["carpeta"]
    return prefijo(desde) + ("%s/%s" % (car, fichero) if car else fichero)


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

# Las secciones de la ficha, en el orden en que se leen, con la clave del JSON
# de productos, la del título en textos.json y con qué se pinta cada una. Todas
# son opcionales: si el producto no trae la clave, la sección no aparece. Una
# ficha corta es mejor que un epígrafe vacío, y mucho mejor que un epígrafe
# inventado, que aquí además sería un consejo de salud.
SECCIONES = [
    ("descripcion",  "seccion_descripcion",  "p"),
    ("modo_empleo",  "seccion_modo_empleo",  "ol"),
    ("composicion",  "seccion_composicion",  "p"),
    ("advertencias", "seccion_advertencias", "ul"),
]

ICONO_WHATSAPP = (
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 '
    '15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm5.6 14.1c-.2.7-1.4 1.3-1.9 1.3-.5 0-1.1.2-3.6-.8-3-1.3-4.9-4.4'
    '-5-4.6-.2-.2-1.2-1.6-1.2-3s.7-2.1 1-2.4c.3-.3.6-.4.8-.4h.6c.2 0 .4 0 .7.5l1 2.3c0 .2 0 .4-.1.6l'
    '-.4.5c-.2.2-.4.3-.2.7.2.3.9 1.4 1.9 2.3 1.3 1.1 2.3 1.5 2.7 1.6.2 0 .4 0 .6-.2l.9-1c.2-.2.4-.2.7'
    '-.1l2.2 1c.3.2.4.3.5.4.1.2.1.7-.2 1.3Z"/></svg>'
)

ICONO_INSTAGRAM = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" '
    'rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r=".9" '
    'fill="currentColor" stroke="none"/></svg>')

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

# El reportaje de prensa. Es el único enlace a un sitio ajeno que hay en la web
# aparte de WhatsApp, y va aquí arriba para que se vea de un vistazo que existe.
PRENSA_URL = "https://www.larepublica.cat/coronavirus/reportatge-la-barcelona-que-no-es-resigna/"
PRENSA_TITULO = "Coronavirus: La Barcelona que no se resigna"
PRENSA_MEDIO = "La República"


def escapa(t):
    """Lo que venga del JSON va a parar dentro del HTML, así que se escapa."""
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def enlace_whatsapp(consulta, idioma):
    texto = T("whatsapp_consulta", idioma) % consulta
    return "https://wa.me/%s?text=%s" % (WHATSAPP, quote(texto, safe=""))


def slug_producto(p):
    """La parte de la URL que identifica al producto dentro de su categoría.

    Se saca del nombre, pero el JSON puede fijarla con "id". Hace falta poder:
    renombrar un producto le cambiaría la URL, y una URL que ya está en Google
    no se cambia a la ligera.

    No depende del idioma a propósito: la misma página en catalán vive en
    ca/catalogo-solares-anthelios-age-correct-spf50.html, con el mismo nombre.
    Traducir los slugs duplicaría el trabajo de mantener URL estables y no
    aporta nada: los nombres de producto son marcas y no se traducen."""
    if p.get("id"):
        return p["id"]
    # Del nombre en español, SIEMPRE, aunque estemos generando el catalán: la
    # URL de un producto es una sola y no cambia de idioma. Si saliera del
    # nombre traducido, la ficha catalana viviría en otro fichero y los
    # hreflang apuntarían a páginas que no existen.
    t = unicodedata.normalize("NFKD", texto_de(p["nombre"], BASICO))
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
    que ya no enlaza a ninguna ficha.

    Tampoco depende del idioma: quien añade algo en español y luego cambia a
    catalán tiene que encontrar su cesta igual, no otra vacía."""
    return "%s-%s" % (c["id"], slug_producto(p))


def nombre_de(c_o_p, idioma, clave=None):
    """El nombre de una categoría o de un producto.

    Las categorías sí se traducen («Solares» / «Solars»); los productos casi
    nunca, porque son marcas. Las dos cosas pasan por aquí, y texto_de deja la
    cadena suelta tal cual cuando no hay traducción que elegir."""
    return texto_de(c_o_p["nombre"], idioma, clave)


def boton_anadir(c, p, idioma):
    """El botón de añadir a la cesta.

    Nace con hidden y lo destapa cesta.js. Sin JavaScript no hay cesta, y un
    botón que no hace nada es peor que no tenerlo: el de WhatsApp, que es un
    enlace de verdad, sigue ahí al lado y funciona siempre.

    El formato va sin la marca amarilla de «pendiente»: esto no se lee, se
    copia a un mensaje de WhatsApp, y «(Formato pendiente)» ahí no se entiende."""
    return ('<button type="button" class="anadir" data-cesta-anade hidden'
            ' data-id="%s" data-nombre="%s" data-formato="%s" data-url="%s">%s %s</button>'
            % (escapa(id_cesta(c, p)), escapa(nombre_de(p, idioma)),
               escapa(texto_de(p.get("formato"), idioma) or ""),
               escapa(ruta_producto(c, p)),
               ICONO_MAS, escapa(T("boton_anadir", idioma))))


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


def formato_html(p, idioma):
    """El envase y el contenido, o la marca amarilla si todavía no se saben.

    Aquí el amarillo sí toca, al revés que con el precio: todo producto tiene un
    formato, así que no tenerlo es una ficha a medias y hay que verlo. El precio
    no lleva marca porque no falta, es que no se publica."""
    f = texto_de(p.get("formato"), idioma, "formato")
    if not f:
        return '<span class="pendiente">%s</span>' % escapa(T("pendiente_formato", idioma))
    return escapa(f)


def resumen_html(p, idioma):
    """La línea que explica el producto, o la marca amarilla si no está.

    Un export del programa de gestión trae nombres y formatos, no frases: por
    eso esto puede faltar y hay que verlo. Igual que el formato."""
    r = texto_de(p.get("resumen"), idioma, "resumen")
    if not r:
        return '<span class="pendiente">%s</span>' % escapa(T("pendiente_resumen", idioma))
    return escapa(r)


def consulta_de(p, idioma):
    """Lo que se escribe solo en el WhatsApp al pulsar Preguntar.

    Si el JSON no la trae, se saca del nombre. Sale un poco más seca que una
    escrita a mano —«el La Roche-Posay Anthelios...»— pero un mensaje algo tieso
    es mejor que cuarenta productos sin botón que funcione."""
    return texto_de(p.get("consulta"), idioma) or nombre_de(p, idioma)


def descripcion_meta(p, idioma):
    """La meta description de la ficha. Se salta lo que falte, que si no queda
    un doble espacio o una frase que empieza por la nada."""
    trozos = [t for t in (texto_de(p.get("resumen"), idioma),
                          texto_de(p.get("formato"), idioma)) if t]
    return T("desc_producto", idioma) % (
        " ".join(trozos) if trozos else nombre_de(p, idioma))


def foto_de(c, p):
    """La foto del producto dentro de fotos/, o None si todavía no la hay.

    Dos maneras. Si el JSON trae "foto", manda ésa. Si no, se busca en fotos/ un
    fichero que se llame igual que la página del producto, y ésa es la buena el
    día que lleguen las cuarenta y siete: basta con dejar el fichero bien
    nombrado y aparece sola. Escribir a mano cuarenta y siete claves "foto" es
    una errata esperando a ocurrir, que es la misma razón por la que existe este
    script.

    Las fotos no se duplican por idioma: una crema se ve igual en catalán."""
    if p.get("foto"):
        return "fotos/%s" % p["foto"]
    base = "%s-%s" % (c["id"], slug_producto(p))
    for ext in EXTENSIONES_FOTO:
        if (CARPETA_FOTOS / (base + ext)).exists():
            return "fotos/%s%s" % (base, ext)
    return None


def foto_html(c, p, icono, idioma):
    ruta = foto_de(c, p)
    if ruta:
        return ('<div class="foto foto-real"><img src="%s%s" alt="%s" loading="lazy"></div>'
                % (prefijo(idioma), escapa(ruta), escapa(nombre_de(p, idioma))))
    return '<div class="foto"><svg viewBox="0 0 24 24" aria-hidden="true">%s</svg></div>' % icono


def tira(categorias, actual, idioma):
    """La tira de arriba, con las diez categorías del idioma en que estemos."""
    filas = []
    for c in categorias:
        nombre = escapa(nombre_de(c, idioma, "nombre de categoria"))
        if c["id"] == actual:
            filas.append('    <a href="catalogo-%s.html" aria-current="page">%s</a>' % (c["id"], nombre))
        else:
            filas.append('    <a href="catalogo-%s.html">%s</a>' % (c["id"], nombre))
    # La actual va primera, que es donde el ojo la busca.
    orden = [f for f in filas if 'aria-current' in f] + [f for f in filas if 'aria-current' not in f]
    return "\n".join(orden)


def ficha(c, p, icono, idioma):
    """Una tarjeta de la rejilla.

    El título lleva a la ficha del producto. Debajo, las dos maneras de pedirlo:
    «Añadir», que lo apunta en la cesta para encargar varias cosas de una vez, y
    «Preguntar», que sigue yendo directo a WhatsApp, porque quien ya sabe lo que
    quiere no tiene por qué dar un rodeo por la cesta.

    Las dos van dentro de .acciones, y es ese bloque el que se pega al fondo de
    la tarjeta. Antes el margen automático vivía en el botón de WhatsApp; con dos
    botones eso habría dejado un hueco distinto en cada tarjeta."""
    consulta = consulta_de(p, idioma)
    return """    <article class="producto">
      %s
      <div class="cuerpo">
        <h2><a href="%s">%s</a></h2>
        <p class="resumen">%s</p>
        <p class="formato">%s</p>%s
        <div class="acciones">
          %s
          <a class="boton" href="%s" target="_blank" rel="noopener" aria-label="%s">%s</a>
        </div>
      </div>
    </article>""" % (
        foto_html(c, p, icono, idioma), escapa(ruta_producto(c, p)),
        escapa(nombre_de(p, idioma)),
        resumen_html(p, idioma), formato_html(p, idioma), precio_html(p, " " * 8),
        boton_anadir(c, p, idioma),
        escapa(enlace_whatsapp(consulta, idioma)),
        escapa(T("boton_preguntar_aria", idioma) % consulta),
        escapa(T("boton_preguntar", idioma)))


def aviso_plantilla(idioma):
    return """
<div class="aviso-plantilla">
  <div class="contenedor">
    %s
    <div>
      <strong class="rotulo">%s</strong>
      <p>%s</p>
    </div>
  </div>
</div>
""" % (ICONO_AVISO, escapa(T("aviso_plantilla_rotulo", idioma)),
       T("aviso_plantilla_texto", idioma))


def cierre_pedido(idioma):
    """El bloque de «cómo se pide» que va al pie de cada categoría con productos."""
    p1, p2, p3 = T("cierre_parrafos", idioma)
    return """  <div class="cierre">
    <h2>%s</h2>
    <p>%s</p>
    <p>%s</p>
    <p>%s</p>
  </div>
""" % (escapa(T("cierre_titulo", idioma)),
       p1 % "",
       p2,
       p3 % (TELEFONO_ENLACE, TELEFONO_VISIBLE))


def cuerpo_categoria(c, icono, idioma):
    """Las fichas, o —si la categoría no lleva lista— la explicación de por qué.

    En ese segundo caso no se añade además el cierre de «cómo se pide»: diría
    lo mismo dos veces seguidas. El teléfono se mete aquí en su lugar."""
    if c["productos"]:
        fichas = "\n\n".join(ficha(c, p, icono, idioma) for p in c["productos"])
        return ('  <div class="productos">\n\n%s\n\n  </div>\n' % fichas) + "\n" + cierre_pedido(idioma)

    sp = c["sin_productos"]
    parrafos = "\n".join("    <p>%s</p>" % escapa(t)
                         for t in texto_de(sp["parrafos"], idioma, "sin_productos"))
    return """  <div class="cierre">
    <h2>%s</h2>
%s
    <p>%s</p>
  </div>
""" % (escapa(texto_de(sp["titulo"], idioma, "sin_productos")), parrafos,
       T("sin_productos_encargar", idioma) % (WHATSAPP, TELEFONO_ENLACE, TELEFONO_VISIBLE))


def seccion(p, clave, clave_titulo, envoltura, idioma):
    """Un epígrafe de la ficha, o nada si el producto no trae ese dato."""
    textos = texto_de(p.get(clave), idioma, clave)
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
        extra, escapa(T(clave_titulo, idioma)), interior)


def otros_de(c, actual, idioma):
    """El resto de la categoría, al pie de la ficha. Sin foto y sin precio: es
    un índice para seguir mirando, no otra rejilla de tarjetas."""
    resto = [p for p in c["productos"] if slug_producto(p) != slug_producto(actual)]
    if not resto:
        return ""
    puntos = "\n".join(
        '      <li><a href="%s"><strong>%s</strong><small>%s</small></a></li>'
        % (escapa(ruta_producto(c, p)), escapa(nombre_de(p, idioma)),
           formato_html(p, idioma))
        for p in resto)
    return """  <section class="otros">
    <h2>%s</h2>
    <ul>
%s
    </ul>
    <a class="volver" href="catalogo-%s.html">%s</a>
  </section>
""" % (escapa(T("otros_titulo", idioma) % nombre_de(c, idioma)), puntos, c["id"],
       escapa(T("otros_volver", idioma)))


def alternativas(idioma, fichero):
    """Los hreflang: le dicen a Google que estas páginas son la misma en otro
    idioma, y no contenido duplicado ni páginas que compiten entre sí.

    Van con URL absolutas porque así lo pide la especificación. El x-default
    apunta al español, que es el que vive en la raíz."""
    filas = []
    for otro in IDIOMAS:
        filas.append('<link rel="alternate" hreflang="%s" href="%s%s">'
                     % (IDIOMAS[otro]["etiqueta_html"], BASE,
                        ruta_publica(otro, fichero)))
    filas.append('<link rel="alternate" hreflang="x-default" href="%s%s">'
                 % (BASE, ruta_publica(BASICO, fichero)))
    return "\n".join(filas)


def selector_idioma(idioma, fichero):
    """El selector de la cabecera. El idioma en que estás va en texto marcado
    con aria-current; los demás, como enlace a la misma página traducida.

    Enlaza página a página, no a la portada del otro idioma: a quien está
    mirando los solares en español y quiere leerlos en catalán no hay que
    mandarlo al principio."""
    trozos = []
    for otro in IDIOMAS:
        corto = escapa(IDIOMAS[otro]["corto"])
        nombre = escapa(IDIOMAS[otro]["nombre"])
        if otro == idioma:
            trozos.append('      <span aria-current="true" title="%s">%s</span>'
                          % (escapa(T("idioma_actual", idioma) % nombre), corto))
        else:
            trozos.append('      <a href="%s" lang="%s" hreflang="%s" title="%s">%s</a>'
                          % (escapa(enlace_idioma(idioma, otro, fichero)),
                             IDIOMAS[otro]["etiqueta_html"],
                             IDIOMAS[otro]["etiqueta_html"],
                             escapa(T("idioma_cambiar", idioma) % nombre), corto))
    return """    <nav class="idiomas" aria-label="%s">
%s
    </nav>""" % (escapa(T("idioma_aria", idioma)), "\n".join(trozos))


def documento(idioma, fichero, titulo, descripcion, contenido, es_plantilla,
              noindex=False, aqui=None):
    """El esqueleto que comparten la página de categoría, la ficha de producto,
    la historia y la cesta: cabeza, cabecera, aviso, <main> y pie. Lo de dentro
    de <main> lo pone quien llama. Nació al montar las fichas, para no tener dos
    copias de la cabecera que se separasen a la primera de cambio, y ahora
    sostiene además los dos idiomas.

    "aqui" dice en qué entrada del menú estamos, para marcarla con aria-current:
    "historia", "cesta" o nada."""
    pre = prefijo(idioma)
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    aqui_historia = ' aria-current="page"' if aqui == "historia" else ""
    aqui_cesta = ' aria-current="page"' if aqui == "cesta" else ""
    return """<!DOCTYPE html>
<html lang="%s">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- ESTE FICHERO SE GENERA. No lo edites a mano: se pierde al ejecutar
     python herramientas/catalogo.py. Los productos están en
     herramientas/catalogo-datos.json y los textos en herramientas/textos.json. -->
%s<link rel="canonical" href="%s%s">
%s
<meta name="description" content="%s">
<title>%s</title>
<link rel="icon" href="%sfavicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#2a1d12">
<!-- Tipografías propias, servidas desde este mismo repositorio. No se duplican
     por idioma: desde ca/ se piden con ../ -->
<link rel="preload" href="%stipografias/playfair-display-variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="%stipografias/karla-variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="%stipografias.css">
<link rel="stylesheet" href="%smarca.css">
<link rel="stylesheet" href="%scatalogo.css">
<link rel="stylesheet" href="%scesta.css">
<link rel="stylesheet" href="%sidiomas.css">
<!-- La cesta es lo único de la web que se ejecuta en el navegador. Con defer
     para que no frene el pintado: lo que depende de ella nace con hidden y se
     destapa al cargar, así que nada parpadea ni se ve a medias. Los textos los
     saca del lang de este <html>. -->
<script src="%scesta.js" defer></script>
</head>
<body>

<!-- Lo que se le dice a un lector de pantalla al añadir o quitar de la cesta.
     Está en todas las páginas porque desde todas se puede añadir. -->
<div class="solo-lectores" role="status" aria-live="polite" data-cesta-avisos></div>

<header class="cabecera">
  <div class="contenedor">
    <a class="marca" href="index.html">Farmàcia Agramonte</a>
    <nav class="nav" aria-label="Principal">
      <a href="index.html">%s</a>
      <a href="index.html#categorias">%s</a>
      <a href="historia.html"%s>%s</a>
      <a href="index.html#contacto">%s</a>
    </nav>
%s
    <a class="cesta-enlace" href="cesta.html" data-cesta-contador hidden%s>
      %s
      <span class="cesta-rotulo">%s</span>
      <span class="cesta-cuenta" data-cesta-cuenta>0</span>
    </a>
    <a class="boton" href="https://wa.me/%s" target="_blank" rel="noopener">
      %s
      %s
    </a>
  </div>
</header>
%s
<main class="contenedor">
%s
</main>

<footer class="pie">
  <div class="contenedor">
    <p>%s</p>
    <p class="pie-social"><a href="%s" aria-label="Instagram: %s" target="_blank" rel="noopener">%s<span>%s</span></a></p>
    <p>
      <a href="aviso-legal.html">%s</a> ·
      <a href="privacidad.html">%s</a> ·
      <a href="cookies.html">%s</a>
    </p>
  </div>
</footer>

</body>
</html>
""" % (IDIOMAS[idioma]["etiqueta_html"],
       robots, BASE, ruta_publica(idioma, fichero),
       alternativas(idioma, fichero),
       escapa(descripcion), escapa(titulo),
       pre, pre, pre, pre, pre, pre, pre, pre, pre,
       escapa(T("nav_inicio", idioma)),
       escapa(T("nav_categorias", idioma)),
       aqui_historia, escapa(T("nav_historia", idioma)),
       escapa(T("nav_contacto", idioma)),
       selector_idioma(idioma, fichero),
       aqui_cesta, ICONO_CESTA, escapa(T("nav_cesta", idioma)),
       WHATSAPP, ICONO_WHATSAPP, escapa(T("nav_pedir", idioma)),
       aviso_plantilla(idioma) if es_plantilla else "",
       contenido,
       escapa(T("pie_derechos", idioma)),
       INSTAGRAM, INSTAGRAM_VISIBLE, ICONO_INSTAGRAM, INSTAGRAM_VISIBLE,
       escapa(T("pie_aviso", idioma)),
       escapa(T("pie_privacidad", idioma)),
       escapa(T("pie_cookies", idioma)))


def pagina(c, categorias, idioma):
    """La página de una categoría: portada, tira y rejilla."""
    icono = ICONOS[c["icono"]]
    es_plantilla = c.get("plantilla", False)
    coletilla = T("coletilla_plantilla", idioma) if es_plantilla else ""
    nombre = nombre_de(c, idioma, "nombre de categoria")

    contenido = """
  <p class="migas"><a href="index.html">%s</a> › <a href="index.html#categorias">%s</a> › %s</p>

  <div class="portada-categoria">
    <h1>%s</h1>
    <p>%s</p>
  </div>

  <nav class="tira" aria-label="%s">
%s
  </nav>

%s""" % (escapa(T("nav_inicio", idioma)), escapa(T("nav_categorias", idioma)),
         escapa(nombre), escapa(nombre),
         escapa(texto_de(c["intro"], idioma, "intro")),
         escapa(T("nav_categorias", idioma)),
         tira(categorias, c["id"], idioma), cuerpo_categoria(c, icono, idioma))

    # Ninguna de las diez lleva noindex: se llega a ellas desde la portada y
    # Google puede indexarlas. Decisión de la farmacia, tomada a sabiendas de
    # que siete siguen siendo de muestra. Lo que sí se les niega mientras sean
    # plantilla es el sitemap, y eso lo decide main() al juntar los indexables:
    # dejar de invitar a Google no es lo mismo que cerrarle la puerta.
    return documento(
        idioma=idioma,
        fichero="catalogo-%s.html" % c["id"],
        titulo=T("titulo_categoria", idioma) % (nombre, coletilla),
        descripcion=T("desc_categoria", idioma) % nombre,
        contenido=contenido,
        es_plantilla=es_plantilla)


def pagina_producto(c, p, idioma):
    """La ficha de un producto: foto, datos, epígrafes y el resto de la categoría."""
    icono = ICONOS[c["icono"]]
    es_plantilla = c.get("plantilla", False)
    coletilla = T("coletilla_plantilla", idioma) if es_plantilla else ""
    nombre = nombre_de(p, idioma)
    consulta = consulta_de(p, idioma)

    secciones = "".join(seccion(p, clave, titulo, env, idioma)
                        for clave, titulo, env in SECCIONES)

    contenido = """
  <p class="migas"><a href="index.html">%s</a> › <a href="index.html#categorias">%s</a> › <a href="catalogo-%s.html">%s</a> › %s</p>

  <div class="ficha-producto">
    %s
    <div class="datos">
      <h1>%s</h1>
      <p class="formato">%s</p>
      <p class="resumen">%s</p>%s
      <div class="acciones">
        %s
        <a class="boton" href="%s" target="_blank" rel="noopener" aria-label="%s">
          %s
          %s
        </a>
      </div>
      <p class="cesta-estado" data-cesta-estado="%s" hidden></p>
      <p class="nota-consejo">%s</p>
    </div>
  </div>

%s%s""" % (
        escapa(T("nav_inicio", idioma)), escapa(T("nav_categorias", idioma)),
        c["id"], escapa(nombre_de(c, idioma)), escapa(nombre),
        foto_html(c, p, icono, idioma), escapa(nombre), formato_html(p, idioma),
        resumen_html(p, idioma), precio_html(p, " " * 6),
        boton_anadir(c, p, idioma),
        escapa(enlace_whatsapp(consulta, idioma)),
        escapa(T("boton_preguntar_aria", idioma) % consulta),
        ICONO_WHATSAPP, escapa(T("boton_preguntar_whatsapp", idioma)),
        escapa(id_cesta(c, p)),
        T("ficha_nota_consejo", idioma) % (TELEFONO_ENLACE, TELEFONO_VISIBLE),
        secciones, otros_de(c, p, idioma))

    # Mientras la categoría sea plantilla, sus fichas van con noindex y, como
    # su página de categoría, fuera del sitemap. Que ninguna de las diez
    # páginas de categoría lleve noindex fue una decisión tomada a sabiendas;
    # una ficha inventada por producto es otra cosa: son decenas de páginas
    # flacas y —en cuanto se rellenen los epígrafes— con texto de salud que no
    # ha firmado nadie. Al quitar "plantilla": true del JSON se indexan solas.
    return documento(
        idioma=idioma,
        fichero=ruta_producto(c, p),
        titulo=T("titulo_producto", idioma) % (nombre, coletilla, nombre_de(c, idioma)),
        descripcion=descripcion_meta(p, idioma),
        contenido=contenido,
        es_plantilla=es_plantilla,
        noindex=es_plantilla)


def pagina_cesta(idioma):
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
    sinjs1, sinjs2 = T("cesta_sinjs", idioma)
    cierre1, cierre2, cierre3 = T("cesta_cierre", idioma)
    contenido = """
  <p class="migas"><a href="index.html">%s</a> › <a href="index.html#categorias">%s</a> › %s</p>

  <div class="portada-categoria">
    <h1>%s</h1>
    <p>%s</p>
  </div>

  <div class="cesta-sinjs" data-cesta-sinjs>
    <p>%s</p>
    <p>%s</p>
  </div>

  <div class="cesta-vacia" data-cesta-vacia hidden>
    <h2>%s</h2>
    <p>%s</p>
    <p><a href="index.html#categorias">%s</a></p>
  </div>

  <div data-cesta-llena hidden>
    <ul class="cesta-lista" data-cesta-lista></ul>

    <p class="cesta-resumen">
      %s <strong data-cesta-total>0</strong>
      <span>%s</span>
    </p>

    <p class="cesta-recorte" data-cesta-recorte hidden></p>

    <div class="cesta-acciones">
      <a class="boton" href="https://wa.me/%s" target="_blank" rel="noopener" data-cesta-whatsapp>
        %s
        %s
      </a>
      <button type="button" class="cesta-secundario" data-cesta-copia>%s</button>
      <a class="cesta-secundario" href="mailto:%s" data-cesta-correo>%s</a>
      <button type="button" class="cesta-secundario cesta-vaciar" data-cesta-vaciar>%s</button>
    </div>
  </div>

  <div class="cierre">
    <h2>%s</h2>
    <p>%s</p>
    <p>%s</p>
    <p>%s</p>
  </div>
""" % (escapa(T("nav_inicio", idioma)), escapa(T("nav_categorias", idioma)),
       escapa(T("cesta_migas", idioma)),
       escapa(T("cesta_h1", idioma)), T("cesta_entradilla", idioma),
       sinjs1,
       sinjs2 % (WHATSAPP, WHATSAPP_VISIBLE, TELEFONO_ENLACE, TELEFONO_VISIBLE),
       escapa(T("cesta_vacia_h2", idioma)), escapa(T("cesta_vacia_p", idioma)),
       escapa(T("cesta_vacia_enlace", idioma)),
       escapa(T("cesta_resumen", idioma)), escapa(T("cesta_resumen_nota", idioma)),
       WHATSAPP, ICONO_WHATSAPP, escapa(T("cesta_enviar", idioma)),
       escapa(T("cesta_copiar", idioma)), CORREO, escapa(T("cesta_correo", idioma)),
       escapa(T("cesta_vaciar", idioma)),
       escapa(T("cesta_cierre_h2", idioma)),
       cierre1, cierre2 % (TELEFONO_ENLACE, TELEFONO_VISIBLE), cierre3 % "")

    return documento(
        idioma=idioma,
        fichero="cesta.html",
        titulo=T("cesta_titulo_pagina", idioma),
        descripcion=T("cesta_descripcion", idioma),
        contenido=contenido,
        es_plantilla=False,
        noindex=True,
        aqui="cesta")


def pagina_historia(idioma):
    """historia.html: quiénes somos y de dónde viene la farmacia.

    El texto lo escribe la farmacia y se edita en herramientas/textos.json, no
    en el HTML, que se pierde al regenerar. Está ahí y no en catalogo-datos.json
    porque ese JSON es de productos.

    Se genera en vez de escribirse a mano por una razón concreta: es una página
    del menú principal, así que comparte cabecera, menú y contador de la cesta
    con las cincuenta y ocho de catálogo, en los dos idiomas. Escrita a mano
    habría cuatro copias de esa cabecera y el día que el menú cambie se
    quedarían atrás sin que nadie lo note."""
    s1 = T("historia_s1", idioma)
    s2 = T("historia_s2", idioma)
    crono = "\n".join(
        "        <li><strong>%s</strong><span>%s</span></li>" % (escapa(a), escapa(b))
        for a, b in T("historia_cronologia", idioma))

    contenido = """
  <p class="migas"><a href="index.html">%s</a> › %s</p>

  <div class="portada-categoria">
    <h1>%s</h1>
    <p>%s</p>
  </div>

  <div class="historia">
    <section class="detalle">
      <h2>%s</h2>
      <p>%s</p>
      <p>%s</p>
    </section>

    <section class="detalle">
      <h2>%s</h2>
      <p>%s</p>
      <p>%s</p>
      <p>%s</p>
      <p>%s</p>
    </section>

    <section class="detalle">
      <h2>%s</h2>
      <p>%s</p>
      <ul class="cronologia">
%s
      </ul>
      <p>%s</p>
    </section>

    <section class="detalle">
      <h2>%s</h2>
      <p>%s</p>
      <a class="prensa" href="%s" target="_blank" rel="noopener">
        <span class="prensa-medio">%s</span>
        <strong>%s</strong>
        <span class="prensa-pie">%s</span>
      </a>
    </section>
  </div>

  <div class="cierre">
    <h2>%s</h2>
    <p>%s</p>
  </div>
""" % (escapa(T("nav_inicio", idioma)), escapa(T("historia_migas", idioma)),
       escapa(T("historia_h1", idioma)), escapa(T("historia_entradilla", idioma)),
       escapa(T("historia_s1_h2", idioma)), s1[0], s1[1],
       escapa(T("historia_s2_h2", idioma)), s2[0], s2[1], s2[2], s2[3],
       escapa(T("historia_s3_h2", idioma)), T("historia_s3_p1", idioma),
       crono, T("historia_s3_p2", idioma),
       escapa(T("historia_s4_h2", idioma)),
       escapa(T("historia_s4_p1", idioma) % PRENSA_MEDIO),
       PRENSA_URL,
       escapa(T("historia_prensa_sufijo", idioma) % PRENSA_MEDIO),
       escapa(PRENSA_TITULO),
       escapa(T("historia_prensa_pie", idioma)),
       escapa(T("historia_cierre_h2", idioma)),
       T("historia_cierre_p", idioma) % (WHATSAPP, TELEFONO_ENLACE, TELEFONO_VISIBLE))

    return documento(
        idioma=idioma,
        fichero="historia.html",
        titulo=T("historia_titulo_pagina", idioma),
        descripcion=T("historia_descripcion", idioma),
        contenido=contenido,
        es_plantilla=False,
        aqui="historia")


# Lo que vive en la raíz y no se duplica por idioma, así que desde ca/ hay que
# pedirlo con ../. Son rutas tal como aparecen escritas en index.html.
RAIZ_PORTADA = (
    'href="favicon.svg"',
    'href="tipografias.css"',
    'href="portada.css"',
    'href="cesta.css"',
    'href="idiomas.css"',
    'src="cesta.js"',
    'href="tipografias/playfair-display-variable.woff2"',
    'href="tipografias/karla-variable.woff2"',
)


def pagina_portada(idioma, pares):
    """La portada de un idioma que no es el español, hecha desde index.html.

    index.html está escrito a mano: lleva su propio CSS, su hero dibujado en SVG
    y el JSON-LD que lee Google. Traducirla a mano habría dejado dos ficheros de
    cuatrocientas líneas que se separan a la primera de cambio, y convertirla en
    plantilla de Python habría hecho que la portada ya no se pueda editar como
    HTML. Así que se traduce: se sustituyen los trozos de texto que están en
    textos.json y se arreglan las rutas y las etiquetas de la cabeza.

    Lo que hace que esto no envejezca en silencio: si un trozo en español ya no
    aparece en index.html, esto PARA. Significa que alguien ha cambiado el texto
    español y la traducción se ha quedado vieja, y es mejor enterarse aquí que
    en la web."""
    t = (RAIZ / "index.html").read_text(encoding="utf-8")

    # De más largo a más corto: si no, «Horario» se comería «Horario y
    # dirección» antes de que a éste le llegue el turno.
    for es, otro in sorted(pares, key=lambda p: -len(p[0])):
        if es not in t:
            raise SystemExit(
                "La portada ya no dice «%s», así que su traducción al «%s» está "
                "vieja.\nArregla el par en la lista \"portada\" de textos.json "
                "y vuelve a ejecutar." % (es[:70], idioma))
        t = t.replace(es, otro)

    # Las rutas de lo que vive en la raíz.
    for ruta in RAIZ_PORTADA:
        clave, valor = ruta.split('="', 1)
        t = t.replace(ruta, '%s="%s%s' % (clave, prefijo(idioma), valor))

    # La cabeza: idioma del documento, canonical, og:url y og:locale.
    car = carpeta(idioma)
    t = t.replace('<html lang="es">',
                  '<html lang="%s">' % IDIOMAS[idioma]["etiqueta_html"], 1)
    t = t.replace('<link rel="canonical" href="%s">' % BASE,
                  '<link rel="canonical" href="%s%s/">' % (BASE, car), 1)
    t = t.replace('<meta property="og:url" content="%s">' % BASE,
                  '<meta property="og:url" content="%s%s/">' % (BASE, car), 1)
    # El locale se declara en textos.json: "%s_ES" % idioma daba "en_ES",
    # que no es un locale real. Se deja como respaldo por si falta la clave.
    t = t.replace('<meta property="og:locale" content="es_ES">',
                  '<meta property="og:locale" content="%s">'
                  % IDIOMAS[idioma].get("og_locale", "%s_ES" % idioma), 1)
    # El JSON-LD describe esta página, así que su url es la de este idioma.
    t = t.replace('"url": "%s",' % BASE, '"url": "%s%s/",' % (BASE, car), 1)

    # El selector de idioma, que no es una traducción sino otro bloque.
    nuevo = selector_idioma(idioma, "index.html")
    t = re.sub(r"    <!-- IDIOMAS.*?/IDIOMAS -->",
               nuevo.replace("\\", "\\\\"), t, count=1, flags=re.S)

    # Y el aviso de que esto se genera, que index.html no lo lleva porque es la
    # que se edita.
    return t.replace("<head>", """<head>
<!-- ESTE FICHERO SE GENERA a partir de index.html. No lo edites a mano: se
     pierde al ejecutar python herramientas/catalogo.py. El texto español está
     en index.html y las traducciones en herramientas/textos.json. -->""", 1)


def comprueba_portada(categorias, idioma):
    """La portada de cada idioma enlaza las categorías a mano, así que aquí se
    comprueba que no se haya descuadrado: una categoría nueva en el JSON que
    nadie enlace, o un enlace de la portada a una página que ya no se genera."""
    fichero = destino(idioma, "index.html")
    if not fichero.exists():
        print("  AVISO: falta la portada de «%s» (%s)"
              % (idioma, fichero.relative_to(RAIZ)))
        return
    portada = fichero.read_text(encoding="utf-8")
    enlazadas = set(re.findall(r'href="catalogo-([a-z0-9-]+)\.html"', portada))
    definidas = {c["id"] for c in categorias}
    if definidas - enlazadas:
        print("  AVISO: sin enlazar desde la portada de «%s»: %s"
              % (idioma, sorted(definidas - enlazadas)))
    if enlazadas - definidas:
        print("  AVISO: la portada de «%s» enlaza páginas que no se generan: %s"
              % (idioma, sorted(enlazadas - definidas)))


# Las páginas que no salen del JSON pero sí van al sitemap, con su prioridad.
# La portada es "" porque su URL es la de la carpeta: / y /ca/.
PAGINAS_FIJAS = (
    ("", "1.0"),
    ("historia.html", "0.8"),
    ("aviso-legal.html", "0.3"),
    ("privacidad.html", "0.3"),
    ("cookies.html", "0.3"),
)


def escribe_sitemap(indexables, hoy):
    """Escribe sitemap.xml entero.

    Antes estaba a mano y el script sólo avisaba de lo que faltaba. Con dos
    idiomas son decenas de URL y la lista crece cada vez que se quita un
    "plantilla": true, así que mantenerla a mano era la errata esperando a
    ocurrir de siempre. Lo que NO entra: la cesta, que lleva noindex porque es
    distinta para cada visitante.

    Las categorías que siguen siendo plantilla tampoco entran, ni ellas ni sus
    fichas: eso lo decide quien llama, en la lista de indexables."""
    filas = []
    for idioma in IDIOMAS:
        for fichero, prioridad in PAGINAS_FIJAS:
            filas.append((ruta_publica(idioma, fichero), prioridad))
    # Los indexables llegan ya con su prioridad: quien los junta sabe si es una
    # página de categoría o una ficha, y adivinarlo aquí por el nombre fallaba
    # con las categorías cuyo id lleva guion (cosmetica-facial).
    filas.extend(indexables)

    cuerpo = "\n".join(
        '  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n'
        '    <priority>%s</priority>\n  </url>' % (BASE, ruta, hoy, prioridad)
        for ruta, prioridad in filas)

    (RAIZ / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!-- ESTE FICHERO SE GENERA. No lo edites a mano: se pierde al\n'
        '     ejecutar python herramientas/catalogo.py. -->\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + cuerpo + "\n</urlset>\n", encoding="utf-8")
    print("  %-38s %d URL" % ("sitemap.xml", len(filas)))


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
                rotas.append("%s → %s" % (nombre_de(p, BASICO), ruta))
            elif ruta:
                puestas += 1
    if rotas:
        print("  AVISO: el JSON nombra fotos que no están en fotos/: %s" % "; ".join(rotas))
    print("  fotos puestas: %d de %d productos" % (puestas, total))


def comprueba_huerfanas(escritas):
    """Avisa de las catalogo-*.html que este script ya no genera, en cualquier
    idioma.

    Al quitar un producto del JSON, su página se queda en el disco: nadie la
    enlaza, pero sigue publicada, sigue en Google si llegó a entrar y sigue
    diciendo lo que decía. No las borro solo —un borrado en cadena por una
    errata en el JSON sería peor— pero hay que verlas."""
    hay = set()
    for idioma in IDIOMAS:
        car = carpeta(idioma)
        base = (RAIZ / car) if car else RAIZ
        if not base.exists():
            continue
        for p in base.glob("catalogo-*.html"):
            hay.add(str(p.relative_to(RAIZ)).replace("\\", "/"))
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
                    % (c["id"], vistos[s], nombre_de(p, BASICO), ruta_producto(c, p)))
            vistos[s] = nombre_de(p, BASICO)


def avisa_sin_traducir():
    """Lo que ha salido en español por no estar traducido, junto y al final.

    Agrupado por idioma a propósito: una línea por hueco serían cientos de
    líneas iguales con doscientas páginas, y nadie las leería."""
    if not SIN_TRADUCIR:
        return
    por_idioma = {}
    for idioma, clave in SIN_TRADUCIR:
        por_idioma.setdefault(idioma, []).append(clave)
    print()
    for idioma in sorted(por_idioma):
        claves = sorted(set(por_idioma[idioma]))
        print("  AVISO: «%s» tiene %d textos sin traducir; han salido en %s."
              % (idioma, len(claves), BASICO))
        print("         %s%s" % (", ".join(claves[:6]),
                                 " …" if len(claves) > 6 else ""))


def main():
    carga_textos()
    datos = json.loads(DATOS.read_text(encoding="utf-8"))
    categorias = datos["categorias"]

    faltan = [c["icono"] for c in categorias if c["icono"] not in ICONOS]
    if faltan:
        raise SystemExit("Iconos que no existen en ICONOS: %s" % faltan)

    comprueba_urls_unicas(categorias)
    comprueba_fotos(categorias)

    indexables, escritas = [], []
    for idioma in IDIOMAS:
        car = carpeta(idioma)
        if car:
            (RAIZ / car).mkdir(exist_ok=True)
        if idioma != BASICO:
            pares = PORTADA.get(idioma)
            if pares:
                destino(idioma, "index.html").write_text(
                    pagina_portada(idioma, pares), encoding="utf-8")
            else:
                print("  AVISO: «%s» no tiene lista \"portada\" en textos.json, "
                      "asi que no hay portada en ese idioma." % idioma)
        comprueba_portada(categorias, idioma)
        print("  --- %s ---" % IDIOMAS[idioma]["nombre"])

        paginas = fichas = 0
        for c in categorias:
            fichero = "catalogo-%s.html" % c["id"]
            destino(idioma, fichero).write_text(pagina(c, categorias, idioma),
                                                encoding="utf-8")
            escritas.append(ruta_publica(idioma, fichero))
            paginas += 1
            if not c.get("plantilla", False):
                indexables.append((ruta_publica(idioma, fichero), "0.6"))

            for p in c["productos"]:
                fichero = ruta_producto(c, p)
                destino(idioma, fichero).write_text(pagina_producto(c, p, idioma),
                                                    encoding="utf-8")
                escritas.append(ruta_publica(idioma, fichero))
                fichas += 1
                if not c.get("plantilla", False):
                    indexables.append((ruta_publica(idioma, fichero), "0.5"))

        destino(idioma, "historia.html").write_text(pagina_historia(idioma),
                                                    encoding="utf-8")
        destino(idioma, "cesta.html").write_text(pagina_cesta(idioma),
                                                 encoding="utf-8")
        print("      %d páginas de categoría, %d fichas, la historia y la cesta"
              % (paginas, fichas))

    comprueba_huerfanas(escritas)
    escribe_sitemap(indexables, datetime.date.today().isoformat())
    avisa_sin_traducir()
    print("\n%d páginas escritas en %d idiomas desde %s y %s"
          % (len(escritas) + 2 * len(IDIOMAS), len(IDIOMAS), DATOS.name, TEXTOS.name))


if __name__ == "__main__":
    main()

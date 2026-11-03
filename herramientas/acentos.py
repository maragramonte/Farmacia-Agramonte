#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprueba la ortografía que se confunde entre los tres idiomas de la web.

    python herramientas/acentos.py

No es un corrector: es una lista de los errores concretos que se cometen al
traducir entre español, catalán e inglés, que son casi siempre los mismos.

  - El catalán lleva acento GRAVE donde el español lleva agudo: «interès» y no
    «interés», «època» y no «época», «Amèrica» y no «América».
  - El catalán tiene la ela geminada, «l·l», que se escribe mal como «ll» o
    como «l.l»: «col·legi», «pal·liar», «til·la», «intel·lectual».
  - El catalán usa la dièresi para romper diptongos: «construïen», «raïm».
  - Hay palabras de un idioma que se cuelan tal cual en el texto de otro:
    españolas en catalán, catalanas en español, y de los dos en inglés.
  - El inglés de la web es británico (catalogue, neighbourhood, personalised):
    una forma americana es una incoherencia.

Mira los ficheros de cada idioma por separado —el 404, que lleva los tres,
parte por parte— y las claves "es", "ca" y "en" de los dos JSON, incluidas
las traducciones de la portada. Lo que encuentra son AVISOS: hay que mirarlos,
no son necesariamente errores.
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Palabras que en un texto CATALÁN son un error, con lo que deberían ser.
# La clave se busca con límites de palabra y sin distinguir mayúsculas.
EN_CATALAN = {
    # Acento agudo donde el catalán lleva grave
    "interés": "interès", "época": "època", "América": "Amèrica",
    "farmacéutic*": "farmacèutic", "telefón*": "telèfon", "teléfon*": "telèfon",
    "própolis": "pròpolis", "diagnóstic": "diagnòstic",
    # Ela geminada escrita mal
    "colegi": "col·legi", "coleg*": "col·leg", "paliar": "pal·liar",
    "tila": "til·la", "intelectual": "intel·lectual",
    "instalar": "instal·lar", "excelent": "excel·lent",
    "ilustració*": "il·lustració", "ilustracio": "il·lustració",
    "passarela": "passarel·la",
    # Acento que falta: «farmàcia» lo lleva siempre, también en el nombre.
    "farmacia": "farmàcia", "parafarmacia": "parafarmàcia",
    # Palabras españolas que se cuelan
    "cesta": "cistella", "pañal": "bolquer", "champú": "xampú",
    "jarabe": "xarop", "aceite": "oli", "cabello": "cabell",
    "manzanilla": "camamilla", "algodón": "cotó", "hierro": "ferro",
    "mostrador": "taulell", "galletas": "galetes",
    "sábado": "dissabte", "miércoles": "dimecres",
    "año": "any", "años": "anys", "niño": "nen", "niños": "nens",
    "esquinces": "esquinços", "muñequera": "canellera",
    "tobillera": "turmellera", "plantillas": "plantilles",
    "aviso": "avís", "privacidad": "privacitat", "cookies": "galetes",
}

# Y al revés: formas catalanas que en un texto ESPAÑOL son un error.
EN_ESPANOL = {
    "cistella": "cesta", "xampú": "champú", "xarop": "jarabe",
    "taulell": "mostrador", "galetes": "cookies", "avís": "aviso",
    "privacitat": "privacidad", "interès": "interés", "època": "época",
    "Amèrica": "América", "farmacèutic*": "farmacéutico",
    "col·legi": "colegio", "cabell": "cabello", "bolquer": "pañal",
    "qualsevol": "cualquiera", "aquest": "este", "aquesta": "esta",
    "també": "también", "però": "pero", "amb": "con",
    # El nombre de la farmacia va en español sin acento: «Farmacia Agramonte».
    "farmàcia": "farmacia", "parafarmàcia": "parafarmacia",
}

# Y en un texto INGLÉS: lo que se queda sin traducir de los otros dos, y la
# ortografía americana, porque la web escribe en inglés británico.
EN_INGLES = {
    # Español y catalán que se cuelan
    "cesta": "basket", "cistella": "basket",
    "receta": "prescription", "recepta": "prescription",
    "mostrador": "counter", "taulell": "counter",
    "horario": "opening hours", "horari": "opening hours",
    "precio": "price", "preu": "price",
    "encargo": "order", "encàrrec": "order",
    "farmacia": "pharmacy", "farmàcia": "pharmacy",
    "farmacéutic*": "pharmacist",
    "farmacèutic*": "pharmacist",
    "aviso": "notice", "avís": "notice",
    "privacidad": "privacy", "privacitat": "privacy", "galetes": "cookies",
    "lunes": "Monday", "dilluns": "Monday",
    "sábado": "Saturday", "dissabte": "Saturday",
    "también": "also", "també": "also",
    "pañal": "nappy", "bolquer": "nappy",
    "champú": "shampoo", "xampú": "shampoo",
    "jarabe": "syrup", "xarop": "syrup",
    # Ortografía americana
    "color*": "colour", "catalog": "catalogue", "catalogs": "catalogues",
    "neighborhood*": "neighbourhood", "center": "centre",
    "favorite*": "favourite", "personaliz*": "personalis…",
    "authoriz*": "authoris…", "organiz*": "organis…",
    "diaper*": "nappy", "matte": "matt",
}

TABLAS = {"es": EN_ESPANOL, "ca": EN_CATALAN, "en": EN_INGLES}

# Lo que no hay que avisar aunque aparezca: nombres propios, marcas y las
# palabras catalanas que la farmacia usa a propósito también en español.
# Perdonan sólo lo que cae dentro de ellas («col·legi» en «Col·legi»), así que
# la mayoría no hace nada hasta que una palabra de las tablas les coincide
# dentro. Una cita entera en otro idioma no va aquí: se marca con lang en el
# HTML, que además le dice al lector de pantalla cómo pronunciarla.
PERDONADAS = {
    "Plaça", "Llana", "Col·legi", "Farmacèutics", "Catalunya",
    "Generalitat", "Salut", "Llei", "Avène", "Cases", "Joaquim", "Agramonte",
    "Caterina", "República", "Havana", "Barcelona", "Born", "Anthelios",
    "Hydrance", "Hydraphase", "Cleanance", "Solaire", "Dermo", "Pediatrics",
    "Posay", "Roche", "Solución", "Casas", "Buchó", "Zoila", "Saurina",
    "cofb", "gencat", "aepd", "boe", "portaljuridic", "salutweb",
    # El correo y la cuenta de Instagram, que llevan «farmacia» sin traducir.
    "farmacia.lallana", "farmacia.agramonte",
    # Marcas con ortografía americana: el nombre es suyo.
    "Color Light", "Heliocare Color",
}

# Y lo que se perdona sólo en un idioma. El nombre de la farmacia se escribe
# como lo pide cada uno: «Farmacia Agramonte» en español y en inglés, que en
# inglés es un nombre propio y no se traduce, y «Farmàcia Agramonte» en
# catalán. Perdonarlo en PERDONADAS lo taparía también en catalán, que es
# justo donde le falta el acento.
PERDONADAS_EN = {
    "en": {"Farmacia Agramonte", "Farmacia Joaquim Cases"},
}

ETIQUETA = re.compile(r"<[^>]+>")

# Lo que no cuenta como texto que lee una persona.
MUDAS = {"script", "style", "svg", "head"}
# Las que no cierran y por tanto no abren nivel.
SUELTAS = {"br", "hr", "img", "meta", "link", "input", "source"}


class Visible(HTMLParser):
    """Saca el texto que lee una persona en un idioma concreto.

    Se salta los <script>, <style>, <svg> y la cabeza, los comentarios —que van
    en español en todos los idiomas a propósito, porque son para quien
    mantiene el código— y, lo importante aquí, **lo que está en otro idioma**:
    cada elemento habla el de su lang o, si no lleva, el de quien lo contiene.
    Así se puede sacar sólo el inglés del 404, que lleva los tres porque GitHub
    Pages sirve el mismo para todo el sitio, y el selector de idioma, que
    nombra cada idioma en su propia lengua, no ensucia ninguno.

    Con un parser y no con expresiones regulares porque las etiquetas se
    anidan: un <div lang="ca"> con <p> dentro tiene un </p> antes de su </div>,
    y a una expresión regular eso la engaña."""

    def __init__(self, idioma, del_documento):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.idioma = idioma
        self.del_documento = del_documento
        self.trozos = []
        self.pila = []          # (etiqueta, idioma, muda)

    def _estado(self):
        return self.pila[-1][1:] if self.pila else (self.del_documento, False)

    def handle_starttag(self, etiqueta, atributos):
        if etiqueta in SUELTAS:
            return
        idioma, muda = self._estado()
        lang = dict(atributos).get("lang")
        self.pila.append((etiqueta, lang[:2] if lang else idioma,
                          muda or etiqueta in MUDAS))

    def handle_endtag(self, etiqueta):
        for i in range(len(self.pila) - 1, -1, -1):
            if self.pila[i][0] == etiqueta:
                del self.pila[i:]
                return

    def handle_data(self, datos):
        idioma, muda = self._estado()
        if not muda and idioma == self.idioma:
            self.trozos.append(datos)


def texto_visible(html, idioma=None):
    """El texto de la página en ese idioma; si no se dice, en el del <html>."""
    m = re.search(r'<html[^>]*\blang="([^"]*)"', html)
    del_documento = m.group(1)[:2] if m else ""
    v = Visible(idioma or del_documento, del_documento)
    v.feed(html)
    return " ".join(v.trozos)


def tramos_perdonados(texto, perdonadas=PERDONADAS):
    """Dónde están, en el texto, los nombres que se perdonan. Entre palabra y
    palabra vale cualquier espacio, porque el HTML parte las frases largas y
    un nombre puede quedar a caballo de dos líneas."""
    return [(m.start(), m.end()) for p in perdonadas
            for m in re.finditer(r"\s+".join(map(re.escape, p.split())), texto)]


def busca(texto, tabla, donde, avisos, perdonadas=PERDONADAS):
    # Se perdona lo que cae DENTRO de un nombre propio («Col·legi» en «Col·legi
    # de Farmacèutics»), no lo que tiene al lado: el nombre de la farmacia sale
    # en todas las páginas, y perdonar su alrededor tapaba los errores de ahí.
    perdonados = tramos_perdonados(texto, perdonadas)
    for mala, buena in tabla.items():
        # Palabra entera, salvo las que acaban en * que son raíces: así
        # «cabell» no casa dentro de «cabelludo», y «farmacéutic*» sí coge
        # tanto «farmacéutico» como «farmacéutica».
        if mala.endswith("*"):
            patron = r"\b%s" % re.escape(mala[:-1])
        else:
            patron = r"\b%s\b" % re.escape(mala)
        for m in re.finditer(patron, texto, re.IGNORECASE):
            if any(ini <= m.start() and m.end() <= fin for ini, fin in perdonados):
                continue
            trozo = texto[max(0, m.start() - 30):m.end() + 30]
            trozo = " ".join(trozo.split())
            avisos.append((donde, mala, buena, trozo))


def ela_geminada(texto, donde, avisos):
    """La ela geminada escrita con punto normal en vez de punt volat. Pasa al
    copiar de un sitio que no lo tiene."""
    # Entre letras y no tras un límite de palabra: la ela geminada va siempre
    # dentro de la palabra (col·legi), así que con \b no saltaba nunca.
    for m in re.finditer(r"(?<=[^\W\d_])l\.l(?=[^\W\d_])", texto):
        trozo = " ".join(texto[max(0, m.start() - 25):m.end() + 25].split())
        avisos.append((donde, "l.l", "l·l", trozo))


def revisa(texto, idioma, donde, avisos):
    """Pasa a un texto la tabla de su idioma, y en catalán la ela geminada."""
    busca(texto, TABLAS[idioma], donde, avisos,
          PERDONADAS | PERDONADAS_EN.get(idioma, set()))
    if idioma == "ca":
        ela_geminada(texto, donde, avisos)


# Las páginas que se escriben a mano. Las demás —catálogo, historia, cesta y
# las portadas traducidas— se generan, y su texto se revisa en los JSON.
A_MANO = ("index.html", "aviso-legal.html", "privacidad.html", "cookies.html")


def textos_de_json(datos):
    """Los textos de un JSON, agrupados por idioma.

    Las claves "es", "ca" y "en" de cualquier sitio, y además las traducciones
    de la portada, que van en pares [español, traducción] dentro de
    "portada" → idioma: de ellas sale index.html en catalán y en inglés."""
    por_idioma = {}

    def recoge(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in TABLAS and not isinstance(v, dict):
                    por_idioma.setdefault(k, []).append(json.dumps(v, ensure_ascii=False))
                elif k not in ("_leeme", "_leeme_portada", "idiomas", "portada"):
                    recoge(v)
        elif isinstance(o, list):
            for v in o:
                recoge(v)

    recoge(datos)
    if isinstance(datos, dict):
        for idioma, pares in datos.get("portada", {}).items():
            if idioma in TABLAS:
                por_idioma.setdefault(idioma, []).extend(p[1] for p in pares)
    return por_idioma


def main():
    avisos = []

    # Las páginas escritas a mano de cada idioma.
    for idioma, carpeta in (("es", ""), ("ca", "ca"), ("en", "en")):
        for nombre in A_MANO:
            f = RAIZ / carpeta / nombre
            if carpeta and nombre == "index.html":
                continue   # la portada traducida se genera desde la española
            if f.exists():
                donde = "%s/%s" % (carpeta, nombre) if carpeta else nombre
                revisa(texto_visible(f.read_text(encoding="utf-8")), idioma, donde, avisos)

    # El 404, que es uno para todo el sitio y lleva los tres idiomas.
    f = RAIZ / "404.html"
    if f.exists():
        html = f.read_text(encoding="utf-8")
        for idioma in TABLAS:
            revisa(texto_visible(html, idioma), idioma, "404.html (%s)" % idioma, avisos)

    # Y los textos de los dos JSON, idioma por idioma.
    for nombre in ("textos.json", "catalogo-datos.json"):
        datos = json.loads((RAIZ / "herramientas" / nombre).read_text(encoding="utf-8"))
        for idioma, trozos in textos_de_json(datos).items():
            t = ETIQUETA.sub(" ", " ".join(trozos))
            revisa(t, idioma, "%s (%s)" % (nombre, idioma), avisos)

    if not avisos:
        print("Sin avisos de ortografía entre idiomas.")
        return 0

    print("%d avisos. Son cosas que MIRAR, no necesariamente errores:\n" % len(avisos))
    ultimo = None
    for donde, mala, buena, trozo in avisos:
        if donde != ultimo:
            print("  %s" % donde)
            ultimo = donde
        print("    «%s» → ¿«%s»?" % (mala, buena))
        print("       …%s…" % trozo)
    return 1


if __name__ == "__main__":
    sys.exit(main())

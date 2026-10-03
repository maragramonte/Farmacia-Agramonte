#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprueba la ortografía que se confunde entre el español y el catalán.

    python herramientas/acentos.py

No es un corrector: es una lista de los errores concretos que se cometen al
traducir entre estos dos idiomas, que son casi siempre los mismos.

  - El catalán lleva acento GRAVE donde el español lleva agudo: «interès» y no
    «interés», «època» y no «época», «Amèrica» y no «América».
  - El catalán tiene la ela geminada, «l·l», que se escribe mal como «ll» o
    como «l.l»: «col·legi», «pal·liar», «til·la», «intel·lectual».
  - El catalán usa la dièresi para romper diptongos: «construïen», «raïm».
  - Y hay palabras españolas que se cuelan tal cual en un texto catalán.

Mira los ficheros de cada idioma por separado, y también las claves "es" y "ca"
de los dos JSON. Lo que encuentra son AVISOS: hay que mirarlos, no son
necesariamente errores.
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
}

# Lo que no hay que avisar aunque aparezca: nombres propios, marcas y las
# palabras catalanas que la farmacia usa a propósito también en español.
PERDONADAS = {
    "Farmàcia", "Plaça", "Llana", "Col·legi", "Farmacèutics", "Catalunya",
    "Generalitat", "Salut", "Llei", "Avène", "Cases", "Joaquim", "Agramonte",
    "Caterina", "República", "Havana", "Barcelona", "Born", "Anthelios",
    "Hydrance", "Hydraphase", "Cleanance", "Solaire", "Dermo", "Pediatrics",
    "Posay", "Roche", "Solución", "Casas", "Bucho", "Zoila", "Saurina",
    "cofb", "gencat", "aepd", "boe", "portaljuridic", "salutweb",
}

ETIQUETA = re.compile(r"<[^>]+>")

# Lo que no cuenta como texto que lee una persona.
MUDAS = {"script", "style", "svg", "head"}
# Las que no cierran y por tanto no abren nivel.
SUELTAS = {"br", "hr", "img", "meta", "link", "input", "source"}


class Visible(HTMLParser):
    """Saca el texto que lee una persona, en el idioma del documento.

    Se salta los <script>, <style>, <svg> y la cabeza, los comentarios —que van
    en español en los dos idiomas a propósito, porque son para quien mantiene
    el código— y, lo importante aquí, **lo que está marcado con un lang
    distinto del documento**: el 404 es bilingüe porque GitHub Pages sirve el
    mismo para todo el sitio, y el selector de idioma nombra cada idioma en su
    propia lengua.

    Con un parser y no con expresiones regulares porque las etiquetas se
    anidan: un <div lang="ca"> con <p> dentro tiene un </p> antes de su </div>,
    y a una expresión regular eso la engaña."""

    def __init__(self, propio):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.propio = propio
        self.trozos = []
        self.pila = []          # (etiqueta, callar)
        self.callando = 0

    def handle_starttag(self, etiqueta, atributos):
        if etiqueta in SUELTAS:
            return
        callar = etiqueta in MUDAS
        if not callar and etiqueta != "html":
            for nombre, valor in atributos:
                if nombre == "lang" and valor and valor[:2] != self.propio:
                    callar = True
        self.pila.append((etiqueta, callar))
        if callar:
            self.callando += 1

    def handle_endtag(self, etiqueta):
        for i in range(len(self.pila) - 1, -1, -1):
            if self.pila[i][0] == etiqueta:
                for _, callar in self.pila[i:]:
                    if callar:
                        self.callando -= 1
                del self.pila[i:]
                return

    def handle_data(self, datos):
        if not self.callando:
            self.trozos.append(datos)


def texto_visible(html):
    m = re.search(r'<html[^>]*\blang="([^"]*)"', html)
    v = Visible(m.group(1)[:2] if m else "")
    v.feed(html)
    return " ".join(v.trozos)


def busca(texto, tabla, donde, avisos):
    for mala, buena in tabla.items():
        if buena is None:
            continue
        # Palabra entera, salvo las que acaban en * que son raíces: así
        # «cabell» no casa dentro de «cabelludo», y «farmacéutic*» sí coge
        # tanto «farmacéutico» como «farmacéutica».
        if mala.endswith("*"):
            patron = r"\b%s" % re.escape(mala[:-1])
        else:
            patron = r"\b%s\b" % re.escape(mala)
        for m in re.finditer(patron, texto, re.IGNORECASE):
            trozo = texto[max(0, m.start() - 30):m.end() + 30]
            trozo = " ".join(trozo.split())
            if any(p in trozo for p in PERDONADAS):
                continue
            avisos.append((donde, mala, buena, trozo))


def ela_geminada(texto, donde, avisos):
    """La ela geminada escrita con punto normal en vez de punt volat. Pasa al
    copiar de un sitio que no lo tiene."""
    for m in re.finditer(r"\bl\.l", texto):
        trozo = " ".join(texto[max(0, m.start() - 25):m.end() + 25].split())
        avisos.append((donde, "l.l", "l·l", trozo))


def main():
    avisos = []

    # Las páginas catalanas que se escriben a mano.
    for f in sorted((RAIZ / "ca").glob("*.html")):
        if f.name.startswith("catalogo-") or f.name in ("index.html", "cesta.html", "historia.html"):
            continue   # ésas se generan; su texto vive en los JSON
        t = texto_visible(f.read_text(encoding="utf-8"))
        busca(t, EN_CATALAN, "ca/" + f.name, avisos)
        ela_geminada(t, "ca/" + f.name, avisos)

    # Las españolas escritas a mano.
    for nombre in ("index.html", "aviso-legal.html", "privacidad.html",
                   "cookies.html", "404.html"):
        f = RAIZ / nombre
        if not f.exists():
            continue
        t = texto_visible(f.read_text(encoding="utf-8"))
        busca(t, EN_ESPANOL, nombre, avisos)

    # Y los textos de los dos JSON, idioma por idioma.
    for nombre in ("textos.json", "catalogo-datos.json"):
        datos = json.loads((RAIZ / "herramientas" / nombre).read_text(encoding="utf-8"))
        por_idioma = {}

        def recoge(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k in ("es", "ca", "en") and not isinstance(v, dict):
                        por_idioma.setdefault(k, []).append(json.dumps(v, ensure_ascii=False))
                    elif k not in ("_leeme", "_leeme_portada", "idiomas", "portada"):
                        recoge(v)
            elif isinstance(o, list):
                for v in o:
                    recoge(v)

        recoge(datos)
        for idioma, trozos in por_idioma.items():
            t = ETIQUETA.sub(" ", " ".join(trozos))
            if idioma == "ca":
                busca(t, EN_CATALAN, "%s (ca)" % nombre, avisos)
                ela_geminada(t, "%s (ca)" % nombre, avisos)
            elif idioma == "es":
                busca(t, EN_ESPANOL, "%s (es)" % nombre, avisos)

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

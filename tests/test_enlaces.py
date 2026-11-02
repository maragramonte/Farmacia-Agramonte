"""Que ninguna página ni hoja de estilos pida un fichero propio que no existe.

Es lo que se rompe al renombrar o borrar algo: al quitar Playfair Display,
una sola página que la siguiera precargando pediría un fichero que ya no está,
y eso no se ve en el navegador salvo mirando la consola."""

import re
from pathlib import Path
from urllib.parse import unquote

import pytest

from conftest import RAIZ

FUERA = {".git", ".gstack", ".claude", ".idea", "diseno", "docs", "tests",
         "herramientas", "__pycache__", ".pytest_cache"}

ATRIBUTO = re.compile(r'\b(?:href|src|srcset|content)="([^"]+)"')
URL_CSS = re.compile(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)')
EXTERNO = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|#|\?)", re.IGNORECASE)


def ficheros(patron):
    for f in sorted(RAIZ.rglob(patron)):
        if not FUERA.intersection(f.relative_to(RAIZ).parts):
            yield f


def rotos(origen, valores):
    for valor in valores:
        valor = valor.strip()
        if not valor or EXTERNO.match(valor):
            continue
        ruta = unquote(valor.split("#")[0].split("?")[0])
        if not ruta or "/" not in ruta and "." not in ruta:
            continue   # un content="..." de texto, no una ruta
        if not (origen.parent / ruta).exists():
            yield valor


def nombre(f):
    return f.relative_to(RAIZ).as_posix()


@pytest.mark.parametrize("pagina", list(ficheros("*.html")), ids=nombre)
def test_la_pagina_no_pide_ficheros_que_no_existen(pagina):
    html = pagina.read_text(encoding="utf-8")
    valores = []
    for v in ATRIBUTO.findall(html):
        # srcset lleva varias rutas, cada una con su ancho detrás
        valores.extend(trozo.split()[0] for trozo in v.split(",") if trozo.strip())
    valores = [v for v in valores if re.search(r"\.[a-z0-9]{2,5}([#?].*)?$", v, re.I)]
    assert not list(rotos(pagina, valores))


@pytest.mark.parametrize("hoja", list(ficheros("*.css")), ids=nombre)
def test_la_hoja_de_estilos_no_pide_ficheros_que_no_existen(hoja):
    css = hoja.read_text(encoding="utf-8")
    assert not list(rotos(hoja, URL_CSS.findall(css)))


def test_cada_tipografia_lleva_su_licencia():
    """La OFL exige que la licencia viaje con la fuente."""
    carpeta = RAIZ / "tipografias"
    fuentes = {f.name.split("-")[0] for f in carpeta.glob("*.woff2")}
    licencias = {f.stem.split("-", 1)[1].lower() for f in carpeta.glob("LICENCIA-*.txt")}
    for familia in fuentes:
        assert any(l.startswith(familia) for l in licencias), familia

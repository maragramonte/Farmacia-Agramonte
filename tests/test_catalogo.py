"""El generador del catálogo: herramientas/catalogo.py."""

import os
import re
import shutil
import subprocess
import sys

import pytest

from conftest import RAIZ


# --- Lo publicado es lo que sale del generador ---------------------------

# Lo que no hace falta para generar y sólo engordaría la copia.
NO_COPIAR = shutil.ignore_patterns(".git", ".gstack", ".claude", ".idea",
                                   "diseno", "docs", "__pycache__", ".pytest_cache")
FECHA = re.compile(r"<lastmod>[^<]*</lastmod>")


def generados(raiz):
    """Las páginas que escribe catalogo.py, más el sitemap."""
    ficheros = {"sitemap.xml"}
    for car in ("", "ca", "en"):
        base = raiz / car if car else raiz
        for patron in ("catalogo-*.html", "historia.html", "cesta.html"):
            for f in base.glob(patron):
                ficheros.add(f.relative_to(raiz).as_posix())
        if car:
            ficheros.add("%s/index.html" % car)
    return ficheros


def test_regenerar_no_cambia_nada(tmp_path):
    """Si alguien edita a mano una página generada, o cambia el JSON y no
    regenera, lo publicado deja de ser lo que dice el JSON. Se genera en una
    copia del repositorio y se compara fichero a fichero con lo que hay."""
    copia = tmp_path / "web"
    shutil.copytree(RAIZ, copia, ignore=NO_COPIAR)

    entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
    hecho = subprocess.run([sys.executable, "herramientas/catalogo.py"], cwd=copia,
                           capture_output=True, text=True, encoding="utf-8", env=entorno,
                           stdin=subprocess.DEVNULL)
    assert hecho.returncode == 0, hecho.stdout + hecho.stderr
    assert "AVISO" not in hecho.stdout, hecho.stdout

    distintos = []
    for nombre in sorted(generados(RAIZ) | generados(copia)):
        antes, despues = RAIZ / nombre, copia / nombre
        if not antes.exists() or not despues.exists():
            distintos.append(nombre)
            continue
        a = antes.read_text(encoding="utf-8")
        d = despues.read_text(encoding="utf-8")
        if nombre == "sitemap.xml":   # lleva la fecha del día en que se generó
            a, d = FECHA.sub("", a), FECHA.sub("", d)
        if a != d:
            distintos.append(nombre)
    assert not distintos, (
        "Estas páginas no coinciden con lo que genera catalogo.py; ejecuta "
        "python herramientas/catalogo.py: %s" % ", ".join(distintos))


# --- Las piezas sueltas -------------------------------------------------

def test_slug_quita_acentos_y_signos(catalogo):
    p = {"nombre": "Muñequera Farmalastic Neopreno, Talla Única"}
    assert catalogo.slug_producto(p) == "munequera-farmalastic-neopreno-talla-unica"


def test_slug_sale_del_espanol_aunque_haya_traduccion(catalogo):
    p = {"nombre": {"es": "Champú Cafeína", "ca": "Xampú Cafeïna"}}
    assert catalogo.slug_producto(p) == "champu-cafeina"


def test_slug_respeta_el_id_fijado(catalogo):
    p = {"nombre": "Nombre nuevo del producto", "id": "nombre-de-siempre"}
    assert catalogo.slug_producto(p) == "nombre-de-siempre"
    assert catalogo.ruta_producto({"id": "solares"}, p) == "catalogo-solares-nombre-de-siempre.html"


def test_urls_repetidas_paran_el_generador(catalogo):
    categorias = [{"id": "solares", "productos": [
        {"nombre": "Crema Solar SPF 50"}, {"nombre": "Crema solar SPF-50"}]}]
    with pytest.raises(SystemExit, match="misma URL"):
        catalogo.comprueba_urls_unicas(categorias)


def test_escapa_lo_que_romperia_el_html(catalogo):
    assert catalogo.escapa('<b>"A & B"</b>') == "&lt;b&gt;&quot;A &amp; B&quot;&lt;/b&gt;"


def test_recorta_deja_igual_lo_que_cabe(catalogo):
    assert catalogo.recorta("Hidratante ligera.", 160) == "Hidratante ligera."


def test_recorta_por_el_final_de_frase(catalogo):
    texto = "Protección solar diaria para el rostro. Textura ligera que no deja brillos."
    assert catalogo.recorta(texto, 50) == "Protección solar diaria para el rostro."


def test_recorta_nunca_parte_una_palabra(catalogo):
    texto = "Crema reparadora intensiva para pieles muy secas y atópicas"
    corto = catalogo.recorta(texto, 30)
    assert corto.endswith("…")
    assert len(corto) <= 30
    sin_puntos = corto[:-1]
    assert texto.startswith(sin_puntos)
    assert texto[len(sin_puntos)] == " "      # cortó justo antes de un espacio


def test_recorta_no_acaba_en_preposicion(catalogo):
    corto = catalogo.recorta("Gel limpiador suave de uso diario para toda la familia", 25)
    assert corto.rsplit(" ", 1)[-1].rstrip("…") not in ("de", "y", "el", "la", "a")


def test_descripcion_meta_cabe_en_160(catalogo):
    import json
    datos = json.loads((RAIZ / "herramientas" / "catalogo-datos.json").read_text(encoding="utf-8"))
    for c in datos["categorias"]:
        for p in c["productos"]:
            for idioma in catalogo.IDIOMAS:
                d = catalogo.descripcion_meta(p, idioma)
                assert len(d) <= catalogo.LARGO_META, (idioma, p["nombre"], d)


# --- El sitemap -----------------------------------------------------------

def test_sitemap_solo_apunta_a_paginas_que_existen():
    sitemap = (RAIZ / "sitemap.xml").read_text(encoding="utf-8")
    base = "https://maragramonte.github.io/Farmacia-Agramonte/"
    locs = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    assert locs
    for loc in locs:
        assert loc.startswith(base), loc
        ruta = loc[len(base):]
        if ruta == "" or ruta.endswith("/"):   # la portada de cada idioma
            ruta += "index.html"
        assert (RAIZ / ruta).is_file(), loc
        assert not ruta.endswith("cesta.html"), "la cesta lleva noindex: " + loc

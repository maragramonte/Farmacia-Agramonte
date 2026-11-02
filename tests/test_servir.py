"""El servidor local, servir.py.

Escucha en toda la red para poder abrir la web desde el móvil, así que lo que
sirve lo ve cualquiera de la misma wifi: no puede servir .git ni lo que se
guarda sólo en local."""

import importlib.util
import threading
import urllib.error
import urllib.request

import pytest

from conftest import RAIZ


@pytest.fixture(scope="module")
def servir():
    spec = importlib.util.spec_from_file_location("servir", RAIZ / "servir.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="module")
def url(servir):
    """El servidor de verdad, en un puerto libre, mientras duren los tests."""
    servidor = servir.Servidor(("127.0.0.1", 0), servir.Manejador)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    yield "http://127.0.0.1:%d/" % servidor.server_address[1]
    servidor.shutdown()
    servidor.server_close()


def estado(url, ruta):
    try:
        with urllib.request.urlopen(url + ruta) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


@pytest.mark.parametrize("ruta", [
    ".git/config", ".git/HEAD", ".claude/settings.json", ".gstack/x",
    "CLAUDE.md", "claude.md", "%2egit/config",
])
def test_no_sirve_lo_oculto_ni_lo_local(url, ruta):
    assert estado(url, ruta) == 404


@pytest.mark.parametrize("ruta", [
    "", "index.html", "cesta.js", "tipografias/karla-variable.woff2", "ca/",
])
def test_sirve_la_web(url, ruta):
    assert estado(url, ruta) == 200


def test_no_lista_carpetas_como_github_pages(url):
    assert estado(url, "herramientas/") == 404


@pytest.mark.parametrize("argumentos, puerto", [
    ([], 8000), (["3000"], 3000), (["--no-abrir", "8080"], 8080),
])
def test_lee_el_puerto(servir, argumentos, puerto):
    assert servir.puerto_de(argumentos) == puerto


@pytest.mark.parametrize("argumentos", [["0"], ["70000"]])
def test_un_puerto_imposible_para_con_un_mensaje(servir, argumentos):
    with pytest.raises(SystemExit, match="puerto"):
        servir.puerto_de(argumentos)

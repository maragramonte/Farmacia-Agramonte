"""Lo que comparten los tests: la raíz del repositorio y cómo cargar las
herramientas, que son scripts sueltos y no un paquete."""

import importlib.util
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent


def carga(nombre):
    """Importa herramientas/<nombre>.py sin ejecutar su main()."""
    ruta = RAIZ / "herramientas" / ("%s.py" % nombre)
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="session")
def catalogo():
    m = carga("catalogo")
    m.carga_textos()
    return m


@pytest.fixture(scope="session")
def acentos():
    return carga("acentos")

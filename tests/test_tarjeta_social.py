"""La tarjeta social, herramientas/tarjeta-social.py: cómo elige las fuentes.

og.png se publica (es la imagen al compartir la web y la del README), así que
si sale con otra tipografía tiene que decirlo, no colarse en silencio."""

import shutil

from conftest import RAIZ

FUENTE_BUENA = RAIZ / "tipografias" / "instrument-serif.woff2"


def carpetas(tarjeta, tmp_path, propia=None, respaldo=False):
    """Monta una carpeta de tipografías y otra de respaldo de mentira."""
    tipos, windows = tmp_path / "tipos", tmp_path / "windows"
    tipos.mkdir()
    windows.mkdir()
    if propia == "buena":
        shutil.copy(FUENTE_BUENA, tipos / "propia.woff2")
    elif propia == "rota":
        (tipos / "propia.woff2").write_bytes(b"esto no es una fuente")
    if respaldo:
        shutil.copy(FUENTE_BUENA, windows / "respaldo.ttf")
    tarjeta.TIPOS, tarjeta.WINDOWS = tipos, windows
    return tipos, windows


def test_usa_la_fuente_propia_sin_avisar(tarjeta, tmp_path, capsys):
    tipos, _ = carpetas(tarjeta, tmp_path, propia="buena", respaldo=True)
    f = tarjeta.fuente("propia.woff2", "respaldo.ttf", 20)
    assert f.path == str(tipos / "propia.woff2")
    assert capsys.readouterr().out == ""


def test_si_la_propia_no_se_lee_cae_en_la_de_respaldo_y_avisa(tarjeta, tmp_path, capsys):
    _, windows = carpetas(tarjeta, tmp_path, propia="rota", respaldo=True)
    f = tarjeta.fuente("propia.woff2", "respaldo.ttf", 20)
    assert f.path == str(windows / "respaldo.ttf")
    assert "AVISO" in capsys.readouterr().out


def test_sin_ninguna_usa_la_de_pillow_y_avisa(tarjeta, tmp_path, capsys):
    carpetas(tarjeta, tmp_path)
    assert tarjeta.fuente("propia.woff2", "respaldo.ttf", 20) is not None
    assert "AVISO" in capsys.readouterr().out

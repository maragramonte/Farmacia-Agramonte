"""El comprobador de ortografía entre español y catalán: herramientas/acentos.py."""


def avisos_de(acentos, texto, tabla):
    avisos = []
    acentos.busca(texto, tabla, "prueba", avisos)
    return [(mala, buena) for _, mala, buena, _ in avisos]


def test_avisa_de_una_palabra_catalana_en_un_texto_espanol(acentos):
    assert ("cistella", "cesta") in avisos_de(
        acentos, "Añade el producto a la cistella y envíalo", acentos.EN_ESPANOL)


def test_avisa_del_acento_agudo_en_catalan(acentos):
    assert ("interés", "interès") in avisos_de(
        acentos, "És d'interés per a tothom", acentos.EN_CATALAN)


def test_las_raices_cogen_masculino_y_femenino(acentos):
    avisos = avisos_de(acentos, "La farmacéutica del barri", acentos.EN_CATALAN)
    assert ("farmacéutic*", "farmacèutic") in avisos


def test_palabra_entera_no_casa_dentro_de_otra(acentos):
    assert avisos_de(acentos, "Cuero cabelludo sensible", acentos.EN_ESPANOL) == []


def test_perdona_los_nombres_propios(acentos):
    # «Farmàcia» va así a propósito también en español
    assert avisos_de(acentos, "Col·legi de Farmacèutics de Barcelona",
                     acentos.EN_ESPANOL) == []


def test_un_nombre_propio_cerca_no_tapa_un_error(acentos):
    # «Farmàcia Agramonte» sale en todas las páginas: si perdonar un nombre
    # perdonase también lo que tiene al lado, ahí no se vería nada.
    assert ("cistella", "cesta") in avisos_de(
        acentos, "Farmàcia Agramonte: tu cistella", acentos.EN_ESPANOL)


def test_ela_geminada_con_punto_normal(acentos):
    avisos = []
    acentos.ela_geminada("Anem al col.legi", "prueba", avisos)
    assert [(m, b) for _, m, b, _ in avisos] == [("l.l", "l·l")]


def test_texto_visible_se_salta_otros_idiomas_y_scripts(acentos):
    html = ('<html lang="es"><head><title>cistella</title></head><body>'
            '<p>Tu cesta</p><div lang="ca"><p>La teva cistella</p></div>'
            '<script>var cistella = 1;</script><p>está vacía</p></body></html>')
    visible = acentos.texto_visible(html)
    assert "Tu cesta" in visible and "está vacía" in visible
    assert "cistella" not in visible


def test_la_web_no_tiene_avisos(acentos, capsys):
    assert acentos.main() == 0, capsys.readouterr().out

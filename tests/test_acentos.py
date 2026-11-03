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
    assert avisos_de(acentos, "Col·legi de Farmacèutics de Barcelona",
                     acentos.EN_ESPANOL) == []


def test_un_nombre_propio_cerca_no_tapa_un_error(acentos):
    # «Plaça de la Llana» sale en todas las páginas: si perdonar un nombre
    # perdonase también lo que tiene al lado, ahí no se vería nada.
    assert ("cistella", "cesta") in avisos_de(
        acentos, "Plaça de la Llana: tu cistella", acentos.EN_ESPANOL)


def avisos_revisando(acentos, texto, idioma):
    avisos = []
    acentos.revisa(texto, idioma, "prueba", avisos)
    return [(mala, buena) for _, mala, buena, _ in avisos]


def test_el_nombre_en_espanol_va_sin_acento(acentos):
    assert ("farmàcia", "farmacia") in avisos_revisando(
        acentos, "¿Por qué elegir Farmàcia Agramonte?", "es")
    assert avisos_revisando(
        acentos, "¿Por qué elegir Farmacia Agramonte?", "es") == []


def test_el_nombre_en_catalan_lleva_acento(acentos):
    assert ("farmacia", "farmàcia") in avisos_revisando(
        acentos, "Per què triar la Farmacia Agramonte?", "ca")
    assert avisos_revisando(
        acentos, "Per què triar la Farmàcia Agramonte?", "ca") == []


def test_el_nombre_en_ingles_va_sin_acento_y_sin_traducir(acentos):
    assert ("farmàcia", "pharmacy") in avisos_revisando(
        acentos, "Why choose Farmàcia Agramonte?", "en")
    assert avisos_revisando(
        acentos, "Why choose Farmacia Agramonte, formerly Farmacia Joaquim "
        "Cases?", "en") == []
    # Aunque el HTML lo parta en dos líneas.
    assert avisos_revisando(acentos, "belong to Farmacia\n    Agramonte", "en") == []
    # Perdonar el nombre no perdona la palabra suelta.
    assert ("farmacia", "pharmacy") in avisos_revisando(
        acentos, "Come to the farmacia", "en")


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


def test_avisa_de_una_palabra_espanola_en_un_texto_ingles(acentos):
    assert ("receta", "prescription") in avisos_de(
        acentos, "Send us your receta on WhatsApp", acentos.EN_INGLES)


def test_avisa_de_una_palabra_catalana_en_un_texto_ingles(acentos):
    assert ("cistella", "basket") in avisos_de(
        acentos, "Add it to your cistella", acentos.EN_INGLES)


def test_avisa_de_la_ortografia_americana(acentos):
    # La web está en inglés británico: catalogue, neighbourhood, personalised.
    avisos = avisos_de(acentos, "Browse the catalog of our neighborhood pharmacy",
                       acentos.EN_INGLES)
    assert ("catalog", "catalogue") in avisos
    assert ("neighborhood*", "neighbourhood") in avisos


def test_el_ingles_britanico_no_avisa(acentos):
    assert avisos_de(acentos, "Browse the catalogue of our neighbourhood "
                     "pharmacy: personalised advice, in colour.", acentos.EN_INGLES) == []


def test_una_marca_con_ortografia_americana_no_avisa(acentos):
    assert avisos_de(acentos, "Color Light Facial Cream SPF 50",
                     acentos.EN_INGLES) == []


def test_texto_visible_de_un_idioma_concreto(acentos):
    # El 404 es uno para todo el sitio y lleva los tres idiomas: cada parte se
    # revisa con la tabla de su idioma.
    html = ('<html lang="es"><body><p>Esta página no existe</p>'
            '<div lang="ca"><p>Aquesta pàgina no existeix</p></div>'
            '<div lang="en"><p>This page does not exist</p></div></body></html>')
    assert acentos.texto_visible(html, "en").strip() == "This page does not exist"
    assert acentos.texto_visible(html, "ca").strip() == "Aquesta pàgina no existeix"
    assert acentos.texto_visible(html).strip() == "Esta página no existe"


def test_la_web_no_tiene_avisos(acentos, capsys):
    assert acentos.main() == 0, capsys.readouterr().out

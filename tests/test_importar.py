"""El importador del export del programa de gestión: herramientas/importar.py.

Lo que más importa aquí es que reimportar no se coma lo escrito a mano: el
export trae nombres y formatos, y la ficha de verdad (resumen, traducciones,
epígrafes) la escribe la farmacia en catalogo-datos.json."""

FICHA_ESCRITA = {
    "id": "avene-agua-termal-150-ml",
    "nombre": {"es": "Avène Agua Termal 150 ml", "ca": "Avène Aigua Termal 150 ml"},
    "formato": "Spray · 150 ml",
    "resumen": {"es": "Calma la piel sensible.", "ca": "Calma la pell sensible."},
}


def importado(nombre, formato=""):
    """Un producto tal como lo deja construye(): id, nombre y quizá formato."""
    p = {"id": nombre.lower().replace(" ", "-"), "nombre": nombre}
    if formato:
        p["formato"] = formato
    return p


def test_reimportar_conserva_la_ficha_escrita_a_mano(importar):
    nuevo = importado("avene agua termal 150 ml", "150 ml")
    lista, conservados = importar.fusiona([FICHA_ESCRITA], [nuevo], anadir=False)
    assert lista == [FICHA_ESCRITA]
    assert conservados == 1


def test_sustituir_quita_lo_que_ya_no_viene_en_el_export(importar):
    otro = importado("cerave limpiadora")
    lista, conservados = importar.fusiona([FICHA_ESCRITA], [otro], anadir=False)
    assert lista == [otro]
    assert conservados == 0


def test_anadir_no_repite_lo_que_ya_estaba(importar):
    repetido = importado("avene agua termal 150 ml")
    nuevo = importado("cerave limpiadora")
    lista, conservados = importar.fusiona([FICHA_ESCRITA], [repetido, nuevo], anadir=True)
    assert lista == [FICHA_ESCRITA, nuevo]
    assert conservados == 1


def test_reconoce_por_el_nombre_una_ficha_sin_id(importar):
    """Las fichas antiguas pueden no llevar "id": su URL sale del nombre en
    español, igual que en catalogo.py."""
    sin_id = {"nombre": {"es": "Avène Agua Termal 150 ml"}, "resumen": "Escrito a mano."}
    nuevo = importado("avene agua termal 150 ml")
    lista, _ = importar.fusiona([sin_id], [nuevo], anadir=False)
    assert lista == [sin_id]


def test_el_slug_coincide_con_el_de_catalogo(importar, catalogo):
    """Si los dos scripts sacaran la URL distinta, fusiona no reconocería la
    ficha y la pisaría."""
    nombre = "Muñequera Farmalastic de Neopreno · Talla Única"
    assert importar.slug(nombre) == catalogo.slug_producto({"nombre": nombre})

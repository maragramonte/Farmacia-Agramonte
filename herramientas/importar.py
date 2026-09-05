#!/usr/bin/env python3
"""
Vuelca un export del programa de gestión a herramientas/catalogo-datos.json.

    python herramientas/importar.py export.csv
    python herramientas/importar.py export.csv --mapa mapa.json --seleccion sel.csv
    python herramientas/importar.py export.csv --mapa mapa.json --seleccion sel.csv --escribir

Sin --escribir no toca nada: cuenta qué haría y para.

Existe porque meter cuarenta productos a mano en el JSON es la misma errata
esperando a ocurrir que llevó a generar las páginas en vez de copiarlas. Con un
export en CSV, actualizar el catálogo pasa a ser: reexportar, ejecutar esto, y
ejecutar catalogo.py.

CÓMO SE USA, la primera vez
---------------------------
1. Saca del programa de gestión un CSV con, como mínimo, el nombre del artículo
   y la familia a la que pertenece. Si además trae el formato o la presentación,
   mejor. Guárdalo como CSV, no como Excel.
2. Ejecuta esto con el CSV y nada más. No escribe: dice qué columnas ha
   reconocido, lista las familias que ha encontrado y deja un mapa-catalogo.json
   con esas familias sin asignar.
3. Abre ese fichero y pon, al lado de cada familia, la categoría del catálogo a
   la que va. Las que dejes en null se quedan fuera.
4. Vuelve a ejecutarlo con --mapa y --seleccion seleccion.csv. Deja ese CSV con
   una fila por producto candidato y para: el catálogo lleva una SELECCIÓN, no
   el fichero de artículos entero.
5. Abre seleccion.csv en Excel y escribe «si» en la columna «incluir» de los
   que quieras en la web. Guarda.
6. Vuelve a ejecutarlo igual. Dirá qué haría. Cuando cuadre, añade --escribir.

Cuando llegue otro export más adelante, se repite con el mismo seleccion.csv:
conserva lo que ya estuviera marcado y añade lo nuevo sin marcar, así que sólo
hay que mirar lo que ha aparecido desde la última vez.

LO QUE ESTE SCRIPT NO HACE, a propósito
---------------------------------------
- No toca los precios. La farmacia ha decidido no publicarlos, así que aunque el
  export traiga una columna de PVP se ignora.
- No escribe resúmenes. Un export trae nombres, no frases. Los productos entran
  sin resumen y salen con la marca amarilla de «Resumen pendiente» hasta que
  alguien los escriba.
- No toca "plantilla". Una categoría que era plantilla lo sigue siendo después
  de importar: nada se publica hasta que alguien lo mira y lo quita a mano.
- No importa a Medicamentos. Enseñar medicamentos en un catálogo es publicidad
  de medicamentos, y esa página existe precisamente para no tener lista.
- No borra las páginas de los productos que desaparezcan. Eso lo dice
  catalogo.py al ejecutarse, con el git rm hecho.
"""

import argparse
import csv
import io
import json
import re
import sys
import unicodedata
from collections import OrderedDict, Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = Path(__file__).resolve().parent / "catalogo-datos.json"

# Nunca, por mucho que lo diga el mapa. Ver el docstring.
PROHIBIDAS = {"medicamentos"}

# Cómo se llama cada cosa en los CSV que sacan estos programas. Se compara sin
# tildes y en minúsculas, y basta con que la cabecera contenga una de éstas.
PISTAS = OrderedDict([
    ("nombre",  ["descripcion articulo", "nombre articulo", "descripcion",
                 "articulo", "producto", "nombre"]),
    ("formato", ["formato", "presentacion", "envase", "contenido", "unidades"]),
    ("familia", ["familia", "subfamilia", "categoria", "grupo", "seccion"]),
    ("marca",   ["laboratorio", "marca", "fabricante", "proveedor"]),
])

# Éstas se reconocen para poder decir en voz alta que se ignoran, que es menos
# desconcertante que no mencionarlas.
IGNORADAS = ["pvp", "precio", "importe", "stock", "existencias", "codigo", "cn",
             "ean", "iva", "coste"]


def sin_tildes(t):
    t = unicodedata.normalize("NFKD", t or "")
    return "".join(c for c in t if not unicodedata.combining(c)).lower().strip()


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", sin_tildes(t)).strip("-")


def lee_csv(ruta):
    """Lee el CSV adivinando codificación y separador.

    Los export de estos programas en un Windows español suelen salir en cp1252
    y separados por punto y coma, no por coma. Se prueban por orden y se avisa
    de lo que ha salido, para que se note si ha adivinado mal."""
    crudo = Path(ruta).read_bytes()
    for codificacion in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            texto = crudo.decode(codificacion)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise SystemExit("No consigo leer %s con ninguna codificación conocida." % ruta)

    primera = texto.splitlines()[0] if texto.splitlines() else ""
    separador = max([";", ",", "\t", "|"], key=primera.count)
    if primera.count(separador) == 0:
        raise SystemExit(
            "La primera línea de %s no parece una cabecera con columnas:\n  %s"
            % (ruta, primera[:120]))

    filas = list(csv.DictReader(io.StringIO(texto), delimiter=separador))
    print("  Leído %s: %s, separado por «%s», %d filas, %d columnas."
          % (ruta, codificacion, separador, len(filas),
             len(filas[0]) if filas else 0))
    return filas


def empareja_columnas(cabeceras, forzadas):
    """Decide qué columna del CSV es cada cosa. Lo dice todo en voz alta: es
    donde más fácil se equivoca y donde menos se nota si no se cuenta."""
    columnas = {}
    usadas = set()
    for campo, pistas in PISTAS.items():
        if campo in forzadas:
            if forzadas[campo] not in cabeceras:
                raise SystemExit("No hay ninguna columna «%s» en el CSV. Hay: %s"
                                 % (forzadas[campo], ", ".join(cabeceras)))
            columnas[campo] = forzadas[campo]
            usadas.add(forzadas[campo])
            continue
        for pista in pistas:
            for cab in cabeceras:
                if cab not in usadas and pista in sin_tildes(cab):
                    columnas[campo] = cab
                    usadas.add(cab)
                    break
            if campo in columnas:
                break

    print("\n  Columnas reconocidas:")
    for campo in PISTAS:
        print("    %-8s %s" % (campo, columnas.get(campo, "— no encontrada —")))

    ignoradas = [c for c in cabeceras
                 if c not in usadas and any(i in sin_tildes(c) for i in IGNORADAS)]
    if ignoradas:
        print("    (se ignoran, a propósito: %s)" % ", ".join(ignoradas))
    sobran = [c for c in cabeceras if c not in usadas and c not in ignoradas]
    if sobran:
        print("    (sin usar: %s)" % ", ".join(sobran))

    if "nombre" not in columnas:
        raise SystemExit(
            "\nNo encuentro la columna del nombre del producto. Dímela con:\n"
            "  --columna nombre=NOMBRE_DE_LA_COLUMNA")
    if "familia" not in columnas:
        raise SystemExit(
            "\nNo encuentro la columna de la familia, que es la que dice a qué\n"
            "categoría va cada producto. Dímela con:\n"
            "  --columna familia=NOMBRE_DE_LA_COLUMNA")
    return columnas


def escribe_mapa_ejemplo(familias, categorias, destino):
    """Deja un mapa a medio hacer, con las familias del CSV sin asignar. Se
    rellena a mano: nadie más que la farmacia sabe qué va dónde."""
    mapa = OrderedDict()
    mapa["_leeme"] = [
        "Pon al lado de cada familia del programa de gestion el id de la",
        "categoria del catalogo a la que va. Las que queden en null se",
        "quedan fuera de la web.",
        "",
        "Categorias disponibles: %s" % ", ".join(
            c for c in categorias if c not in PROHIBIDAS),
        "",
        "Medicamentos no admite productos: esa pagina existe para no tener",
        "lista. Si mapeas algo ahi, el script para.",
    ]
    mapa["familias"] = OrderedDict((f, None) for f, _ in familias.most_common())
    Path(destino).write_text(
        json.dumps(mapa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n  Escrito %s con %d familias sin asignar." % (destino, len(familias)))
    print("  Rellénalo y vuelve a ejecutar esto con --mapa %s" % destino)


def construye(filas, columnas, mapa, categorias_validas):
    """Convierte las filas del CSV en productos, agrupados por categoría."""
    por_categoria = OrderedDict()
    sin_mapear = Counter()
    descartados = 0

    for fila in filas:
        nombre = (fila.get(columnas["nombre"]) or "").strip()
        familia = (fila.get(columnas["familia"]) or "").strip()
        if not nombre:
            descartados += 1
            continue

        destino = mapa.get(familia)
        if not destino:
            sin_mapear[familia or "(vacía)"] += 1
            continue
        if destino in PROHIBIDAS:
            raise SystemExit(
                "El mapa manda la familia «%s» a «%s», y ahí no puede ir nada.\n"
                "Enseñar medicamentos en un catálogo es publicidad de\n"
                "medicamentos: esa página existe precisamente para no tener lista."
                % (familia, destino))
        if destino not in categorias_validas:
            raise SystemExit(
                "El mapa manda «%s» a la categoría «%s», que no existe en el JSON.\n"
                "Las que hay: %s" % (familia, destino, ", ".join(categorias_validas)))

        # La marca delante del nombre, si viene aparte y no está ya dentro.
        if columnas.get("marca"):
            marca = (fila.get(columnas["marca"]) or "").strip()
            if marca and sin_tildes(marca) not in sin_tildes(nombre):
                nombre = "%s %s" % (marca, nombre)

        producto = OrderedDict()
        producto["id"] = slug(nombre)
        producto["nombre"] = nombre
        if columnas.get("formato"):
            formato = (fila.get(columnas["formato"]) or "").strip()
            if formato:
                producto["formato"] = formato
        # Sin resumen y sin precio, a propósito. Ver el docstring de arriba.
        por_categoria.setdefault(destino, []).append(producto)

    return por_categoria, sin_mapear, descartados


COLUMNAS_SELECCION = ["categoria", "id", "nombre", "formato", "incluir"]

# Lo que cuenta como un sí en la columna «incluir». Se compara sin tildes y en
# minúsculas, porque esto lo rellena una persona con prisa en un Excel.
AFIRMATIVOS = {"si", "s", "x", "1", "true", "v", "y", "yes", "ok"}

# A partir de aquí, importar sin lista de selección casi seguro es un descuido:
# un export de farmacia son miles de referencias y el catálogo lleva una
# selección. Cuarenta fichas escritas valen más que tres mil sin resumen.
SIN_SELECCION_MAXIMO = 50


def lee_seleccion(ruta):
    """Devuelve qué productos están marcados y cuáles ya figuran en el fichero."""
    texto = Path(ruta).read_text(encoding="utf-8-sig")
    marcados, conocidos = set(), set()
    for fila in csv.DictReader(io.StringIO(texto), delimiter=";"):
        clave = ((fila.get("categoria") or "").strip(),
                 (fila.get("id") or "").strip())
        conocidos.add(clave)
        if sin_tildes(fila.get("incluir") or "") in AFIRMATIVOS:
            marcados.add(clave)
    return marcados, conocidos


def sincroniza_seleccion(ruta, por_categoria):
    """Deja en el CSV de selección una fila por producto candidato.

    Va en CSV y no en JSON a propósito: esto lo rellena quien conoce el
    mostrador, en Excel, escribiendo «si» en una columna. Un JSON con tres mil
    llaves no lo revisa nadie.

    Conserva lo ya marcado y añade lo que haya aparecido desde la última vez,
    sin marcar. Así el segundo export no obliga a repasarlo todo otra vez."""
    marcados, conocidos = (set(), set())
    if Path(ruta).exists():
        marcados, conocidos = lee_seleccion(ruta)

    filas, nuevos = [], 0
    for cid, productos in por_categoria.items():
        for p in productos:
            clave = (cid, p["id"])
            if clave not in conocidos:
                nuevos += 1
            filas.append([cid, p["id"], p["nombre"], p.get("formato", ""),
                          "si" if clave in marcados else ""])

    with io.open(ruta, "w", encoding="utf-8-sig", newline="") as f:
        escritor = csv.writer(f, delimiter=";")
        escritor.writerow(COLUMNAS_SELECCION)
        escritor.writerows(filas)
    return marcados, len(filas), nuevos


def aplica_seleccion(por_categoria, marcados):
    """Se queda con lo marcado. Una categoría sin nada marcado sale del lote
    entera: mejor no tocarla que vaciarla por un descuido."""
    for cid in list(por_categoria):
        elegidos = [p for p in por_categoria[cid] if (cid, p["id"]) in marcados]
        if elegidos:
            por_categoria[cid] = elegidos
        else:
            del por_categoria[cid]


def quita_repetidos(por_categoria):
    """Dos filas que den el mismo id se pisarían la página. Se queda la primera
    y se avisa: en un export es normal que el mismo artículo salga dos veces."""
    encabezado = False
    for categoria, productos in por_categoria.items():
        vistos, limpios, repes = set(), [], []
        for p in productos:
            if p["id"] in vistos:
                repes.append(p["nombre"])
                continue
            vistos.add(p["id"])
            limpios.append(p)
        if repes:
            if not encabezado:
                print("\n  Repetidos en el CSV, fuera:")
                encabezado = True
            print("    %-22s %d (%s%s)"
                  % (categoria, len(repes), ", ".join(repes[:2]),
                     "…" if len(repes) > 2 else ""))
        por_categoria[categoria] = limpios


def main():
    ap = argparse.ArgumentParser(
        description="Vuelca un export CSV a herramientas/catalogo-datos.json.")
    ap.add_argument("csv", help="el fichero exportado del programa de gestión")
    ap.add_argument("--mapa", help="JSON que dice qué familia va a qué categoría")
    ap.add_argument("--columna", action="append", default=[], metavar="campo=COLUMNA",
                    help="fuerza una columna, p. ej. --columna formato=PRESENTACION")
    ap.add_argument("--seleccion", metavar="CSV",
                    help="CSV donde se marca qué productos entran en la web. Si no "
                         "existe, lo escribe con todos los candidatos y para")
    ap.add_argument("--anadir", action="store_true",
                    help="añade a los productos que ya hay en vez de sustituirlos")
    ap.add_argument("--escribir", action="store_true",
                    help="sin esto no toca el JSON: sólo cuenta qué haría")
    args = ap.parse_args()

    forzadas = {}
    for par in args.columna:
        if "=" not in par:
            raise SystemExit("--columna se usa así: --columna formato=PRESENTACION")
        campo, valor = par.split("=", 1)
        if campo not in PISTAS:
            raise SystemExit("Campo desconocido «%s». Los que hay: %s"
                             % (campo, ", ".join(PISTAS)))
        forzadas[campo] = valor

    datos = json.loads(DATOS.read_text(encoding="utf-8"), object_pairs_hook=OrderedDict)
    categorias = OrderedDict((c["id"], c) for c in datos["categorias"])

    filas = lee_csv(args.csv)
    if not filas:
        raise SystemExit("El CSV no tiene ni una fila de datos.")
    columnas = empareja_columnas(list(filas[0].keys()), forzadas)

    familias = Counter((f.get(columnas["familia"]) or "").strip() for f in filas)

    if not args.mapa:
        print("\n  Familias encontradas en el CSV (%d):" % len(familias))
        for nombre, cuantos in familias.most_common():
            print("    %-40s %d" % (nombre or "(vacía)", cuantos))
        # Junto al CSV, no en la raíz del repositorio: es un fichero de trabajo
        # de quien importa, no algo que deba acabar en git.
        escribe_mapa_ejemplo(familias, list(categorias),
                             Path(args.csv).resolve().parent / "mapa-catalogo.json")
        return

    crudo = json.loads(Path(args.mapa).read_text(encoding="utf-8"))
    mapa = {k: v for k, v in (crudo.get("familias") or crudo).items()
            if not k.startswith("_") and v}

    por_categoria, sin_mapear, descartados = construye(
        filas, columnas, mapa, list(categorias))

    quita_repetidos(por_categoria)
    candidatos = sum(len(ps) for ps in por_categoria.values())

    if args.seleccion:
        marcados, total, nuevos = sincroniza_seleccion(args.seleccion, por_categoria)
        print("\n  Selección (%s): %d candidatos, %d marcados%s."
              % (args.seleccion, total, len(marcados),
                 ", %d nuevos sin marcar" % nuevos if nuevos else ""))
        if not marcados:
            print("\n  Ninguno marcado todavía, así que no hay nada que importar.")
            print("  Abre ese CSV en Excel, escribe «si» en la columna «incluir»")
            print("  de los que quieras en la web, guárdalo y repite esto.")
            return
        aplica_seleccion(por_categoria, marcados)
    elif args.escribir and candidatos > SIN_SELECCION_MAXIMO:
        raise SystemExit(
            "\n  Son %d productos y no me has dado lista de selección.\n"
            "  El catálogo lleva una selección, no el fichero de artículos entero:\n"
            "  cuarenta fichas escritas valen más que tres mil sin resumen.\n\n"
            "  Añade --seleccion seleccion.csv y vuelve a ejecutarlo: te dejará el\n"
            "  fichero con los %d candidatos para que marques cuáles entran."
            % (candidatos, candidatos))

    print("\n  Qué haría:")
    for cid, productos in por_categoria.items():
        c = categorias[cid]
        antes = len(c["productos"])
        sin_formato = sum(1 for p in productos if not p.get("formato"))
        accion = "añade a" if args.anadir else "sustituye"
        print("    %-22s %s %d por %d  (%d sin formato)"
              % (cid, accion, antes, len(productos), sin_formato))
        if c.get("plantilla"):
            print("      ojo: sigue siendo plantilla, así que no se publica")

    if descartados:
        print("\n  %d fila%s sin nombre, fuera."
              % (descartados, "s" if descartados != 1 else ""))
    if sin_mapear:
        print("\n  Familias sin mapear, fuera (%d productos):"
              % sum(sin_mapear.values()))
        for nombre, cuantos in sin_mapear.most_common(10):
            print("    %-40s %d" % (nombre, cuantos))

    if not args.escribir:
        print("\n  NO he tocado nada. Cuando cuadre, repítelo con --escribir.")
        return

    for cid, productos in por_categoria.items():
        c = categorias[cid]
        c["productos"] = c["productos"] + productos if args.anadir else productos

    texto = json.dumps(datos, ensure_ascii=False, indent=2)
    texto = re.sub(r'\n  \],\n  "categorias"', '\n  ],\n\n  "categorias"', texto, count=1)
    DATOS.write_text(texto + "\n", encoding="utf-8")
    print("\n  Escrito %s." % DATOS.name)
    print("  Ahora: python herramientas/catalogo.py")


if __name__ == "__main__":
    main()

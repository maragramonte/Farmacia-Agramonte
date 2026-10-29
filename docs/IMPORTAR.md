# Importar desde el programa de gestión

Meter cuarenta productos a mano en el JSON es la misma errata esperando a
ocurrir que llevó a generar las páginas en vez de copiarlas. Para eso está
`herramientas/importar.py`, que lee un CSV exportado de Farmatic, Unycop,
Nixfarma o el que sea, y lo vuelca a `herramientas/catalogo-datos.json`.

```
python herramientas/importar.py export.csv
python herramientas/importar.py export.csv --mapa mapa.json --seleccion sel.csv
python herramientas/importar.py export.csv --mapa mapa.json --seleccion sel.csv --escribir
```

## Dos filtros seguidos, y ninguno lo decide el script

1. **El mapa, por familias.** Sin `--mapa` no escribe nada: dice qué columnas
   ha reconocido, lista las familias que trae el CSV y deja al lado un
   `mapa-catalogo.json` con esas familias sin asignar. Se rellena a mano (qué
   familia va a qué categoría) y las que queden en `null` se quedan fuera.
2. **La selección, producto a producto.** Con `--seleccion` deja un CSV con
   una fila por candidato y una columna `incluir` vacía. Se abre en Excel, se
   escribe `si` en los que entran, y sólo ésos se importan. **El catálogo
   lleva una selección, no el fichero de artículos entero**: un export de
   farmacia son miles de referencias, y cuarenta fichas bien escritas valen
   más que tres mil con «Resumen pendiente». Por eso, importar más de **50
   productos** sin lista de selección lo rechaza en vez de hacerlo.

Cuando llegue otro export más adelante se repite con el mismo CSV de
selección: conserva lo ya marcado y añade lo nuevo sin marcar, así que sólo
hay que mirar lo que ha aparecido desde la última vez.

## Las opciones

| Opción | Para qué |
|---|---|
| `--mapa mapa.json` | Qué familia del CSV va a qué categoría. Sin él no escribe |
| `--seleccion sel.csv` | La lista de productos marcados uno a uno |
| `--columna campo=COLUMNA` | Forzar una columna que no haya adivinado |
| `--anadir` | Añadir a lo que ya hay en vez de reemplazar |
| `--escribir` | El único que toca el JSON. Sin él, cuenta qué haría y para |

**Sin `--escribir` no toca nada en ningún caso.** Adivina la codificación (los
export de un Windows español suelen salir en cp1252) y el separador (suele ser
`;`, no `,`), y dice cuál ha usado para que se note si ha adivinado mal. Si no
acierta con alguna columna, se le fuerza con `--columna formato=PRESENTACION`.

## Cinco cosas que no hace, y todas a propósito

- **No toca los precios.** Aunque el CSV traiga el PVP, se ignora: ya está
  decidido que no se publican.
- **No escribe resúmenes.** Un export trae nombres, no frases. Los productos
  entran sin resumen y salen con la marca amarilla hasta que alguien lo
  escriba.
- **No toca `plantilla`.** Una categoría que era plantilla lo sigue siendo
  después de importar, así que nada se publica hasta que alguien lo mira y lo
  quita a mano.
- **No importa a Medicamentos.** Si el mapa manda algo ahí, para y lo dice.
  El porqué está en [CATALOGO.md](CATALOGO.md#por-qué-medicamentos-está-vacía).
- **No borra las páginas** de los productos que desaparezcan. Eso lo avisa
  `catalogo.py`, con el `git rm` ya escrito.

Quita los productos repetidos (en un export es normal que el mismo artículo
salga dos veces) y, si el CSV trae el laboratorio en una columna aparte, lo
pone delante del nombre salvo que ya estuviera dentro.

# El catálogo

Diez categorías, una página cada una, y dentro una ficha por producto. Hoy son
**35 productos reales**, con marca y formato, repartidos entre nueve
categorías. **Medicamentos no lleva ninguno, y eso es deliberado.**

## Las diez categorías

Son diez y **no se solapan**, que es la única condición que importa: si dos
cajones valen para el mismo producto, nadie sabe dónde buscarlo ni dónde
guardarlo.

| Categoría | Qué recoge | Productos |
|---|---|---|
| Medicamentos | Sin receta y encargos de receta, siempre para recoger en el mostrador | 0 |
| Cosmética facial | Cremas, limpiadores, tratamientos de rostro | 4 |
| Cosmética corporal | Cuerpo, manos, higiene | 4 |
| Solares | Fotoprotección, adulta e infantil | 9 |
| Cabello | Champús, anticaída, cuero cabelludo | 3 |
| Bebé e infantil | Pañal, lactancia, higiene y cuidado del niño | 3 |
| Salud íntima | Higiene íntima, anticoncepción, menopausia | 3 |
| Nutrición y vitaminas | Complementos alimenticios y nutrición específica | 3 |
| Fitoterapia | Plantas medicinales y derivados | 3 |
| Ortopedia | Vendajes, plantillas, ayudas técnicas | 3 |

Tres decisiones que conviene no deshacer sin pensarlo:

- **«Dermocosmética» ya no está** como categoría suelta: era el paraguas de
  facial, corporal, solares y cabello, así que convivir con ellas creaba
  cuatro solapamientos. Se parte en facial y corporal, que es donde iban sus
  productos. Sigue existiendo como **servicio** en la portada, que es otra
  cosa.
- **Bebés e infantil van juntas**, y las **vitaminas dentro de nutrición**:
  eran la misma estantería partida en dos.
- **«Fitoterapia», no «medicina natural».** Lo segundo atribuye propiedades
  medicinales a productos que no son medicamentos, y eso choca con las normas
  de declaraciones de salud de los complementos alimenticios.

## Por qué Medicamentos está vacía

Enseñar medicamentos en un catálogo es publicidad de medicamentos, que la ley
prohíbe al público para los de receta y sólo permite con advertencias
obligatorias para el resto. Su página explica en su lugar cómo se encarga una
receta. El importador, además, **se niega a meter nada en esa categoría**: ver
[IMPORTAR.md](IMPORTAR.md).

## El generador

Las páginas **se generan**. No se editan a mano:

```
python herramientas/catalogo.py
```

Lee `herramientas/catalogo-datos.json` y `herramientas/textos.json`, y escribe:

```
catalogo-<id>.html              la rejilla de tarjetas de la categoría
catalogo-<id>-<producto>.html   la ficha de cada uno de sus productos
historia.html                   quiénes somos
cesta.html                      la cesta, que comparte cabecera con ellas
ca/…                            todo lo anterior otra vez, en catalán
ca/index.html                   la portada catalana, hecha desde index.html
en/…                            y lo mismo en inglés
sitemap.xml                     las páginas indexables de los tres idiomas
```

Son **143 páginas**: 10 de categoría, 35 fichas, la historia y la cesta en
cada uno de los tres idiomas, más las dos portadas traducidas.

Existe por una razón concreta: la tira de categorías que va arriba las lista
todas, así que añadir una obligaba a tocar las diez a mano, y eso es una
errata esperando a ocurrir. Con una ficha por producto, escribirlas a mano ya
no es ni discutible.

Para cambiar productos o fotos se edita **el JSON**, y se vuelve a ejecutar el
script.

### El generador para en vez de escribir algo mal

Es lo que más justifica que el sitio se genere y no se copie:

- **Un texto español de la portada que ya no case con su par traducido**: para
  y dice qué par de `textos.json` se ha quedado viejo.
- **Dos productos de la misma categoría que den la misma URL**: para y pide
  una clave `id` distinta, en vez de pisar el fichero en silencio.
- **Un icono de categoría que no existe**: para.
- **Una clave `foto` que apunte a algo que no está**: avisa, en lugar de dejar
  una imagen rota que sólo se ve abriendo esa ficha.
- **Páginas de productos que ya no se generan y siguen en el disco**: las
  lista con el `git rm` ya escrito. No las borra solo: un borrado en cadena
  por una errata del JSON sería peor.
- **Los cajones de la portada**, que están escritos a mano en `index.html`:
  comprueba que la lista coincide con el JSON y avisa si sobra o falta alguna.
- **Lo que ha salido en español por no estar traducido**: lo cuenta agrupado
  por idioma al terminar.

## Los precios

**No se publican.** La decisión es de la farmacia y la razón es doble: un
precio expuesto al público es una oferta, y mantener decenas al día en una web
estática es de esas cosas que se quedan viejas sin que nadie se entere. El
catálogo enseña lo que hay y el precio se pregunta; para eso está el botón.

Un producto sin precio no deja hueco ni marca amarilla: sencillamente no lleva
esa línea, y la tarjeta se queda con el nombre, el formato y «Preguntar». Eso
es deliberado. El amarillo de `.pendiente` quiere decir «esto falta», y aquí
no falta nada.

La clave `precio` sigue existiendo en el JSON: al ponérsela a un producto
(`"precio": "12,95 €"`) el precio sale, y sólo en ése. Antes de usarla,
acuérdate de lo de la oferta.

## La ficha de producto

La tarjeta de la rejilla lleva al título enlazado; el botón «Preguntar» sigue
yendo directo a WhatsApp, que quien ya sabe lo que quiere no tiene por qué dar
un rodeo. La ficha repite foto, formato, precio y botón, y debajo cuatro
epígrafes que salen del JSON:

| Clave | Epígrafe | Se pinta como |
|---|---|---|
| `descripcion` | Para qué es | párrafos |
| `modo_empleo` | Modo de empleo | lista numerada |
| `composicion` | Composición | párrafos |
| `advertencias` | Advertencias | lista, y en un recuadro aparte |

**Los cuatro son opcionales y el que falta no se pinta.** Es a propósito: en
una farmacia esto es consejo de salud y lo firma la casa, así que una ficha
corta es mejor que un epígrafe rellenado a ojo. **Ahora mismo no los trae
ninguno de los 35.** Hay un ejemplo montado en
`git show b215896:herramientas/catalogo-datos.json`, por si sirve de plantilla
al escribir los de verdad.

El **formato** sí lleva marca amarilla cuando falta: todo producto tiene uno,
y no tenerlo es una ficha a medias. Hoy les falta a cuatro. Es lo contrario
que el precio, que no lleva marca porque no es que falte, es que no se
publica.

## Las fotos

Van en `fotos/`, que **hoy está vacía**: por eso las 35 fichas siguen
enseñando el recuadro de «Foto pendiente». Se ponen dejando el fichero con el
nombre de la página del producto, sin el `catalogo-` de delante ni el `.html`
de detrás:

```
catalogo-solares-cleanance-solaire-spf50.html   la página
fotos/solares-cleanance-solaire-spf50.jpg       su foto
```

Y ya está: se ejecuta el script y aparece en la tarjeta y en la ficha, sin
tocar el JSON. Escribir 35 claves `foto` a mano es la misma errata esperando a
ocurrir que llevó a generar las páginas en vez de copiarlas. La clave `foto`
del JSON sigue existiendo para el fichero que no siga el convenio, y manda por
encima de él; si apunta a algo que no está, el script avisa en lugar de dejar
una imagen rota. Al terminar dice cuántas fotos hay puestas de los 35
productos.

Valen `.webp`, `.avif`, `.jpg`, `.jpeg` y `.png`, en ese orden de preferencia.
**Cuadradas y con el producto centrado**: la misma foto se recorta a 4:3 en la
tarjeta y a 1:1 en la ficha, así que lo que vaya pegado a un borde se pierde
en uno de los dos recortes. El resto (tamaño, fondo, y de quién tienen que ser
las fotos antes de publicarlas) está en `fotos/LEEME.txt`.

## La URL de un producto

Sale de su nombre (`Crema hidratante corporal` →
`catalogo-cosmetica-corporal-crema-hidratante-corporal.html`). Se puede fijar
con una clave `id` en el JSON, y **hay que hacerlo antes de renombrar un
producto que ya esté en Google**. Los 35 productos de hoy llevan su `id`
puesto, así que renombrar uno no mueve su URL.

## `plantilla`, que hoy no usa ninguna

Mientras una categoría lleve `"plantilla": true`, **ni ella ni sus fichas
entran en `sitemap.xml`**, sus fichas salen con `noindex` y la página lleva
una franja amarilla avisando de que los productos son de muestra. Fue el
mecanismo que sostuvo el catálogo mientras se llenaba.

**Ninguna de las diez la lleva ya**: los productos inventados se fueron y
entraron los reales. El mecanismo se queda puesto por si vuelve a hacer falta
al abrir una categoría nueva.

Por eso el `sitemap.xml` tiene hoy **150 URL**: las 154 páginas menos el 404 y
las tres cestas, que llevan `noindex` a propósito.

## Lo que falta

Por orden:

1. **Las fotos**, en `fotos/`. La carpeta y el mecanismo ya están; faltan las
   35 imágenes.
2. **Los cuatro formatos** que faltan, que salen con la marca amarilla.
3. **Los epígrafes de cada ficha**, escritos por quien pueda firmarlos. Hoy no
   los tiene ninguno.
4. **Los resúmenes y las intros** que todavía salgan en español por no estar
   traducidos: el generador los cuenta al terminar.

El estilo va en dos hojas: `marca.css` con la identidad compartida (paleta,
cabecera, botón y pie) y `catalogo.css` con lo que sólo existe aquí. Hay que
cargar `marca.css` primero.

# Farmàcia Agramonte — web

### 👉 **<https://maragramonte.github.io/Farmacia-Agramonte/>**

**La web está publicada y en marcha.** Ese enlace es el bueno: es lo que ve
cualquiera que la abra. Cada `git push` a `main` la republica sola, en un par
de minutos y sin tocar nada más.

Landing de la Farmàcia Agramonte, en la Plaça de la Llana (El Born, Barcelona),
maquetada a partir del boceto y del diseño visual, que se guardan **fuera del
repositorio**: son lo único que no ve quien visita la web, así que no viajan
con ella.

Es una web **estática**: HTML y CSS, sin dependencias, sin proceso de
compilación y sin servidor de aplicación. No hace falta contratar a nadie ni
instalar nada para verla, y tampoco para publicarla.

Lo único que se ejecuta en el navegador de quien la visita es `cesta.js`, y se
explica abajo en «La cesta». Son trescientas líneas sin dependencias: **no hay
`npm`, ni `node_modules`, ni nada que compilar**. Para trabajar en la web sigue
bastando un editor de texto y Python.

## Verla en tu ordenador

La forma más rápida es **doble clic en `servir.bat`**. Se abre una ventana
negra, arranca el servidor y se abre el navegador solo. Para pararlo, cierra la
ventana o pulsa `Ctrl+C`.

Desde la terminal, lo mismo:

```
python servir.py            # puerto 8000, abre el navegador
python servir.py 3000       # otro puerto, por si el 8000 está ocupado
python servir.py --no-abrir # sin abrir el navegador
```

Al arrancar imprime dos direcciones: la de este equipo (`localhost`) y la de la
red local, con la IP. **Esa segunda sirve para verla en el móvil** con solo
escribirla, estando en la misma wifi — útil para comprobar cómo queda de verdad
en una pantalla pequeña.

También se puede abrir `index.html` con doble clic, sin servidor. Funciona, pero
la ruta será `file://` y algunas cosas no se comportan igual que en producción,
así que para comprobar cambios es mejor el servidor.

## Publicarla en internet

**Ya está hecho.** La web está publicada en GitHub Pages, en
<https://maragramonte.github.io/Farmacia-Agramonte/>, y no cuesta nada: ni
hosting, ni agencia, ni panel de control. Esto queda escrito por si algún día
hay que rehacerlo o entenderlo, no porque haya algo pendiente.

Para publicar un cambio, el único paso es subirlo:

```
git add -A
git commit -m "..."
git push
```

**Cada `git push` a `main` republica la web sola**, en un par de minutos. No hay
más pasos, no hay botón que pulsar y no hay nada que avisar. Si acabas de
empujar y no ves el cambio, recarga sin caché (`Ctrl+Shift+R`): suele ser el
navegador, no el despliegue.

Cómo quedó montado, que es lo que habría que repetir en un repositorio nuevo:

1. El repositorio es **público**. Pages gratis sólo publica los públicos; en los
   privados es una función de pago. Eso significa que **el código se ve**, y es
   asumido: ver «Derechos», más abajo.
2. En GitHub, repositorio → **Settings** → **Pages**.
3. En *Source*, **Deploy from a branch**; rama `main` y carpeta `/ (root)`.
4. Un par de minutos y la dirección responde.

Dos apuntes:

- La URL sale del nombre del repositorio, que ahora es `Farmacia-Agramonte`.
  Si se vuelve a renombrar (Settings → General → Repository name), hay que
  **actualizar la dirección en seis sitios**: en `index.html` el `canonical`,
  el `og:url`, el `og:image` y el `url` y el `image` del JSON-LD; y además
  `robots.txt` y `sitemap.xml`. GitHub redirige el nombre viejo, pero una web
  que se anuncia a sí misma con una dirección que ya no es la suya confunde a
  los buscadores.
- Cuando haya un dominio propio (`farmaciaagramonte.com` o similar), se apunta
  a GitHub Pages desde el registrador y se añade un fichero `CNAME` en la raíz
  con el dominio dentro. El único gasto sería el dominio, unos 12 €/año.

## Estructura

```
index.html          La landing completa (HTML + CSS + iconos SVG en línea)
404.html            Lo que se ve al abrir una dirección que no existe
tipografias.css     Declara las tipografías propias (@font-face)
aviso-legal.html    Titular, datos profesionales y condiciones de uso
privacidad.html     Qué datos se tratan, para qué y con qué base legal
cookies.html        No hay cookies; explica la cesta y que no hay terceros
legal.css           Estilo compartido de esas páginas de texto y del 404

catalogo-*.html     Las diez categorías y las fichas de sus productos.
                    SE GENERAN, no se editan a mano
historia.html       Quiénes somos y la historia de la farmacia. SE GENERA:
                    el texto está en herramientas/catalogo.py
cesta.html          La lista de lo que alguien quiere encargar. SE GENERA
catalogo.css        Lo propio del catálogo: aviso, tira, rejilla y ficha
cesta.css           Lo propio de la cesta: contador, botón y lista
cesta.js            La cesta. Lo único de la web que se ejecuta al visitarla
marca.css           Paleta, cabecera, botón y pie: la identidad compartida

servir.py           Servidor local (sólo necesita Python)
servir.bat          Doble clic para lo mismo, en Windows

fotos/              Las fotos de los productos. Hoy vacía: ver su LEEME.txt

favicon.svg         Icono de la pestaña: el monograma en oro sobre tinta
og.png              Imagen que se ve al compartir el enlace (1200×630)
robots.txt          Permite indexar y apunta al sitemap
sitemap.xml         Las veinte páginas indexables, para los buscadores
.nojekyll           Le dice a GitHub Pages que sirva los ficheros tal cual

LICENSE             Qué se puede hacer con este código y qué no

tipografias/
  playfair-display-variable.woff2  Los títulos. Fuente variable: un solo
                                   fichero cubre del peso 400 al 500
  playfair-display-cursiva.woff2   La itálica de «de tu barrio»
  karla-variable.woff2             El texto, del 400 al 600
  LICENCIA-karla.txt               SIL Open Font License 1.1
  LICENCIA-playfairdisplay.txt     La OFL exige distribuirla con la fuente

herramientas/
  catalogo.py           Escribe las catalogo-*.html y cesta.html
  catalogo-datos.json   Los productos. Se edita ESTE
  importar.py           Vuelca un export en CSV al JSON de arriba
  tarjeta-social.py     Regenera og.png si cambia el lema o los datos
```

El boceto y el diseño visual (`diseno/`) están ignorados por git y viven sólo
en el ordenador. Conviene tener una copia de seguridad aparte, porque el
repositorio ya no hace esa función.

## Secciones de la landing

Cabecera fija con acceso directo a WhatsApp · hero con la propuesta («envíanos
la receta, la preparamos y te avisamos») · diez categorías de producto que no se
solapan entre sí, **cada una lleva a su página de catálogo** · tres
motivos para elegir la farmacia ·
datos de contacto y horario · pie con enlaces legales e información de contacto.

En el móvil el menú no se esconde: la cabecera pasa a dos filas y los enlaces
quedan en una tira que se desliza si no caben. Las anclas se paran por debajo de
la cabecera, que va fija, para que el título de la sección no quede tapado.

**El menú está escrito en dos sitios**, y hay que tocar los dos o se descuadra:
a mano en `index.html`, y generado en `documento()` de
`herramientas/catalogo.py` para las sesenta páginas restantes. Hoy son cuatro
entradas: Inicio, Categorías, **Historia** y Contacto, más la cesta y el botón
de pedir.

## Quiénes somos

`historia.html` cuenta de dónde viene la farmacia: que es la antigua Farmàcia
Joaquim Cases, tienda modernista protegida como Bien Cultural de Interés Local,
con referencias documentadas desde 1600, los Saurina hasta 1747, los Cases de
1864 a 2014 y Zoila Agramonte Bucho como titular desde 2019. Lleva además el
enlace al reportaje de *La República* sobre el barrio de Santa Caterina durante
la pandemia, que es **el único enlace a un sitio ajeno de toda la web** aparte
de los de WhatsApp.

**El texto se edita en `pagina_historia()`, dentro de
`herramientas/catalogo.py`**, no en el HTML, que se pierde al regenerar. Está en
el generador y no en `catalogo-datos.json` porque ese JSON es de productos y
esto es prosa, igual que el `CIERRE_PEDIDO` que va al pie de las categorías. Y
se genera en vez de escribirse a mano porque es una página del menú principal:
escrita aparte habría una tercera copia de la cabecera, y el día que cambie el
menú se quedaría atrás sin que nadie se entere.

Un desajuste que conviene resolver algún día: la portada dice **«Desde 1890»**
en seis sitios —el `og:description`, el `foundingDate` del JSON-LD que lee
Google, el sello dibujado y el pie— y 1890 no aparece en esta historia. Se dejó
así a propósito, pendiente de decidir qué fecha es la buena.

## Datos de la farmacia

| | |
|---|---|
| Dirección | Plaça de la Llana, 11 — 08003 Barcelona (El Born) |
| Teléfono | 933 19 59 21 |
| WhatsApp | 661 192 472 |
| Correo | farmacia.lallana@gmail.com |
| Horario | Lunes a Sábado, 9:00–14:30 y 16:00–20:30 |
| Desde | 1890 |

Estos datos están además en `index.html` como **JSON-LD de tipo `Pharmacy`**,
que es lo que lee Google para montar la ficha de la farmacia en los resultados
de búsqueda y en Maps: dirección, teléfono y los dos tramos de horario. Si
cambia un horario o un teléfono, hay que tocarlo **en los dos sitios**: en el
texto visible y en ese bloque `<script type="application/ld+json">`.

## Derechos

El código, los textos y el diseño son de la farmacia: `LICENSE` dice qué se
puede hacer con ellos y qué no. No es una licencia libre.

Que el repositorio sea público no regala nada: una web estática se descarga
entera en el navegador de quien la abre, con su HTML y su CSS, así que eso es
copiable de todos modos y lo es en cualquier web del mundo. Lo que protege el
trabajo no es esconderlo, es el derecho de autor —automático, sin registrar
nada— y el hecho de que lo copiable es la maqueta, no el negocio: el nombre, la
licencia de oficina de farmacia, la Plaça de la Llana y la ficha de Google no
se clonan.

## Las categorías

Son diez y **no se solapan**, que es la única condición que importa si algún día
cuelga de ellas un catálogo: si dos cajones valen para el mismo producto, nadie
sabe dónde buscarlo ni dónde guardarlo.

| Categoría | Qué recoge |
|---|---|
| Medicamentos | Sin receta y encargos de receta, siempre para recoger en el mostrador |
| Cosmética facial | Cremas, limpiadores, tratamientos de rostro |
| Cosmética corporal | Cuerpo, manos, higiene |
| Solares | Fotoprotección, adulta e infantil |
| Cabello | Champús, anticaída, cuero cabelludo |
| Bebé e infantil | Pañal, lactancia, higiene y cuidado del niño |
| Salud íntima | Higiene íntima, anticoncepción, menopausia |
| Nutrición y vitaminas | Complementos alimenticios y nutrición específica |
| Fitoterapia | Plantas medicinales y derivados |
| Ortopedia | Vendajes, plantillas, ayudas técnicas |

Tres decisiones que conviene no deshacer sin pensarlo:

- **«Dermocosmética» ya no está** como categoría suelta: era el paraguas de
  facial, corporal, solares y cabello, así que convivir con ellas creaba cuatro
  solapamientos. Se parte en facial y corporal, que es donde iban sus productos.
- **Bebés e infantil van juntas**, y las **vitaminas dentro de nutrición**: eran
  la misma estantería partida en dos.
- **«Fitoterapia», no «medicina natural».** Lo segundo atribuye propiedades
  medicinales a productos que no son medicamentos, y eso choca con las normas de
  declaraciones de salud de los complementos alimenticios.

## El catálogo

Están las **diez categorías**, una página cada una, y dentro una ficha por
producto. **Dos ya tienen productos reales** —Solares y Cosmética facial, cinco
entre las dos— y están publicadas sin aviso y sin `noindex`. Las otras siete
siguen con seis productos de muestra y su franja amarilla. **Medicamentos no
lleva ninguno**, y eso es deliberado: enseñar
medicamentos en un catálogo es publicidad de medicamentos, que la ley prohíbe al
público para los de receta y sólo permite con advertencias obligatorias para el
resto. Su página explica en su lugar cómo se encarga una receta.

**Las páginas se generan.** No se editan a mano:

```
python herramientas/catalogo.py
```

Lee `herramientas/catalogo-datos.json` y escribe dos cosas:

```
catalogo-<id>.html              la rejilla de tarjetas de la categoría
catalogo-<id>-<producto>.html   la ficha de cada uno de sus productos
cesta.html                      la cesta, que comparte cabecera con ellas
```

Hoy son 10 páginas de categoría, 47 fichas y la cesta. Es lo mismo que hace
`tarjeta-social.py` con `og.png`: las páginas se escriben cuando cambian los
productos, no cuando alguien las visita. Existe por una razón
concreta: la tira de categorías que va arriba las lista todas, así que añadir
una obligaba a tocar las diez a mano, y eso es una errata esperando a ocurrir.
Con una ficha por producto, escribirlas a mano ya no es ni discutible.

Para cambiar productos o fotos se edita **el JSON**, y se vuelve a ejecutar el
script.

### Los precios

**No se publican.** La decisión es de la farmacia y la razón es doble: un precio
expuesto al público es una oferta, y mantener decenas al día en una web estática
es de esas cosas que se quedan viejas sin que nadie se entere. El catálogo
enseña lo que hay y el precio se pregunta; para eso está el botón.

Un producto sin precio no deja hueco ni marca amarilla: sencillamente no lleva
esa línea, y la tarjeta se queda con el nombre, el formato y «Preguntar». Eso es
deliberado. El amarillo de `.pendiente` quiere decir «esto falta», y aquí no
falta nada.

La clave `precio` sigue existiendo en el JSON: al ponérsela a un producto
(`"precio": "12,95 €"`) el precio sale, y sólo en ése. Antes de usarla, acuérdate
de lo de la oferta.

### La ficha de producto

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

**Los cuatro son opcionales y el que falta no se pinta.** Es a propósito: en una
farmacia esto es consejo de salud y lo firma la casa, así que una ficha corta es
mejor que un epígrafe rellenado a ojo. **Ahora mismo no los trae ninguno**: los
que tenía Solares eran de muestra y se fueron con sus productos inventados. Hay
un ejemplo montado en `git show b215896:herramientas/catalogo-datos.json`, por
si sirve de plantilla al escribir los de verdad.

El **formato** sí lleva marca amarilla cuando falta: todo producto tiene uno, y
no tenerlo es una ficha a medias. Es lo contrario que el precio, que no lleva
marca porque no es que falte, es que no se publica.

### La cesta

Cada tarjeta y cada ficha llevan un botón **«Añadir»** que apunta el producto en
una cesta. La cesta se ve en `cesta.html`, con el contador en la cabecera de
todas las páginas, y desde ahí se cambian las cantidades, se quitan cosas y se
manda el encargo: **el mensaje de WhatsApp se escribe solo** con la lista
entera, y lo envía la persona desde su móvil.

**Aquí no se paga, y eso es lo que importa entender.** No hay pasarela, no se
piden datos, no se cobra nada y la farmacia no recibe nada hasta que alguien le
manda el mensaje. El encargo se confirma, se valora y se paga **en el
mostrador**. Por eso la web sigue fuera del régimen de venta a distancia y el
aviso legal de hoy sigue siendo cierto. Los precios, que no se publican,
tampoco salen en la cesta: se confirman al contestar.

Todo vive en dos ficheros, `cesta.js` y `cesta.css`, y el HTML lo pone el mismo
generador que el resto. Cuatro decisiones que conviene no deshacer:

- **La cesta se guarda en el `localStorage` de quien mira la web**, no en un
  servidor. No hay nada que administrar, nada que respaldar y ningún dato de
  nadie en ninguna parte. A cambio, la cesta es de ese navegador: no sigue a la
  persona de un dispositivo a otro, y se pierde al borrar los datos del sitio.
  Para una lista de la compra que se manda en el momento, es el trato bueno.
- **El botón de añadir nace con `hidden` y lo destapa el JavaScript.** Si
  `cesta.js` no carga, no aparece: lo que se ve es el botón de WhatsApp, que es
  un enlace de verdad y funciona siempre. `cesta.html` tiene su propio aviso para
  ese caso, y nace visible a propósito.
- **No hay nada que no se pueda hacer con el teclado.** Las cantidades son
  botones, el foco no se pierde al quitar una línea y lo que cambia se anuncia
  en una región `aria-live`, que es lo que lee un lector de pantalla.
- **Un `wa.me` con un texto larguísimo falla sin avisar.** Así que la cesta
  recorta la lista al llegar al tope, lo dice dentro del propio mensaje y
  **avisa en la página** de cuántos productos se han quedado fuera, con «Copiar
  la lista» y el correo al lado, que esos sí van enteros. Son unos quince
  productos con nombre de laboratorio; de ahí para arriba se avisa.

Los medicamentos no entran en la cesta porque no hay catálogo de medicamentos:
su página explica cómo se encarga una receta, y eso no cambia.

**El día que se quiera cobrar de verdad** —Stripe Checkout, o el TPV virtual del
banco— el carrito ya está hecho y lo que hay que cambiar es el botón final de
`cesta.html`. Lo que hace falta antes no es código: publicar precios, dejar
Medicamentos fuera, escribir condiciones de venta y derecho de desistimiento, y
rehacer el aviso legal y la privacidad. Y la clave secreta de la pasarela no
puede vivir en GitHub Pages, así que haría falta además una función en servidor
(Cloudflare Workers o Netlify, gratis en este volumen). Es una decisión del
negocio, no una tarde de trabajo.

### Importar desde el programa de gestión

Meter cuarenta productos a mano en el JSON es la misma errata esperando a
ocurrir que llevó a generar las páginas en vez de copiarlas. Para eso está
`herramientas/importar.py`, que lee un CSV exportado de Farmatic, Unycop,
Nixfarma o el que sea:

```
python herramientas/importar.py export.csv
python herramientas/importar.py export.csv --mapa mapa.json --seleccion sel.csv
python herramientas/importar.py export.csv --mapa mapa.json --seleccion sel.csv --escribir
```

Son **dos filtros seguidos**, y ninguno lo decide el script:

1. **El mapa**, por familias. Sin `--mapa` no escribe nada: dice qué columnas ha
   reconocido, lista las familias que trae el CSV y deja al lado un
   `mapa-catalogo.json` con esas familias sin asignar. Se rellena a mano —qué
   familia va a qué categoría— y las que queden en `null` se quedan fuera.
2. **La selección**, producto a producto. Con `--seleccion` deja un CSV con una
   fila por candidato y una columna `incluir` vacía. Se abre en Excel, se
   escribe `si` en los que entran, y sólo ésos se importan. **El catálogo lleva
   una selección, no el fichero de artículos entero**: un export de farmacia son
   miles de referencias, y cuarenta fichas bien escritas valen más que tres mil
   con «Resumen pendiente». Por eso, importar más de 50 productos sin lista de
   selección lo rechaza en vez de hacerlo.

Cuando llegue otro export más adelante se repite con el mismo CSV de selección:
conserva lo ya marcado y añade lo nuevo sin marcar, así que sólo hay que mirar
lo que ha aparecido desde la última vez.

Sin `--escribir` no toca nada en ningún caso: cuenta qué haría y para. Adivina
la codificación (los export de un Windows español suelen salir en cp1252) y el
separador (suele ser `;`, no `,`), y dice cuál ha usado para que se note si ha
adivinado mal. Si no acierta con alguna columna, se le fuerza con
`--columna formato=PRESENTACION`.

**Cinco cosas que no hace, y todas a propósito:**

- **No toca los precios.** Aunque el CSV traiga el PVP, se ignora: ya está
  decidido que no se publican.
- **No escribe resúmenes.** Un export trae nombres, no frases. Los productos
  entran sin resumen y salen con la marca amarilla hasta que alguien lo
  escriba.
- **No toca `plantilla`.** Una categoría que era plantilla lo sigue siendo
  después de importar, así que nada se publica hasta que alguien lo mira y lo
  quita a mano.
- **No importa a Medicamentos.** Si el mapa manda algo ahí, para y lo dice.
- **No borra las páginas** de los productos que desaparezcan. Eso lo avisa
  `catalogo.py`, con el `git rm` ya escrito.

Quita los productos repetidos —en un export es normal que el mismo artículo
salga dos veces— y, si el CSV trae el laboratorio en una columna aparte, lo
pone delante del nombre salvo que ya estuviera dentro.

### Las fotos

Van en `fotos/`, que **hoy está vacía**: por eso las 47 fichas siguen enseñando
el recuadro de «Foto pendiente». Se ponen dejando el fichero con el nombre de la
página del producto, sin el `catalogo-` de delante ni el `.html` de detrás:

```
catalogo-solares-stick-labial-spf-50.html   la página
fotos/solares-stick-labial-spf-50.jpg       su foto
```

Y ya está: se ejecuta el script y aparece en la tarjeta y en la ficha, sin tocar
el JSON. Escribir 47 claves `foto` a mano es la misma errata esperando a ocurrir
que llevó a generar las páginas en vez de copiarlas. La clave `foto` del JSON
sigue existiendo para el fichero que no siga el convenio, y manda por encima de
él; si apunta a algo que no está, el script avisa en lugar de dejar una imagen
rota. Al terminar dice cuántas fotos hay puestas de los 47 productos.

Valen `.webp`, `.avif`, `.jpg`, `.jpeg` y `.png`, en ese orden de preferencia.
**Cuadradas y con el producto centrado**: la misma foto se recorta a 4:3 en la
tarjeta y a 1:1 en la ficha, así que lo que vaya pegado a un borde se pierde en
uno de los dos recortes. El resto —tamaño, fondo, y de quién tienen que ser las
fotos antes de publicarlas— está en `fotos/LEEME.txt`.

La URL del producto sale de su nombre (`Stick labial SPF 50` →
`catalogo-solares-stick-labial-spf-50.html`). Se puede fijar con una clave `id`
en el JSON, y **hay que hacerlo antes de renombrar un producto que ya esté en
Google**. Si dos productos de la misma categoría dan la misma URL, el script
para y lo dice en vez de pisar el fichero en silencio.

Mientras la categoría lleve `"plantilla": true`, sus fichas salen con
`noindex` y fuera del `sitemap.xml`. Que las diez páginas de categoría **sí** se
indexen fue una decisión tomada a sabiendas; cincuenta y cuatro fichas
inventadas son otra cosa: páginas flacas, con nombres de productos que no
existen y con texto de salud que no ha escrito nadie. Al quitar `plantilla`
se indexan solas, y entonces hay que **meterlas a mano en `sitemap.xml`**: el
script avisa de las que falten.

El estilo va en dos hojas: `marca.css` con la identidad compartida —paleta,
cabecera, botón y pie— y `catalogo.css` con lo que sólo existe aquí. Hay que
cargar `marca.css` primero.

Tres cosas que hay que entender antes de tocarla:

- **Siete categorías siguen inventadas.** Seis productos genéricos cada una,
  sin marca, con el aviso grande arriba en la página y en cada ficha, y con
  `noindex` en las fichas. **Las diez páginas de categoría están enlazadas
  desde la portada, en `sitemap.xml` y sin `noindex`**, así que cualquiera
  llega a ellas y Google puede indexarlas. No las des por buenas hasta poner
  productos reales.
- **Hay cesta, pero no hay pago.** Se puede apuntar lo que se quiera y el
  encargo sale por WhatsApp; desde la web no se cobra nada y no se piden datos.
  Eso es deliberado: mientras no se pueda **pagar** aquí, la web sigue fuera del
  régimen de venta a distancia y el aviso legal actual sigue siendo cierto. Está
  explicado abajo, en «La cesta».
- **La tira de arriba enlaza las diez**, con la categoría en la que estás la
  primera y en tinta rellena. Antes las demás iban en texto porque no tenían
  página; ya la tienen.

Para añadir un producto o una categoría se edita el JSON y se ejecuta el
script. La tira se rehace sola en las diez páginas, y la ficha del producto
nuevo aparece con él.

Las pastillas de la portada llevan a estas páginas. Esa lista está escrita a
mano en `index.html`, así que el generador comprueba al ejecutarse que coincide
con el JSON y avisa si sobra o falta alguna.

**Lo que falta para que esto deje de ser una maqueta**, por orden:

1. Productos reales, en el JSON. Sin precios: eso ya está decidido.
2. Las fotos, en `fotos/`. La carpeta y el mecanismo ya están; falta meterlas.
3. Los formatos que faltan: cuatro de los cinco productos reales están sin él
   y salen con la marca amarilla.
4. Los epígrafes de cada ficha, escritos por quien pueda firmarlos. Hoy no los
   tiene ninguno.
5. Quitar `"plantilla": true` de las siete que quedan: con ello se va el aviso
   amarillo y sus fichas dejan de llevar `noindex`.
6. Meter esas fichas en `sitemap.xml`, y borrar las páginas de los productos
   que hayan salido. El script dice cuáles faltan y cuáles sobran.

Y **esto no es hipotético: la web está publicada**. Las páginas de categoría
están enlazadas desde la portada, en `sitemap.xml` y sin `noindex`, así que un
visitante cualquiera llega hoy mismo a las siete de muestra y Google puede
indexarlas. El aviso amarillo es lo único que dice que no son de verdad.

Por lo mismo hay otra cosa que corre prisa y no es de catálogo: **los datos del
titular**, que son los que la LSSI obliga a publicar. El nombre ya está
—Zoila Agramonte Bucho, en `aviso-legal.html` y en `privacidad.html`—, pero
siguen en amarillo, sin rellenar, y con la web ya publicada:

- el **NIF/CIF**, en las dos páginas;
- el **número de colegiada** y el de **autorización sanitaria**;
- la referencia de **homologación en España** del título. El título es
  *Licenciada en Farmacia por la Universidad de La Habana*, y la ley pide el
  título y el Estado que lo expidió: aquí ese Estado no es España, así que
  conviene decir además con qué resolución está homologado o reconocido para
  ejercer aquí.

## Decisiones de diseño

La paleta y las tipografías salen del diseño visual: tinta `#2a1d12`, crema
`#f5f0e6` y oro `#c9a055`, con **Playfair Display** para los títulos —incluida
su itálica en «de tu barrio»— y **Karla** para el texto.

Es un **tema único**, no claro/oscuro: al ser una identidad de marca debe verse
igual para todo el mundo, así que la página fija sus colores explícitamente en
lugar de seguir la preferencia del sistema.

**No hace falta ninguna clave de API.** Las opiniones de Google, que sí la
necesitarían, quedaron fuera igual que en el diseño acabado.

Y **la web no hace ninguna petición externa**: las tipografías se sirven desde
`tipografias/`, no desde Google Fonts. Son de licencia libre (OFL), así que
redistribuirlas es legal siempre que viaje con ellas su licencia, y por eso
están los dos `LICENCIA-*.txt`. Sólo se incluye el subconjunto latino, que cubre
todo el texto del sitio; y como Playfair Display y Karla son fuentes variables,
un único fichero por familia cubre todos los pesos: 82 KB en total en lugar de
los 144 KB que ocuparían sueltos. Al dejar de pedirle nada a Google, las
políticas de privacidad y de cookies se simplificaron: ya no hay ninguna
transferencia de datos por el mero hecho de visitar la página.

Los datos que todavía no tenemos —el nombre del farmacéutico titular, su número
de colegiado, el NIF— aparecen marcados en amarillo con la clase `.pendiente`.
Se ven a la legua a propósito: así nadie publica la página dándolos por buenos.
Al rellenarlos, hay que quitar también el `<span>` que los envuelve.

## Qué falta

Ordenado por lo que más urge antes de enseñar la web a nadie.

- **Nº de colegiado y farmacéutico titular.** Marcados como `PENDIENTE` en el
  pie de `index.html` y en `aviso-legal.html`. En España es obligatorio
  identificarlos, así que esto va primero.
- **NIF y razón social del titular**, en `aviso-legal.html` y `privacidad.html`.
- **Fotos.** El hero lleva una ilustración provisional del mostrador, dibujada
  en SVG y con un aviso encima. Hay que sustituirla por la foto real.
- **Blog.** Los tres artículos («Cómo cuidar tu piel en primavera» y los otros
  dos) eran texto de relleno y sus «Leer más» no llevaban a ninguna parte, así
  que la sección salió de la página: un consejo de salud firmado por el
  farmacéutico que nadie ha escrito no debe publicarse. El CSS sigue en su
  sitio y la maquetación está en el historial (`git show 4bd4d10:index.html`),
  lista para volver en cuanto haya un artículo de verdad.
- **Perfiles de redes sociales.** Los iconos de Instagram y Facebook están
  comentados en el pie, con la URL de ejemplo lista para sustituir. Un icono que
  no lleva a ninguna parte es peor que no tenerlo.
- **Catálogo y venta en línea.** Están las **diez categorías** montadas,
  enlazadas desde la portada y **en el sitemap, sin `noindex`**: Google puede
  indexarlas. **Dos ya tienen productos reales**, Solares y Cosmética facial,
  con cinco productos entre ambas y sus cinco fichas indexadas; **las otras
  siete siguen inventadas** y marcadas como tales. Acabar de llenarlas es, con
  diferencia, lo más urgente del proyecto. Precios no hay y no va a haberlos,
  que está decidido; carrito tampoco. Antes de vender
  hay dos cosas que decidir. Una, que **«Medicamentos» no puede venderse a
  distancia** sin notificarlo a la autoridad sanitaria, aparecer en el registro
  DISTAFARMA de la AEMPS y mostrar el logotipo europeo; y los de receta no
  pueden venderse a distancia nunca. El resto de categorías son parafarmacia y
  no tienen esa limitación. Y dos, que en cuanto haya carrito hay que **cambiar
  el aviso legal**, que hoy dice que esto no es una tienda, y añadir condiciones
  de venta, desistimiento de catorce días, envíos y formas de pago.
- **Tienda.** Cuenta de usuario, carrito, checkout, formas de pago, devoluciones
  y envíos están comentados en el pie a la espera del catálogo. Buscador,
  productos destacados y CMS quedaron fuera de esta primera versión por lo
  mismo, tal y como ya preveía el wireframe.

# Farmàcia Agramonte — web

Landing de la Farmàcia Agramonte, en la Plaça de la Llana (El Born, Barcelona),
maquetada a partir del boceto y del diseño visual, que se guardan **fuera del
repositorio**: son lo único que no ve quien visita la web, así que no viajan
con ella.

Es una web **estática**: HTML y CSS, sin dependencias, sin proceso de
compilación y sin servidor de aplicación. No hace falta contratar a nadie ni
instalar nada para verla, y tampoco para publicarla.

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

El repositorio ya está en GitHub, y GitHub Pages publica gratis cualquier
repositorio **público** con un `index.html` en la raíz. **No hace falta hosting
de pago, ni agencia, ni panel de control.** Son cuatro clics, una sola vez:

0. **El repositorio tiene que ser público.** Ahora mismo es privado, y en los
   repositorios privados Pages es una función de pago: por eso la dirección de
   abajo responde 404. Se cambia en Settings → General → Danger Zone →
   *Change repository visibility* → **Public**. La web es pública de todos
   modos; lo único que pasa a verse además es el código, que no guarda ninguna
   contraseña ni dato de nadie.
1. Sube los cambios: `git add -A`, `git commit -m "..."`, `git push`.
2. En GitHub, entra en el repositorio → pestaña **Settings** → **Pages**.
3. En *Source*, elige **Deploy from a branch**; luego rama `main` y carpeta
   `/ (root)`. Guarda.
4. Espera un par de minutos. La web queda en:
   `https://maragramonte.github.io/Farmacia-Agramonte/`

A partir de ahí, **cada `git push` republica la web sola**. No hay más pasos.

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
cookies.html        No hay cookies; se explica la única petición externa
legal.css           Estilo compartido de esas páginas de texto y del 404

catalogo-solares.html            PLANTILLA de catálogo, Solares de muestra
catalogo-cosmetica-facial.html   La misma, con cosmética facial
catalogo.css        Lo propio del catálogo: aviso, tira y rejilla de fichas
marca.css           Paleta, cabecera, botón y pie: la identidad compartida

servir.py           Servidor local (sólo necesita Python)
servir.bat          Doble clic para lo mismo, en Windows

favicon.svg         Icono de la pestaña: el monograma en oro sobre tinta
og.png              Imagen que se ve al compartir el enlace (1200×630)
robots.txt          Permite indexar y apunta al sitemap
sitemap.xml         Las cuatro páginas, para los buscadores
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
  tarjeta-social.py Regenera og.png si cambia el lema o los datos
```

El boceto y el diseño visual (`diseno/`) están ignorados por git y viven sólo
en el ordenador. Conviene tener una copia de seguridad aparte, porque el
repositorio ya no hace esa función.

## Secciones de la landing

Cabecera fija con acceso directo a WhatsApp · hero con la propuesta («envíanos
la receta, la preparamos y te avisamos») · diez categorías de producto que no se
solapan entre sí, cada una abre WhatsApp con la consulta ya escrita · tres
motivos para elegir la farmacia ·
datos de contacto y horario · pie con enlaces legales e información de contacto.

En el móvil el menú no se esconde: la cabecera pasa a dos filas y los enlaces
quedan en una tira que se desliza si no caben. Las anclas se paran por debajo de
la cabecera, que va fija, para que el título de la sección no quede tapado.

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

## La plantilla del catálogo

Hay dos páginas de muestra, **Solares** y **Cosmética facial**, para ver cómo
quedaría una categoría y cómo se navega de una a otra. Las dos son parafarmacia
pura, así que sirven para ver la maqueta sin rozar el régimen de venta a
distancia ni el de publicidad de medicamentos.

El estilo va en dos hojas: `marca.css` con la identidad compartida —paleta,
cabecera, botón y pie— y `catalogo.css` con lo que sólo existe aquí. Hay que
cargar `marca.css` primero. Se separaron al montar la segunda categoría, para no
copiar la paleta una cuarta vez.

Tres cosas que hay que entender antes de tocarla:

- **Los datos son inventados.** Seis productos genéricos, sin marca, y los
  precios en amarillo como todo lo que aún no es real. Un aviso grande arriba lo
  dice. La página lleva `noindex`, no está en `sitemap.xml` y no la enlaza
  ninguna otra: aun así **cualquiera que sepa la URL puede abrirla**, así que no
  la enseñes sin ese aviso ni la des por buena hasta poner productos reales.
- **Es un escaparate, no una tienda.** El botón de cada ficha abre WhatsApp; no
  hay carrito ni pago. Eso es deliberado: mientras no se pueda comprar desde
  aquí, la web sigue fuera del régimen de venta a distancia y el aviso legal
  actual sigue siendo cierto.
- **Sólo la categoría actual es un enlace** en la tira de arriba. Las demás son
  texto porque todavía no tienen página, y ya aprendimos en la portada que un
  enlace que no lleva a ninguna parte es peor que no tenerlo.

Para añadir un producto se copia un bloque `<article class="producto">` y se
cambian nombre, resumen, formato, precio y el texto del enlace de WhatsApp.

Para una categoría nueva se copia una de las dos páginas enteras y se cambian el
título, la introducción y los productos. **Y hay que acordarse de la tira**: la
categoría nueva pasa de `<span>` a `<a>` en *todas* las páginas de catálogo, no
sólo en la suya. Con dos se lleva a mano; a partir de cinco o seis conviene
generar esa tira en lugar de copiarla.

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
- **Catálogo y venta en línea.** Hay **dos plantillas**, Solares y cosmética
  facial, para ver cómo quedaría. Sus productos y sus precios **son inventados**
  y están marcados como tales. Las diez categorías de la
  portada siguen siendo atajos a WhatsApp: no hay fichas reales, ni precios, ni
  carrito. Antes de vender
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

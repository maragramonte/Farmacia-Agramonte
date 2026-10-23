# Decisiones de diseño

La paleta y las tipografías salen del diseño visual, que vive fuera del
repositorio: tinta `#2a1d12`, crema `#f5f0e6` y oro `#c9a055`, con **Playfair
Display** para los títulos —incluida su itálica en «de tu barrio»— y **Karla**
para el texto.

## Un tema único, no claro/oscuro

Al ser una identidad de marca debe verse igual para todo el mundo, así que la
página fija sus colores explícitamente en lugar de seguir la preferencia del
sistema.

## La web no pide nada a nadie

**No hace falta ninguna clave de API.** Las opiniones de Google, que sí la
necesitarían, quedaron fuera igual que en el diseño acabado.

Y **no hay ninguna petición externa**: las tipografías se sirven desde
`tipografias/`, no desde Google Fonts. Son de licencia libre (OFL), así que
redistribuirlas es legal siempre que viaje con ellas su licencia, y por eso
están los dos `LICENCIA-*.txt`. Sólo se incluye el subconjunto latino, que
cubre todo el texto del sitio; y como Playfair Display y Karla son fuentes
variables, un único fichero por familia cubre todos los pesos: **82 KB en
total** en lugar de los 144 KB que ocuparían sueltos.

Al dejar de pedirle nada a Google, las políticas de privacidad y de cookies se
simplificaron: ya no hay ninguna transferencia de datos por el mero hecho de
visitar la página.

Los únicos enlaces a sitios ajenos son deliberados y salen de la portada: los
`wa.me` del botón de pedir, el Instagram del pie, los tres artículos del blog
de `farmaciaagramonte.com`, Take Care en la sección de servicios, y el
reportaje de *La República* en la página de historia.

## Las categorías son cajones de botica, no píldoras

Diez píldoras en fila se leían como una nube de etiquetas de blog, que era lo
más genérico que tenía la página. Cada una es ahora el frente de un cajón:
fondo crema, moldura interior en oro, el icono grande, el rótulo en versalitas
y un tirador debajo; al pasar por encima el cajón «se abre». Las clases son
`.cajonera` y `.cajon`, y la moldura y el tirador los dibuja el CSS con
`::before` y `::after`, así que en el HTML un cajón sigue siendo un `<a>` con
su icono y su nombre.

La tira de categorías del catálogo **sí sigue siendo de píldoras**, a
propósito: ahí no se elige destino, se cambia entre hermanas con una marcada
como actual, y es la forma correcta para un filtro.

## El sello de 1890 vive fuera de la ilustración del mostrador

Mientras estuvo dentro de aquel `<svg>` era un grupo más del decorado, y el
decorado es provisional: el día que llegue la foto real ese dibujo se borra
entero y se habría llevado por delante la única marca propia de la página.
Ahora es su propio `<svg class="sello">`, colocado encima del escaparate por
CSS, que es donde lo pone el diseño.

Su aro de texto se centra solo —el arco empieza abajo y da la vuelta entera,
de modo que `startOffset="50%"` con `text-anchor="middle"` deja el rótulo
arriba mida lo que mida—, y la única palabra traducible, el «desde», está
dentro del círculo en recto y no en el aro. Las dos cosas son por lo mismo: en
SVG, lo que se sale del recorrido no se dibuja, así que un aro que no se
centre solo se recorta al traducirlo.

## El monograma del pie es un sello, no un adorno de columna

Era un circulito de 62 px encima del nombre; ahora es una columna propia al
final de la rejilla. Columna y no posición absoluta a propósito: absoluto se
le montaría encima a los enlaces de «Información», que llegan hasta el borde
derecho.

## La cronología de «Quiénes somos» es una línea de tiempo

No una tabla de filas: el hilo baja por la izquierda y cada etapa cuelga de su
nudo, con la fecha en Playfair y cifras tabulares. El último nudo va macizo
porque es la etapa que no se ha cerrado. Hilo y nudo son `::before` y
`::after` del `<li>`, así que el generador no cambia.

## Dos selectores llevan el elemento delante a propósito

Y no hay que «simplificarlos»: `ul.cronologia` en `catalogo.css` y
`.pie-rejilla p` en `portada.css`. Escritos como `.cronologia` y `.pie p` los
gana una regla de elemento de más arriba en su propia hoja, que les cuela una
sangría y un `max-width` ajenos; cada uno costó un fallo visible antes de
verse. Misma forma las dos veces: una regla de elemento dentro de un
contenedor le gana a la clase del hijo, y lo que hereda el padre no sirve de
nada frente a una regla que apunta al elemento. Los dos llevan su comentario
en la hoja.

## El amarillo de `.pendiente`

El recuadro amarillo quiere decir «esto falta y no es real». Se ve a la legua
a propósito, así nadie publica la página dándolo por bueno, y al rellenar un
dato hay que quitar también el `<span>` que lo envuelve.

Hoy sigue en uso para **los cuatro productos a los que les falta el formato**
y para el aviso de las páginas legales traducidas sin revisar. Los datos del
titular, que fueron su primer uso, ya están todos puestos.

La regla que se siguió con ellos, por si vuelve a hacer falta: **un dato se
rellena en los tres idiomas a la vez**, porque dejarlo puesto en español y en
amarillo en catalán es peor que tenerlo vacío en los tres. Y lo que tenga
dígito de control se comprueba antes de escribirlo: del NIF llegó primero uno
que no validaba, y no se escribió.

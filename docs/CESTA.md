# La cesta

Cada tarjeta y cada ficha llevan un botón **«Añadir»** que apunta el producto
en una cesta. La cesta se ve en `cesta.html`, con el contador en la cabecera
de todas las páginas, y desde ahí se cambian las cantidades, se quitan cosas y
se manda el encargo: **el mensaje de WhatsApp se escribe solo** con la lista
entera, y lo envía la persona desde su móvil.

## Aquí no se paga, y eso es lo que importa entender

No hay pasarela, no se piden datos, no se cobra nada y la farmacia no recibe
nada hasta que alguien le manda el mensaje. El encargo se confirma, se valora
y se paga **en el mostrador**. Por eso la web sigue fuera del régimen de venta
a distancia y el aviso legal de hoy sigue siendo cierto. Los precios, que no
se publican, tampoco salen en la cesta: se confirman al contestar.

Los medicamentos no entran en la cesta porque no hay catálogo de medicamentos:
su página explica cómo se encarga una receta, y eso no cambia.

## Cuatro decisiones que conviene no deshacer

Todo vive en dos ficheros, `cesta.js` (566 líneas, sin dependencias) y
`cesta.css`; el HTML lo pone el mismo generador que el resto.

- **La cesta se guarda en el `localStorage` de quien mira la web**, no en un
  servidor. No hay nada que administrar, nada que respaldar y ningún dato de
  nadie en ninguna parte. A cambio, la cesta es de ese navegador: no sigue a
  la persona de un dispositivo a otro, y se pierde al borrar los datos del
  sitio. Para una lista de la compra que se manda en el momento, es el trato
  bueno.
- **El botón de añadir nace con `hidden` y lo destapa el JavaScript.** Si
  `cesta.js` no carga, no aparece: lo que se ve es el botón de WhatsApp, que
  es un enlace de verdad y funciona siempre. `cesta.html` tiene su propio
  aviso para ese caso, y nace visible a propósito.
- **No hay nada que no se pueda hacer con el teclado.** Las cantidades son
  botones, el foco no se pierde al quitar una línea y lo que cambia se anuncia
  en una región `aria-live`, que es lo que lee un lector de pantalla.
- **Un `wa.me` con un texto larguísimo falla sin avisar.** Así que la cesta
  recorta la lista al llegar al tope, lo dice dentro del propio mensaje y
  **avisa en la página** de cuántos productos se han quedado fuera, con
  «Copiar la lista» y el correo al lado, que esos sí van enteros. Son unos
  quince productos con nombre de laboratorio; de ahí para arriba se avisa.

La cesta es **una sola para los tres idiomas**: su clave de `localStorage` no
lleva el idioma. El matiz está en [IDIOMAS.md](IDIOMAS.md#lo-que-comparten-los-tres-idiomas).

## El día que se quiera cobrar de verdad

Stripe Checkout, o el TPV virtual del banco: el carrito ya está hecho y lo que
hay que cambiar es el botón final de `cesta.html`. **Lo que hace falta antes
no es código:**

- **Dejar Medicamentos fuera.** No puede venderse a distancia sin notificarlo
  a la autoridad sanitaria, aparecer en el registro DISTAFARMA de la AEMPS y
  mostrar el logotipo europeo; y los de receta no pueden venderse a distancia
  nunca. El resto de categorías son parafarmacia y no tienen esa limitación.
- **Rehacer el aviso legal**, que hoy dice que esto no es una tienda, y añadir
  condiciones de venta, desistimiento de catorce días, envíos y formas de
  pago. También la privacidad.
- **Publicar precios**, con lo que eso implica (ver
  [CATALOGO.md](CATALOGO.md#los-precios)).
- **Una función en servidor.** La clave secreta de la pasarela no puede vivir
  en GitHub Pages; haría falta algo como Cloudflare Workers o Netlify, gratis
  en este volumen.

Es una decisión del negocio, no una tarde de trabajo.

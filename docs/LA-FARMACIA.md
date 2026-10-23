# La farmacia

Los datos reales que lleva la web, de dónde salen y qué hay que tocar cuando
cambian.

## Datos de contacto

| | |
|---|---|
| Dirección | Plaça de la Llana, 11 — 08003 Barcelona (El Born) |
| Teléfono | 933 19 59 21 |
| WhatsApp | 661 192 472 |
| Correo | farmacia.lallana@gmail.com |
| Horario | Lunes a Sábado, 9:00–14:30 y 16:00–20:30 |
| Instagram | [@farmacia.agramonte](https://www.instagram.com/farmacia.agramonte/) |
| Desde | 1890 |

Estos datos están además en `index.html` como **JSON-LD de tipo `Pharmacy`**,
que es lo que lee Google para montar la ficha de la farmacia en los resultados
de búsqueda y en Maps: dirección, teléfono y los dos tramos de horario.

**Si cambia un horario o un teléfono, hay que tocarlo en los dos sitios**: en
el texto visible y en ese bloque `<script type="application/ld+json">`. Y el
enlace de Instagram está en las 154 páginas a través de **tres pies
distintos**: ver
[ESTRUCTURA.md](ESTRUCTURA.md#tres-cabeceras-tres-pies-dos-menús).

## Datos del titular

Son los que la LSSI obliga a publicar, y están completos en `aviso-legal.html`:

- Zoila Agramonte Bucho, colegiada **17594**
- NIF **35756987Z**
- Autorización sanitaria **08/3254**
- Título: *Licenciada en Farmacia por la Universidad de La Habana*, con su
  homologación — resolución **2015/08432** del Ministerio de Educación,
  Cultura y Deporte

Lo último hacía falta porque la ley pide el título y el Estado que lo expidió,
y aquí ese Estado no es España.

## Quiénes somos

`historia.html` cuenta de dónde viene la farmacia: que es la antigua Farmàcia
Joaquim Cases, tienda modernista protegida como Bien Cultural de Interés
Local, con referencias documentadas desde 1600, los Saurina hasta 1747, los
Cases de 1864 a 2014 y Zoila Agramonte Bucho como titular desde 2019. Lleva
además el enlace al reportaje de *La República* sobre el barrio de Santa
Caterina durante la pandemia.

**El texto se edita en `pagina_historia()`, dentro de
`herramientas/catalogo.py`**, no en el HTML, que se pierde al regenerar. Está
en el generador y no en `catalogo-datos.json` porque ese JSON es de productos
y esto es prosa, igual que el `CIERRE_PEDIDO` que va al pie de las categorías.
Y se genera en vez de escribirse a mano porque es una página del menú
principal: escrita aparte habría una tercera copia de la cabecera, y el día
que cambie el menú se quedaría atrás sin que nadie se entere.

### El desajuste de 1890

La portada dice **1890** en seis sitios —el `og:description`, la
`description` y el `foundingDate` del JSON-LD que lee Google, el `aria-label`
del sello, el año dibujado dentro del sello y el párrafo del pie— y **1890 no
aparece ni una vez en esta historia**, cuya cronología va de 1600 a 2019. La
sección «¿Por qué elegirnos?» añade un tercer dato, «más de 130 años», que
cuadra con 1890 y no con 1600.

Se dejó así a propósito, pendiente de decidir qué fecha es la buena. Es lo
único del sitio que se contradice consigo mismo.

## Las páginas legales

Tres por idioma, **escritas a mano** y no generadas:

| Página | Qué dice |
|---|---|
| `aviso-legal.html` | Titular, datos profesionales y condiciones de uso |
| `privacidad.html` | Qué datos se tratan, para qué y con qué base legal |
| `cookies.html` | Que no hay cookies; explica la cesta y que no hay terceros |

La de cookies puede decir lo que dice porque la web **no hace ninguna petición
externa**: las tipografías se sirven desde el propio repositorio y no desde
Google Fonts (ver [DISENO.md](DISENO.md#la-web-no-pide-nada-a-nadie)), y la
cesta vive en el `localStorage` del navegador y no sale de ahí (ver
[CESTA.md](CESTA.md)).

Las versiones catalana e inglesa **están traducidas pero sin revisar**, y lo
dicen arriba en amarillo: la española es la original y la que prevalece. Son
textos jurídicos, así que conviene que los lea alguien antes de quitar ese
aviso.

El día que se pueda pagar aquí, estas tres hay que rehacerlas: ver
[CESTA.md](CESTA.md#el-día-que-se-quiera-cobrar-de-verdad).

## Derechos

El código, los textos y el diseño son de la farmacia: [`LICENSE`](../LICENSE)
dice qué se puede hacer con ellos y qué no. **No es una licencia libre.**

Que el repositorio sea público no regala nada: una web estática se descarga
entera en el navegador de quien la abre, con su HTML y su CSS, así que eso es
copiable de todos modos y lo es en cualquier web del mundo. Lo que protege el
trabajo no es esconderlo, es el derecho de autor —automático, sin registrar
nada— y el hecho de que lo copiable es la maqueta, no el negocio: el nombre,
la licencia de oficina de farmacia, la Plaça de la Llana y la ficha de Google
no se clonan.

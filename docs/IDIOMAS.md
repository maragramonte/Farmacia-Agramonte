# Los tres idiomas

Español, catalán e inglés. El español en la raíz, el catalán en `ca/` y el
inglés en `en/`, con un selector en la cabecera que lleva de cada página a su
traducción. El inglés está porque la Plaça de la Llana es de las zonas con más
turismo de Barcelona.

## Por qué el español se queda en la raíz

No es un detalle de gusto: las URL en español llevan tiempo publicadas, están
en Google y en el sitemap, y mover el español a `/es/` las rompería todas.
Dejándolo donde está no se pierde nada y los idiomas se añaden encima, que es
exactamente lo que pasó con el inglés: **no hubo que tocar ni una URL
existente**.

## Cómo se traduce un texto

En `herramientas/textos.json`, cada clave lleva sus idiomas juntos, para que
se vea de un golpe el que falta:

```json
"nav_inicio": { "es": "Inicio", "ca": "Inici", "en": "Home" }
```

Son **74 textos de interfaz**, hoy traducidos al 100 % en los tres idiomas.

En `catalogo-datos.json` un campo acepta **las dos formas**:

```json
"resumen": "Hidratante en gel para piel deshidratada."
"resumen": { "es": "Hidratante en gel...", "ca": "Hidratant en gel..." }
```

La cadena suelta vale para todos los idiomas, que es lo correcto en el nombre
de una marca. En un resumen o en una intro significa que **está sin traducir**,
y el generador lo cuenta al terminar. Así se traduce producto a producto sin
tocarlos todos de golpe, y **nada se queda en blanco por el camino**: lo que
falta sale en español.

Hoy el catálogo tiene **121 campos traducibles** y los únicos sueltos son los
**34 nombres de producto**, que son marcas y están bien así.

## La portada, que es el caso raro

`index.html` está escrita a mano (lleva su hero en SVG y el JSON-LD que lee
Google) y **las otras dos se generan de ella**, sustituyendo los trozos de
texto que están en la lista `portada` de `textos.json`, una lista por idioma.
Hoy son **102 pares por idioma**. Ni tres ficheros de cuatrocientas líneas que
se separan, ni una plantilla de Python que impide editar la portada como HTML.

Lo que hace que no envejezca en silencio: **si cambias un texto español de la
portada, el generador para** y dice qué par de `textos.json` se ha quedado
viejo. Es a propósito; sin eso, las portadas traducidas se irían quedando
atrás sin que nadie se enterara. Y es la razón de que añadir un idioma dé
trabajo una vez y no cada vez.

Dos cosas de la cabeza de la portada **no son traducción y se sustituyen
aparte**: el selector de idioma, que se escribe entero según los idiomas que
haya, y el `og:locale`, que sale de la clave `og_locale` de cada idioma en
`textos.json` y no se deduce del código de idioma, que daría locales que no
existen.

## Lo que comparten los tres idiomas

Las hojas de estilo, las tipografías, `cesta.js` y las fotos **no se
duplican**: viven en la raíz y desde `ca/` y `en/` se piden con `../`, que lo
pone el generador. Se calcula en vez de usar rutas absolutas porque ésas
llevan dentro el nombre del repositorio y se romperían al renombrarlo o al
poner un dominio propio.

La **cesta también es una sola**: su clave de `localStorage` no lleva el
idioma, así que quien añade algo en español y cambia de idioma encuentra su
cesta y no otra vacía. Con un matiz: cada línea guarda el nombre y el formato
**tal como se veían al añadirla**, así que una cesta montada en varios idiomas
sale mezclada. Arreglarlo exigiría llevar el catálogo entero también en
JavaScript, que es justo lo que esta web no hace.

El `404.html` lleva **los tres idiomas en un solo fichero**, porque GitHub
Pages sirve el mismo para todo el sitio y no hay manera de saber en qué idioma
estaba quien se ha perdido. Al añadir un idioma se le añade su bloque, con su
`lang` para que el comprobador de acentos sepa saltárselo.

## Para los buscadores

Cada página lleva su `canonical` y los `hreflang` de todas sus traducciones,
con `x-default` al español. Eso le dice a Google que son la misma página en
otro idioma y no contenido duplicado.

**La URL de un producto no se traduce**:
`ca/catalogo-solares-cleanance-solaire-spf50.html` tiene el mismo nombre que
la española, porque los nombres de producto son marcas y porque traducir los
slugs duplicaría el trabajo de mantener URL estables.

## Comprobar los acentos

El catalán y el español se parecen lo justo para equivocarse:

```
python herramientas/acentos.py
```

Busca los errores concretos que se cometen al traducir entre los dos (el
acento grave que el español pone agudo (`interès`, `època`, `Amèrica`), la ela
geminada escrita como `ll` o `l.l`, y las palabras de un idioma colándose en
el otro) y avisa de cada uno con su contexto. **No es un corrector**: son
avisos que hay que mirar. Se salta los comentarios del código, que van en
español en los tres idiomas a propósito, y los bloques marcados con otro
`lang`, que es como se salta el inglés: no comparte estos errores, así que no
entra en la comprobación.

## Añadir otro idioma

El inglés se añadió así, y queda documentado porque el cuarto costará lo
mismo. Son nueve pasos; los seis primeros los lleva el generador, los tres
últimos van a mano porque no pasan por él.

1. En `textos.json`, mete el idioma en `idiomas`, con su `carpeta`, su
   `etiqueta_html`, su `corto` para el selector y su `og_locale`.
2. Añade su clave a cada uno de los **74 textos**. Lo que no traduzcas sale en
   español y el generador dice cuántos faltan, así que se puede ir por partes.
3. Una lista con su nombre en `portada`, con los **102 pares** de la portada.
4. En `catalogo-datos.json`, su clave en los campos traducibles: las 10
   categorías, sus intros, la página de Medicamentos y los productos. Una
   cadena suelta se deja como está: significa «vale para todos los idiomas»,
   que es lo correcto en una marca.
5. En `cesta.js`, su bloque en `TEXTOS`. No están en `textos.json` a
   propósito, que esto se ejecuta en el navegador.
6. En `catalogo.css`, su regla del rótulo «Foto pendiente», que lo pone el CSS
   y no el generador.
7. Ejecuta el generador: escribe la carpeta entera, con sus `hreflang`, su
   selector y su parte del sitemap.
8. Las tres legales hay que escribirlas a mano, y el aviso de traducción sin
   revisar va puesto hasta que alguien las firme.
9. Y a mano también, porque no se generan: el bloque del idioma en
   `404.html`, y su `hreflang` y su enlace en el selector de las **seis
   legales que ya existían** más `index.html`. Es lo único que el generador no
   toca.

## Lo que falta de las traducciones

Vale igual para el catalán y para el inglés:

- **Las tres páginas legales de cada idioma están traducidas pero sin
  revisar**, y lo dicen arriba en amarillo: la versión española es la original
  y la que prevalece. Son textos jurídicos, así que conviene que los lea
  alguien antes de quitar ese aviso.
- Los textos de salud de los productos están traducidos **sin revisar**. En
  una farmacia eso es consejo, así que hay que mirarlos igual que los
  españoles.

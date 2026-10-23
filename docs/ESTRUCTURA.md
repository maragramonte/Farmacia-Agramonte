# Estructura del repositorio

Qué hay en cada fichero, qué se escribe a mano y qué lo escribe el generador.

## Lo que se edita y lo que se genera

El sitio son **154 páginas HTML**: 52 en español —la raíz, con el `404.html`
dentro—, 51 en catalán y 51 en inglés. **Sólo once se escriben a mano**: la
portada española, el 404 y las tres legales de cada idioma. Las **143
restantes** las escribe `herramientas/catalogo.py`, y llevan un comentario
arriba que lo dice.

| Dónde se escribe | Qué sale de ahí |
|---|---|
| `herramientas/catalogo-datos.json` | Los productos: nombres, resúmenes, formatos, epígrafes |
| `herramientas/textos.json` | Todo lo que no es un producto: menú, botones, pie, la cesta y la historia |
| `index.html` | La portada española. La catalana y la inglesa se generan **de ella** |
| `aviso-legal.html` y compañía | Las tres legales de cada idioma, y el `404.html`, a mano |

## El árbol

```
index.html          La landing completa. Se edita ESTA: la catalana y la
                    inglesa se generan a partir de ella
404.html            Lo que se ve al abrir una dirección que no existe.
                    Trilingüe: Pages sirve el mismo para todo el sitio
tipografias.css     Declara las tipografías propias (@font-face)
portada.css         Lo propio de la portada. La cargan las tres portadas
aviso-legal.html    Titular, datos profesionales y condiciones de uso
privacidad.html     Qué datos se tratan, para qué y con qué base legal
cookies.html        No hay cookies; explica la cesta y que no hay terceros
legal.css           Estilo compartido de esas páginas de texto y del 404

ca/                 Toda la web en catalán. index.html, las catalogo-*,
                    historia.html y cesta.html SE GENERAN; las tres
                    legales están a mano
en/                 Lo mismo en inglés, con las mismas reglas
idiomas.css         El selector de idioma de la cabecera

catalogo-*.html     Las diez categorías y las fichas de sus productos.
                    SE GENERAN, no se editan a mano
historia.html       Quiénes somos y la historia de la farmacia. SE GENERA:
                    el texto está en pagina_historia(), en catalogo.py
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
sitemap.xml         Las páginas indexables de los tres idiomas. SE GENERA
.nojekyll           Le dice a GitHub Pages que sirva los ficheros tal cual

LICENSE             Qué se puede hacer con este código y qué no

docs/               Esta documentación

tipografias/
  playfair-display-variable.woff2  Los títulos. Fuente variable: un solo
                                   fichero cubre del peso 400 al 500
  playfair-display-cursiva.woff2   La itálica de «de tu barrio»
  karla-variable.woff2             El texto, del 400 al 600
  LICENCIA-karla.txt               SIL Open Font License 1.1
  LICENCIA-playfairdisplay.txt     La OFL exige distribuirla con la fuente

herramientas/
  catalogo.py           Escribe el catálogo, la historia, la cesta, las
                        portadas traducidas y el sitemap, en los tres
                        idiomas
  textos.json           TODOS los textos de la interfaz, en cada idioma
  acentos.py            Comprueba la ortografía que se confunde entre el
                        español y el catalán. El inglés no entra: no
                        comparte esos errores
  catalogo-datos.json   Los productos. Se edita ESTE
  importar.py           Vuelca un export en CSV al JSON de arriba
  tarjeta-social.py     Regenera og.png si cambia el lema o los datos
```

El boceto y el diseño visual (`diseno/`) están ignorados por git y viven sólo
en el ordenador. Conviene tener una copia de seguridad aparte, porque el
repositorio ya no hace esa función.

## Las secciones de la portada

Cabecera fija con acceso directo a WhatsApp · hero con la propuesta
(«envíanos la receta, la preparamos y te avisamos») · las diez categorías,
cada una a su página de catálogo · **Novedades**, cuatro productos destacados
que enlazan a su ficha · **Servicios de la farmacia**, ocho servicios de
mostrador más el aviso de Take Care · tres motivos para elegir la farmacia ·
**Del blog**, tres artículos del blog de `farmaciaagramonte.com` · datos de
contacto y horario · pie con enlaces legales e información de contacto.

**La portada alterna fondos de arriba abajo**: tinta en el hero, crema en las
categorías, tinta otra vez en los motivos para elegir la farmacia, crema en el
contacto y tinta en el pie. Lo que separa una sección de la siguiente es ese
cambio de fondo y no un filete. La sección oscura lleva la clase `.banda`, y
su `.contenedor` va **dentro** de la sección y no en ella, como en el hero y
en el pie, porque el fondo tiene que llegar de borde a borde.

En el móvil el menú no se esconde: la cabecera pasa a dos filas y los enlaces
quedan en una tira que se desliza si no caben. Las anclas se paran por debajo
de la cabecera, que va fija, para que el título de la sección no quede tapado:
eso lo hace `scroll-padding-top` con la variable `--alto-cabecera`, y conviene
saber que **pasarse de largo ahí es inocuo y quedarse corto no**, porque corto
deja el título debajo de la cabecera.

## Tres cabeceras, tres pies, dos menús

**Hay tres cabeceras, no una**: la de la portada (`portada.css`), la del
catálogo (`marca.css`) y la de las páginas de texto (`legal.css`), que no
comparten hoja. Las tres llevan trato de móvil y `flex-wrap`; la de
`legal.css` fue la última en tenerlo y es **la primera que hay que mirar si
algún día se añade un cuarto idioma**, porque es la más justa de sitio a
320 px: la marca, el «Volver» y los códigos de idioma en una sola fila.

Y **tres pies**, por el mismo reparto: el largo de la portada, con sus cuatro
columnas de enlaces y el monograma (`portada.css`); el de una fila de las
páginas generadas, con el copyright, el Instagram y las legales (`marca.css`,
y el HTML lo pone `documento()` en `catalogo.py`); y el de una sola línea
centrada de las páginas de texto y el 404 (`legal.css`, escrito a mano en cada
uno de esos diez ficheros). Lo que vaya en «todos los pies» hay que ponerlo
tres veces: el enlace a `@farmacia.agramonte` es el ejemplo vivo. **Si cambia
la cuenta, hay que tocar los tres.**

**El menú está escrito en dos sitios**, y hay que tocar los dos o se
descuadra: a mano en `index.html`, y generado en `documento()` de
`herramientas/catalogo.py` para las que genera. Hoy son cuatro entradas:
Inicio, Categorías, Historia y Contacto, más la cesta y el botón de pedir.

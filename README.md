# Farmàcia Agramonte — web

Landing de la Farmàcia Agramonte, en la Plaça de la Llana (El Born, Barcelona),
maquetada a partir del boceto y del diseño visual que están en `diseno/`.

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
repositorio con un `index.html` en la raíz. **No hace falta hosting de pago, ni
agencia, ni panel de control.** Son cuatro clics, una sola vez:

1. Sube los cambios: `git add -A`, `git commit -m "..."`, `git push`.
2. En GitHub, entra en el repositorio → pestaña **Settings** → **Pages**.
3. En *Source*, elige **Deploy from a branch**; luego rama `main` y carpeta
   `/ (root)`. Guarda.
4. Espera un par de minutos. La web queda en:
   `https://maragramonte.github.io/Farm-cia-Agramonte/`

A partir de ahí, **cada `git push` republica la web sola**. No hay más pasos.

Dos apuntes:

- La URL sale del nombre del repositorio, y ahora mismo es `Farm-cia-Agramonte`
  porque GitHub no admitió la `à` de *Farmàcia*. Renombrando el repositorio a
  `farmacia-agramonte` (Settings → General → Repository name) la dirección queda
  mucho mejor. Si lo haces, hay que **actualizar la URL** en `index.html`
  (`canonical`, `og:url`, `og:image` y el JSON-LD), en `robots.txt` y en
  `sitemap.xml`.
- Cuando haya un dominio propio (`farmaciaagramonte.com` o similar), se apunta
  a GitHub Pages desde el registrador y se añade un fichero `CNAME` en la raíz
  con el dominio dentro. El único gasto sería el dominio, unos 12 €/año.

## Estructura

```
index.html          La landing completa (HTML + CSS + iconos SVG en línea)
aviso-legal.html    Titular, datos profesionales y condiciones de uso
privacidad.html     Qué datos se tratan, para qué y con qué base legal
cookies.html        No hay cookies; se explica la única petición externa
legal.css           Estilo compartido de esas tres páginas de texto

servir.py           Servidor local (sólo necesita Python)
servir.bat          Doble clic para lo mismo, en Windows

favicon.svg         Icono de la pestaña: el monograma en oro sobre tinta
og.png              Imagen que se ve al compartir el enlace (1200×630)
robots.txt          Permite indexar y apunta al sitemap
sitemap.xml         Las cuatro páginas, para los buscadores
.nojekyll           Le dice a GitHub Pages que sirva los ficheros tal cual

herramientas/
  tarjeta-social.py Regenera og.png si cambia el lema o los datos
diseno/
  01-wireframe.png       Bloques de la página y qué depende de datos reales
  02-diseno-visual.png   El diseño acabado del que sale la maquetación
```

## Secciones de la landing

Cabecera fija con acceso directo a WhatsApp · hero con la propuesta («envíanos
la receta, la preparamos y te avisamos») · seis categorías de producto · tres
motivos para elegir la farmacia · consejos del farmacéutico · datos de contacto
y horario · pie con enlaces legales e información de contacto.

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

## Decisiones de diseño

La paleta y las tipografías salen del diseño visual: tinta `#2a1d12`, crema
`#f5f0e6` y oro `#c9a055`, con **Playfair Display** para los títulos —incluida
su itálica en «de tu barrio»— y **Karla** para el texto.

Es un **tema único**, no claro/oscuro: al ser una identidad de marca debe verse
igual para todo el mundo, así que la página fija sus colores explícitamente en
lugar de seguir la preferencia del sistema.

**No hace falta ninguna clave de API.** Las opiniones de Google, que sí la
necesitarían, quedaron fuera igual que en el diseño acabado. La única petición a
un tercero son las tipografías de Google Fonts.

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
  en SVG y con un aviso encima. Los tres huecos del blog son bloques con
  textura. Hay que sustituirlos por las fotos reales.
- **Perfiles de redes sociales.** Los iconos de Instagram y Facebook están
  comentados en el pie, con la URL de ejemplo lista para sustituir. Un icono que
  no lleva a ninguna parte es peor que no tenerlo.
- **Alojar las tipografías** en el propio repositorio en lugar de pedirlas a
  Google Fonts. Son de licencia libre (OFL), así que se pueden descargar y
  servir desde aquí. Con eso la web deja de hacer ninguna petición externa y las
  políticas de privacidad y cookies se simplifican.
- **Tienda.** Cuenta de usuario, carrito, checkout, formas de pago, devoluciones
  y envíos están comentados en el pie a la espera del catálogo. Buscador,
  productos destacados y CMS quedaron fuera de esta primera versión por lo
  mismo, tal y como ya preveía el wireframe.

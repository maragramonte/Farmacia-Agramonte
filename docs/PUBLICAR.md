# Verla y publicarla

## Verla en tu ordenador

La forma más rápida es **doble clic en `servir.bat`**. Se abre una ventana
negra, arranca el servidor y se abre el navegador solo. Para pararlo, cierra
la ventana o pulsa `Ctrl+C`.

Desde la terminal, lo mismo:

```
python servir.py            # puerto 8000, abre el navegador
python servir.py 3000       # otro puerto, por si el 8000 está ocupado
python servir.py --no-abrir # sin abrir el navegador
```

Al arrancar imprime dos direcciones: la de este equipo (`localhost`) y la de
la red local, con la IP. **Esa segunda sirve para verla en el móvil** con sólo
escribirla, estando en la misma wifi — útil para comprobar cómo queda de
verdad en una pantalla pequeña.

También se puede abrir `index.html` con doble clic, sin servidor. Funciona,
pero la ruta será `file://` y algunas cosas no se comportan igual que en
producción, así que para comprobar cambios es mejor el servidor.

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

**Cada `git push` a `main` republica la web sola**, en un par de minutos. No
hay más pasos, no hay botón que pulsar y no hay nada que avisar. Si acabas de
empujar y no ves el cambio, recarga sin caché (`Ctrl+Shift+R`): suele ser el
navegador, no el despliegue.

### Cómo quedó montado

Es lo que habría que repetir en un repositorio nuevo:

1. El repositorio es **público**. Pages gratis sólo publica los públicos; en
   los privados es una función de pago. Eso significa que **el código se ve**,
   y es asumido: ver [LA-FARMACIA.md](LA-FARMACIA.md#derechos).
2. En GitHub, repositorio → **Settings** → **Pages**.
3. En *Source*, **Deploy from a branch**; rama `main` y carpeta `/ (root)`.
4. Un par de minutos y la dirección responde.

El fichero `.nojekyll` de la raíz le dice a Pages que sirva los ficheros tal
cual, sin pasarlos por Jekyll.

## Si se renombra el repositorio

La URL sale del nombre del repositorio, que ahora es `Farmacia-Agramonte`. Si
se vuelve a renombrar (Settings → General → Repository name), hay que
**actualizar la dirección en seis sitios**: en `index.html` el `canonical`, el
`og:url`, el `og:image` y el `url` y el `image` del JSON-LD; y además
`robots.txt` y `sitemap.xml`.

GitHub redirige el nombre viejo, pero una web que se anuncia a sí misma con
una dirección que ya no es la suya confunde a los buscadores.

Dentro del sitio no hay que tocar nada: las rutas entre páginas se calculan
con `../` y no llevan el nombre del repositorio dentro, precisamente para
esto.

## Un dominio propio

Cuando lo haya, se apunta a GitHub Pages desde el registrador y se añade un
fichero `CNAME` en la raíz con el dominio dentro. El único gasto sería el
dominio, unos 12 €/año.

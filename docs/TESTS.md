# Los tests

```
pip install pytest      # una vez
python -m pytest        # todos, en unos segundos
```

Los de la tarjeta social (`test_tarjeta_social.py`) necesitan además Pillow,
igual que el script que prueban. Sin él se saltan, no fallan; el CI lo
instala y los pasa siempre.

La web no los necesita para funcionar: son para quien la mantiene. Se pasan
solos en GitHub en cada `push` y en cada pull request
(`.github/workflows/tests.yml`), y un pull request en rojo es un aviso de
que algo de lo que se va a publicar está roto.

## Qué comprueban

**Que lo publicado es lo que sale del generador** (`tests/test_catalogo.py`).
Genera el catálogo en una copia del repositorio y lo compara, página a
página, con lo que hay. Falla si alguien edita a mano una página generada o
cambia `catalogo-datos.json` o `textos.json` y se olvida de ejecutar
`python herramientas/catalogo.py`. Al sitemap no se le compara la fecha.
También prueba las piezas del generador que tienen más letra pequeña: los
slugs de las URL, el recorte de la meta description y el aviso de URL
repetidas.

**Que nada pide un fichero que no existe** (`tests/test_enlaces.py`). Cada
`href` y `src` de cada página y cada `url()` de cada hoja de estilos tienen
que apuntar a un fichero del repositorio. Es lo que se rompe al renombrar o
borrar algo, y en el navegador sólo se ve mirando la consola. De paso, cada
tipografía tiene que llevar su licencia.

**Que el comprobador de acentos avisa de lo que debe**
(`tests/test_acentos.py`), y que hoy la web no tiene ningún aviso.

## Lo que no comprueban

Cómo se ve. Una cabecera que se monta encima del texto en el móvil o un
color que no contrasta no los pilla ningún test de estos: eso sigue siendo
abrir la web con `servir.py` y mirarla, a ser posible también en el móvil.

## Al añadir algo

- Una función nueva en `herramientas/` con condiciones dentro: un test por
  cada camino.
- Un fallo arreglado: primero un test que lo reproduzca.
- Nunca un commit con los tests en rojo.

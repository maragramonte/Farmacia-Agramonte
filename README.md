# Farmàcia Agramonte — web

Landing de la Farmàcia Agramonte, en la Plaça de la Llana (El Born, Barcelona),
maquetada a partir del boceto y del diseño visual que están en `diseno/`.

Es una página **estática**: un solo `index.html` con el CSS dentro. No hay
dependencias, ni proceso de compilación, ni servidor. Se abre haciendo doble
clic en el fichero y se publica copiándolo a cualquier alojamiento.

## Estructura

```
index.html    La página completa (HTML + CSS + iconos SVG en línea)
diseno/
  01-wireframe.png       Bloques de la página y qué depende de datos reales
  02-diseno-visual.png   El diseño acabado del que sale la maquetación
```

## Secciones

Cabecera fija con acceso directo a WhatsApp · hero con la propuesta («envíanos
la receta, la preparamos y te avisamos») · seis categorías de producto · tres
motivos para elegir la farmacia · consejos del farmacéutico · datos de contacto
y horario · pie con enlaces de tienda e información legal.

## Datos de la farmacia

| | |
|---|---|
| Dirección | Plaça de la Llana, 11 — 08003 Barcelona (El Born) |
| Teléfono | 933 19 59 21 |
| WhatsApp | 661 192 472 |
| Correo | farmacia.lallana@gmail.com |
| Horario | Lunes a Sábado, 9:00–14:30 y 16:00–20:30 |
| Desde | 1890 |

## Decisiones de diseño

La paleta y las tipografías salen del diseño visual: tinta `#2a1d12`, crema
`#f5f0e6` y oro `#c9a055`, con **Playfair Display** para los títulos —incluida
su itálica en «de tu barrio»— y **Karla** para el texto.

Es un **tema único**, no claro/oscuro: al ser una identidad de marca debe verse
igual para todo el mundo, así que la página fija sus colores explícitamente en
lugar de seguir la preferencia del sistema.

Las únicas peticiones externas son las tipografías de Google Fonts y los enlaces
`wa.me`. **No hace falta ninguna clave de API**: las opiniones de Google, que sí
la necesitarían, quedaron fuera igual que en el diseño acabado.

## Qué falta

- **Fotos.** El hero lleva una ilustración provisional del mostrador, dibujada
  en SVG y con un aviso encima. Los tres huecos del blog son bloques con
  textura. Hay que sustituirlos por las fotos reales.
- **Número de colegiado** en el pie. En España suele ser obligatorio.
- **URL del pie.** Los enlaces de *Atención al cliente* e *Información* apuntan
  a `#` porque las direcciones de la tienda están pendientes.
- **Buscador, productos destacados y CMS**, que el wireframe ya dejaba fuera de
  esta primera versión porque dependen del catálogo.

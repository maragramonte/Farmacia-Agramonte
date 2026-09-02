#!/usr/bin/env python3
"""
Genera og.png, la tarjeta que se ve al compartir la web en WhatsApp,
Facebook, LinkedIn o Telegram.

    python herramientas/tarjeta-social.py

Usa Georgia y Calibri (que ya están en Windows) porque son las mismas
alternativas que declara el CSS para Playfair Display y Karla. Sólo hay que
volver a ejecutarlo si cambian el lema o los datos de la farmacia.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "og.png"

ANCHO, ALTO = 1200, 630
TINTA = (42, 29, 18)
ORO = (201, 160, 85)
ORO_CLARO = (224, 194, 133)
CREMA = (240, 232, 219)

FUENTES = Path("C:/Windows/Fonts")


def fuente(archivo, tamano):
    ruta = FUENTES / archivo
    if ruta.exists():
        return ImageFont.truetype(str(ruta), tamano)
    return ImageFont.load_default(tamano)


def main():
    img = Image.new("RGB", (ANCHO, ALTO), TINTA)
    d = ImageDraw.Draw(img)

    # Marco fino de oro, como el borde de las etiquetas de la página.
    d.rectangle([38, 38, ANCHO - 39, ALTO - 39], outline=ORO, width=2)

    titulo = fuente("georgia.ttf", 86)
    titulo_it = fuente("georgiai.ttf", 86)
    etiqueta = fuente("calibrib.ttf", 26)
    cuerpo = fuente("calibri.ttf", 34)

    x = 92
    d.text((x, 120), "E L   B O R N ,   B A R C E L O N A", font=etiqueta, fill=ORO)

    d.text((x, 178), "Consejo de siempre,", font=titulo, fill=CREMA)
    d.text((x, 278), "de tu barrio", font=titulo_it, fill=ORO_CLARO)

    d.text((x, 410), "Envíanos la receta, la preparamos y te avisamos.", font=cuerpo, fill=CREMA)

    d.line([x, 486, x + 96, 486], fill=ORO, width=2)
    d.text((x, 510), "Farmàcia Agramonte · desde 1890", font=cuerpo, fill=ORO_CLARO)

    img.save(SALIDA, "PNG", optimize=True)
    print(f"Escrito {SALIDA.relative_to(RAIZ)} ({SALIDA.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

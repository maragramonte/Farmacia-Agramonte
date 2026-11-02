#!/usr/bin/env python3
"""
Genera og.png, la tarjeta que se ve al compartir la web en WhatsApp,
Facebook, LinkedIn o Telegram.

    python herramientas/tarjeta-social.py

Usa las mismas tipografías que la web, las de tipografias/: Pillow lee los
.woff2 directamente. Paleta del rediseño 07: el verde de la cabecera, el
acento, la crema y la franja de horizonte abajo. Si alguna fuente no
cargara, cae en Georgia y Calibri, que ya están en Windows.

Sólo hay que volver a ejecutarlo si cambian el lema, los datos de la
farmacia o la paleta.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "og.png"
TIPOS = RAIZ / "tipografias"
WINDOWS = Path("C:/Windows/Fonts")

ANCHO, ALTO = 1200, 630
VERDE_PIE = (63, 86, 73)       # --tinta   #3f5649
VERDE = (83, 109, 92)          # --verde   #536d5c
ACENTO = (240, 162, 74)        # --oro     #f0a24a
ACENTO_CLARO = (246, 192, 127) # --oro-claro
CREMA = (246, 236, 224)        # --crema   #f6ece0
CREMA_2 = (236, 211, 185)      # --crema-2 #ecd3b9
TENUE = (217, 199, 176)        # --tenue-tinta

# Los tejados de la franja de horizonte, los mismos que dibuja el CSS
# (viewBox 0 0 240 28), en puntos para repetirlos a lo ancho.
TEJADOS = [(0, 28), (0, 18), (14, 18), (14, 12), (22, 12), (22, 8), (26, 8), (26, 12),
           (40, 12), (40, 16), (52, 16), (52, 10), (60, 4), (68, 10), (68, 16), (84, 16),
           (84, 20), (96, 20), (96, 14), (108, 14), (108, 6), (112, 6), (112, 2), (114, 2),
           (114, 6), (118, 6), (118, 14), (132, 14), (132, 18), (150, 18), (150, 11),
           (162, 11), (162, 15), (176, 15), (176, 9), (184, 5), (192, 9), (192, 17),
           (206, 17), (206, 12), (218, 12), (218, 18), (240, 18), (240, 28)]


def fuente(propia, respaldo, tamano, peso=None):
    for ruta in (TIPOS / propia, WINDOWS / respaldo):
        if ruta.exists():
            f = ImageFont.truetype(str(ruta), tamano)
            if peso:
                try:
                    f.set_variation_by_axes([peso])
                except (OSError, AttributeError):
                    pass
            return f
    return ImageFont.load_default(tamano)


def main():
    img = Image.new("RGB", (ANCHO, ALTO), VERDE_PIE)
    d = ImageDraw.Draw(img)

    titulo = fuente("instrument-serif.woff2", "georgia.ttf", 104)
    titulo_it = fuente("instrument-serif-cursiva.woff2", "georgiai.ttf", 104)
    rotulo = fuente("cinzel-variable.woff2", "georgiab.ttf", 26, peso=600)
    cuerpo = fuente("karla-variable.woff2", "calibri.ttf", 32)

    # La franja de horizonte, abajo: los tejados en verde sobre la crema.
    alto_franja, base = 56, ALTO - 12
    d.rectangle([0, base - alto_franja, ANCHO, base], fill=CREMA_2)
    escala = alto_franja / 28
    for i in range(0, ANCHO // int(240 * escala) + 2):
        dx = i * 240 * escala
        d.polygon([(dx + x * escala, base - alto_franja + y * escala) for x, y in TEJADOS], fill=VERDE)
    d.rectangle([0, base, ANCHO, ALTO], fill=VERDE_PIE)

    x = 92
    # La etiqueta, enmarcada como la de la portada.
    texto = "EL BORN, BARCELONA"
    caja = d.textbbox((0, 0), texto, font=rotulo)
    ancho_txt = caja[2] - caja[0]
    d.rectangle([x, 74, x + ancho_txt + 40, 74 + 54], outline=ACENTO, width=2)
    d.text((x + 20, 74 + 13), texto, font=rotulo, fill=ACENTO_CLARO)

    d.text((x, 150), "Consejo de siempre,", font=titulo, fill=CREMA)
    d.text((x, 258), "de tu barrio", font=titulo_it, fill=ACENTO)

    d.line([x, 400, x, 470], fill=ACENTO, width=3)
    d.text((x + 24, 398), "Envíanos la receta, la preparamos y te avisamos.", font=cuerpo, fill=CREMA)
    d.text((x + 24, 438), "Farmàcia Agramonte · desde 1890", font=cuerpo, fill=TENUE)

    img.save(SALIDA, "PNG", optimize=True)
    print(f"Escrito {SALIDA.relative_to(RAIZ)} ({SALIDA.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

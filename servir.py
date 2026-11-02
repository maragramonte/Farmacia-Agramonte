#!/usr/bin/env python3
"""
Servidor local para la web de la Farmàcia Agramonte.

    python servir.py            # arranca en el puerto 8000 y abre el navegador
    python servir.py 3000       # usa otro puerto
    python servir.py --no-abrir # no abre el navegador

No necesita instalar nada: sólo Python, que ya viene con el sistema en muchos
equipos. Sirve la carpeta del proyecto tal cual, sin compilar nada.
Para pararlo: Ctrl+C.

Escucha en toda la red, no sólo en este equipo, para poder abrirla desde el
móvil. Por eso no sirve lo que no se publica: nada que empiece por punto
(.git, .claude, .gstack…) ni CLAUDE.md, que se queda en local. Desde la misma
wifi, .git bastaría para llevarse el repositorio entero.
"""

import http.server
import socket
import sys
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PUERTO = 8000

# Ficheros de la carpeta que no se publican, en minúsculas: en Windows el
# disco no distingue «CLAUDE.md» de «claude.md».
SOLO_LOCAL = {"claude.md"}


def prohibida(ruta):
    """Si una ruta del disco es de las que no se sirven.

    Se mira la ruta ya resuelta y no la URL: así da igual cómo venga escrita
    (%2e en vez de punto, mayúsculas, un punto final que Windows se come)."""
    try:
        partes = Path(ruta).resolve().relative_to(RAIZ).parts
    except ValueError:
        return True   # fuera de la carpeta del proyecto
    return any(p.startswith(".") or p.lower() in SOLO_LOCAL for p in partes)


class Servidor(http.server.ThreadingHTTPServer):
    """Un hilo por petición, como «python -m http.server»: los navegadores
    abren conexiones de más por adelantado, y con un solo hilo una de ésas
    deja al resto esperando. Aquí se conectan el ordenador y el móvil a la vez.

    En Windows, reutilizar la dirección deja abrir dos servidores en el mismo
    puerto sin error, y no se sabe cuál contesta. Fuera de Windows hace falta
    para poder relanzarlo justo después de un Ctrl+C."""
    allow_reuse_address = sys.platform != "win32"


class Manejador(http.server.SimpleHTTPRequestHandler):
    """Sirve desde la carpeta del proyecto y no deja que el navegador cachee."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(RAIZ), **kwargs)

    def send_head(self):
        if prohibida(self.translate_path(self.path)):
            self.send_error(404)
            return None
        return super().send_head()

    def list_directory(self, ruta):
        # Como GitHub Pages: una carpeta sin index.html no se lista.
        self.send_error(404)
        return None

    def end_headers(self):
        # Sin caché: al recargar siempre se ve el último cambio del HTML.
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, formato, *args):
        # Una línea por petición, sin la marca de tiempo larga de serie.
        sys.stderr.write("  %s\n" % (formato % args))


def ip_de_la_red():
    """La IP de este equipo en la red local, para abrirla desde el móvil."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # no envía nada, sólo elige la interfaz
            return s.getsockname()[0]
    except OSError:
        return None


def puerto_de(argumentos):
    """El puerto de la línea de órdenes, o el de siempre si no viene ninguno."""
    puertos = [int(a) for a in argumentos if a.isdigit()]
    puerto = puertos[0] if puertos else PUERTO
    if not 1 <= puerto <= 65535:
        sys.exit(f"El puerto tiene que ir de 1 a 65535, y {puerto} no. "
                 f"Prueba: python servir.py {PUERTO}")
    return puerto


def main():
    argumentos = sys.argv[1:]
    abrir = "--no-abrir" not in argumentos
    puerto = puerto_de(argumentos)

    if not (RAIZ / "index.html").exists():
        sys.exit(f"No encuentro index.html en {RAIZ}")

    try:
        servidor = Servidor(("0.0.0.0", puerto), Manejador)
    except OSError as e:
        sys.exit(f"No puedo usar el puerto {puerto} ({e}). Prueba: python servir.py {puerto + 1}")

    local = f"http://localhost:{puerto}/"
    ip = ip_de_la_red()

    print()
    print("  Farmàcia Agramonte — servidor local")
    print(f"  En este equipo   {local}")
    if ip:
        print(f"  En el móvil      http://{ip}:{puerto}/   (misma wifi)")
    print("  Parar            Ctrl+C")
    print()

    if abrir:
        webbrowser.open(local)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n  Servidor parado.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()

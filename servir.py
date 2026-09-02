#!/usr/bin/env python3
"""
Servidor local para la web de la Farmàcia Agramonte.

    python servir.py            # arranca en el puerto 8000 y abre el navegador
    python servir.py 3000       # usa otro puerto
    python servir.py --no-abrir # no abre el navegador

No necesita instalar nada: sólo Python, que ya viene con el sistema en muchos
equipos. Sirve la carpeta del proyecto tal cual, sin compilar nada.
Para pararlo: Ctrl+C.
"""

import http.server
import socket
import socketserver
import sys
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


class Manejador(http.server.SimpleHTTPRequestHandler):
    """Sirve desde la carpeta del proyecto y no deja que el navegador cachee."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(RAIZ), **kwargs)

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


def main():
    argumentos = sys.argv[1:]
    abrir = "--no-abrir" not in argumentos
    puertos = [int(a) for a in argumentos if a.isdigit()]
    puerto = puertos[0] if puertos else 8000

    if not (RAIZ / "index.html").exists():
        sys.exit(f"No encuentro index.html en {RAIZ}")

    socketserver.TCPServer.allow_reuse_address = True
    try:
        servidor = socketserver.TCPServer(("0.0.0.0", puerto), Manejador)
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

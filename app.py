#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Pagos CNI - Aplicacion de Escritorio
Consejo Nacional de Inversiones - Honduras

Aplicacion de escritorio para gestion de recursos humanos y nomina.
Soporta dos modos:
  - Modo Escritorio: Ventana nativa con PyWebView (si esta disponible)
  - Modo Navegador: Abre la app en el navegador por defecto

Desarrollado por: Ing. Luis Martinez
Software Developer
Email: luismartinez.94mc@gmail.com
Version: 2.1.0
Fecha: 16 de Febrero 2026
Estado: Produccion
"""

import threading
import socket
import sys
import os
import webbrowser
import time

from server import app

WEBVIEW_AVAILABLE = False
try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    pass

APP_TITLE = "Sistema de Pagos - Consejo Nacional de Inversiones"
APP_WIDTH = 1400
APP_HEIGHT = 900


def get_free_port():
    """Encuentra un puerto libre para el servidor Flask."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def start_server(port):
    """Inicia el servidor Flask en un hilo separado."""
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)


def run_desktop_mode(port):
    """Ejecuta la app en una ventana nativa con PyWebView."""
    url = f'http://127.0.0.1:{port}'
    time.sleep(1)

    window_config = {
        'title': APP_TITLE,
        'url': url,
        'width': APP_WIDTH,
        'height': APP_HEIGHT,
        'resizable': True,
        'fullscreen': False,
        'min_size': (1200, 700),
        'background_color': '#f1f5f9',
        'text_select': True,
        'confirm_close': True
    }

    webview.create_window(**window_config)
    webview.start(debug=False)


def run_browser_mode(port):
    """Ejecuta la app en el navegador por defecto."""
    url = f'http://127.0.0.1:{port}'
    time.sleep(1)

    print(f"\n{'='*55}")
    print(f"  Sistema de Pagos CNI v2.1.0")
    print(f"  Consejo Nacional de Inversiones")
    print(f"{'='*55}")
    print(f"\n  Aplicacion ejecutandose en: {url}")
    print(f"  Abriendo navegador...")
    print(f"\n  Para cerrar: Presione Ctrl+C en esta ventana")
    print(f"{'='*55}\n")

    webbrowser.open(url)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Cerrando aplicacion...")
        sys.exit(0)


def main():
    """Funcion principal de la aplicacion."""
    port = get_free_port()

    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()

    if WEBVIEW_AVAILABLE:
        try:
            run_desktop_mode(port)
        except Exception as e:
            print(f"Error con PyWebView: {e}")
            print("Cambiando a modo navegador...")
            run_browser_mode(port)
    else:
        run_browser_mode(port)


if __name__ == '__main__':
    main()

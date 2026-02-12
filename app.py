#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Pagos CNI - Aplicación de Escritorio
Consejo Nacional de Inversiones - Honduras

Aplicación de escritorio para gestión de recursos humanos y nómina.

Desarrollado por: Ing. Luis Martínez
Software Developer
Email: luismartinez.94mc@gmail.com
Versión: 2.0.0
Fecha: 11 de Febrero 2026
Estado: Producción
"""

import webview
import threading
import socket
import sys
import os
from server import app

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

def main():
    """Función principal de la aplicación."""
    # Encontrar puerto libre
    port = get_free_port()
    url = f'http://127.0.0.1:{port}'
    
    # Iniciar servidor Flask en hilo separado
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()
    
    # Esperar a que el servidor esté listo
    import time
    time.sleep(1)
    
    # Configurar ventana
    window_config = {
        'title': 'Sistema de Pagos - Consejo Nacional de Inversiones',
        'url': url,
        'width': 1400,
        'height': 900,
        'resizable': True,
        'fullscreen': False,
        'min_size': (1200, 700),
        'background_color': '#f1f5f9',
        'text_select': True,
        'confirm_close': True
    }
    
    # Crear y mostrar ventana
    try:
        webview.create_window(**window_config)
        webview.start(debug=False)
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

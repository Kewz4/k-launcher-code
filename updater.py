import requests
import re
import logging
import os
import sys
import subprocess
import time
import json
import threading

# Configurar un logger simple para el módulo de actualización
log = logging.getLogger(__name__)

class Updater:
    """
    Maneja la comprobación, descarga y aplicación de actualizaciones para el launcher.
    """
    def __init__(self, repo_owner_repo, current_version, progress_callback=None, log_callback=None):
        """
        Inicializa el Updater.
        :param repo_owner_repo: String en formato 'usuario/repositorio'.
        :param current_version: La versión actual del launcher (ej: '1.0').
        :param progress_callback: Función opcional para reportar progreso (message, percentage).
        :param log_callback: Función opcional para enviar logs a la UI.
        """
        self.github_repo = repo_owner_repo
        self.current_version = current_version
        self.api_url = f"https://api.github.com/repos/{self.github_repo}/releases/tags/Update"
        self.latest_release_data = None
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cancel_event = threading.Event()

    def _log(self, message):
        """Envía un mensaje de log al logger y opcionalmente a la UI."""
        log.info(message)
        if self.log_callback:
            self.log_callback(message)

    def _update_progress(self, message, percentage=None):
        """Envía una actualización de progreso a la UI."""
        if self.progress_callback:
            self.progress_callback(message, percentage)

    def check_for_updates(self):
        """
        Comprueba si hay una nueva versión del launcher disponible en GitHub.

        Returns:
            dict: Un diccionario con el resultado.
        """
        self._log(f"Buscando actualizaciones en {self.api_url}")
        try:
            current_version_float = float(self.current_version)
        except (ValueError, TypeError):
            return {'error': f"Formato de versión actual inválido: '{self.current_version}'"}

        try:
            response = requests.get(self.api_url, timeout=15)
            response.raise_for_status()
            self.latest_release_data = response.json()

            assets = self.latest_release_data.get("assets", [])
            if not assets:
                return {'error': "La última release no tiene archivos adjuntos (assets)."}

            latest_version_from_asset = 0.0
            version_pattern = re.compile(r"Kewz\.Launcher\.v(\d+(\.\d+)?)\.exe")

            for asset in assets:
                asset_name = asset.get("name", "")
                match = version_pattern.search(asset_name)
                if match:
                    version_str = match.group(1)
                    try:
                        version_float = float(version_str)
                        if version_float > latest_version_from_asset:
                            latest_version_from_asset = version_float
                    except ValueError:
                        self._log(f"Se encontró una versión con formato no válido '{version_str}' en el asset '{asset_name}'.")

            if latest_version_from_asset == 0.0:
                return {'error': "No se encontró un asset con un nombre de versión válido (ej: 'Kewz.Launcher.v1.1.exe')."}

            self._log(f"Versión actual: {current_version_float}, Versión más reciente encontrada: {latest_version_from_asset}")

            if latest_version_from_asset > current_version_float:
                notes = self.latest_release_data.get("body", "No hay notas para esta versión.").strip()
                return {
                    'update_available': True,
                    'version': str(latest_version_from_asset),
                    'notes': notes,
                    'release_data': self.latest_release_data
                }
            else:
                return {'update_available': False}

        except requests.RequestException as e:
            self._log(f"Error de red buscando actualizaciones: {e}")
            return {'error': f"Error de red: {e}"}
        except (ValueError, TypeError) as e:
            self._log(f"Error parseando la versión desde el nombre del asset: {e}")
            return {'error': "No se pudo parsear la versión desde los assets de la release."}
        except Exception as e:
            log.exception("Ocurrió un error inesperado durante la comprobación de actualizaciones.")
            return {'error': f"Ocurrió un error inesperado: {e}"}

    def _download_file(self, url, destination_path):
        """Descarga un archivo y reporta el progreso."""
        self._log(f"Iniciando descarga: {url} -> {destination_path}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            with requests.get(url, stream=True, timeout=60, headers=headers, allow_redirects=True) as resp:
                resp.raise_for_status()
                total_bytes = int(resp.headers.get('content-length', 0))
                chunk_size = 8192
                downloaded = 0

                with open(destination_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=chunk_size):
                        if self.cancel_event.is_set():
                            raise InterruptedError("Descarga cancelada.")
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                        if total_bytes > 0:
                            percentage = downloaded / total_bytes
                            # Escalar progreso de descarga entre 20% y 90% del total de la UI
                            ui_progress = 20 + (percentage * 70)
                            self._update_progress(f"Descargando... ({downloaded/1024/1024:.1f}/{total_bytes/1024/1024:.1f} MB)", ui_progress)

            self._log("Descarga completa.")
            self._update_progress("Descarga completa", 90)

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error de red durante la descarga: {e}")
        except InterruptedError:
            raise
        except Exception as e:
            raise IOError(f"Error escribiendo el archivo descargado: {e}")


    def download_and_apply_update(self, release_data, on_finish_callback):
        """
        Descarga el nuevo ejecutable y crea el script .bat para reemplazarlo.

        :param release_data: El diccionario de datos de la release de GitHub.
        :param on_finish_callback: Función a llamar cuando el proceso termina (éxito o error).
        """
        try:
            latest_version_str = "0.0"
            version_pattern = re.compile(r"Kewz\.Launcher\.v(\d+(\.\d+)?)\.exe")
            for asset in release_data.get("assets", []):
                match = version_pattern.search(asset.get("name", ""))
                if match:
                    version_str = match.group(1)
                    # Tomamos la primera coincidencia válida
                    break

            if version_str == "0.0":
                 raise ValueError("No se pudo determinar la versión desde los assets.")

            self._update_progress(f"Descargando v{version_str}...", 20)

            asset_name_pattern = f"Kewz.Launcher.v{version_str}.exe"
            asset_url = next(
                (asset.get("browser_download_url") for asset in release_data.get("assets", [])
                 if asset.get("name") == asset_name_pattern), None
            )

            if not asset_url:
                raise FileNotFoundError(f"No se encontró el asset '{asset_name_pattern}' en el release.")

            if not getattr(sys, 'frozen', False):
                 raise RuntimeError("La auto-actualización solo funciona en el ejecutable compilado (.exe).")

            current_exe_path = os.path.realpath(sys.executable)
            base_dir = os.path.dirname(current_exe_path)
            new_exe_path = os.path.join(base_dir, "Kewz.Launcher.new.exe")

            self._download_file(asset_url, new_exe_path)

            self._update_progress("Creando script de actualización...", 95)
            updater_script_path = os.path.join(base_dir, "updater.bat")
            final_exe_name = os.path.basename(current_exe_path)

            script_content = f"""
@echo off
echo Cerrando el launcher para actualizar...
taskkill /F /IM "{final_exe_name}" > nul
timeout /t 3 /nobreak > nul

:retry
echo Intentando reemplazar el archivo...
move /Y "{new_exe_path}" "{current_exe_path}"
if exist "{new_exe_path}" (
    echo El reemplazo fallo, reintentando en 2 segundos...
    timeout /t 2 /nobreak > nul
    goto :retry
)

echo Actualizacion completa. Reiniciando el launcher...
start "" "{current_exe_path}"
del "%~f0"
"""
            with open(updater_script_path, "w", encoding='utf-8') as f:
                f.write(script_content)

            self._update_progress("Reiniciando para actualizar...", 100)

            # Lanzar el script y terminar
            subprocess.Popen(f'"{updater_script_path}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

            on_finish_callback(True, None) # Éxito

        except Exception as e:
            self._log(f"Error durante la descarga o aplicación: {e}")
            on_finish_callback(False, str(e))

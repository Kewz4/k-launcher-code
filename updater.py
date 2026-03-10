import requests
import re
import logging
import os
import sys
import subprocess
import time
import json
import threading

log = logging.getLogger(__name__)

LAUNCHER_VERSION_URL = "https://gitlab.com/Kewz4/kewz-cobblemon/-/raw/main/launcher_version.txt"

class Updater:
    """Handles checking, downloading and applying launcher updates."""
    def __init__(self, repo_owner_repo, current_version, progress_callback=None, log_callback=None):
        """
        :param repo_owner_repo: String in 'owner/repo' format.
        :param current_version: Current launcher version (e.g. '1.0').
        :param progress_callback: Optional function to report progress (message, percentage).
        :param log_callback: Optional function to send logs to the UI.
        """
        self.github_repo = repo_owner_repo
        self.current_version = current_version
        # (MODIFICADO) Ya no usamos hardcode "Update". Se construye dinámicamente en check_for_updates.
        self.base_api_url = f"https://api.github.com/repos/{self.github_repo}/releases"
        self.latest_release_data = None
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cancel_event = threading.Event()

    def _log(self, message):
        log.info(message)
        if self.log_callback:
            self.log_callback(message)

    def _update_progress(self, message, percentage=None):
        if self.progress_callback:
            self.progress_callback(message, percentage)

    def check_for_updates(self):
        """
        Checks if a new launcher version is available.
        Queries the unified GitLab repo for the latest version, then fetches the asset from GitHub.

        Returns:
            dict: Result dictionary.
        """
        self._log(f"Checking version at {LAUNCHER_VERSION_URL}")
        try:
            current_version_float = float(self.current_version)
        except (ValueError, TypeError):
            return {'error': f"Invalid current version format: '{self.current_version}'"}

        # 1. Fetch latest version from unified GitLab repo
        try:
            v_response = requests.get(LAUNCHER_VERSION_URL, timeout=10)
            v_response.raise_for_status()
            remote_version_str = v_response.text.strip()
            remote_version_float = float(remote_version_str)
        except Exception as e:
            self._log(f"Error fetching remote version from GitLab: {e}")
            return {'error': f"Error fetching remote version: {e}"}

        self._log(f"Local version: {current_version_float} | Remote version: {remote_version_float}")

        if remote_version_float <= current_version_float:
            return {'update_available': False}

        # 2. Update available — find GitHub release asset
        self._log(f"Update detected. Looking for release v{remote_version_str} on GitHub...")

        target_asset_name = f"Kewz.Launcher.v{remote_version_str}.exe"
        full_release_data = None

        try:
            # Strategy 1: exact tag (e.g. "1.0")
            try:
                tag_url = f"{self.base_api_url}/tags/{remote_version_str}"
                self._log(f"Trying release by tag: {tag_url}")
                response = requests.get(tag_url, timeout=15)
                if response.status_code == 200:
                    self._log("Release found by exact tag.")
                    full_release_data = response.json()
                elif response.status_code == 404:
                    self._log(f"Tag '{remote_version_str}' not found. Trying 'latest'...")
                else:
                    response.raise_for_status()
            except Exception as e:
                self._log(f"Warning: tag lookup failed: {e}")

            # Strategy 2: fallback to 'latest' release
            if not full_release_data:
                try:
                    latest_url = f"{self.base_api_url}/latest"
                    self._log(f"Trying 'latest' release: {latest_url}")
                    response = requests.get(latest_url, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        temp_assets = data.get("assets", [])
                        if any(a.get("name") == target_asset_name for a in temp_assets):
                            self._log(f"'latest' release contains '{target_asset_name}'. Using it.")
                            full_release_data = data
                        else:
                            self._log(f"'latest' release ({data.get('tag_name')}) does NOT contain '{target_asset_name}'.")
                except Exception as e:
                    self._log(f"Warning: latest lookup failed: {e}")

            if not full_release_data:
                error_msg = f"Could not find a valid GitHub release for version {remote_version_str}."
                self._log(error_msg)
                return {'error': error_msg}

            # Find the asset in the release
            assets = full_release_data.get("assets", [])
            found_asset = None
            available_assets = [a.get("name") for a in assets]
            self._log(f"Available assets in release: {available_assets}")

            for asset in assets:
                if asset.get("name") == target_asset_name:
                    found_asset = asset
                    break

            if not found_asset:
                error_msg = f"Release exists but does not contain '{target_asset_name}'. (Available: {available_assets})"
                self._log(error_msg)
                return {'error': error_msg}

            filtered_release_data = full_release_data.copy()
            filtered_release_data['assets'] = [found_asset]
            self.latest_release_data = filtered_release_data

            notes = full_release_data.get("body", "No release notes.").strip()

            return {
                'update_available': True,
                'version': remote_version_str,
                'notes': notes,
                'release_data': filtered_release_data
            }
        except Exception as e:
            log.exception("Unexpected error during update check.")
            return {'error': f"Unexpected error: {e}"}

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
            version_str = None
            asset_to_download = None
            version_pattern = re.compile(r"Kewz\.Launcher\.v(\d+(\.\d+)?)\.exe")
            for asset in release_data.get("assets", []):
                match = version_pattern.search(asset.get("name", ""))
                if match:
                    version_str = match.group(1)
                    asset_to_download = asset
                    break # Found the first valid asset, stop here

            if not version_str or not asset_to_download:
                 raise ValueError("No se pudo determinar la versión o el asset de descarga desde la release.")

            self._update_progress(f"Descargando v{version_str}...", 20)

            asset_url = asset_to_download.get("browser_download_url")
            if not asset_url:
                raise FileNotFoundError(f"No se encontró la URL de descarga para el asset.")


            if not getattr(sys, 'frozen', False):
                 raise RuntimeError("La auto-actualización solo funciona en el ejecutable compilado (.exe).")

            current_exe_path = os.path.realpath(sys.executable)
            base_dir = os.path.dirname(current_exe_path)
            new_exe_path = os.path.join(base_dir, "Kewz.Launcher.new.exe")

            self._download_file(asset_url, new_exe_path)

            self._update_progress("Creando script de actualización...", 95)
            updater_script_path = os.path.join(base_dir, "updater.bat")
            final_exe_name = os.path.basename(current_exe_path)

            script_content = f'''
@echo off
chcp 65001 > nul
cd /d "%~dp0"

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

echo Actualizacion completa. Escribiendo nuevo archivo de version...
echo {version_str}>"launcher_version.txt"

echo Reiniciando el launcher con flag post-update...
start "" "{current_exe_path}" --post-update

echo Limpiando...
del "%~f0"
'''
            with open(updater_script_path, "w", encoding='utf-8') as f:
                f.write(script_content)

            self._update_progress("Reiniciando para actualizar...", 100)

            # Lanzar el script y terminar
            # (CORREGIDO) Limpiar variables de entorno que puedan contaminar el nuevo proceso (PYTHONPATH, etc.)
            env = os.environ.copy()
            for key in ['PYTHONPATH', 'PYTHONHOME', 'LD_LIBRARY_PATH']:
                env.pop(key, None)

            subprocess.Popen(f'"{updater_script_path}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW, env=env)

            on_finish_callback(True, None) # Éxito

        except Exception as e:
            self._log(f"Error durante la descarga o aplicación: {e}")
            on_finish_callback(False, str(e))

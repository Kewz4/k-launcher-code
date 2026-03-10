import os
import sys
import tempfile

# (NUEVO) Solución para PyInstaller: Añadir la carpeta temporal al path
if getattr(sys, 'frozen', False):
    # Limpieza AGRESIVA de sys.path para evitar cargar librerías de versiones anteriores (v1.5 -> v1.6)
    try:
        temp_base = tempfile.gettempdir().lower()
        my_meipass = sys._MEIPASS.lower()

        # Filtrar sys.path: Eliminar cualquier ruta en TEMP que no sea la nuestra
        new_sys_path = []
        for p in sys.path:
            p_lower = p.lower()
            if p_lower.startswith(temp_base):
                if p_lower.startswith(my_meipass):
                    new_sys_path.append(p)
                # else: Ignorar (basura de v1.5)
            else:
                new_sys_path.append(p)

        sys.path = new_sys_path
    except Exception as e:
        print(f"Advertencia limpiando sys.path: {e}")

    # Asegurar que nuestra carpeta temporal esté PRIMERO
    if sys._MEIPASS not in sys.path:
        sys.path.insert(0, sys._MEIPASS)
    elif sys.path[0] != sys._MEIPASS:
        sys.path.remove(sys._MEIPASS)
        sys.path.insert(0, sys._MEIPASS)

import threading
import time
import zipfile
import requests
import shutil
import re
import platform
import json
import subprocess  # Para lanzar Prism y Winget
import psutil      # Para terminar procesos
import webview     # Necesitarás: pip install pywebview requests
try:
    from music_player import MusicLibrary
except ImportError:
    print("ERROR CRÍTICO: No se pudo encontrar el archivo 'music_player.py'.")
    print("Asegúrate de que 'music_player.py' esté en la misma carpeta.")
    sys.exit(1)

# (NUEVO) Importar el módulo de actualización
try:
    from updater import Updater
except ImportError:
    print("ERROR CRÍTICO: No se pudo encontrar el archivo 'updater.py'.")
    print("Asegúrate de que 'updater.py' esté en la misma carpeta.")
    sys.exit(1)


# (ELIMINADO) --- LÓGICA DE CARGA DE ARCHIVOS LOCALES ---

# (NUEVO) Importar el HTML desde el archivo separado
try:
    from launcher_ui import HTML_CONTENT
except ImportError:
    print("ERROR CRÍTICO: No se pudo encontrar el archivo 'launcher_ui.py'.")
    print("Asegúrate de que ambos archivos (launcher_main.py y launcher_ui.py) estén en la misma carpeta.")
    sys.exit(1)
except AttributeError:
    print("ERROR CRÍTICO: Parece que 'launcher_ui.py' no define la variable 'HTML_CONTENT'.")
    print("Asegúrate de que el archivo 'launcher_ui.py' tenga la estructura correcta.")
    sys.exit(1)


# (NUEVO) Importar pywin32 si está disponible (solo para Windows)
IS_WINDOWS = platform.system() == "Windows"
try:
    if IS_WINDOWS:
        import win32gui
        import win32con
        import ctypes # (NUEVO) Necesario para la comprobación de administrador
        print("pywin32 y ctypes importados exitosamente.")
    else:
        win32gui = None
        win32con = None
        ctypes = None
        print("Plataforma no es Windows, pywin32 y ctypes no serán usados.")
except ImportError:
    print("ADVERTENCIA: pywin32 o ctypes no encontrado (pip install pywin32). Se usará el método on_top estándar (menos robusto).")
    win32gui = None
    win32con = None
    ctypes = None
    IS_WINDOWS = False # Desactivar lógica de Windows si no se pudo importar


# --- Lógica de la Aplicación (Backend de Python) ---

# --- Unified Repository (all assets in one place) ---
UNIFIED_REPO_RAW_URL = "https://raw.githubusercontent.com/Kewz4/kewz-cobblemon/main"
REPO_ZIP_URL = "https://github.com/Kewz4/kewz-cobblemon/archive/refs/heads/main.zip"
GITHUB_RAW_URL = UNIFIED_REPO_RAW_URL  # Used by music player
MUSIC_DATA_URL = UNIFIED_REPO_RAW_URL  # Music library base URL
VERSION_URL = f"{UNIFIED_REPO_RAW_URL}/version.txt"
RESOURCE_PACK_OPTIONS_URL = f"{UNIFIED_REPO_RAW_URL}/resourcepacksoptions.txt"
LOCAL_OPTIONS_BACKUP_FILENAME = "options_backup.txt"

# --- Prism Launcher ---
PRISM_DEFAULT_PATHS_WINDOWS = [
    os.path.expandvars(r"%LocalAppData%\Programs\PrismLauncher\prismlauncher.exe"),
    os.path.expandvars(r"%LocalAppData%\Programs\Prism Launcher\prismlauncher.exe"),
    os.path.expandvars(r"%LocalAppData%\PrismLauncher\prismlauncher.exe"),
    r"C:\Program Files\Prism Launcher\prismlauncher.exe",
    r"C:\Program Files\Prism Launcher\PrismLauncher.exe",
    r"C:\Program Files\PrismLauncher\prismlauncher.exe",
    r"C:\Program Files\PrismLauncher\PrismLauncher.exe",
    r"C:\Program Files (x86)\Prism Launcher\prismlauncher.exe",
    r"C:\Program Files (x86)\Prism Launcher\PrismLauncher.exe",
    r"C:\Program Files (x86)\PrismLauncher\prismlauncher.exe",
]
MODPACK_INSTANCE_NAME = "Kewz's Cobblemon"
# URL of the text file that contains the modpack download link (from GoFile)
MODPACK_URL_SOURCE = f"{UNIFIED_REPO_RAW_URL}/modpack-url.txt"
# Fallback URL if dynamic fetch fails
MODPACK_INSTALL_ZIP_URL = ""  # Set via modpack-url.txt (GoFile link)
PRISM_PORTABLE_URL = "https://github.com/PrismLauncher/PrismLauncher/releases/download/10.0.5/PrismLauncher-Windows-MinGW-w64-Portable-10.0.5.zip"

# --- Stable download directory for crash-resumable downloads ---
STABLE_DOWNLOAD_DIR = os.path.join(os.getcwd(), ".launcher_downloads")
DOWNLOAD_STATE_FILE = os.path.join(os.getcwd(), ".download_state.json")

# --- Background video definitions ---
# Host the pre-trimmed .mp4 files as assets on a GitHub Release and paste
# the direct download URLs here.  Each URL must return the raw video bytes
# (GitHub Release assets, R2, S3, etc. all work fine).
# NOTE: raw.githubusercontent.com does NOT work for Git LFS files — it serves
# the 134-byte LFS pointer text instead of the actual video.  Use GitHub Release
# asset URLs or another direct-download host.
def _get_video_dir():
    if getattr(sys, 'frozen', False):
        # Frozen exe: store in %APPDATA%\KewzLauncher\videos
        appdata = os.environ.get('APPDATA') or os.path.expanduser('~')
        return os.path.join(appdata, 'KewzLauncher', 'videos')
    # Dev: store next to the script
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')

VIDEO_DIR = _get_video_dir()
MIN_VIDEO_SIZE = 2_000_000   # 2 MB — any real background video will exceed this
LFS_POINTER_PREFIX = b'version https://git-lfs.github.com/spec/v1'

VIDEO_DEFINITIONS = [
    {"url": "https://raw.githubusercontent.com/Kewz4/kewz-cobblemon/main/bg/video_bg1_cob.mp4", "filename": "video_bg1_cob.mp4"},
    {"url": "https://raw.githubusercontent.com/Kewz4/kewz-cobblemon/main/bg/video_bg2_cob.mp4", "filename": "video_bg2_cob.mp4"},
    {"url": "https://raw.githubusercontent.com/Kewz4/kewz-cobblemon/main/bg/video_bg3_cob.mp4", "filename": "video_bg3_cob.mp4"},
]

# (NUEVO) Lógica para leer la versión del launcher dinámicamente
def get_current_launcher_version(default_version="1.0"):
    """Lee la versión desde 'launcher_version.txt', o devuelve la versión por defecto."""
    version_file = "launcher_version.txt"
    if os.path.exists(version_file):
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                if re.fullmatch(r'\d+(\.\d+)*', version):
                    print(f"Versión del launcher leída desde archivo: {version}")
                    return version
                else:
                    print(f"Advertencia: Contenido de '{version_file}' no es una versión válida: '{version}'. Usando por defecto.")
        except Exception as e:
            print(f"Advertencia: No se pudo leer '{version_file}': {e}. Usando por defecto.")

    print(f"Archivo '{version_file}' no encontrado. Usando versión por defecto: {default_version}")
    return default_version

# La versión del Launcher ahora se lee dinámicamente
LAUNCHER_VERSION = get_current_launcher_version()
GITHUB_REPO = "Kewz4/k-launcher-code" # Repositorio para la auto-actualización

# La línea que indica que el juego está listo
LOG_TRIGGER_LINE = "[ModernFix/]: Game took"


class ModpackLauncherAPI:
    """
    (Refactorizado)
    Clase que maneja la configuración, instalación, actualización y lanzamiento.
    """
    # Lista de palabras clave para ignorar en el log pass-through
    LOG_IGNORE_KEYWORDS = [
        "ForkJoinPool", "at java.base/java.util.concurrent", "at TRANSFORMER/",
        "[Worker-ResourceReload-", "Unable to load model:", "Missing textures in model",
        "Failed to load model", "com.google.gson.JsonParseException: Model loader",
        "[EMF/]", "[Entity Texture Features/]", "[Puzzles Lib/]",
        "[net.minecraft.client.sounds.SoundEngine/]: Missing sound for event:",
        "[net.minecraft.client.resources.model.ModelBakery/]", "[net.minecraft.client.resources.model.ModelManager/]",
        "[com.cerbon.beb.util.BEBConstants/]", "[Polytone/]", "[wiki.minecraft.heywiki.resource.WikiFamilyManager/]",
        "[ShoulderSurfing/]", "[snownee.jade.Jade/]", "[JamLib/]", "[Configured/]",
        "[CorgiLib/]", "[net.minecraft.server.LoggedPrintStream/]", "[Palladium/]",
        "[Tooltip Overhaul/]", "[XaeroPlus/]", "[xaero.hud.minimap.MinimapLogs/]",
        "[xaero.map.WorldMap/]", "[patchouli/]", "[com.teamabnormals.blueprint.core.Blueprint/]",
        "[Straw Golem/]"
    ]


    def __init__(self):
        self.window = None
        self.hwnd = None # Handle de la ventana (solo Windows)
        self.cancel_event = threading.Event()
        self.pause_event = threading.Event()   # When SET, download is paused
        self.game_ready_event = threading.Event()
        self.on_top_thread = None
        self.prism_exe_path = None
        self.instance_mc_path = None
        self.backup_dir = None
        self.added_files = []
        self.removed_files = [] # Tupla: ((rel_folder, item_name), backup_unique_name)
        self.changelog_processed_items = set()

        self.config_lock = threading.Lock()
        self.avg_launch_time_sec = 400.0
        self.music_library = None
        self.updater = Updater(
            repo_owner_repo=GITHUB_REPO,
            current_version=LAUNCHER_VERSION,
            progress_callback=self._update_updater_ui,
            log_callback=self._log
        )
        self.latest_release_data = None

        # (NUEVO) Estado para el hilo de tareas
        self.current_task_thread = None

        # (NUEVO) Atributos para el panel de depuración
        self.debug_mode = False # (MODIFICADO) Oculto por defecto
        self.close_trigger_status = "PENDING"
        self.prism_process = None # (NUEVO) Para rastrear el proceso de Prism

    def _update_updater_ui(self, message, progress=None):
        """(NUEVO) Envía actualizaciones a la UI del actualizador."""
        if self.window:
            safe_message_js = json.dumps(message)
            js_code = f"logToUpdaterConsole({safe_message_js});"
            if progress is not None:
                js_code += f" updateUpdaterProgress({progress});"
            self.window.evaluate_js(js_code)

    def _save_download_state(self, url, dest_path, task_type, extra=None):
        """Save download state to allow crash-recovery on next launch."""
        state = {
            "url": url,
            "dest_path": dest_path,
            "task_type": task_type,
            "extra": extra or {},
            "saved_at": time.time()
        }
        try:
            with open(DOWNLOAD_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f)
        except Exception as e:
            self._log(f"Warn: Could not save download state: {e}")

    def _clear_download_state(self):
        """Remove the download state file on successful completion."""
        try:
            if os.path.exists(DOWNLOAD_STATE_FILE):
                os.remove(DOWNLOAD_STATE_FILE)
        except Exception as e:
            self._log(f"Warn: Could not clear download state: {e}")

    def py_check_interrupted_download(self):
        """Check if a previous download was interrupted and can be resumed."""
        if not os.path.exists(DOWNLOAD_STATE_FILE):
            return {"found": False}
        try:
            with open(DOWNLOAD_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            dest_path = state.get("dest_path", "")
            part_path = dest_path + ".part"
            bytes_downloaded = os.path.getsize(part_path) if os.path.exists(part_path) else (
                os.path.getsize(dest_path) if os.path.exists(dest_path) else 0
            )
            if bytes_downloaded == 0:
                # Nothing to resume
                self._clear_download_state()
                return {"found": False}
            return {
                "found": True,
                "task_type": state.get("task_type", "unknown"),
                "filename": os.path.basename(dest_path),
                "bytes_downloaded": bytes_downloaded,
                "url": state.get("url", ""),
                "dest_path": dest_path,
                "extra": state.get("extra", {})
            }
        except Exception as e:
            self._log(f"Warn: Could not read download state: {e}")
            return {"found": False}

    def py_discard_interrupted_download(self):
        """Discard a previously interrupted download (delete .part file and state)."""
        try:
            if os.path.exists(DOWNLOAD_STATE_FILE):
                with open(DOWNLOAD_STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                part_path = state.get("dest_path", "") + ".part"
                if os.path.exists(part_path):
                    os.remove(part_path)
                full_path = state.get("dest_path", "")
                if os.path.exists(full_path):
                    os.remove(full_path)
            self._clear_download_state()
            return True
        except Exception as e:
            self._log(f"Error discarding download: {e}")
            return False

    # --- Background Video Server ---

    def _start_video_server(self):
        """Start a simple HTTP server to serve VIDEO_DIR on a random localhost port."""
        if getattr(self, '_video_server_port', None):
            return self._video_server_port
        import http.server
        import socketserver

        os.makedirs(VIDEO_DIR, exist_ok=True)

        class _Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=VIDEO_DIR, **kwargs)
            def log_message(self, format, *args):
                pass  # Silence access logs

        # Bind to port 0 to get a free port
        server = socketserver.TCPServer(("127.0.0.1", 0), _Handler)
        port = server.server_address[1]
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        self._video_server = server
        self._video_server_port = port
        self._log(f"Video HTTP server started on port {port}")
        return port

    def py_ensure_background_videos(self):
        """
        Called on startup. For each video:
          - If already cached, immediately fires onBgVideoReady(url) in JS.
          - Otherwise: downloads the source file, compresses it to 1080p H.264 CRF 28
            using the ffmpeg binary bundled inside imageio-ffmpeg (no install needed),
            caches the small result, then fires onBgVideoReady(url).
        All runs in a background thread so it never blocks the UI.
        All evaluate_js calls are guarded with typeof checks so they are safe to call
        before the JS page has fully initialised.
        """
        import urllib.request
        import subprocess
        import re as _re

        def _resolve_lfs_url(pointer_bytes, original_url):
            """
            Parse a Git LFS pointer and call the LFS batch API to get the real
            download URL.  Works for any public GitHub repo.
            """
            text = pointer_bytes.decode('utf-8', errors='replace')
            oid_m  = _re.search(r'oid sha256:([0-9a-f]{64})', text)
            size_m = _re.search(r'size (\d+)', text)
            if not oid_m or not size_m:
                raise RuntimeError("Could not parse Git LFS pointer")
            oid  = oid_m.group(1)
            size = int(size_m.group(1))

            # Extract owner/repo from raw.githubusercontent.com URL
            gh_m = _re.match(
                r'https?://raw\.githubusercontent\.com/([^/]+)/([^/]+)/', original_url
            )
            if not gh_m:
                raise RuntimeError("URL is not a raw.githubusercontent.com URL — cannot resolve LFS")
            owner, repo = gh_m.group(1), gh_m.group(2)

            import json as _json
            lfs_api = f"https://github.com/{owner}/{repo}.git/info/lfs/objects/batch"
            payload = _json.dumps({
                "operation": "download",
                "transfers": ["basic"],
                "objects": [{"oid": oid, "size": size}],
            }).encode()
            req = urllib.request.Request(
                lfs_api, data=payload,
                headers={
                    "Content-Type": "application/vnd.git-lfs+json",
                    "Accept":       "application/vnd.git-lfs+json",
                    "User-Agent":   "KewzLauncher/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = _json.loads(resp.read())
            return data['objects'][0]['actions']['download']['href']

        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            ffmpeg_exe = None

        os.makedirs(VIDEO_DIR, exist_ok=True)
        port = self._start_video_server()
        video_total = len(VIDEO_DEFINITIONS)
        CHUNK = 1024 * 256  # 256 KB read chunks

        def _js(expr):
            """Evaluate JS, ignoring errors if the window/page isn't ready yet."""
            try:
                if self.window:
                    self.window.evaluate_js(expr)
            except Exception:
                pass

        def _compress(src, dst):
            """Re-encode to 1080p H.264 CRF 28, no audio. Returns True on success."""
            try:
                result = subprocess.run(
                    [
                        ffmpeg_exe, "-y", "-i", src,
                        "-c:v", "libx264", "-crf", "28", "-preset", "fast",
                        "-vf", "scale='min(1920,iw)':-2",
                        "-movflags", "+faststart", "-an",
                        dst,
                    ],
                    capture_output=True, timeout=600,
                )
                return result.returncode == 0 and os.path.getsize(dst) > 0
            except Exception as e:
                self._log(f"Compression error: {e}")
                return False

        def _process_video(video_idx, vdef):
            """Download + optionally compress one video, then fire onBgVideoReady."""
            out_path = os.path.join(VIDEO_DIR, vdef["filename"])
            serve_url = f"http://127.0.0.1:{port}/{vdef['filename']}"

            # Already cached with a plausible size — notify immediately.
            # If the cached file is suspiciously small (e.g. a stale LFS pointer),
            # delete it and re-download.
            if os.path.exists(out_path):
                if os.path.getsize(out_path) >= MIN_VIDEO_SIZE:
                    _js(f'typeof onBgVideoReady==="function"&&onBgVideoReady({json.dumps(serve_url)})')
                    return
                else:
                    self._log(f"Cached file {vdef['filename']} is too small ({os.path.getsize(out_path)} bytes) — deleting and re-downloading")
                    try:
                        os.remove(out_path)
                    except Exception:
                        pass

            src_url = vdef["url"]
            if src_url.startswith("PLACEHOLDER"):
                self._log(f"Skipping {vdef['filename']}: URL not configured")
                _js(f'typeof onBgVideoError==="function"&&onBgVideoError({json.dumps("URL not configured for " + vdef["filename"])})')
                return

            tmp_path = out_path + ".tmp"
            try:
                import time as _time

                def _dl_loop(response, file_obj, total_b, on_tick):
                    """Read chunks, call on_tick(downloaded, speed_mbps, eta_s, pct) periodically."""
                    downloaded = 0
                    t_start = _time.monotonic()
                    t_last_tick = t_start
                    last_pct = -1
                    while True:
                        chunk = response.read(CHUNK)
                        if not chunk:
                            break
                        file_obj.write(chunk)
                        downloaded += len(chunk)
                        now = _time.monotonic()
                        elapsed = max(now - t_start, 0.001)
                        speed = downloaded / elapsed / 1024 / 1024  # MB/s
                        pct = int(downloaded / total_b * 100) if total_b > 0 else 0
                        eta_s = int((total_b - downloaded) / (downloaded / elapsed)) if total_b > 0 and downloaded > 0 else 0
                        if pct - last_pct >= 1 or now - t_last_tick >= 0.5:
                            last_pct = pct
                            t_last_tick = now
                            on_tick(downloaded, speed, eta_s, pct)

                self._log(f"Downloading background video: {vdef['filename']}")
                req = urllib.request.Request(src_url, headers={"User-Agent": "KewzLauncher/1.0"})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    total_b = int(resp.headers.get("Content-Length") or 0)
                    total_mb_str = f"{total_b / 1024 / 1024:.1f} MB" if total_b else "? MB"

                    def _on_tick(dl, spd, eta, pct):
                        dl_mb = dl / 1024 / 1024
                        if total_b:
                            eta_str = f"{eta // 60}m {eta % 60}s" if eta >= 60 else f"{eta}s"
                            detail = f"{dl_mb:.1f} / {total_mb_str}  •  {spd:.2f} MB/s  •  ETA {eta_str}"
                        else:
                            detail = f"{dl_mb:.1f} MB  •  {spd:.2f} MB/s"
                        _js(
                            f'typeof onBgVideoStatus==="function"&&'
                            f'onBgVideoStatus({video_idx},{video_total},'
                            f'{json.dumps("Downloading video")},{json.dumps(detail)})'
                        )
                        _js(f'typeof onBgVideoProgress==="function"&&onBgVideoProgress({video_idx},{video_total},{pct})')

                    with open(tmp_path, "wb") as f:
                        _dl_loop(resp, f, total_b, _on_tick)

                if not os.path.exists(tmp_path):
                    raise RuntimeError("Download produced no file")

                dl_size = os.path.getsize(tmp_path)
                if dl_size < MIN_VIDEO_SIZE:
                    with open(tmp_path, 'rb') as _f:
                        header = _f.read(256)
                    if header.lstrip().startswith(LFS_POINTER_PREFIX):
                        # Transparently resolve the LFS pointer → real CDN URL and re-download
                        def _lfs_status(stage, detail=""):
                            self._log(f"[LFS] {stage}{': ' + detail if detail else ''}")
                            _js(
                                f'typeof onBgVideoStatus==="function"&&'
                                f'onBgVideoStatus({video_idx},{video_total},'
                                f'{json.dumps(stage)},{json.dumps(detail)})'
                            )

                        _lfs_status("Detected Git LFS pointer", vdef['filename'])
                        with open(tmp_path, 'rb') as _pf:
                            pointer_bytes = _pf.read()
                        os.remove(tmp_path)

                        _lfs_status("Contacting LFS batch API", "getting real download URL...")
                        lfs_url = _resolve_lfs_url(pointer_bytes, src_url)
                        _lfs_status("LFS URL resolved", "starting download")

                        lfs_req = urllib.request.Request(lfs_url, headers={"User-Agent": "KewzLauncher/1.0"})
                        with urllib.request.urlopen(lfs_req, timeout=300) as lfs_resp:
                            total_b = int(lfs_resp.headers.get("Content-Length") or 0)
                            total_mb_str = f"{total_b / 1024 / 1024:.1f} MB" if total_b else "? MB"
                            _lfs_status("Downloading LFS content", total_mb_str)

                            def _on_lfs_tick(dl, spd, eta, pct):
                                dl_mb = dl / 1024 / 1024
                                if total_b:
                                    eta_str = f"{eta // 60}m {eta % 60}s" if eta >= 60 else f"{eta}s"
                                    detail = f"{dl_mb:.1f} / {total_mb_str}  •  {spd:.2f} MB/s  •  ETA {eta_str}"
                                else:
                                    detail = f"{dl_mb:.1f} MB  •  {spd:.2f} MB/s"
                                _lfs_status("Downloading LFS content", detail)
                                _js(f'typeof onBgVideoProgress==="function"&&onBgVideoProgress({video_idx},{video_total},{pct})')

                            with open(tmp_path, "wb") as f:
                                _dl_loop(lfs_resp, f, total_b, _on_lfs_tick)
                        dl_size = os.path.getsize(tmp_path)
                        if dl_size < MIN_VIDEO_SIZE:
                            raise RuntimeError(f"LFS download also too small ({dl_size} bytes)")
                        _lfs_status("LFS download complete", f"{dl_size / 1024 / 1024:.1f} MB received")
                    else:
                        raise RuntimeError(f"Download too small ({dl_size} bytes) — expected a real video file")

                # Compress using bundled ffmpeg; fall back to raw file if unavailable
                if ffmpeg_exe:
                    self._log(f"Compressing {vdef['filename']}...")
                    comp_tmp = out_path + ".comp.tmp"
                    if _compress(tmp_path, comp_tmp):
                        before_mb = os.path.getsize(tmp_path) / 1024 / 1024
                        after_mb  = os.path.getsize(comp_tmp)  / 1024 / 1024
                        self._log(f"Compressed {vdef['filename']}: {before_mb:.0f}MB -> {after_mb:.0f}MB")
                        os.remove(tmp_path)
                        os.replace(comp_tmp, out_path)
                    else:
                        if os.path.exists(comp_tmp):
                            os.remove(comp_tmp)
                        os.replace(tmp_path, out_path)
                else:
                    os.replace(tmp_path, out_path)

                self._log(f"Background video ready: {vdef['filename']}")
                _js(f'typeof onBgVideoReady==="function"&&onBgVideoReady({json.dumps(serve_url)})')

            except Exception as e:
                self._log(f"Error downloading {vdef['filename']}: {e}")
                _js(f'typeof onBgVideoError==="function"&&onBgVideoError({json.dumps(str(e))})')
                for p in (tmp_path, out_path + ".comp.tmp"):
                    if os.path.exists(p):
                        try:
                            os.remove(p)
                        except Exception:
                            pass

        def _task():
            if not VIDEO_DEFINITIONS:
                return
            # Process the first video synchronously so the main screen can show ASAP
            _process_video(1, VIDEO_DEFINITIONS[0])
            # Stream remaining videos in the background while the first one plays
            for video_idx, vdef in enumerate(VIDEO_DEFINITIONS[1:], start=2):
                _process_video(video_idx, vdef)

        t = threading.Thread(target=_task, daemon=True)
        t.start()
        return True

    def py_start_update_check(self):
        """(REFACTORIZADO) Inicia la comprobación de actualizaciones usando el módulo Updater."""
        if not getattr(sys, 'frozen', False):
            self._log("Omitiendo búsqueda de actualizaciones en entorno de desarrollo.")
            if self.window:
                self.window.evaluate_js("startMainApp();")
            return

        def check_thread_task():
            try:
                self._update_updater_ui("Buscando actualizaciones del launcher...", 5)
                result = self.updater.check_for_updates()

                if 'error' in result:
                    error_message = f"Error comprobando actualizaciones: {result['error']}"
                    self._update_updater_ui(error_message)
                    if self.window:
                        self.window.evaluate_js(f'onUpdateError({json.dumps(error_message)})')
                elif result.get('update_available'):
                    self.latest_release_data = result['release_data']
                    details = {"version": result['version'], "notes": result['notes']}
                    if self.window:
                        self.window.evaluate_js(f'onUpdateCheckComplete(true, {json.dumps(json.dumps(details))})')
                else:
                    self._update_updater_ui("El launcher ya está actualizado.", 100)
                    if self.window:
                        self.window.evaluate_js("onUpdateCheckComplete(false, null);")
            except Exception as e:
                self._log(f"Update check crashed: {e}")
                error_message = f"Update check failed: {e}"
                if self.window:
                    self.window.evaluate_js(f'onUpdateError({json.dumps(error_message)})')

        update_thread = threading.Thread(target=check_thread_task, daemon=True)
        update_thread.start()

    def py_download_and_apply_update(self):
        """(REFACTORIZADO) Inicia la descarga usando el módulo Updater."""
        if not self.latest_release_data:
            self._update_updater_ui("Error: No hay información de la actualización para descargar.")
            return

        def on_update_finish(success, error_message):
            if success:
                self.py_quit_launcher()
            else:
                error_message = f"Error durante la actualización: {error_message}"
                self._update_updater_ui(error_message)
                if self.window:
                    self.window.evaluate_js(f'onUpdateError({json.dumps(error_message)})')

        def download_thread_task():
            self.updater.download_and_apply_update(self.latest_release_data, on_update_finish)

        update_thread = threading.Thread(target=download_thread_task, daemon=True)
        update_thread.start()


    def _migrate_and_load_config(self):
        """(NUEVO) Carga la configuración, añade claves por defecto si faltan y guarda."""
        config_path = self._get_config_path()

        default_config = {
            "prism_exe_path": None,
            "instance_mc_path": None,
            "launch_times_sec": [],
            "music_player_volume": 1.0
        }

        with self.config_lock:
            config_data = {}
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                except json.JSONDecodeError:
                    self._log("Advertencia: launcher_config.json está corrupto. Se creará uno nuevo.")
                    config_data = {}

            # Migración: Añadir claves que falten
            needs_saving = False
            for key, default_value in default_config.items():
                if key not in config_data:
                    config_data[key] = default_value
                    needs_saving = True

            # Guardar si se ha modificado
            if needs_saving:
                try:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=4)
                    self._log("Configuración actualizada con nuevos valores por defecto.")
                except Exception as e:
                    self._log(f"Error guardando configuración migrada: {e}")

            # Ahora, cargar y validar los datos como en la función original
            prism_path = config_data.get("prism_exe_path")
            instance_path = config_data.get("instance_mc_path")
            is_prism_valid = self._validate_prism_path(prism_path)
            is_instance_valid = self._validate_instance_path(instance_path)

            if is_prism_valid and is_instance_valid:
                self.prism_exe_path = prism_path
                self.instance_mc_path = instance_path

                # (NUEVO) Sincronizar configuración de Prism (Portable/Installer)
                self._sync_prism_config()

                # Cargar el resto de las configuraciones
                self.avg_launch_time_sec = self._calculate_avg_launch_time(config_data.get("launch_times_sec", []))
                # El volumen de la música se carga desde JS
                return True
            else:
                return False

    def _sync_prism_config(self):
        """Sincroniza prismlauncher.cfg según si es portable o instalador."""
        if not self.prism_exe_path: return

        # 1. Check Portable: prismlauncher.cfg en la misma carpeta que el exe
        prism_dir = os.path.dirname(self.prism_exe_path)
        portable_cfg = os.path.join(prism_dir, "prismlauncher.cfg")

        if os.path.exists(portable_cfg):
            self._log(f"Detectado Prism Portable config en: {portable_cfg}")
            self._update_prism_cfg_file(portable_cfg, remove_instance_dir=True)
            return

        # 2. Check Installer: %AppData%\PrismLauncher\prismlauncher.cfg
        if IS_WINDOWS:
            appdata = os.environ.get('APPDATA')
            if appdata:
                installer_cfg = os.path.join(appdata, "PrismLauncher", "prismlauncher.cfg")
                if os.path.exists(installer_cfg):
                    self._log(f"Detectado Prism Installer config en: {installer_cfg}")
                    self._update_prism_cfg_file(installer_cfg, remove_instance_dir=False, new_path=self.instance_mc_path)
                    return

        # Si no se encuentra ninguno, no hacemos nada (o podríamos loguear aviso)
        # self._log("No se encontró prismlauncher.cfg (ni portable ni en AppData).")

    def _update_prism_cfg_file(self, filepath, remove_instance_dir=False, new_path=None):
        """Lee y modifica prismlauncher.cfg para gestionar 'InstanceDir'."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            new_lines = []
            in_general = False
            key_found = False

            for line in lines:
                stripped = line.strip()
                if stripped == '[General]':
                    in_general = True
                    new_lines.append(line)
                    continue

                if in_general and stripped.startswith('[') and stripped != '[General]':
                    in_general = False

                if in_general and stripped.split('=')[0].strip() == 'InstanceDir':
                    key_found = True
                    if remove_instance_dir:
                        self._log("Eliminando InstanceDir de prismlauncher.cfg (Modo Portable)")
                        continue # Skip (Remove)
                    else:
                        if new_path:
                            # Normalizar a barras inclinadas (Prism suele aceptarlas mejor en config)
                            clean_path = new_path.replace('\\', '/')
                            new_lines.append(f"InstanceDir={clean_path}\n")
                            self._log(f"Actualizando InstanceDir a: {clean_path}")
                        continue

                new_lines.append(line)

            # Si necesitamos añadirlo y no estaba presente
            if not remove_instance_dir and not key_found and new_path:
                clean_path = new_path.replace('\\', '/')
                final_lines = []
                inserted = False
                has_general = any(l.strip() == '[General]' for l in new_lines)

                if not has_general:
                     # Si no hay sección [General], la creamos al final
                     final_lines = new_lines + ["\n", "[General]\n", f"InstanceDir={clean_path}\n"]
                     self._log(f"Añadiendo sección [General] y InstanceDir: {clean_path}")
                else:
                    for line in new_lines:
                        final_lines.append(line)
                        if line.strip() == '[General]' and not inserted:
                            final_lines.append(f"InstanceDir={clean_path}\n")
                            inserted = True
                            self._log(f"Insertando InstanceDir en [General]: {clean_path}")
                new_lines = final_lines

            # Escribir de vuelta (sobrescribir)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

        except Exception as e:
            self._log(f"Error actualizando prismlauncher.cfg: {e}")

    def _calculate_avg_launch_time(self, launch_times):
        """Calcula el tiempo de lanzamiento promedio desde una lista de tiempos."""
        if launch_times and isinstance(launch_times, list):
            try:
                valid_times = [float(t) for t in launch_times if isinstance(t, (int, float)) and t > 0]
                if valid_times:
                    avg = sum(valid_times) / len(valid_times)
                    self._log(f"Tiempo de carga promedio cargado: {avg:.2f}s ({len(valid_times)} muestras)")
                    return avg
            except Exception as e:
                self._log(f"Error calculando promedio de carga, usando default: {e}")
        self._log("No se encontró historial de tiempos de carga, usando default (400s).")
        return 400.0

    # --- (NUEVO) API para el Panel de Depuración ---
    def py_get_debug_status(self):
        """Devuelve si el modo depuración está activo."""
        return self.debug_mode

    def py_get_current_paths(self):
        """Devuelve las rutas actuales configuradas para actualizar la UI."""
        return {
            "prism_path": self.prism_exe_path,
            "instance_path": self.instance_mc_path
        }

    def py_is_modpack_installed(self):
        """Returns True if the modpack instance has actual .jar mod files installed."""
        if not self.instance_mc_path or not os.path.isdir(self.instance_mc_path):
            return False
        mods_path = os.path.join(self.instance_mc_path, 'mods')
        if not os.path.isdir(mods_path):
            return False
        try:
            return any(f.lower().endswith('.jar') for f in os.listdir(mods_path))
        except OSError:
            return False

    # --- Funciones de Utilidad de la GUI ---

    def _log(self, message):
        """Envía un mensaje de registro a la consola de la GUI."""
        print(f"[Launcher Log] {message}")
        if self.window:
            safe_message = json.dumps(message)[1:-1]
            try:
                self.window.evaluate_js(f'requestAnimationFrame(() => logToConsole("{safe_message}"))')
            except Exception as e:
                pass

    def _update_progress(self, percentage, label=""):
        """Actualiza la barra de progreso y la etiqueta de estado."""
        if self.window:
            safe_label = json.dumps(label)[1:-1]
            try:
                self.window.evaluate_js(f'updateProgress({percentage}, "{safe_label}")')
            except Exception as e:
                print(f"Error evaluating JS for progress: {e}")

    def _show_result(self, success, title, details=""):
        """Muestra la pantalla de resultado (éxito o error)."""
        if self.window:
            safe_title = json.dumps(title)[1:-1]
            safe_details_html = json.dumps(details)[1:-1].replace('\\n', '<br>')
            try:
                self.window.evaluate_js(f'showResult({str(success).lower()}, "{safe_title}", "{safe_details_html}")')
            except Exception as e:
                print(f"Error evaluating JS for result: {e}")

    # (NUEVO) Función para enviar estado al asistente de instalación
    def _update_install_status(self, message):
        """Envía un mensaje de estado al panel de progreso del asistente."""
        print(f"[Install Wizard] {message}")
        if self.window:
            safe_message = json.dumps(message)[1:-1]
            try:
                self.window.evaluate_js(f'updateInstallStatus("{safe_message}")')
            except Exception as e:
                pass # Evitar bucles


    # --- (ACTUALIZADO) Funciones de Configuración QoL ---

    def _get_config_path(self):
        return os.path.join(os.getcwd(), "launcher_config.json")

    def py_load_and_migrate_config(self):
        """(NUEVO) Expone la función de migración y carga a la API de JS."""
        return self._migrate_and_load_config()

    def py_save_paths(self, prism_path, instance_path):
        """(ACTUALIZADO) Guarda AMBAS rutas en config.json, preservando otros datos."""
        if not self._validate_prism_path(prism_path):
            self._log(f"Error al guardar: Ruta Prism inválida ('{prism_path}')")
            return False
        if not self._validate_instance_path(instance_path):
            self._log(f"Error al guardar: Ruta Instancia inválida ('{instance_path}')")
            return False

        self.prism_exe_path = prism_path
        self.instance_mc_path = instance_path
        config_path = self._get_config_path()

        with self.config_lock:
            config_data = {}
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                except Exception as e:
                    self._log(f"Advertencia: No se pudo leer config existente al guardar: {e}. Se sobrescribirá.")
                    config_data = {}

            config_data["prism_exe_path"] = self.prism_exe_path
            config_data["instance_mc_path"] = self.instance_mc_path

            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=4)
                self._log(f"Configuración guardada en: {config_path}")
                return True
            except Exception as e:
                self._log(f"Error al guardar la configuración en '{config_path}': {e}")
                return False

    def _save_new_launch_time(self, time_sec):
        """Guarda un nuevo tiempo de carga en el config, manteniendo los últimos 5."""
        if not isinstance(time_sec, (int, float)) or time_sec <= 0:
            self._log(f"Intento de guardar tiempo de carga inválido: {time_sec}")
            return

        with self.config_lock:
            config_path = self._get_config_path()
            config_data = {}

            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                except Exception as e:
                    self._log(f"Error leyendo config para guardar tiempo: {e}. Se creará uno nuevo.")
                    config_data = {}

            launch_times = config_data.get("launch_times_sec", [])
            if not isinstance(launch_times, list):
                launch_times = []

            launch_times.append(time_sec)
            launch_times = launch_times[-5:]
            config_data["launch_times_sec"] = launch_times

            try:
                valid_times = [float(t) for t in launch_times if isinstance(t, (int, float)) and t > 0]
                if valid_times:
                    self.avg_launch_time_sec = sum(valid_times) / len(valid_times)
            except Exception:
                pass

            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=4)
                self._log(f"Nuevo tiempo de carga ({time_sec:.2f}s) guardado. Nuevo promedio: {self.avg_launch_time_sec:.2f}s")
            except Exception as e:
                self._log(f"Error guardando config con tiempo de carga: {e}")

    def py_save_music_volume(self, volume):
        """(NUEVO) Guarda el volumen de la música en config.json."""
        try:
            volume = float(volume)
            if not (0.0 <= volume <= 1.0):
                self._log(f"Error: Intento de guardar volumen inválido: {volume}")
                return False
        except (ValueError, TypeError):
            self._log(f"Error: El valor del volumen no es un número: {volume}")
            return False

        config_path = self._get_config_path()
        with self.config_lock:
            config_data = {}
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                except Exception as e:
                    self._log(f"Advertencia: No se pudo leer config existente al guardar volumen: {e}.")
                    config_data = {}

            config_data["music_player_volume"] = volume

            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=4)
                return True
            except Exception as e:
                self._log(f"Error al guardar el volumen en '{config_path}': {e}")
                return False

    def py_load_music_volume(self):
        """(NUEVO) Carga el volumen de la música desde config.json."""
        config_path = self._get_config_path()
        with self.config_lock:
            if not os.path.exists(config_path):
                return 1.0 # Default
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                volume = config_data.get("music_player_volume")

                if isinstance(volume, (float, int)) and 0.0 <= volume <= 1.0:
                    self._log(f"Volumen de música cargado: {volume}")
                    return volume
                else:
                    self._log("No se encontró volumen de música válido, usando default (1.0).")
                    return 1.0
            except Exception as e:
                self._log(f"Error leyendo config para volumen, usando default: {e}")
                return 1.0


    # --- Lógica de Auto-detección ---

    def _find_instance_from_prism_path(self, exe_path):
        """Intenta encontrar la instancia por defecto desde la ruta del exe."""
        try:
            if not exe_path or not isinstance(exe_path, str) or not os.path.isfile(exe_path):
                return None

            prism_dir = os.path.dirname(exe_path)

            # 1. Intentar ruta relativa (Portable)
            instance_mc_path = os.path.join(prism_dir, "instances", MODPACK_INSTANCE_NAME, "minecraft")
            if self._validate_instance_path(instance_mc_path):
                self._log(f"Instancia auto-detectada con éxito (Portable): {instance_mc_path}")
                return instance_mc_path

            # 2. Intentar ruta AppData/Roaming (Non-portable)
            if IS_WINDOWS:
                appdata = os.environ.get('APPDATA')
                if appdata:
                    # Probar variantes de carpeta de datos
                    roaming_paths = [
                        os.path.join(appdata, "PrismLauncher", "instances", MODPACK_INSTANCE_NAME, "minecraft"),
                        os.path.join(appdata, "Prism Launcher", "instances", MODPACK_INSTANCE_NAME, "minecraft")
                    ]
                    for path in roaming_paths:
                        if self._validate_instance_path(path):
                            self._log(f"Instancia auto-detectada con éxito (Roaming): {path}")
                            return path

            self._log(f"Auto-detect: No se encontró la instancia '{MODPACK_INSTANCE_NAME}/minecraft' ni en '{prism_dir}' ni en AppData.")
            return None
        except Exception as e:
            self._log(f"Error durante la auto-detección de instancia: {e}")
        return None

    # --- (ACTUALIZADO) Funciones de la API de Python <-> JS ---

    def py_get_playlist(self):
        """Devuelve la lista de reproducción completa desde MusicLibrary."""
        self._log("JS solicitó la lista de reproducción de GitLab.")
        if self.music_library is None:
            self._log("Inicializando MusicLibrary...")
            try:
                self.music_library = MusicLibrary(github_raw_url=GITHUB_RAW_URL)
            except Exception as e:
                self._log(f"ERROR CRÍTICO: No se pudo inicializar MusicLibrary: {e}")
                return []

        try:
            playlist = self.music_library.get_playlist()
            self._log(f"Enviando {len(playlist)} canciones a JS.")
            return playlist
        except Exception as e:
            self._log(f"ERROR: No se pudo obtener la playlist de MusicLibrary: {e}")
            return []

    def py_toggle_fullscreen(self):
        if self.window:
            try:
                self.window.toggle_fullscreen()
                self._log("Fullscreen toggled.")
            except Exception as e:
                print(f"Error toggling fullscreen: {e}")

    def py_get_os_sep(self):
        return os.path.sep

    def py_get_launcher_version(self):
        """(NUEVO) Devuelve la versión actual del launcher."""
        return LAUNCHER_VERSION

    # --- (MODIFICADO) API de Configuración Antigua (Ahora usada por Ajustes) ---

    def py_browse_for_prism_exe(self):
        """Abre diálogo para buscar .exe Y auto-detecta la instancia."""
        self._log("py_browse_for_prism_exe called")
        result_data = {"is_valid": False, "prism_path": None, "instance_path": None}
        if self.window:
            try:
                file_types = ('Executables (*.exe)', 'All files (*.*)') if IS_WINDOWS else ('All files (*.*)',)
                self._log("Attempting to create file dialog...")
                result = self.window.create_file_dialog(webview.OPEN_DIALOG, file_types=file_types, allow_multiple=False)
                self._log(f"File dialog result: {result}")

                if result and isinstance(result, tuple) and len(result) > 0:
                    exe_path = result[0]
                    if self._validate_prism_path(exe_path):
                        result_data["is_valid"] = True
                        result_data["prism_path"] = exe_path
                        result_data["instance_path"] = self._find_instance_from_prism_path(exe_path)
                    else:
                        self._log(f"Archivo seleccionado '{os.path.basename(exe_path)}' no parece ser un ejecutable de Prism válido.")
                elif result:
                    self._log(f"Diálogo de archivo devolvió resultado inesperado: {result}")
                else:
                    self._log("File dialog returned None or empty. (User cancelled?)")
            except Exception as e:
                self._log(f"--- ERROR AL ABRIR DIÁLOGO PRISM ---: {e}")
                import traceback
                self._log(traceback.format_exc())
        self._log(f"Returning from py_browse_for_prism_exe: {result_data}")
        return result_data

    def py_browse_for_instance_folder(self):
        """Abre un diálogo para buscar la carpeta de la INSTANCIA."""
        self._log("py_browse_for_instance_folder called")
        path = None
        if self.window:
            try:
                self._log("Attempting to create folder dialog...")
                result = self.window.create_file_dialog(webview.FOLDER_DIALOG, allow_multiple=False)
                self._log(f"Folder dialog result: {result}")

                if result and isinstance(result, tuple) and len(result) > 0:
                    selected_path = result[0]
                    self._log(f"Carpeta seleccionada por usuario: {selected_path}")
                    if os.path.basename(selected_path).lower() != 'minecraft':
                        potential_mc_path = os.path.join(selected_path, 'minecraft')
                        self._log(f"Intentando auto-corregir a: {potential_mc_path}")
                        if self._validate_instance_path(potential_mc_path):
                            path = potential_mc_path
                            self._log("Auto-corrección exitosa.")
                        else:
                            self._log(f"Carpeta seleccionada '{os.path.basename(selected_path)}' no contiene una subcarpeta 'minecraft' válida.")
                    elif self._validate_instance_path(selected_path):
                            path = selected_path
                            self._log("Carpeta 'minecraft' seleccionada es válida.")
                    else:
                            self._log(f"Carpeta 'minecraft' seleccionada '{os.path.basename(selected_path)}' no es válida.")
                elif result:
                    self._log(f"Diálogo de carpeta devolvió resultado inesperado: {result}")
                else:
                    self._log("Folder dialog returned None or empty. (User cancelled?)")
            except Exception as e:
                self._log(f"--- ERROR AL ABRIR DIÁLOGO INSTANCIA ---: {e}")
                import traceback
                self._log(traceback.format_exc())
        self._log(f"Returning from py_browse_for_instance_folder: {path}")
        return path

    def py_process_prism_path_drop(self, path):
        """Valida el .exe arrastrado Y auto-detecta la instancia."""
        result_data = {"is_valid": False, "prism_path": path, "instance_path": None}
        if os.path.isdir(path):
            self._log(f"Elemento arrastrado es una carpeta, buscando 'PrismLauncher.exe' o 'prismlauncher.exe' dentro...")

            # (CORREGIDO) Comprobar ambas capitalizaciones
            potential_exe_path_capital = os.path.join(path, 'PrismLauncher.exe')
            potential_exe_path_lower = os.path.join(path, 'prismlauncher.exe')

            if self._validate_prism_path(potential_exe_path_capital):
                path = potential_exe_path_capital
                self._log(f"Ejecutable (P mayúscula) encontrado dentro de la carpeta: {path}")
            elif self._validate_prism_path(potential_exe_path_lower):
                path = potential_exe_path_lower
                self._log(f"Ejecutable (p minúscula) encontrado dentro de la carpeta: {path}")
            else:
                self._log(f"No se encontró un ejecutable de Prism válido en la carpeta arrastrada.")
                return result_data

        if self._validate_prism_path(path):
            result_data["is_valid"] = True
            result_data["prism_path"] = path
            result_data["instance_path"] = self._find_instance_from_prism_path(path)
        else:
            self._log(f"Archivo arrastrado '{os.path.basename(path)}' no es un ejecutable de Prism válido.")
        return result_data

    def py_process_instance_path_drop(self, path):
        """Valida la carpeta de instancia arrastrada (o su carpeta padre)."""
        result_data = {"is_valid": False, "path": path}
        if not os.path.isdir(path):
            self._log(f"Elemento arrastrado para Instancia no es una carpeta: {os.path.basename(path)}")
            return result_data

        if self._validate_instance_path(path):
            result_data["is_valid"] = True
            result_data["path"] = path
            return result_data

        potential_mc_path = os.path.join(path, 'minecraft')
        if self._validate_instance_path(potential_mc_path):
            result_data["is_valid"] = True
            result_data["path"] = potential_mc_path
            return result_data

        self._log(f"Carpeta arrastrada '{os.path.basename(path)}' no es o no contiene una carpeta 'minecraft' válida.")
        return result_data

    def py_validate_instance_path(self, path):
        """Solo valida la ruta de la instancia (para UI)."""
        isValid = self._validate_instance_path(path)
        return isValid

    # --- (NUEVO) API para el Asistente de Configuración Inicial ---

    def py_setup_check_prism_default_path(self):
        """
        Paso 1: Comprueba la ruta de instalación por defecto de Prism.
        Retorna: {{status: 'prism_detected', path: '...'} o {status: 'not_found'}}
        """
        self._log(f"Asistente: Comprobando rutas por defecto...")
        if IS_WINDOWS:
            # 1. Check known install locations
            for path in PRISM_DEFAULT_PATHS_WINDOWS:
                self._log(f"Asistente: Comprobando: {path}")
                if self._validate_prism_path(path):
                    self._log(f"Asistente: Prism detectado en: {path}")
                    return {"status": "prism_detected", "path": path}

            # 2. Fallback: check Windows registry (covers custom install paths)
            try:
                import winreg
                reg_keys = [
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\PrismLauncher"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\PrismLauncher"),
                    (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\PrismLauncher"),
                ]
                for hive, key_path in reg_keys:
                    try:
                        with winreg.OpenKey(hive, key_path) as key:
                            install_dir, _ = winreg.QueryValueEx(key, "InstallLocation")
                            for exe_name in ("prismlauncher.exe", "PrismLauncher.exe"):
                                candidate = os.path.join(install_dir, exe_name)
                                if self._validate_prism_path(candidate):
                                    self._log(f"Asistente: Prism detectado via registro: {candidate}")
                                    return {"status": "prism_detected", "path": candidate}
                    except (FileNotFoundError, OSError):
                        continue
            except ImportError:
                pass  # winreg only available on Windows CPython, skip silently

        self._log("Asistente: Prism no encontrado en rutas por defecto ni en registro.")
        return {"status": "not_found"}

    def py_setup_ask_for_prism_path(self):
        """
        Paso 3a: El usuario busca manualmente el .exe.
        Retorna: {{status: 'path_valid', path: '...'} o {status: 'path_invalid', error: '...'} o {status: 'cancelled'}}
        """
        self._log("Asistente: Usuario buscando .exe manualmente...")
        if self.window:
            try:
                file_types = ('Executables (*.exe)', 'All files (*.*)') if IS_WINDOWS else ('All files (*.*)',)
                result = self.window.create_file_dialog(webview.OPEN_DIALOG, file_types=file_types, allow_multiple=False)
                if result and isinstance(result, tuple) and len(result) > 0:
                    exe_path = result[0]
                    if self._validate_prism_path(exe_path):
                        self._log(f"Asistente: Usuario seleccionó .exe válido: {exe_path}")
                        return {"status": "path_valid", "path": exe_path}
                    else:
                        msg = f"El archivo '{os.path.basename(exe_path)}' no es un ejecutable de Prism válido."
                        self._log(f"Asistente: {msg}")
                        return {"status": "path_invalid", "error": msg}
                else:
                    self._log("Asistente: Usuario canceló la búsqueda manual.")
                    return {"status": "cancelled"}
            except Exception as e:
                msg = f"Error al abrir diálogo: {e}"
                self._log(f"Asistente: {msg}")
                return {"status": "path_invalid", "error": msg}
        return {"status": "cancelled"} # Fallback

    def py_setup_ask_for_install_location(self):
        """
        Paso 3b: El usuario elige dónde instalar Prism.
        Retorna: {{status: 'path_valid', path: '...'} o {status: 'cancelled'}}
        """
        self._log("Asistente: Usuario eligiendo ubicación de instalación...")
        if self.window:
            try:
                result = self.window.create_file_dialog(webview.FOLDER_DIALOG, allow_multiple=False)
                if result and isinstance(result, tuple) and len(result) > 0:
                    install_path = result[0]
                    self._log(f"Asistente: Usuario seleccionó carpeta de instalación: {install_path}")
                    return {"status": "path_valid", "path": install_path}
                else:
                    self._log("Asistente: Usuario canceló la selección de carpeta.")
                    return {"status": "cancelled"}
            except Exception as e:
                msg = f"Error al abrir diálogo de carpeta: {e}"
                self._log(f"Asistente: {msg}")
                self._show_result(False, "Error de Diálogo", msg)
                return {"status": "cancelled"}
        return {"status": "cancelled"} # Fallback

    def py_setup_check_modpack_installed(self, prism_exe_path):
        """
        Paso 4: Comprueba si la instancia del modpack ya existe.
        Retorna: {status: 'modpack_installed', ...} o {status: 'modpack_not_installed', ...} o {status: 'error', ...}
        """
        self._log(f"Asistente: Comprobando si el modpack '{MODPACK_INSTANCE_NAME}' existe para Prism en '{prism_exe_path}'")
        try:
            # Use _find_instance_from_prism_path which checks BOTH portable and AppData/Roaming
            instance_mc_path = self._find_instance_from_prism_path(prism_exe_path)
            if instance_mc_path:
                self._log("Asistente: Modpack ya está instalado.")
                return {
                    "status": "modpack_installed",
                    "prism_path": prism_exe_path,
                    "instance_path": instance_mc_path
                }

            # Not installed — determine where Prism actually stores its instances
            # so the installer puts the modpack in the right place.
            prism_dir = os.path.dirname(prism_exe_path)
            instance_base_path = None

            # Prefer the portable instances folder if it already exists
            portable_instances = os.path.join(prism_dir, "instances")
            if os.path.isdir(portable_instances):
                instance_base_path = portable_instances
                self._log(f"Asistente: Modo portable detectado, instancias en: {instance_base_path}")
            elif IS_WINDOWS:
                # Installer (non-portable): instances live in AppData\Roaming
                appdata = os.environ.get('APPDATA', '')
                for folder in ("PrismLauncher", "Prism Launcher"):
                    candidate = os.path.join(appdata, folder, "instances")
                    if os.path.isdir(candidate):
                        instance_base_path = candidate
                        self._log(f"Asistente: Modo instalador detectado, instancias en: {instance_base_path}")
                        break

            # If neither exists yet, default to portable (will be created during install)
            if not instance_base_path:
                instance_base_path = portable_instances
                self._log(f"Asistente: Sin instancias previas, usando portable por defecto: {instance_base_path}")

            self._log("Asistente: Modpack no encontrado. Listo para instalar.")
            return {
                "status": "modpack_not_installed",
                "prism_path": prism_exe_path,
                "instance_base_path": instance_base_path
            }
        except Exception as e:
            msg = f"Error comprobando instancia: {e}"
            self._log(f"Asistente: {msg}")
            return {"status": "error", "error": msg}

    def py_setup_open_prism_for_login(self, prism_exe_path):
        """
        Paso 6: Abre Prism (sin lanzar juego) para que el usuario inicie sesión.
        """
        self._log("Asistente: Abriendo Prism para inicio de sesión manual...")
        if not self._validate_prism_path(prism_exe_path):
            msg = "Ruta de Prism no válida. No se puede abrir."
            self._log(f"Asistente: {msg}")
            self._show_result(False, "Error", msg)
            return

        try:
            command = [prism_exe_path]
            # Lanzar Prism de forma normal (no-bloqueante)
            subprocess.Popen(command)
            self._log("Asistente: Comando para abrir Prism enviado.")
        except Exception as e:
            msg = f"Error al intentar abrir Prism: {e}"
            self._log(f"Asistente: {msg}")
            self._show_result(False, "Error al Abrir", msg)

    # --- Hilos de Tareas (Instalación) ---

    def py_start_threaded_task(self, task_name, *args):
        """
        (NUEVO) Inicia una tarea larga en un hilo separado
        y llama a un callback de JS al completarse.
        """
        if self.current_task_thread and self.current_task_thread.is_alive():
            self._log(f"Advertencia: Tarea '{task_name}' solicitada pero ya hay una tarea activa. Restaurando vista...")
            # Don't error — just tell the UI to show whatever is already running
            if self.window:
                self.window.evaluate_js('restoreRunningTaskView()')
            return

        self.cancel_event.clear()
        self.pause_event.clear()  # Ensure download is not paused at start of new task

        if task_name == 'install_prism':
            self.current_task_thread = threading.Thread(target=self._task_install_prism, args=args, daemon=True)
        elif task_name == 'install_modpack':
            self.current_task_thread = threading.Thread(target=self._task_install_modpack, args=args, daemon=True)
        else:
            self._log(f"Error: Nombre de tarea desconocido: {task_name}")
            return

        self._log(f"Iniciando hilo para tarea: {task_name}")
        self.current_task_thread.start()

    def _task_install_prism(self, install_location_base):
        """
        (REESCRITO) Tarea en hilo: Descarga y extrae la versión portable de Prism.
        Llama a JS: onPrismInstallComplete(success, path, error)
        """
        time.sleep(0.5) # Esperar a que la UI esté lista
        self._update_install_status("DEBUG: Hilo de instalación de Prism iniciado.")

        tmp_dir = None
        try:
            if install_location_base is None:
                raise ValueError("La ruta de instalación base es None.")

            dedicated_install_path = os.path.join(install_location_base, "Prism Launcher")
            self._update_install_status(f"Creando directorio de instalación en: {dedicated_install_path}")

            os.makedirs(dedicated_install_path, exist_ok=True)

            if self.cancel_event.is_set():
                raise InterruptedError("Instalación cancelada por el usuario.")

            tmp_dir = tempfile.mkdtemp(prefix="prism_portable_")
            self._update_install_status(f"Directorio temporal creado: {os.path.basename(tmp_dir)}")
            zip_path = os.path.join(tmp_dir, "prismlauncher.zip")

            # 1. Descargar
            self._update_install_status(f"Descargando Prism Launcher desde: {PRISM_PORTABLE_URL}")
            self._download_file(PRISM_PORTABLE_URL, zip_path, "wizard_install")

            if self.cancel_event.is_set(): raise InterruptedError("Descarga cancelada.")

            # 2. Extraer
            self._update_install_status("Descarga completa. Extrayendo archivos...")

            with zipfile.ZipFile(zip_path, 'r') as zf:
                if zf.testzip() is not None:
                    raise zipfile.BadZipFile("Archivo ZIP de Prism Launcher corrupto.")

                total_files = len(zf.infolist())
                extracted_count = 0
                last_update_time = time.time()

                for member in zf.infolist():
                    if self.cancel_event.is_set(): raise InterruptedError("Extracción cancelada.")
                    zf.extract(member, dedicated_install_path)
                    extracted_count += 1

                    now = time.time()
                    if now - last_update_time > 0.1 or extracted_count == total_files:
                        pct = extracted_count / total_files if total_files > 0 else 0
                        self._update_install_status(f"Extrayendo: {member.filename}")
                        if self.window: self.window.evaluate_js(f'updateProgress({pct}, "Extrayendo... {extracted_count}/{total_files}")')
                        last_update_time = now

            self._update_install_status("Extracción completa. Verificando ejecutable...")

            final_exe_path = os.path.join(dedicated_install_path, "PrismLauncher.exe")
            final_exe_path_lower = os.path.join(dedicated_install_path, "prismlauncher.exe")

            if self._validate_prism_path(final_exe_path):
                self._update_install_status("¡Prism Launcher instalado con éxito!")
                if self.window: self.window.evaluate_js(f'onPrismInstallComplete(true, {json.dumps(final_exe_path)}, null)')
            elif self._validate_prism_path(final_exe_path_lower):
                self._update_install_status("¡Prism Launcher instalado con éxito!")
                if self.window: self.window.evaluate_js(f'onPrismInstallComplete(true, {json.dumps(final_exe_path_lower)}, null)')
            else:
                msg = f"Se extrajo el ZIP, pero no se encontró 'PrismLauncher.exe' en '{dedicated_install_path}'."
                self._log(msg)
                if self.window: self.window.evaluate_js(f'onPrismInstallComplete(false, null, {json.dumps(msg)})')

        except BaseException as e:
            msg = f"Fallo en la instalación de Prism Launcher: {e}"
            self._log(msg)
            import traceback
            self._log(traceback.format_exc())
            if self.window: self.window.evaluate_js(f'onPrismInstallComplete(false, null, {json.dumps(str(msg))})')

        finally:
            self.current_task_thread = None # Liberar referencia al hilo
            if tmp_dir and os.path.exists(tmp_dir):
                try:
                    shutil.rmtree(tmp_dir)
                    self._log(f"Temporal de instalación '{os.path.basename(tmp_dir)}' eliminado.")
                except Exception as e:
                    self._log(f"Warn: Fallo eliminando temporal de instalación: {e}")

    def _task_install_modpack(self, prism_exe_path, instance_base_path):
        """
        (NUEVO) Tarea en hilo: Descarga y extrae el modpack.
        Llama a JS: onModpackInstallComplete(success, prismPath, instancePath, error)
        """
        time.sleep(0.5) # Esperar a que la UI esté lista
        self._update_install_status("DEBUG: Hilo de instalación de modpack iniciado.")

        # Validar argumentos explícitamente y reportar a la UI si fallan
        if prism_exe_path is None or instance_base_path is None:
             error_msg = f"Argumentos inválidos: prism={prism_exe_path}, instance={instance_base_path}"
             self._update_install_status(error_msg)
             # Esto lanzará excepción abajo y se capturará
        else:
             self._update_install_status(f"DEBUG: Args recibidos: Prism='{prism_exe_path}', InstanceBase='{instance_base_path}'")

        tmp_dir = None
        try:
            # Comprobación de integridad de requests
            if 'requests' not in sys.modules:
                raise ImportError("El módulo 'requests' no está disponible en este entorno.")

            if prism_exe_path is None or instance_base_path is None:
                raise ValueError("Se recibieron rutas nulas (None) desde la interfaz.")

            final_instance_path = os.path.join(instance_base_path, MODPACK_INSTANCE_NAME)
            final_mc_path = os.path.join(final_instance_path, "minecraft")

            # Use stable download directory so the .part file survives a crash
            os.makedirs(STABLE_DOWNLOAD_DIR, exist_ok=True)
            zip_path = os.path.join(STABLE_DOWNLOAD_DIR, "modpack.zip")
            self._update_install_status(f"Directorio de descarga: {STABLE_DOWNLOAD_DIR}")
            # Temp dir only used for extraction (can be recreated if crashed)
            tmp_dir = tempfile.mkdtemp(prefix="cobblemon_extract_")

            # 1. Obtener URL y Descargar
            modpack_url = None

            self._update_install_status(f"Obteniendo enlace de descarga dinámico...")
            try:
                # Intentar obtener la URL desde GitLab
                self._log(f"DEBUG: Consultando {MODPACK_URL_SOURCE}")
                resp = requests.get(MODPACK_URL_SOURCE, timeout=15)
                resp.raise_for_status()
                # Limpiar la respuesta (quitar saltos de línea y espacios)
                remote_url = resp.text.replace('\n', '').replace('\r', '').strip()

                if remote_url.startswith('http'):
                    modpack_url = remote_url
                    self._log(f"URL de modpack obtenida dinámicamente: {modpack_url}")
                else:
                    raise ValueError(f"El contenido de modpack-url.txt no es una URL válida: '{remote_url}'")
            except Exception as e:
                # Si falla, lanzamos error para detener la instalación (sin fallback)
                err_msg = f"No se pudo obtener la URL de descarga: {e}"
                self._update_install_status(f"ERROR: {err_msg}")
                raise RuntimeError(err_msg)

            self._update_install_status(f"Descargando Modpack desde: {modpack_url}")
            # Save state before download so we can resume if the launcher crashes
            self._save_download_state(modpack_url, zip_path, "install_modpack", {
                "prism_exe_path": prism_exe_path,
                "instance_base_path": instance_base_path
            })
            # Skip download if zip already fully downloaded (previous crash after extract)
            if os.path.exists(zip_path):
                self._update_install_status("Archivo ZIP ya descargado, omitiendo descarga.")
            else:
                # (NOTA) Esta URL debe apuntar a un .ZIP, no a un .RAR
                self._download_file(modpack_url, zip_path, "wizard_install")

            if self.cancel_event.is_set(): raise InterruptedError("Descarga cancelada.")

            # 2. Extraer
            self._update_install_status("Descarga completa. Extrayendo archivos...")
            extract_target = os.path.join(tmp_dir, "extracted")

            with zipfile.ZipFile(zip_path, 'r') as zf:
                if zf.testzip() is not None:
                    raise zipfile.BadZipFile("Archivo ZIP del modpack corrupto.")

                total_files = len(zf.infolist())
                extracted_count = 0
                last_update_time = time.time()

                for member in zf.infolist():
                    if self.cancel_event.is_set(): raise InterruptedError("Extracción cancelada.")
                    zf.extract(member, extract_target)
                    extracted_count += 1

                    now = time.time()
                    if now - last_update_time > 0.1 or extracted_count == total_files:
                        pct = extracted_count / total_files if total_files > 0 else 0
                        self._update_install_status(f"Extrayendo: {member.filename}")
                        # Usar el mismo _update_progress pero para el wizard
                        if self.window: self.window.evaluate_js(f'updateProgress({pct}, "Extrayendo... {extracted_count}/{total_files}")')
                        last_update_time = now

            # 2. Crear directorio de destino y extraer
            self._update_install_status(f"Creando directorio de instancia: {os.path.basename(final_instance_path)}")

            # (CORREGIDO) Asegurarse de que la carpeta 'instances' exista
            try:
                os.makedirs(instance_base_path, exist_ok=True)
            except Exception as e:
                raise IOError(f"No se pudo crear el directorio 'instances': {e}")

            if os.path.exists(final_instance_path):
                self._update_install_status("Una carpeta de instancia antigua existe. Eliminándola...")
                try:
                    shutil.rmtree(final_instance_path)
                except Exception as e:
                    raise IOError(f"No se pudo eliminar la instancia antigua: {e}")

            os.makedirs(final_instance_path, exist_ok=True)

            self._update_install_status("Extrayendo archivos de modpack...")

            with zipfile.ZipFile(zip_path, 'r') as zf:
                if zf.testzip() is not None:
                    raise zipfile.BadZipFile("Archivo ZIP del modpack corrupto.")

                total_files = len(zf.infolist())
                extracted_count = 0
                last_update_time = time.time()

                for member in zf.infolist():
                    if self.cancel_event.is_set(): raise InterruptedError("Extracción cancelada.")
                    # Extraer directamente en la carpeta de instancia final
                    zf.extract(member, final_instance_path)
                    extracted_count += 1

                    now = time.time()
                    if now - last_update_time > 0.1 or extracted_count == total_files:
                        pct = extracted_count / total_files if total_files > 0 else 0
                        self._update_install_status(f"Extrayendo: {member.filename}")
                        if self.window: self.window.evaluate_js(f'updateProgress({pct}, "Extrayendo... {extracted_count}/{total_files}")')
                        last_update_time = now

            self._update_install_status("Extracción completa. Verificando...")

            self._update_install_status("Verificación final de la instancia...")
            if self._validate_instance_path(final_mc_path):
                self._update_install_status("¡Modpack instalado con éxito!")
                # Clear crash-recovery state and downloaded zip on success
                self._clear_download_state()
                try:
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
                except Exception:
                    pass
                if self.window: self.window.evaluate_js(f'onModpackInstallComplete(true, {json.dumps(prism_exe_path)}, {json.dumps(final_mc_path)}, null)')
            else:
                raise FileNotFoundError("La instancia se movió pero no es válida.")

        except BaseException as e:
            msg = f"Fallo en la instalación del Modpack: {e}"
            self._log(msg)
            import traceback
            self._log(traceback.format_exc())
            if self.window: self.window.evaluate_js(f'onModpackInstallComplete(false, null, null, {json.dumps(str(msg))})')

        finally:
            self.current_task_thread = None # Liberar referencia al hilo
            # Only clean up the extraction tmpdir; .launcher_downloads is kept for resume.
            if tmp_dir and os.path.exists(tmp_dir):
                try:
                    shutil.rmtree(tmp_dir)
                    self._log(f"Temporal de extracción '{os.path.basename(tmp_dir)}' eliminado.")
                except Exception as e:
                    self._log(f"Warn: Fallo eliminando temporal de extracción: {e}")

    # --- Lógica de Inicio (Actualizar y Lanzar) ---

    def py_start_game(self):
        """Inicia el proceso completo: Actualizar y Luego Lanzar."""
        self._log("Botón JUGAR presionado.")
        if not self.prism_exe_path or not self.instance_mc_path:
            self._log("Rutas no encontradas, recargando desde config...")
            if not self._migrate_and_load_config():
                self._log("Error Crítico: Faltan las rutas. Volviendo a configuración.")
                self._show_result(False, "Error de Configuración", "Las rutas guardadas no son válidas. Por favor, configúralas de nuevo.")
                if self.window:
                    try:
                        # (MODIFICADO) Llamar a la pantalla de AJUSTES
                        self.window.evaluate_js('forceShowSetupScreen()')
                    except Exception as e:
                        self._log(f"Error forcing setup screen: {e}")
                return

        self.cancel_event.clear()
        self.game_ready_event.clear() # <-- CORRECCIÓN
        self.changelog_processed_items = set()

        self._log("Iniciando hilo de actualización/lanzamiento...")
        thread = threading.Thread(target=self._game_start_thread)
        thread.daemon = True
        thread.start()

    def py_cancel_update(self):
        """Sets cancellation events and starts process termination thread."""
        self._log("Cancellation requested by user...")
        self.cancel_event.set()
        self.pause_event.clear()  # Unblock any paused download so it can exit
        self.game_ready_event.set()  # Stop on_top loop if cancelling

        self._log("Iniciando hilo de terminación de procesos...")
        kill_thread = threading.Thread(target=self._terminate_game_processes)
        kill_thread.daemon = True
        kill_thread.start()

    def _terminate_game_processes(self):
        """Intenta encontrar y terminar procesos de Prism Launcher y Java (JDK)."""
        self._log("[KILL] Iniciando terminación de procesos de juego...")
        target_names = ['prismlauncher.exe', 'prismlauncher', 'java.exe', 'javaw.exe', 'java']
        target_cmdline_keywords = ['jdk', 'prismlauncher', 'minecraft']
        killed_pids = set()
        my_pid = os.getpid()

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    proc_pid = proc_info['pid']
                    if proc_pid == my_pid: continue

                    proc_name = proc_info['name'].lower() if proc_info['name'] else ''
                    proc_cmdline = ' '.join(proc_info['cmdline']).lower() if proc_info['cmdline'] else ''
                    should_kill = False

                    if any(name in proc_name for name in target_names):
                        should_kill = True

                    if not should_kill and proc_cmdline:
                        if any(keyword in proc_cmdline for keyword in target_cmdline_keywords):
                            if 'vplus_launcher' not in proc_cmdline and 'launcher_main' not in proc_cmdline:
                                should_kill = True

                    if should_kill:
                        if proc_pid not in killed_pids:
                            self._log(f"[KILL] Intentando terminar: {proc.info['name']} (PID: {proc_pid})")
                            proc.kill()
                            killed_pids.add(proc_pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                except Exception as e:
                    pass
        except Exception as e:
            self._log(f"[KILL] Error fatal durante la iteración de procesos: {e}")

        if killed_pids:
            self._log(f"[KILL] Terminación completada. {len(killed_pids)} procesos terminados.")
        else:
            self._log("[KILL] No se encontraron procesos de juego para terminar.")

    def py_quit_launcher(self):
        """Cierra la aplicación (llamado por JS después del fade-out)."""
        self._log("Cerrando el launcher vía JS.")
        self._force_quit()

    def _force_quit(self):
        """(NUEVO) Cierre forzado del proceso."""
        # IMPORTANTE: NO usar self._log aquí. Si la UI está colgada, self._log bloqueará.
        print("Ejecutando _force_quit()...")

        # Intento 1: os._exit
        try:
            print("Saliendo del proceso Python (os._exit)...")
            os._exit(0)
        except Exception as e:
            print(f"Fallo en os._exit: {e}")

        # Intento 2: psutil suicide
        try:
            print("Saliendo del proceso Python (psutil.kill)...")
            p = psutil.Process(os.getpid())
            p.kill()
        except Exception as e:
            print(f"Fallo en psutil kill: {e}")

        # Intento 3: Taskkill (Windows nuclear option)
        if IS_WINDOWS:
            try:
                print("Ejecutando taskkill de emergencia...")
                subprocess.Popen(f"taskkill /F /PID {os.getpid()}", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as e:
                print(f"Fallo en taskkill: {e}")

    # --- Lógica de Validación ---

    def _validate_prism_path(self, path):
        """Valida si la ruta es un ejecutable de Prism Launcher válido."""
        if not path or not isinstance(path, str) or not os.path.isfile(path):
            return False
        try:
            name = os.path.basename(path).lower()
            is_prism = "prismlauncher" in name or "polymc" in name
            is_valid_ext = (IS_WINDOWS and name.endswith(".exe")) or ('.' not in name or name.endswith(".exe"))
            if is_prism and is_valid_ext:
                if platform.system() == "Windows" or os.access(path, os.X_OK):
                    return True
                else:
                    self._log(f"Advertencia de Validación: '{os.path.basename(path)}' parece Prism pero no tiene permisos de ejecución.")
                    return False
        except Exception as e:
            self._log(f"Error validando ruta Prism '{os.path.basename(path)}': {e}")
            return False
        return False

    def _validate_instance_path(self, path):
        """Valida si la ruta es una carpeta 'minecraft' de instancia válida."""
        if not path or not isinstance(path, str) or not os.path.isdir(path):
            return False
        try:
            if os.path.basename(path).lower() != 'minecraft':
                return False
            mods_path = os.path.join(path, 'mods')
            options_path = os.path.join(path, 'options.txt')
            if os.path.isdir(mods_path) and os.path.isfile(options_path):
                return True
            else:
                return False
        except Exception as e:
            self._log(f"Error validando ruta Instancia '{os.path.basename(path)}': {e}")
            return False

    # --- Lógica de Lanzamiento del Juego ---

    def _game_start_thread(self):
        """Hilo que maneja la secuencia completa de JUGAR."""
        try:
            # --- (NUEVO) Paso 1: Sincronizar options.txt ---
            if not self._sync_options_txt():
                self._log("La sincronización de options.txt falló. Abortando lanzamiento.")
                # El mensaje de error ya se mostró en _sync_options_txt
                return

            # --- Paso 2: Actualizar ---
            self._log("Iniciando comprobación de actualizaciones...")
            self.added_files = []
            self.removed_files = []
            try:
                self.backup_dir = tempfile.mkdtemp(prefix="vplus_backup_")
                self._log(f"Directorio de respaldo creado: {self.backup_dir}")
            except Exception as e:
                self._log(f"Error CRÍTICO: No se pudo crear el directorio de respaldo: {e}")
                self._show_result(False, "Error Crítico", f"No se pudo crear directorio temporal para respaldos: {e}")
                return

            update_success = self._update_modpack_logic()

            if self.cancel_event.is_set():
                self._log("Proceso cancelado detectado después de la lógica de actualización.")
                return

            if update_success:
                # --- Paso 2: Lanzar ---
                self._log("Actualización comprobada/realizada. Iniciando el juego...")
                if self.backup_dir and os.path.exists(self.backup_dir):
                    try:
                        shutil.rmtree(self.backup_dir)
                        self._log("Limpieza de respaldo (post-éxito) completada.")
                        self.backup_dir = None
                    except Exception as e:
                        self._log(f"Advertencia: No se pudo limpiar el respaldo tras éxito: {e}")

                self._launch_game()
            else:
                self._log("La actualización falló o fue cancelada. No se iniciará el juego.")

        except Exception as e:
            self._log(f"Error fatal inesperado en el hilo de inicio: {e}")
            import traceback
            self._log(traceback.format_exc())
            self._show_result(False, "Error Fatal del Launcher", f"Ocurrió un error inesperado: {e}")
            if self.backup_dir and os.path.exists(self.backup_dir):
                self._log("Intentando revertir debido a error fatal...")
                self._revert_changes()
            self.game_ready_event.set()
            if IS_WINDOWS and self.hwnd and win32gui:
                try: win32gui.SetWindowPos(self.hwnd, win32con.HWND_NOTOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                except: pass
            elif self.window:
                try: self.window.on_top = False
                except: pass

    def _sync_options_txt(self):
        """
        Sincroniza las opciones de resource packs desde GitLab con el options.txt del usuario,
        preservando y respaldando sus otras configuraciones.
        """
        self._log("--- Iniciando Sincronización de options.txt ---")
        self._update_progress(0.01, "Sincronizando opciones...")

        instance_options_path = os.path.join(self.instance_mc_path, 'options.txt')
        backup_options_path = os.path.join(os.getcwd(), LOCAL_OPTIONS_BACKUP_FILENAME)

        # 1. Descargar el archivo de resource packs
        try:
            self._log(f"Descargando lista de resource packs desde: {RESOURCE_PACK_OPTIONS_URL}")
            response = requests.get(RESOURCE_PACK_OPTIONS_URL, timeout=15)
            response.raise_for_status()
            remote_options_content = response.text
            self._log("Lista de resource packs descargada con éxito.")
        except requests.RequestException as e:
            self._log(f"ERROR CRÍTICO: No se pudo descargar la configuración de resource packs: {e}")
            self._show_result(False, "Error de Red", f"No se pudo descargar la configuración de resource packs.<br>Revisa tu conexión a internet.<br><br>Error: {e}")
            return False

        # Extraer las líneas importantes del archivo descargado
        new_rp_line, new_irp_line = None, None
        for line in remote_options_content.splitlines():
            if line.startswith("resourcePacks:"):
                new_rp_line = line.strip()
            elif line.startswith("incompatibleResourcePacks:"):
                new_irp_line = line.strip()

        if not new_rp_line:
            self._log("ERROR CRÍTICO: El archivo remoto no contiene la línea 'resourcePacks:'.")
            self._show_result(False, "Error de Configuración Remota", "El archivo de resource packs descargado está corrupto o malformado.")
            return False

        # 2. Determinar el archivo base a usar (NUEVA LÓGICA)
        base_content_lines = []
        # PRIORIDAD 1: El options.txt actual del juego, para capturar cambios del usuario.
        if os.path.exists(instance_options_path):
            self._log("Usando 'options.txt' de la instancia como base (prioridad #1).")
            with open(instance_options_path, 'r', encoding='utf-8') as f:
                base_content_lines = f.readlines()
        # PRIORIDAD 2: El respaldo local, si el del juego se corrompió o borró.
        elif os.path.exists(backup_options_path):
            self._log(f"ADVERTENCIA: No se encontró options.txt en la instancia. Usando respaldo local '{LOCAL_OPTIONS_BACKUP_FILENAME}' como base.")
            with open(backup_options_path, 'r', encoding='utf-8') as f:
                base_content_lines = f.readlines()
        else:
            self._log("ADVERTENCIA: No existe 'options.txt' ni respaldo. Se creará uno desde cero.")
            # Se usará una lista vacía y se añadirán las líneas necesarias.

        # 3. Fusionar las configuraciones
        final_lines = []
        rp_found, irp_found, pof_found = False, False, False

        for line in base_content_lines:
            if line.startswith("resourcePacks:"):
                final_lines.append(new_rp_line + '\n')
                rp_found = True
            elif line.startswith("incompatibleResourcePacks:"):
                if new_irp_line:
                    final_lines.append(new_irp_line + '\n')
                else: # Si el remoto no lo tiene, mantener el del usuario
                    final_lines.append(line)
                irp_found = True
            elif line.startswith("pauseOnLostFocus:"):
                final_lines.append("pauseOnLostFocus:false\n")
                pof_found = True
            else:
                final_lines.append(line)

        # Si alguna línea no existía en el archivo base, añadirla
        if not rp_found: final_lines.append(new_rp_line + '\n')
        if not irp_found and new_irp_line: final_lines.append(new_irp_line + '\n')
        if not pof_found: final_lines.append("pauseOnLostFocus:false\n")

        final_content = "".join(final_lines)

        # 4. Guardar los archivos actualizados
        try:
            # Guardar en la carpeta de la instancia
            self._log(f"Guardando 'options.txt' actualizado en: {self.instance_mc_path}")
            with open(instance_options_path, 'w', encoding='utf-8') as f:
                f.write(final_content)

            # Guardar el respaldo en la carpeta del launcher
            self._log(f"Creando/actualizando respaldo '{LOCAL_OPTIONS_BACKUP_FILENAME}'.")
            with open(backup_options_path, 'w', encoding='utf-8') as f:
                f.write(final_content)

        except IOError as e:
            self._log(f"ERROR CRÍTICO: No se pudo escribir el archivo 'options.txt' o su respaldo: {e}")
            self._show_result(False, "Error de Archivo", f"No se pudo guardar la configuración de opciones.<br>Asegúrate de que el launcher no esté en una carpeta protegida.<br><br>Error: {e}")
            return False

        self._log("--- Sincronización de options.txt completada con éxito ---")
        return True

    def _launch_game(self):
        """Inicia el monitor de logs, la animación de carga y lanza el juego."""
        self.hwnd = None
        try:
            instance_folder_path = os.path.dirname(self.instance_mc_path)
            instance_name = os.path.basename(instance_folder_path)

            if not instance_name:
                raise ValueError(f"No se pudo determinar el nombre de la instancia: {self.instance_mc_path}")

            self._log(f"Iniciando instancia: '{instance_name}'")
            self._log(f"Usando ejecutable: {self.prism_exe_path}")

            log_path = os.path.join(self.instance_mc_path, 'logs', 'latest.log')
            if os.path.exists(log_path):
                self._log("Limpiando log anterior ('latest.log')...")
                try:
                    os.remove(log_path)
                except Exception as e:
                    self._log(f"Advertencia: No se pudo borrar 'latest.log': {e}.")

            try:
                self._log(f"Iniciando animación de carga (promedio: {self.avg_launch_time_sec:.2f}s).")
                if self.window:
                    # (NUEVO) Mostrar y resetear el panel de depuración si está activo
                    if self.debug_mode:
                        self.close_trigger_status = "PENDING"
                        self.window.evaluate_js(f'updateDebugPanel("PENDING")')
                        self.window.evaluate_js(f'toggleDebugPanel(true)')

                    self.window.evaluate_js(f'setLoadScreen("Cargando el Modpack", "Iniciando Minecraft...")')
                    self.window.evaluate_js(f'startLoadingAnimation({self.avg_launch_time_sec})')
            except Exception as e:
                self._log(f"Error al iniciar animación JS: {e}")

            watch_thread = threading.Thread(target=self._watch_log, args=(log_path,), name="LogWatcherThread")
            watch_thread.daemon = True
            watch_thread.start()

            if not os.path.isfile(self.prism_exe_path):
                raise FileNotFoundError(f"El ejecutable de Prism no se encontró en: {self.prism_exe_path}")

            command = [self.prism_exe_path, "--launch", instance_name]
            self._log(f"Ejecutando comando: {' '.join(command)}")

            self.prism_process = None # (NUEVO) Resetear antes de lanzar
            try:
                # (NUEVO) Directorio de trabajo para Prism Launcher
                prism_working_dir = os.path.dirname(self.prism_exe_path)
                self._log(f"Estableciendo CWD para Prism en: {prism_working_dir}")

                startupinfo = None
                if IS_WINDOWS:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    # (CORREGIDO) Usar SW_SHOWNOACTIVATE (4) para que se muestre pero no robe foco (launcher sigue encima)
                    # Esto evita que el juego se pause o mutee por estar minimizado.
                    startupinfo.wShowWindow = 4 # win32con.SW_SHOWNOACTIVATE might not be defined in all versions

                self.prism_process = subprocess.Popen(command, startupinfo=startupinfo,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           encoding='utf-8', errors='ignore',
                                           cwd=prism_working_dir) # <-- AÑADIDO

                # (NUEVO) Hilos para leer la salida de Prism y evitar bloqueos
                stdout_thread = threading.Thread(target=self._stream_reader, args=(self.prism_process.stdout, "Prism Stdout"), daemon=True)
                stderr_thread = threading.Thread(target=self._stream_reader, args=(self.prism_process.stderr, "Prism Stderr"), daemon=True)
                stdout_thread.start()
                stderr_thread.start()

                self._log(f"Comando de lanzamiento enviado a Prism Launcher (PID: {self.prism_process.pid}).")

                if IS_WINDOWS and self.window and win32gui:
                    try:
                        time.sleep(0.3)
                        window_title = self.window.title
                        if window_title:
                            self._log(f"Buscando HWND para título: '{window_title}'...")
                            found_hwnd = win32gui.FindWindow(None, window_title)
                            if found_hwnd != 0:
                                self.hwnd = found_hwnd
                                self._log(f"HWND encontrado vía FindWindow: {self.hwnd}")
                            else:
                                self._log(f"ADVERTENCIA: FindWindow no encontró ventana con título '{window_title}'.")
                        else:
                            self._log("ADVERTENCIA: No se pudo obtener el título de la ventana.")
                    except Exception as e:
                        self._log(f"ADVERTENCIA: Error al buscar HWND vía FindWindow: {e}.")
                        self.hwnd = None

                self._log("Esperando que el vigilante de log inicie el bucle 'Siempre Encima'...")

            except Exception as popen_err:
                raise RuntimeError(f"Fallo al ejecutar Popen para Prism Launcher: {popen_err}")

        except (FileNotFoundError, ValueError, RuntimeError) as launch_err:
            self._log(f"Error de Lanzamiento: {launch_err}")
            self.game_ready_event.set()
            if self.window:
                try: self.window.on_top = False
                except: pass
            self._show_result(False, "Error al Lanzar", f"Fallo al iniciar el proceso: {launch_err}")
        except Exception as e:
            self._log(f"Error inesperado al lanzar el juego: {e}")
            import traceback
            self._log(traceback.format_exc())
            self.game_ready_event.set()
            if self.window:
                try: self.window.on_top = False
                except: pass
            self._show_result(False, "Error Inesperado al Lanzar", f"No se pudo iniciar el juego: {e}")

    def _stream_reader(self, stream, log_prefix):
        """(NUEVO) Lee y registra la salida de un stream en un hilo."""
        try:
            for line in iter(stream.readline, ''):
                if line:
                    self._log(f"[{log_prefix}] {line.strip()}")
            stream.close()
        except Exception as e:
            self._log(f"Error leyendo stream '{log_prefix}': {e}")

    def _focus_game_window(self):
        """(NUEVO) Busca y enfoca la ventana principal de Minecraft/Java."""
        if not IS_WINDOWS or not win32gui: return

        self._log("Intentando enfocar ventana del juego...")

        def find_mc_window(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                # Buscar ventanas que contengan 'Minecraft' (ej: 'Minecraft 1.20.1', 'Minecraft* 1.20.1', etc.)
                if "Minecraft" in title:
                    results.append(hwnd)
            return True

        hwnds = []
        try:
            win32gui.EnumWindows(find_mc_window, hwnds)
            if hwnds:
                # Si hay varias, tomamos la primera (usualmente solo hay una instancia lanzada por nosotros)
                target_hwnd = hwnds[0]
                self._log(f"Ventana encontrada: {target_hwnd} - '{win32gui.GetWindowText(target_hwnd)}'")

                # Restaurar si está minimizada (aunque con SW_SHOWNOACTIVATE no debería estarlo)
                if win32gui.IsIconic(target_hwnd):
                    win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)

                # Traer al frente y dar foco
                win32gui.SetForegroundWindow(target_hwnd)
                self._log("Foco transferido al juego.")
            else:
                self._log("No se encontró ninguna ventana visible con 'Minecraft' en el título.")
        except Exception as e:
            self._log(f"Error al intentar enfocar el juego: {e}")

    def _keep_on_top(self, hwnd):
        """Hilo agresivo que mantiene la ventana del launcher "siempre encima"."""
        self._log(f"[OnTopThread] Iniciado (HWND: {hwnd}, Usando pywin32: {IS_WINDOWS and hwnd and win32gui}).")
        is_using_win32 = IS_WINDOWS and hwnd and win32gui
        try:
            while not self.game_ready_event.wait(0.1):
                if is_using_win32:
                    try:
                        if win32gui.IsWindow(hwnd):
                            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
                        else:
                            self._log("[OnTopThread] HWND ya no es válido. Deteniendo.")
                            break
                    except Exception as e:
                        if hasattr(e, 'winerror') and e.winerror in [1400, 0]:
                             self._log(f"[OnTopThread] Error SetWindowPos (HWND_TOPMOST) esperado al cerrar: {e}")
                             break
                        else:
                             self._log(f"[OnTopThread] Error inesperado en SetWindowPos (HWND_TOPMOST): {e}")
                             is_using_win32 = False
                             time.sleep(1)

                if not is_using_win32:
                    if self.window:
                        try:
                            if not self.window.minimized:
                                self.window.on_top = True
                        except Exception as e:
                            pass
                    else:
                        self._log("[OnTopThread] self.window no existe. Deteniendo.")
                        break
        except Exception as e:
            self._log(f"[OnTopThread] Error fatal: {e}")
        finally:
            self._log("[OnTopThread] Finalizando y quitando 'Siempre Encima'...")
            if is_using_win32 and hwnd:
                try:
                    if win32gui.IsWindow(hwnd):
                        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
                        self._log("[OnTopThread] HWND_NOTOPMOST aplicado.")
                except Exception as e:
                    self._log(f"[OnTopThread] Error SetWindowPos (HWND_NOTOPMOST) al finalizar (ignorado): {e}")
            if self.window:
                try:
                    self.window.on_top = False
                    self._log("[OnTopThread] Fallback self.window.on_top = False aplicado.")
                except:
                    pass
            self._log("Limpieza finalizada.")


    def _watch_log(self, log_path):
        """Vigila 'latest.log', inicia on_top, guarda tiempo de carga y llama a fadeOut."""
        log_filename = os.path.basename(log_path)
        self._log(f"Vigilando el log: {log_filename}")
        self._log(f"Buscando línea gatillo de cierre: '{LOG_TRIGGER_LINE}'")

        file_handle = None
        self.on_top_thread = None

        try:
            start_wait = time.time()
            # (MODIFICADO) Aumentado de 120s a 900s (15 min) para permitir la descarga inicial de bibliotecas
            timeout_seconds = 900
            log_found = False

            # (NUEVO) Log de diagnóstico
            self._log(f"Vigilante: Comprobando estado antes del bucle de espera: window_exists={not not self.window}, cancel_event={self.cancel_event.is_set()}, game_ready_event={self.game_ready_event.is_set()}")

            while time.time() - start_wait < timeout_seconds:
                if not self.window or self.cancel_event.is_set() or self.game_ready_event.is_set():
                    self._log("Vigilante: Ventana cerrada o cancelado/listo, deteniendo espera.")
                    return
                if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
                    log_found = True
                    break
                time.sleep(0.5)

            if not log_found:
                self._log(f"Error: Timeout ({timeout_seconds}s) esperando por '{log_filename}'.")
                if self.window:
                    try:
                        self.window.evaluate_js('returnToPlayScreen()')
                        self._show_result(False, "Error de Inicio", f"Minecraft no generó el archivo '{log_filename}' en {int(timeout_seconds/60)} minutos (descarga lenta o error).")
                    except Exception: pass
                return

            self._log(f"Archivo '{log_filename}' detectado. Iniciando bucle 'Siempre Encima'...")
            self.on_top_thread = threading.Thread(target=self._keep_on_top, args=(self.hwnd,), name="OnTopThread")
            self.on_top_thread.daemon = True
            self.on_top_thread.start()

            self._log("Leyendo log en tiempo real...")
            time.sleep(0.1)
            file_handle = open(log_path, 'r', encoding='utf-8', errors='ignore')
            file_handle.seek(0, os.SEEK_END)
            self._log("Monitoreando nuevas líneas en tiempo real...")

            read_start_time = time.time()
            read_timeout_seconds = 300
            trigger_lines = [LOG_TRIGGER_LINE]
            line_batch = []
            last_batch_time = time.time()

            while True:
                if not self.window or self.cancel_event.is_set() or self.game_ready_event.is_set():
                    self._log("Vigilante: Ventana cerrada, cancelado o ya listo. Deteniendo lectura.")
                    return

                try:
                    line = file_handle.readline()
                except Exception as read_err:
                    self._log(f"Error leyendo línea del log: {read_err}. Reintentando...")
                    time.sleep(0.5)
                    try:
                        if file_handle.closed:
                            self._log("Reabriendo handle del log...")
                            file_handle = open(log_path, 'r', encoding='utf-8', errors='ignore')
                            file_handle.seek(0, os.SEEK_END)
                        else:
                            current_pos = file_handle.tell()
                            file_handle.seek(current_pos)
                        self._log("Re-sincronizado con el log...")
                    except Exception as reopen_err:
                        self._log(f"Fallo al re-sincronizar/reabrir log: {reopen_err}. Deteniendo vigilancia.")
                        raise
                    continue

                if line:
                    line_strip = line.strip()
                    if not line_strip: continue

                    read_start_time = time.time()
                    trigger_line_found = None
                    for trigger in trigger_lines:
                        if trigger in line_strip:
                            trigger_line_found = trigger
                            break

                    if trigger_line_found:
                        # (CRÍTICO) Iniciar el timer de cierre forzoso INMEDIATAMENTE.
                        # Reducido a 1.0s para ser más agresivo.
                        # Esto garantiza que el proceso muera pase lo que pase con la UI o los hilos.
                        kill_timer = threading.Timer(1.0, self._force_quit)
                        kill_timer.daemon = True
                        kill_timer.start()

                        # Intentar logging y UI (Best Effort)
                        try:
                            if line_batch: self._log("\n".join(line_batch))
                            self._log(f"[LOG_TRIGGER] {line_strip}")

                            match = re.search(r'Game took ([\d\.]+) seconds', line_strip)
                            if match:
                                try:
                                    game_load_time = float(match.group(1))
                                    # Lanzar en hilo daemon para no bloquear
                                    threading.Thread(target=self._save_new_launch_time, args=(game_load_time,), daemon=True).start()
                                except Exception: pass

                            # Enfocar juego (Prioritario)
                            self._focus_game_window()

                            if self.window:
                                # Intentar fade out, pero no bloquear si falla
                                self.window.evaluate_js('fadeLauncherOut()')

                        except Exception as e:
                            print(f"Error durante cierre suave (Ignorado, kill timer activo): {e}")

                        return

                    is_spam = any(keyword in line_strip for keyword in self.LOG_IGNORE_KEYWORDS)
                    if is_spam: continue

                    line_batch.append(f"[LOG_PASSTHROUGH] {line_strip}")

                current_time = time.time()
                if len(line_batch) >= 20 or (not line and current_time - last_batch_time > 0.25):
                    if line_batch: self._log("\n".join(line_batch)); line_batch.clear()
                    last_batch_time = current_time

                if not line and current_time - read_start_time > read_timeout_seconds:
                    self._log(f"Error: Timeout ({read_timeout_seconds}s) de inactividad del log esperando trigger.")
                    if self.window:
                        try:
                            self.window.evaluate_js('returnToPlayScreen()')
                            self._show_result(False, "Error de Timeout", "El juego se inició pero no respondió en 5 minutos.")
                        except Exception as e: self._log(f"Error al llamar returnToPlayScreen: {e}")
                    return

                if not line: time.sleep(0.1)

        except FileNotFoundError as e:
            self._log(f"Error crítico: Archivo de log no encontrado o inaccesible: {e}")
            if self.window:
                try:
                    self.window.evaluate_js('returnToPlayScreen()')
                    self._show_result(False, "Error de Log", f"No se encontró o no se pudo leer '{log_filename}'.")
                except: pass
        except Exception as e:
            self._log(f"Error inesperado en el vigilante de log: {e}")
            import traceback
            self._log(traceback.format_exc())
            if self.window:
                try:
                    self.window.evaluate_js('returnToPlayScreen()')
                    self._show_result(False,"Error del Vigilante", f"Ocurrió un error leyendo el log: {e}")
                except: pass
        finally:
            if file_handle:
                try: file_handle.close()
                except: pass
            self._log("Vigilante de log finalizado. Señalando a OnTopThread para que pare...")
            self.game_ready_event.set()
            if self.on_top_thread and self.on_top_thread.is_alive():
                self._log("Esperando a que OnTopThread termine...")
                self.on_top_thread.join(timeout=1.0)
                if self.on_top_thread.is_alive():
                    self._log("ADVERTENCIA: OnTopThread no terminó a tiempo.")
                else:
                    self._log("OnTopThread join() completado.")
            
            if IS_WINDOWS and self.hwnd and win32gui:
                try:
                    if win32gui.IsWindow(self.hwnd):
                        win32gui.SetWindowPos(self.hwnd, win32con.HWND_NOTOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
                except: pass
            elif self.window:
                try: self.window.on_top = False
                except: pass
            self._log("Limpieza final de _watch_log completada.")


    # --- Lógica de Reversión ---

    def _revert_changes(self):
        """Revierte los cambios en caso de error o cancelación."""
        if not self.backup_dir or not os.path.isdir(self.backup_dir):
            self._log("Info: No hay directorio de respaldo válido para revertir.")
            return
        if not self.instance_mc_path or not os.path.isdir(self.instance_mc_path):
             self._log("Error crítico de reversión: La ruta de la instancia no es válida o no existe.")
             return

        self._log(f"--- Iniciando Reversión desde: {os.path.basename(self.backup_dir)} ---")
        folder_path = self.instance_mc_path
        revert_errors = []

        self._log("  Restaurando archivos/carpetas eliminados/sobrescritos...")
        for (rel_folder, item_name), backup_unique_name in self.removed_files:
            backup_item_path = os.path.join(self.backup_dir, backup_unique_name)
            destination_path = os.path.join(folder_path, rel_folder, item_name)
            log_rel_path = os.path.join(rel_folder, item_name) if rel_folder else item_name

            try:
                if os.path.exists(backup_item_path):
                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                    if os.path.exists(destination_path):
                        try:
                            if os.path.isdir(destination_path): shutil.rmtree(destination_path)
                            else: os.remove(destination_path)
                        except Exception as pre_del_err:
                            self._log(f"          - Advertencia: No se pudo borrar '{log_rel_path}' antes de restaurar: {pre_del_err}")

                    if os.path.isdir(backup_item_path):
                        shutil.copytree(backup_item_path, destination_path)
                    else:
                        shutil.copy2(backup_item_path, destination_path)
                    self._log(f"          - Restaurado: {log_rel_path}")
                else:
                    self._log(f"          - Advertencia: Respaldo '{backup_unique_name}' no encontrado para '{log_rel_path}'.")
                    revert_errors.append(f"Respaldo no encontrado para {log_rel_path}")
            except Exception as e:
                msg = f"          - ERROR al restaurar '{log_rel_path}': {e}"
                self._log(msg)
                revert_errors.append(msg)

        self._log("  Eliminando archivos/carpetas agregados...")
        for rel_folder, item_name in reversed(self.added_files):
            path_to_remove = os.path.join(folder_path, rel_folder, item_name)
            log_rel_path = os.path.join(rel_folder, item_name) if rel_folder else item_name
            try:
                if os.path.exists(path_to_remove):
                    if os.path.isdir(path_to_remove):
                        shutil.rmtree(path_to_remove)
                    else:
                        os.remove(path_to_remove)
                    self._log(f"          - Eliminado (agregado): {log_rel_path}")
            except Exception as e:
                msg = f"          - ERROR al eliminar (agregado) '{log_rel_path}': {e}"
                self._log(msg)
                revert_errors.append(msg)

        try:
            shutil.rmtree(self.backup_dir)
            self._log(f"Directorio de respaldo '{os.path.basename(self.backup_dir)}' eliminado.")
            self.backup_dir = None
        except Exception as e:
            msg = f"Error Crítico: No se pudo eliminar respaldo '{os.path.basename(self.backup_dir)}': {e}"
            self._log(msg)
            revert_errors.append(msg)

        if revert_errors:
            self._log("--- Reversión completada con ERRORES ---")
        else:
            self._log("--- Reversión completada con éxito ---")

    # --- Download Manager (Resumable, Pausable) ---

    def py_pause_download(self):
        """Pauses an active download. Call py_resume_download() to continue."""
        self.pause_event.set()
        self._log("Download paused by user.")

    def py_resume_download(self):
        """Resumes a paused download."""
        self.pause_event.clear()
        self._log("Download resumed by user.")

    @staticmethod
    def _format_eta(seconds):
        """Formats seconds into a human-readable ETA string."""
        if seconds <= 0 or seconds >= 36000:
            return "--:--"
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        if h > 0:
            return f"{h}h {m:02d}m {s:02d}s"
        elif m > 0:
            return f"{m}m {s:02d}s"
        else:
            return f"{s}s"

    @staticmethod
    def _format_size(bytes_val):
        """Formats bytes into a human-readable size string."""
        if bytes_val >= 1024 * 1024 * 1024:
            return f"{bytes_val / (1024**3):.2f} GB"
        elif bytes_val >= 1024 * 1024:
            return f"{bytes_val / (1024**2):.1f} MB"
        elif bytes_val >= 1024:
            return f"{bytes_val / 1024:.1f} KB"
        return f"{bytes_val} B"

    def _send_download_progress(self, context, pct, filename, downloaded, total, speed_bps, eta_str, paused=False):
        """Sends rich download progress info to the UI."""
        dl_size = self._format_size(downloaded)
        total_size = self._format_size(total) if total > 0 else "?"
        speed_mb = speed_bps / (1024 * 1024) if speed_bps > 0 else 0

        if paused:
            label = f"PAUSED  {dl_size} / {total_size}"
        elif total > 0:
            label = f"{dl_size} / {total_size}  •  {speed_mb:.1f} MB/s  •  ETA: {eta_str}"
        else:
            label = f"{dl_size}  •  {speed_mb:.1f} MB/s"

        # Send to UI via JS
        if self.window:
            safe_filename = json.dumps(filename)
            safe_label = json.dumps(label)
            paused_js = "true" if paused else "false"
            try:
                self.window.evaluate_js(
                    f'updateDownloadDetails({safe_filename}, {pct}, {safe_label}, {paused_js})'
                )
            except Exception:
                pass

        if context == "wizard_install":
            self._update_install_status(f"{'[PAUSED] ' if paused else ''}{label}")
            if self.window:
                try:
                    self.window.evaluate_js(f'updateProgress({pct}, {json.dumps(label)})')
                except Exception:
                    pass
        else:
            self._update_progress(pct * 0.4, label)

    def _download_file(self, url, destination_path, progress_context="update", filename_hint=None):
        """
        Downloads a file with:
        - Resume support via HTTP Range headers (.part file)
        - Pause/resume via self.pause_event
        - Rich progress: filename, downloaded/total size, speed (MB/s), ETA
        :param url: Download URL
        :param destination_path: Local path to save the file
        :param progress_context: 'update' or 'wizard_install'
        :param filename_hint: Display name for the file (defaults to basename)
        """
        filename = filename_hint or os.path.basename(destination_path) or "file"
        part_path = destination_path + ".part"
        self._log(f"Download starting: {filename}")
        self._log(f"  URL: {url}")
        self._log(f"  Destination: {destination_path}")

        # Check for existing partial download to resume
        existing_size = 0
        if os.path.exists(part_path):
            existing_size = os.path.getsize(part_path)
            if existing_size > 0:
                self._log(f"  Found partial file ({self._format_size(existing_size)}). Attempting resume...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Encoding': 'identity',  # Prevent compression so we get raw bytes
        }
        if existing_size > 0:
            headers['Range'] = f'bytes={existing_size}-'

        try:
            with requests.get(url, stream=True, timeout=60, headers=headers, allow_redirects=True) as resp:
                # Handle resume (206) vs fresh download (200)
                if resp.status_code == 206:
                    content_range = resp.headers.get('Content-Range', '')
                    # Content-Range: bytes 1024-9999/10000 -> total = 10000
                    total_match = re.search(r'/(\d+)$', content_range)
                    total_bytes = int(total_match.group(1)) if total_match else int(resp.headers.get('content-length', 0)) + existing_size
                    downloaded = existing_size
                    file_mode = 'ab'
                    self._log(f"  Server supports resume. Resuming from {self._format_size(existing_size)}, total: {self._format_size(total_bytes)}")
                elif resp.status_code == 200:
                    total_bytes = int(resp.headers.get('content-length', 0))
                    downloaded = 0
                    existing_size = 0
                    file_mode = 'wb'
                    if existing_size > 0:
                        self._log("  Server doesn't support resume. Starting fresh.")
                else:
                    resp.raise_for_status()
                    return

                chunk_size = 65536  # 64KB chunks
                start_time = time.time()
                last_update_time = time.time()

                with open(part_path, file_mode) as f:
                    for chunk in resp.iter_content(chunk_size=chunk_size):
                        # --- Cancel check ---
                        if self.cancel_event.is_set():
                            self._log("Download cancelled. Partial file kept for resume.")
                            raise InterruptedError("Download cancelled.")

                        # --- Pause support ---
                        if self.pause_event.is_set():
                            self._log("Download paused. Waiting for resume...")
                            # Send paused status to UI
                            self._send_download_progress(
                                progress_context, downloaded / total_bytes if total_bytes > 0 else 0,
                                filename, downloaded, total_bytes, 0, "--:--", paused=True
                            )
                            while self.pause_event.is_set():
                                if self.cancel_event.is_set():
                                    raise InterruptedError("Download cancelled during pause.")
                                time.sleep(0.15)
                            self._log("Download resumed.")
                            start_time = time.time() - (downloaded - existing_size) / max(1, downloaded - existing_size)  # Reset speed calc
                            start_time = time.time()

                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                        now = time.time()
                        # Update UI at most 5x per second
                        if now - last_update_time > 0.2 or (total_bytes > 0 and downloaded >= total_bytes):
                            elapsed = now - start_time
                            net_downloaded = downloaded - existing_size
                            speed_bps = net_downloaded / elapsed if elapsed > 0.01 else 0
                            eta_s = (total_bytes - downloaded) / speed_bps if speed_bps > 0.1 and total_bytes > downloaded else 0
                            eta_str = self._format_eta(eta_s)
                            pct = downloaded / total_bytes if total_bytes > 0 else 0

                            self._send_download_progress(
                                progress_context, pct, filename,
                                downloaded, total_bytes, speed_bps, eta_str
                            )
                            last_update_time = now

            # Rename .part to final destination
            if os.path.exists(destination_path):
                os.remove(destination_path)
            os.rename(part_path, destination_path)

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error: {e}")
        except InterruptedError:
            raise  # Re-raise cancellation
        except Exception as e:
            raise IOError(f"Error writing downloaded file: {e}")

        final_size = self._format_size(downloaded)
        self._log(f"Download complete: {filename} ({final_size})")
        # Final progress update
        self._send_download_progress(progress_context, 1.0, filename, downloaded, downloaded, 0, "")
        if progress_context == "wizard_install":
            self._update_install_status(f"Download complete: {filename} ({final_size})")
        else:
            self._update_progress(0.4, f"Download complete: {final_size}")

    # --- Lógica de Actualización (MODIFICADA para usar _download_file) ---

    def _process_all_changelogs(self, versions_path, updates_to_apply):
        """Itera sobre las versiones a aplicar y envía la info al panel de changelog."""
        self._log("--- Iniciando procesamiento de Changelogs para todas las versiones ---")
        self._update_progress(0.55, "Analizando cambios...")
        total_versions = len(updates_to_apply)
        processed_versions = 0
        self.changelog_processed_items = set()

        for ver_float in updates_to_apply:
            processed_versions += 1
            ver_str = str(ver_float)
            if self.cancel_event.is_set():
                self._log(f"Cancelado durante análisis de changelog v{ver_str}.")
                raise InterruptedError(f"Cancelado durante análisis de changelog v{ver_str}.")

            self._log(f"  Procesando changelog para v{ver_str}...")
            progress = 0.55 + (processed_versions / total_versions) * 0.20
            self._update_progress(progress, f"Analizando cambios v{ver_str}...")
            update_version_path = os.path.join(versions_path, ver_str)

            # Procesar modsinfo.txt (Añadidos/Actualizados)
            mod_info_path = os.path.join(update_version_path, 'mods', 'modsinfo.txt')
            if os.path.exists(mod_info_path):
                self._log(f"    Leyendo modsinfo.txt para v{ver_str}...")
                self._process_mod_info(mod_info_path)
                time.sleep(0.5)
            else:
                self._log(f"    modsinfo.txt no encontrado para v{ver_str}.")

            # Procesar removedmods.txt (Eliminados)
            removed_mods_file = os.path.join(update_version_path, 'mods', 'removedmods.txt')
            if os.path.exists(removed_mods_file):
                self._log(f"    Leyendo removedmods.txt para v{ver_str}...")
                try:
                    with open(removed_mods_file, 'r', encoding='utf-8') as f_rem:
                        for line in f_rem:
                            if self.cancel_event.is_set(): raise InterruptedError(f"Cancelado leyendo removedmods.txt v{ver_str}.")
                            line_strip = line.strip()
                            if not line_strip: continue

                            parts = line_strip.split(maxsplit=1)
                            filename = parts[0]
                            display_name = parts[1] if len(parts) > 1 else os.path.basename(filename)
                            item_identifier = display_name

                            if filename.lower().endswith('.jar') and item_identifier not in self.changelog_processed_items:
                                self.changelog_processed_items.add(item_identifier)
                                if self.window:
                                    try:
                                        self._log(f"            - Enviando mod eliminado a JS: {display_name}")
                                        self.window.evaluate_js(f'addChangelogItem({json.dumps(display_name)}, null, null, null, "Removed")')
                                        time.sleep(0.05)
                                    except Exception as js_err:
                                        self._log(f"            - Error al enviar mod eliminado '{display_name}' a JS: {js_err}")
                except Exception as read_rem_err:
                    self._log(f"    Advertencia: No se pudo leer {os.path.basename(removed_mods_file)} para v{ver_str}: {read_rem_err}")
            else:
                self._log(f"    removedmods.txt no encontrado para v{ver_str}.")

            time.sleep(0.3)

        self._log("--- Fin del procesamiento de Changelogs ---")
        self._update_progress(0.75, "Análisis de cambios completo.")


    def _update_modpack_logic(self):
        """Lógica principal de actualización (Descargar, Extraer, Comparar, Aplicar)."""
        folder_path = self.instance_mc_path
        tmp_dir = None

        try:
            if not os.path.isdir(folder_path):
                raise FileNotFoundError(f"Carpeta instancia '{folder_path}' no existe.")

            # --- 1. Verificación de Versión ANTES de descargar ---
            self._log("Verificando versión del modpack...")
            self._update_progress(0.05, "Verificando versión...")

            user_version = 0.0
            try:
                user_version_files = [f for f in os.listdir(folder_path) if f.endswith('.txt') and re.match(r'^\d+(\.\d+)*\.txt$', f)]
                if user_version_files:
                    versions_found = [float(os.path.splitext(f)[0]) for f in user_version_files if re.fullmatch(r'\d+(\.\d+)*', os.path.splitext(f)[0])]
                    user_version = max(versions_found) if versions_found else 0.0
            except Exception as e:
                self._log(f"Advertencia: No se pudo leer la versión local: {e}")

            self._log(f"Versión actual local: {user_version}")

            try:
                response = requests.get(VERSION_URL, timeout=10)
                response.raise_for_status()
                latest_version_str = response.text.strip()
                latest_version = float(latest_version_str)
            except (requests.RequestException, ValueError) as e:
                self._log(f"Error crítico: No se pudo obtener la versión más reciente desde {VERSION_URL}: {e}")
                self._show_result(False, "Error de Red", "No se pudo comprobar la versión del modpack. Revisa tu conexión a internet.")
                return False

            self._log(f"Última versión disponible: {latest_version}")

            if user_version >= latest_version:
                self._log("El modpack ya está actualizado. Iniciando el juego...")
                self._update_progress(1.0, "Modpack ya actualizado.")
                time.sleep(1) # Pequeña pausa para que el usuario vea el mensaje
                return True

            # --- Si hay actualización, proceder con la descarga ---
            tmp_dir = tempfile.mkdtemp(prefix="vplus_update_")
            self._log(f"Directorio temporal: {tmp_dir}")

            # --- 2. Descarga --- (Progreso 0% a 40%)
            self._log("Descargando paquete de actualización...")
            self._update_progress(0, "Iniciando descarga...")
            zip_path = os.path.join(tmp_dir, "paquete.zip")

            self._download_file(REPO_ZIP_URL, zip_path, "modpack_update")

            self._log(f"Descarga completa ({os.path.getsize(zip_path) / (1024*1024):.2f} MB).")
            self._update_progress(0.4, "Descarga completa")

            # --- 3. Extracción --- (Progreso 40% a 50%)
            if self.cancel_event.is_set(): raise InterruptedError("Cancelado post-descarga.")
            self._log("Extrayendo paquete...")
            self._update_progress(0.45, "Extrayendo...")
            extract_target = os.path.join(tmp_dir, "extracted")
            versions_path = None
            try:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    if zf.testzip() is not None: raise zipfile.BadZipFile("ZIP corrupto.")
                    os.makedirs(extract_target, exist_ok=True)
                    zf.extractall(extract_target)
                    # Buscar la carpeta 'versions'
                    for root, dirs, _ in os.walk(extract_target):
                        if 'versions' in dirs:
                            versions_path = os.path.join(root, 'versions')
                            break
                    if versions_path is None:
                        raise FileNotFoundError("No se encontró la carpeta 'versions' en el ZIP.")
            except Exception as e:
                raise IOError(f"Error extrayendo ZIP: {e}")
            self._log("'versions' encontrada y validada.")
            self._update_progress(0.50, "Extracción completa.")

            # --- 4. Verificación de Versiones a Aplicar --- (Progreso 50% a 55%)
            if self.cancel_event.is_set(): raise InterruptedError("Cancelado post-extracción.")

            available_versions = []
            try:
                dirs = [v for v in os.listdir(versions_path) if os.path.isdir(os.path.join(versions_path, v))]
                available_versions_found = [float(v) for v in dirs if re.fullmatch(r'\d+(\.\d+)*', v)]
                if not available_versions_found:
                    raise FileNotFoundError("No hay carpetas de versión válidas en paquete.")
                available_versions = sorted(available_versions_found)
            except Exception as e:
                raise IOError(f"Error leyendo versiones del paquete: {e}")

            updates_to_apply = [v for v in available_versions if v > user_version]
            if not updates_to_apply:
                self._log("El paquete descargado no contiene una versión más nueva. Saltando actualización.")
                return True

            self._log(f"Versiones a aplicar: {updates_to_apply}")

            # --- 4. (NUEVO) Procesar TODOS los Changelogs ANTES de aplicar --- (Progreso 55% a 75%)
            if updates_to_apply:
                self._process_all_changelogs(versions_path, updates_to_apply)
                time.sleep(1) # Pausa después de mostrar changelog

            # --- 5. Aplicar Actualizaciones (Borrar y Copiar) --- (Progreso 75% a 95%)
            total_updates = len(updates_to_apply)
            self.added_files.clear(); self.removed_files.clear()
            for i, ver in enumerate(updates_to_apply):
                if self.cancel_event.is_set(): raise InterruptedError(f"Cancelado aplicando v{ver}.")
                progress = 0.75 + ((i + 1) / total_updates) * 0.20
                self._update_progress(progress, f"Aplicando v{ver} ({i+1}/{total_updates})...")
                self._log(f"--- Aplicando v{ver} ---")
                update_version_path = os.path.join(versions_path, str(ver))
                if not os.path.isdir(update_version_path):
                    self._log(f"Warn: Carpeta v{ver} no encontrada. Saltando."); continue

                # Fase Borrado
                self._log(f"  [{ver}] Procesando eliminaciones...")

                # (LÓGICA DE ELIMINACIÓN CORREGIDA)
                # Busca 'removed...' en las subcarpetas del paquete de actualización, no en la raíz.
                folders_to_check_for_removal = ['config', 'shaderpacks', 'mods']

                for folder_name in folders_to_check_for_removal:
                    removal_filename = f"removed{folder_name}.txt"
                    # Ruta al archivo de texto DENTRO de la carpeta de origen (p.ej. .../1.3/shaderpacks/removedshaderpacks.txt)
                    list_path = os.path.join(update_version_path, folder_name, removal_filename)

                    if os.path.exists(list_path):
                        self._log(f"    Procesando archivo de eliminación encontrado: '{folder_name}/{removal_filename}'...")
                        # Ruta a la carpeta de destino en la instancia del usuario (p.ej. .../minecraft/shaderpacks)
                        target_base_abs = os.path.join(folder_path, folder_name)

                        try:
                            with open(list_path, 'r', encoding='utf-8') as f_rem:
                                lines = [line.strip() for line in f_rem if line.strip()]

                            if "all" in [line.lower() for line in lines]:
                                self._log(f"      - [LOG] Palabra clave 'all' encontrada. Vaciando directorio '{folder_name}'.")

                                if os.path.exists(target_base_abs) and os.path.isdir(target_base_abs):
                                    bname = f"DIR_FULL_{folder_name}".replace(os.sep, '_')[:150]
                                    if not any(rf[0] == ("", folder_name) for rf in self.removed_files):
                                        try:
                                            bpath = os.path.join(self.backup_dir, bname)
                                            shutil.copytree(target_base_abs, bpath, dirs_exist_ok=True)
                                            self.removed_files.append((("", folder_name), bname))
                                            self._log(f"        - [LOG] Respaldo completo de '{folder_name}' creado.")
                                        except Exception as bk_err:
                                            self._log(f"        - ERROR CRÍTICO al respaldar '{folder_name}': {bk_err}. Saltando.")
                                            continue

                                    try:
                                        shutil.rmtree(target_base_abs)
                                        os.makedirs(target_base_abs)
                                        self._log(f"        - [LOG] Directorio '{folder_name}' vaciado con éxito.")
                                    except Exception as empty_err:
                                        raise IOError(f"No se pudo vaciar el directorio {folder_name}") from empty_err
                                else:
                                    self._log(f"      - [LOG] Directorio de destino '{folder_name}' no existe. No se necesita vaciar.")
                                continue

                            for item_rel in lines:
                                if self.cancel_event.is_set(): raise InterruptedError("Cancelado durante eliminación.")
                                item_abs_to_remove = os.path.join(target_base_abs, item_rel.replace('/', os.sep))
                                log_remove_path = os.path.join(folder_name, item_rel)

                                if os.path.exists(item_abs_to_remove):
                                    try:
                                        bname = log_remove_path.replace(os.sep, '_')[:150]
                                        if not any(rf[0] == (folder_name, item_rel) for rf in self.removed_files):
                                             bpath = os.path.join(self.backup_dir, bname)
                                             os.makedirs(os.path.dirname(bpath), exist_ok=True)
                                             if os.path.isdir(item_abs_to_remove): shutil.copytree(item_abs_to_remove, bpath, dirs_exist_ok=True)
                                             else: shutil.copy2(item_abs_to_remove, bpath)
                                             self.removed_files.append(((folder_name, item_rel), bname))

                                        if os.path.isdir(item_abs_to_remove): shutil.rmtree(item_abs_to_remove)
                                        else: os.remove(item_abs_to_remove)
                                        self._log(f"        - Eliminado: {log_remove_path}")
                                    except Exception as del_err:
                                        self._log(f"        - ERROR eliminando '{log_remove_path}': {del_err}")
                        except Exception as read_list_err:
                            self._log(f"    - ERROR leyendo lista '{removal_filename}': {read_list_err}")

                # Fase Copiado/Fusión
                if self.cancel_event.is_set(): raise InterruptedError(f"Cancelado antes de copiar v{ver}.")
                self._log(f"  [{ver}] Copiando/Fusionando archivos...")
                for item_name in os.listdir(update_version_path):
                    if self.cancel_event.is_set(): raise InterruptedError("Cancelado durante copia.")
                    src_item_path = os.path.join(update_version_path, item_name)
                    dest_item_path = os.path.join(folder_path, item_name)
                    if (item_name.startswith('removed') and item_name.endswith('.txt')) or \
                       item_name == 'modsinfo.txt' or item_name == 'resourcepackoptions.txt': continue
                    try:
                        if os.path.isdir(src_item_path):
                            os.makedirs(dest_item_path, exist_ok=True)
                            self._copy_and_backup_folder_contents(src_item_path, dest_item_path, item_name)
                        elif os.path.isfile(src_item_path):
                            self._backup_and_copy_file(src_item_path, dest_item_path, "")
                    except Exception as copy_err: self._log(f"        - ERROR procesando item raíz '{item_name}': {copy_err}")

                # Fase options.txt
                if self.cancel_event.is_set(): raise InterruptedError(f"Cancelado antes de options.txt v{ver}.")
                resourcepack_options_path = os.path.join(update_version_path, 'resourcepackoptions.txt')
                if os.path.exists(resourcepack_options_path):
                    self._log(f"  [{ver}] Actualizando options.txt para resource packs...")
                    user_options_path = os.path.join(folder_path, 'options.txt')
                    if os.path.exists(user_options_path):
                        try:
                            with open(resourcepack_options_path, 'r', encoding='utf-8') as f_new: new_rp_lines_content = f_new.read()
                            with open(user_options_path, 'r', encoding='utf-8') as f_user: user_options_content = f_user.read()
                            rp_match = re.search(r'^resourcePacks:(\[.*?\])$', new_rp_lines_content, re.MULTILINE | re.DOTALL); irp_match = re.search(r'^incompatibleResourcePacks:(\[.*?\])$', new_rp_lines_content, re.MULTILINE | re.DOTALL)
                            new_rp = rp_match.group(0) if rp_match else None; new_irp = irp_match.group(0) if irp_match else None
                            if not new_rp: continue
                            backup_unique_name = "ROOT_options.txt"
                            if not any(rf[0] == ("", "options.txt") for rf in self.removed_files):
                                try:
                                    backup_options_path = os.path.join(self.backup_dir, backup_unique_name); os.makedirs(os.path.dirname(backup_options_path), exist_ok=True); shutil.copy2(user_options_path, backup_options_path); self.removed_files.append((("", "options.txt"), backup_unique_name))
                                except Exception as bk_err: self._log(f"        - CRITICAL ERROR backing up options.txt: {bk_err}. Skipping update."); continue
                            modified_content = user_options_content; changed = False; pattern_rp = r'^resourcePacks:\[.*?\]$'; pattern_irp = r'^incompatibleResourcePacks:\[.*?\]$'
                            if re.search(pattern_rp, modified_content, re.MULTILINE | re.DOTALL): modified_content, c = re.subn(pattern_rp, new_rp, modified_content, 1, re.MULTILINE | re.DOTALL); changed |= c > 0
                            else: modified_content = modified_content.rstrip() + "\n" + new_rp + "\n"; changed = True
                            if new_irp:
                                if re.search(pattern_irp, modified_content, re.MULTILINE | re.DOTALL): modified_content, c = re.subn(pattern_irp, new_irp, modified_content, 1, re.MULTILINE | re.DOTALL); changed |= c > 0
                                else: modified_content = modified_content.rstrip() + "\n" + new_irp + "\n"; changed = True
                            if changed:
                                with open(user_options_path, 'w', encoding='utf-8') as f_user_w: f_user_w.write(modified_content)
                                if not any(af == ("", 'options.txt') for af in self.added_files): self.added_files.append(("", 'options.txt'))
                                self._log("        - options.txt actualizado.")
                        except Exception as opt_err: self._log(f"        - ERROR actualizando options.txt: {opt_err}")

            # --- 6. Finalización --- (Progreso 95% a 100%)
            if self.cancel_event.is_set(): raise InterruptedError("Cancelado después de aplicar versiones.")
            self._log("Finalizando actualización...")
            self._update_progress(0.98, "Finalizando...")
            if user_version_files:
                self._log("  Eliminando archivos .txt de versión antiguos...")
                for old_f in user_version_files:
                    try:
                        old_p = os.path.join(folder_path, old_f)
                        bname = f"ROOT_{old_f.replace(os.sep,'_')}"[:100]
                        bpath = os.path.join(self.backup_dir, bname)
                        if os.path.exists(old_p):
                            if not any(rf[0] == ("", old_f) for rf in self.removed_files):
                                os.makedirs(os.path.dirname(bpath), exist_ok=True)
                                shutil.copy2(old_p, bpath)
                                self.removed_files.append((("", old_f), bname))
                            os.remove(old_p)
                    except Exception as e: self._log(f"                - Advertencia: Fallo eliminando archivo de versión antiguo '{old_f}': {e}")

            final_version_num = latest_version
            new_fname = f'{final_version_num}.txt'; new_fpath = os.path.join(folder_path, new_fname)
            try:
                with open(new_fpath, 'w', encoding='utf-8') as f: f.write(f"Version: {final_version_num}\nUpdated by Launcher.")
                if not any(af == ("", new_fname) for af in self.added_files):
                    self.added_files.append(("", new_fname))
            except Exception as e: raise IOError(f"ERROR CRÍTICO creando archivo de versión final '{new_fname}': {e}")

            self._update_progress(1.0, f"Modpack actualizado a v{final_version_num}.")
            self._log(f"¡Éxito! Actualizado a v{final_version_num}.")
            return True

        # --- Manejo Errores y Limpieza ---
        except InterruptedError as e:
            self._log(f"Detenido: {e}"); self._revert_changes(); self._show_result(False, "Cancelado", f"{e}<br>Revertido."); return False
        except (FileNotFoundError, ValueError, IOError, ConnectionError, zipfile.BadZipFile, RuntimeError) as e:
            etype = type(e).__name__; msg = f"Error ({etype}): {e}"; self._log(f"--- ¡ERROR ({etype})! ---"); self._log(str(e)); self._log("--- Revertir ---"); self._revert_changes(); self._show_result(False, f"Error ({etype})", f"{msg}<br>Revertido."); return False
        except Exception as e:
            etype = type(e).__name__; msg = f"Error inesperado ({etype}): {e}"; self._log(f"--- ¡ERROR INESPERADO ({etype})! ---"); self._log(str(e)); import traceback; self._log(traceback.format_exc()); self._log("--- Revertir ---"); self._revert_changes(); self._show_result(False, "¡Error Inespero!", f"{msg}<br>Revertido. Revisa logs."); return False
        finally:
            if tmp_dir and os.path.exists(tmp_dir):
                try:
                    shutil.rmtree(tmp_dir)
                    self._log(f"Temporal '{os.path.basename(tmp_dir)}' eliminado.")
                except Exception as e:
                    self._log(f"Warn: Fallo eliminando temporal '{os.path.basename(tmp_dir)}': {e}")

    # --- Funciones Auxiliares para Copiar/Fusionar ---
    def _backup_and_copy_file(self, src_file, dest_file, base_rel_folder):
        """Respalda dest_file si existe, luego copia src_file a dest_file."""
        item_name = os.path.basename(src_file)
        rel_path_full = os.path.join(base_rel_folder, item_name) if base_rel_folder else item_name
        try:
            if os.path.exists(dest_file):
                backup_unique_name = rel_path_full.replace(os.sep, '_')[:150]
                backup_dest_abs_path = os.path.join(self.backup_dir, backup_unique_name)
                try:
                    if not any(rf[0] == (base_rel_folder, item_name) for rf in self.removed_files):
                        os.makedirs(os.path.dirname(backup_dest_abs_path), exist_ok=True)
                        shutil.copy2(dest_file, backup_dest_abs_path)
                        self.removed_files.append(((base_rel_folder, item_name), backup_unique_name))
                except Exception as bk_err:
                    self._log(f"                  - ERROR CRÍTICO al respaldar '{rel_path_full}': {bk_err}. Saltando copia.")
                    return

            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.copy2(src_file, dest_file)

            if not any(af == (base_rel_folder, item_name) for af in self.added_files):
                 self.added_files.append((base_rel_folder, item_name))
        except Exception as e:
            self._log(f"                  - ERROR COPIANDO archivo '{rel_path_full}': {e}")

    def _copy_and_backup_folder_contents(self, src_folder, dest_folder, base_rel_folder):
        """Copia recursivamente contenidos de src a dest, respaldando antes de sobrescribir."""
        if self.cancel_event.is_set(): raise InterruptedError("Cancelado durante fusión.")
        os.makedirs(dest_folder, exist_ok=True)

        for item_name in os.listdir(src_folder):
            if self.cancel_event.is_set(): raise InterruptedError("Cancelado.")

            src_item_path = os.path.join(src_folder, item_name)
            dest_item_path = os.path.join(dest_folder, item_name)
            current_rel_path = os.path.join(base_rel_folder, item_name)

            # (CORREGIDO) Excluir todos los archivos 'removed...txt' de ser copiados.
            if item_name.lower().startswith('removed') and item_name.lower().endswith('.txt'):
                self._log(f"                  - Ignorando archivo de control: {os.path.join(base_rel_folder, item_name)}")
                continue

            if item_name.lower() == 'modsinfo.txt' and base_rel_folder.lower() == 'mods':
                continue

            try:
                if os.path.isdir(src_item_path):
                    self._copy_and_backup_folder_contents(src_item_path, dest_item_path, current_rel_path)
                elif os.path.isfile(src_item_path):
                    self._backup_and_copy_file(src_item_path, dest_item_path, base_rel_folder)
            except InterruptedError: raise
            except Exception as e:
                self._log(f"                  - ERROR procesando sub-item '{current_rel_path}': {e}")

    def _get_mod_details(self, filename, url, status):
        """Obtiene detalles del mod desde Modrinth API si es posible."""
        title = filename
        description = "Añadido o actualizado en esta versión."
        icon_url = None
        item_identifier = filename
        self._log(f"    [Changelog] Procesando: '{filename}', URL: '{url}', Status: {status}")

        try:
            if url and status != "Removed" and "modrinth.com/mod/" in url:
                slug_match = re.search(r"modrinth\.com/mod/([^/]+)", url)
                if slug_match:
                    slug = slug_match.group(1)
                    self._log(f"                - Es Modrinth. Obteniendo info para slug: '{slug}'")
                    api_url = f"https://api.modrinth.com/v2/project/{slug}"
                    headers = {'User-Agent': 'Kewz/VanillaPlusLauncher/1.0 (launcher@example.com)'}
                    try:
                        self._log(f"                - Llamando Modrinth API: {api_url}")
                        mod_resp = requests.get(api_url, headers=headers, timeout=5)
                        self._log(f"                - Modrinth API response: {mod_resp.status_code}")
                        mod_resp.raise_for_status()
                        data = mod_resp.json()
                        title = data.get('title', filename)
                        item_identifier = title
                        description = data.get('description', description)
                        icon_url = data.get('icon_url', None)
                        self._log(f"                - Info obtenida: '{title}' (Icono: {'Sí' if icon_url else 'No'})")
                    except requests.exceptions.Timeout:
                         self._log(f"                - ERROR API Modrinth: Timeout para '{slug}'. Usando datos por defecto.")
                    except requests.exceptions.RequestException as e:
                        status_code = f" (Status: {e.response.status_code})" if e.response is not None else ""
                        self._log(f"                - ERROR API Modrinth{status_code}: {e}. Usando datos por defecto.")
                    except Exception as e:
                        self._log(f"                - ERROR inesperado procesando respuesta Modrinth: {e}. Usando datos por defecto.")
                else:
                    self._log(f"                - URL parece de Modrinth pero no se pudo extraer slug: '{url}'. Usando datos por defecto.")
            elif status == "Removed":
                item_identifier = title
                description = "Eliminado en esta versión."
                icon_url = None
                self._log(f"                - Mod marcado como eliminado. Usando nombre: '{title}'")
            else:
                self._log(f"                - URL no es de Modrinth o no disponible. Usando datos por defecto para: '{filename}'")
        except Exception as e:
            self._log(f"                - Error procesando URL/Slug: {e}")

        if item_identifier in self.changelog_processed_items:
            self._log(f"                - Item '{item_identifier}' ya procesado para UI. Saltando envío a JS.")
            return

        self.changelog_processed_items.add(item_identifier)
        final_description = description if isinstance(description, str) else "Info no disponible."
        if self.window:
            log_desc = (final_description[:30] + '...') if len(final_description) > 30 else final_description
            self._log(f"                - Enviando a JS: Title='{title}', Desc='{log_desc}', Icon='{icon_url}', URL='{url}', Status='{status}'")
            try:
                self.window.evaluate_js(f'addChangelogItem({json.dumps(title)}, {json.dumps(final_description)}, {json.dumps(icon_url)}, {json.dumps(url)}, {json.dumps(status)})')
            except Exception as e:
                self._log(f"                - ERROR CRÍTICO al llamar a JS addChangelogItem para '{title}': {e}")

    def _process_mod_info(self, mod_info_path):
        """Lee modsinfo.txt y llama a _get_mod_details con status 'Updated'."""
        try:
            with open(mod_info_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            self._log(f"    Procesando {len(lines)} líneas de modsinfo.txt...")
            mods_found = 0
            threads = []
            for line_num, line in enumerate(lines, 1):
                if self.cancel_event.is_set():
                    self._log("      - Cancelado durante procesamiento de modsinfo.txt")
                    return
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    filename, url = parts
                    if filename.lower().endswith('.jar'):
                        mods_found += 1
                        self._log(f"      - Línea {line_num}: Detectado mod '{filename}', URL: '{url}'. Iniciando thread...")
                        thread = threading.Thread(target=self._get_mod_details, args=(filename, url, "Updated"), daemon=True)
                        threads.append(thread)
                        thread.start()
                        time.sleep(0.15)
                    else:
                        self._log(f"      - Línea {line_num}: Ignorando (no es .jar): '{filename}'")
                else:
                    self._log(f"                - Advertencia: Línea {line_num} malformada en modsinfo.txt: '{line}'")

            self._log(f"    {mods_found} mods procesados desde modsinfo.txt.")
        except FileNotFoundError:
             self._log(f"      - ERROR: No se encontró el archivo modsinfo.txt en: {mod_info_path}")
        except Exception as e:
             self._log(f"      - ERROR al procesar modsinfo.txt: {e}")


# --- Punto de Entrada Principal ---

def main():
    api = ModpackLauncherAPI()
    window_title = "Vanilla+ Launcher"
    try:
        window = webview.create_window(
            window_title,
            html=HTML_CONTENT,
            js_api=api,
            width=900,
            height=650,
            resizable=False,
            fullscreen=True,
            min_size=(800, 600)
        )
        api.window = window
        print(f"Ventana '{window_title}' creada. Iniciando WebView...")

        # Mantenemos http_server=True
        webview.start(debug=False, http_server=True)

        print("WebView cerrado.")

    except Exception as e:
       print(f"--- ERROR FATAL AL INICIAR WEBVIEW ---")
       print(f"Error: {e}")
       import traceback
       print(traceback.format_exc())
       try:
           import importlib
           tk_spec = importlib.util.find_spec("tkinter")
           if tk_spec:
               import tkinter as tk
               from tkinter import messagebox
               root = tk.Tk()
               root.withdraw()
               messagebox.showerror("Error Crítico del Launcher", f"No se pudo iniciar la interfaz gráfica.\n\nError: {e}\n\nRevisa la consola para más detalles.")
               root.destroy()
           else:
               print("tkinter no encontrado. No se puede mostrar mensaje gráfico.")
       except Exception as tk_e: print(f"Error adicional al intentar mostrar mensaje con tkinter: {tk_e}")
       sys.exit(1)

if __name__ == "__main__":
    # (NUEVO) Redirigir stdout/stderr a un archivo si se ejecuta como .exe compilado
    if getattr(sys, 'frozen', False):
        try:
            log_file_path = os.path.join(os.path.dirname(sys.executable), 'launcher_output.log')
            sys.stdout = open(log_file_path, 'w', encoding='utf-8')
            sys.stderr = sys.stdout
        except Exception as e:
            # Si no podemos crear el log, no hay mucho que podamos hacer, pero lo intentamos.
            pass

    # (NUEVO) Lógica para solicitar permisos de Administrador en Windows
    if IS_WINDOWS and ctypes:
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("Permisos de administrador no detectados. Solicitando...")
                # Relanzar el script con permisos de administrador
                script_path = os.path.abspath(sys.argv[0])
                params = " ".join([f'"{arg}"' for arg in sys.argv])

                # 'runas' es el verbo para solicitar elevación (UAC)
                ret = ctypes.windll.shell32.ShellExecuteW(
                    None,           # hwnd
                    "runas",        # lpVerb
                    sys.executable, # lpFile (el intérprete de python)
                    f'"{script_path}" {params}', # lpParameters
                    None,           # lpDirectory
                    1               # nShowCmd
                )

                if ret > 32:
                    print("Solicitud de elevación enviada. Cerrando instancia actual.")
                    sys.exit(0) # Salir de la instancia no-admin
                else:
                    print(f"Error al solicitar permisos de administrador. Código: {ret}")
                    # (Opcional) Mostrar un error gráfico aquí si falla
            else:
                print("El script ya se está ejecutando como administrador.")
        except Exception as e:
            print(f"Error al comprobar/solicitar permisos de administrador: {e}")
            # Decidir si continuar o salir
            # Por ahora, continuaremos, pero winget fallará.

    # --- Fin del chequeo de admin ---

    try:
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))

        os.chdir(script_dir)
    except Exception as e:
        print(f"ADVERTENCIA: No se pudo cambiar el directorio de trabajo: {e}")

    print(f"Iniciando Vanilla+ Launcher... WD: {os.getcwd()}")

    # --- (NUEVO) Lógica para manejar el reinicio post-actualización ---
    if "--post-update" in sys.argv:
        print("Argumento --post-update detectado. Limpiando archivos de bloqueo antiguos...")
        time.sleep(2) # Dar tiempo a que el proceso antiguo termine completamente
        temp_dir_for_cleanup = tempfile.gettempdir()
        old_pid_file = os.path.join(temp_dir_for_cleanup, 'vplus_launcher.pid')
        old_lock_file = os.path.join(temp_dir_for_cleanup, 'vplus_launcher.lock')
        try:
            if os.path.exists(old_lock_file):
                os.remove(old_lock_file)
                print(f"Archivo de bloqueo antiguo eliminado: {old_lock_file}")
            if os.path.exists(old_pid_file):
                os.remove(old_pid_file)
                print(f"Archivo PID antiguo eliminado: {old_pid_file}")
        except Exception as e:
            print(f"Advertencia: No se pudieron eliminar los archivos de bloqueo antiguos: {e}")
        print("Limpieza completada. Continuando con el inicio normal...")


    # --- Lógica de Instancia Única Mejorada (Auto-Kill) ---
    temp_dir = tempfile.gettempdir()
    pid_file_path = os.path.join(temp_dir, 'vplus_launcher.pid')
    lock_file_path = os.path.join(temp_dir, 'vplus_launcher.lock')
    lock_file_handle = None

    def acquire_lock():
        try:
            flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | getattr(os, 'O_BINARY', 0)
            handle = os.open(lock_file_path, flags)
            print(f"Archivo de bloqueo creado: {lock_file_path}")
            try:
                with open(pid_file_path, 'w') as f:
                    f.write(str(os.getpid()))
            except Exception as e:
                print(f"Advertencia: No se pudo escribir el PID file: {e}")
            return handle
        except OSError as e:
            if e.errno == 17: # EEXIST
                return None
            else:
                raise e

    lock_file_handle = acquire_lock()

    if lock_file_handle is None:
        print("Archivo de bloqueo detectado. Intentando matar instancia anterior automáticamente...")
        old_pid = None
        try:
            if os.path.exists(pid_file_path):
                with open(pid_file_path, 'r') as f:
                    old_pid_str = f.read().strip()
                    if old_pid_str.isdigit():
                        old_pid = int(old_pid_str)
        except Exception as e:
            print(f"Error leyendo PID anterior: {e}")

        if old_pid:
            print(f"Terminando proceso anterior (PID: {old_pid})...")
            try:
                if platform.system() == "Windows":
                    subprocess.run(["taskkill", "/PID", str(old_pid), "/F"], check=False, capture_output=True)
                else:
                    try:
                        os.kill(old_pid, 9)
                    except ProcessLookupError:
                        pass # Ya no existe
                print("Proceso terminado (o intento realizado).")
                time.sleep(1) # Esperar liberación de recursos
            except Exception as kill_err:
                print(f"Fallo al matar proceso: {kill_err}")

        # Limpiar locks antiguos
        try:
            if os.path.exists(lock_file_path): os.remove(lock_file_path)
            if os.path.exists(pid_file_path): os.remove(pid_file_path)
        except Exception as e:
            print(f"Error limpiando archivos de lock: {e}")

        # Reintentar adquirir lock
        try:
            lock_file_handle = acquire_lock()
            if lock_file_handle is None:
                print("Error: No se pudo adquirir el lock incluso después de matar la instancia anterior.")
                sys.exit(1)
            print("Lock adquirido exitosamente tras limpieza.")
        except Exception as e:
            print(f"Error fatal al re-adquirir lock: {e}")
            sys.exit(1)

    # --- Ejecución Principal ---
    try:
        main()
    except Exception as main_err:
       print(f"--- ERROR INESPERADO EN MAIN ---")
       print(f"Error: {main_err}")
       import traceback
       print(traceback.format_exc())
       try:
           import importlib
           if importlib.util.find_spec("tkinter"):
               import tkinter as tk; from tkinter import messagebox
               root = tk.Tk(); root.withdraw()
               messagebox.showerror("Error Inesperado del Launcher", f"Ocurrió un error inesperado durante la ejecución:\n\n{main_err}\n\nRevisa la consola para más detalles.")
               root.destroy()
       except Exception: pass
    finally:
        if lock_file_handle is not None:
            try:
                os.close(lock_file_handle)
                os.remove(lock_file_path)
                print(f"Archivo de bloqueo eliminado: {lock_file_path}")
            except Exception as clean_err:
                print(f"Advertencia: No se pudo eliminar archivo de bloqueo '{lock_file_path}': {clean_err}")
        try:
            if os.path.exists(pid_file_path):
                current_pid = str(os.getpid())
                pid_in_file = "";
                try:
                    with open(pid_file_path, 'r') as f: pid_in_file = f.read().strip()
                except Exception: pass
                if pid_in_file == current_pid:
                    os.remove(pid_file_path)
                    print(f"Archivo PID eliminado: {pid_file_path}")
                elif pid_in_file:
                    print(f"Advertencia: PID en archivo ({pid_in_file}) no coincide con PID actual ({current_pid}). No se eliminó PID file.")
        except Exception as clean_err:
            print(f"Advertencia: No se pudo eliminar archivo PID '{pid_file_path}': {clean_err}")

        print("Launcher finalizado.")
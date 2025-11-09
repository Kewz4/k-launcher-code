import os
import sys

# --- HTML Content Definition ---

FONT_IMPORT_URL = f"https://fonts.googleapis.com/css2?family={'&family='.join(f.replace(' ', '+') for f in ['Inter:wght@400;500;700;900', 'Montserrat:wght@900'])}&display=swap"
FONT_AWESOME_URL = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
LOGO_URL = "https://gitlab.com/Kewz4/kewz-launcher/-/raw/main/minecraftlogo.png"
URL_ALBUM_COVER = "https://gitlab.com/Kewz4/kewz-launcher/-/raw/148f8426c0b238c82ff1d52cab94f0abbcb23685/albumcover.png"
VIMEO_EMBED_SRC = "https://player.vimeo.com/video/1131522974?badge=0&autopause=0&player_id=0&app_id=58479&background=1&autoplay=1&loop=1&muted=1"


# (CORREGIDO) HTML_CONTENT es ahora un f-string para inyectar variables directamente.
# Todas las llaves literales de CSS/JS deben escaparse con {{ y }}.
HTML_CONTENT = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vanilla+ Launcher</title>
    <link rel="stylesheet" href="{FONT_IMPORT_URL}">
    <link rel="stylesheet" href="{FONT_AWESOME_URL}">
    <style>
        /* --- Reset y Fuentes --- */
        :root {{
            --font-family-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --font-family-display: 'Montserrat', sans-serif;
            --color-bg: #000000;
            --color-bg-light: #1e1e1e;
            --color-bg-lighter: #2a2a2a;
            --color-text: #e0e0e0;
            --color-text-muted: #888;
            /* Paleta dorada */
            --color-accent: #eebd3b;
            --color-accent-dark: #b65009;
            --color-danger: #e53935;
            --color-danger-dark: #b71c1c;
            --color-success: #43a047;
            --color-success-dark: #2e7d32;
            --radius-md: 8px;
            --radius-lg: 12px;
            --radius-btn: 11px;
            --shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            /* Colores botones */
            --play-btn-grad-start: #b65009;
            --play-btn-grad-end: #eebd3b;
            --cancel-btn-grad-start: #b71c1c;
            --cancel-btn-grad-end: #e53935;

            --menu-btn-fill-start: #000000;
            --menu-btn-fill-end: #383737;
            --menu-btn-stroke-start: #000000;
            --menu-btn-stroke-end: #b4b4b3;
            /* Panel lateral */
            --panel-bg: #1a1a1a;
            --panel-width: 280px;
            /* Altura y ancho del reproductor para cálculo */
            --player-height: 80px;
            --player-width: 300px;
            /* Sombra para texto del reproductor */
            --player-text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ width: 100%; height: 100%; font-family: var(--font-family-sans); background-color: var(--color-bg); color: var(--color-text); overflow: hidden; user-select: none; display: flex; align-items: center; justify-content: center; }}

        /* --- Animaciones --- */
        @keyframes fadeOut {{ from {{ opacity: 1; }} to {{ opacity: 0; }} }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        @keyframes shake {{ 0%, 100% {{ transform: translateX(0); }} 25% {{ transform: translateX(-5px); }} 75% {{ transform: translateX(5px); }} }}
        @keyframes modalSlideIn {{ from {{ opacity: 0; transform: translateY(30px) scale(0.95); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes fadeOutOverlay {{
            0% {{ opacity: 1; }}
            90% {{ opacity: 1; }}
            100% {{ opacity: 0; }}
        }}

        /* --- Overlay de Carga Inicial --- */
        .loading-overlay {{ display: flex; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: var(--color-bg); align-items: center; justify-content: center; flex-direction: column; z-index: 10000; color: white; padding: 20px; text-align: center; }}
        .loading-overlay h1 {{ font-size: 24px; font-weight: 700; color: var(--color-accent); margin-bottom: 15px; }}
        .loading-overlay p {{ font-size: 14px; color: var(--color-text-muted); max-width: 80%; word-wrap: break-word; }}
        .spinner {{ width: 50px; height: 50px; border: 5px solid var(--color-bg-lighter); border-top-color: var(--color-accent); border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px; }}

        /* --- Contenedor Principal (Setup / Settings) --- */
        .container {{ width: 100%; max-width: 650px; background-color: var(--color-bg-light); border-radius: var(--radius-lg); box-shadow: var(--shadow); padding: 24px 32px; border: 1px solid var(--color-bg-lighter); transition: opacity 0.3s ease; position: relative; z-index: 101; display: none; }}
        .container.visible {{ display: block; }}
        .header {{ text-align: center; margin-bottom: 24px; }}
        .header h1 {{ font-size: 28px; font-weight: 700; background: linear-gradient(90deg, var(--color-accent-dark), var(--color-accent)); -webkit-background-clip: text; background-clip: text; color: transparent; -webkit-text-fill-color: transparent; margin-bottom: 4px; }}
        .header p {{ font-size: 14px; color: var(--color-text-muted); }}

        /* --- Pantallas (Contenedores generales) --- */
        .screen {{ display: none; }}
        .screen.active {{ /* display set dynamically */ animation: fadeIn 0.5s ease; }}

        /* --- (RENOMBRADO) Pantalla de Ajustes (Post-Setup) --- */
        #screen-settings .setup-label {{ font-size: 16px; font-weight: 500; margin-bottom: 8px; margin-top: 16px; display: block; }}
        #screen-settings .folder-display {{ display: flex; align-items: center; background-color: var(--color-bg); border-radius: var(--radius-md); padding: 12px 16px; border: 2px dashed var(--color-bg-lighter); margin-bottom: 12px; transition: all 0.3s ease; min-height: 48px; cursor: default; }}
        #screen-settings .folder-display.dragover {{ border-color: var(--color-accent); background-color: rgba(238, 189, 59, 0.1); }}
        #screen-settings .folder-display.valid {{ border-style: solid; border-color: var(--color-success-dark); background-color: rgba(67, 160, 71, 0.1); }}
        #screen-settings .folder-display.invalid {{ border-style: solid; border-color: var(--color-danger-dark); background-color: rgba(229, 57, 53, 0.1); }}
        #screen-settings .folder-display span {{ flex-grow: 1; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.4; pointer-events: none; }}
        #screen-settings .folder-display span.placeholder {{ color: var(--color-text-muted); font-style: italic; }}
        #screen-settings .folder-buttons {{ display: grid; grid-template-columns: 1fr; gap: 12px; }}
        #screen-settings #save-settings-btn {{ margin-top: 24px; }}

        /* --- (NUEVO) Asistente de Configuración Inicial --- */
        #screen-initial-setup .wizard-step {{ display: none; }}
        #screen-initial-setup .wizard-step.active {{ display: block; animation: fadeIn 0.3s ease-out; }}
        #screen-initial-setup .wizard-step-content {{ text-align: center; }}
        #screen-initial-setup .wizard-step-content p {{ font-size: 15px; color: var(--color-text); margin-bottom: 24px; line-height: 1.6; }}
        #screen-initial-setup .wizard-buttons-horizontal {{ display: flex; gap: 16px; justify-content: center; }}
        #screen-initial-setup .wizard-buttons-horizontal .btn {{ flex: 1; }}
        #screen-initial-setup .wizard-spinner {{ width: 40px; height: 40px; border: 4px solid var(--color-bg-lighter); border-top-color: var(--color-accent); border-radius: 50%; animation: spin 1s linear infinite; margin: 10px auto 20px auto; }}
        
        /* (NUEVO) Consola y progreso para el asistente */
        #wizard-progress-container {{ display: flex; flex-direction: column; gap: 12px; margin-top: 20px; }}
        #wizard-console {{ height: 250px; background-color: var(--color-bg); border-radius: var(--radius-md); border: 1px solid var(--color-bg-lighter); padding: 12px; overflow-y: auto; font-family: 'Menlo', 'Courier New', monospace; font-size: 12px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; scrollbar-width: thin; scrollbar-color: var(--color-bg-lighter) var(--color-bg); user-select: text; cursor: text; text-align: left; }}
        #wizard-console p {{ margin-bottom: 4px; word-break: break-all; user-select: text; font-size: 12px !important; color: var(--color-text-muted) !important; }}
        #wizard-console p:last-child {{ margin-bottom: 0; }}
        
        #wizard-progress-bar-container {{ width: 100%; height: 10px; background-color: var(--color-bg); border-radius: 5px; overflow: hidden; }}
        #wizard-progress-bar-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, var(--color-accent-dark), var(--color-accent)); border-radius: 5px; transition: width 0.3s ease; }}
        #wizard-progress-label {{ font-size: 12px; color: var(--color-text-muted); text-align: center; height: 16px; }}
        #wizard-step-install-progress .btn, #wizard-step-install-modpack .btn {{ margin-top: 16px; }}


        /* --- Pantalla 2: JUGAR --- */
        #screen-play {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
            z-index: 50; overflow: hidden; background-color: #000;
            padding: 40px 20px; padding-bottom: calc(var(--player-height) + 30px);
        }}
        #screen-play.active {{ z-index: 100; }}

        #vimeo-bg {{
            position: absolute; top: 50%; left: 50%;
            width: 100vw; height: 56.25vw; /* 16:9 ratio */
            min-height: 100vh; min-width: 177.77vh; /* 16:9 ratio */
            transform: translate(-50%, -50%);
            z-index: -1; pointer-events: none; border: none;
        }}
        #video-overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-color: var(--color-bg);
            z-index: 0; pointer-events: none;
            animation: fadeOutOverlay 3s ease-out forwards;
        }}

        #minecraft-logo {{
            display: block; width: 90%; max-width: 1000px; height: auto;
            object-fit: contain; z-index: 1; pointer-events: none;
            margin: 0 auto; margin-top: 1%;
        }}
        #bottom-gradient {{
            position: absolute; bottom: 0; left: 0; width: 100%; height: 150px;
            background: linear-gradient(to top, rgba(0,0,0,1) 30%, rgba(0,0,0,0.7) 60%, transparent);
            z-index: 0; pointer-events: none;
        }}

        #play-btn {{
            position: fixed; bottom: 15px; left: 50%;
            transform: translateX(-50%);
            font-family: var(--font-family-display); font-weight: 900; font-size: 28px;
            color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            padding: 12px 50px; border-radius: var(--radius-btn);
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease, background-image 0.3s ease;
            z-index: 101;
            background-image: linear-gradient(30deg, var(--play-btn-grad-start), var(--play-btn-grad-end));
            border: none; box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }}
        #play-btn::before {{ content: ''; position: absolute; inset: -6px; border-radius: calc(var(--radius-btn) + 6px); background-image: linear-gradient(90deg, var(--play-btn-grad-start), var(--play-btn-grad-end)); z-index: -1; padding: 6px; -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); -webkit-mask-composite: xor; mask-composite: exclude; transition: background-image 0.3s ease; }}
        #play-btn:hover {{ transform: translateX(-50%) scale(1.03); box-shadow: 0 8px 20px rgba(0,0,0,0.4); }}
        #play-btn:active {{ transform: translateX(-50%) scale(0.98); box-shadow: 0 3px 10px rgba(0,0,0,0.2); }}

        #play-btn.cancel-mode {{
            background-image: linear-gradient(30deg, var(--cancel-btn-grad-start), var(--cancel-btn-grad-end));
        }}
        #play-btn.cancel-mode::before {{
            background-image: linear-gradient(90deg, var(--cancel-btn-grad-start), var(--cancel-btn-grad-end));
        }}


        #menu-btn {{ position: absolute; top: 20px; left: 20px; right: auto; width: 50px; height: 50px; border-radius: var(--radius-btn); cursor: pointer; z-index: 102; display: flex; flex-direction: column; justify-content: space-around; align-items: center; padding: 10px; transition: transform 0.2s ease; background-image: linear-gradient(84deg, var(--menu-btn-fill-start), var(--menu-btn-fill-end)); border: none; }}
        #menu-btn::before {{ content: ''; position: absolute; inset: -3px; border-radius: calc(var(--radius-btn) + 3px); background-image: linear-gradient(62deg, var(--menu-btn-stroke-start), var(--menu-btn-stroke-end)); z-index: -1; padding: 3px; -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); -webkit-mask-composite: xor; mask-composite: exclude; }}
        #menu-btn .menu-line {{ width: 70%; height: 3px; background-color: var(--color-text); border-radius: 2px; transition: background-color 0.2s ease; }}
        #menu-btn:hover {{ transform: scale(1.05); }}
        #menu-btn:active {{ transform: scale(0.95); }}

        /* --- Estilos Reproductor de Música --- */
        #music-player {{
            position: fixed; bottom: 15px; left: 15px;
            width: var(--player-width); height: var(--player-height);
            background-color: rgba(30, 30, 30, 0.5);
            backdrop-filter: blur(5px);
            border-radius: var(--radius-md);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: var(--shadow);
            z-index: 2000; /* (CORREGIDO) Aumentado para estar por encima de todo */
            display: none;
            flex-direction: column;
            padding: 8px 10px; overflow: visible;
            color: var(--color-text); text-shadow: var(--player-text-shadow);
            transition: background-color 0.3s ease;
        }}
        #music-player:hover {{
             background-color: rgba(40, 40, 40, 0.7);
        }}
        #music-player.visible {{
            display: flex;
            animation: fadeIn 0.5s ease forwards;
        }}
        .player-top-row {{ display: flex; align-items: center; gap: 10px; width: 100%; height: 50px; }}
        #album-cover {{ width: 50px; height: 50px; border-radius: 4px; object-fit: cover; flex-shrink: 0; background-color: var(--color-bg-lighter); box-shadow: 0 2px 5px rgba(0,0,0,0.4); }}
        .track-info {{ flex-grow: 1; overflow: hidden; display: flex; flex-direction: column; justify-content: center; }}
        #track-title {{ font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--color-text); }}
        #track-artist {{ font-size: 11px; color: var(--color-text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .controls {{ display: flex; align-items: center; gap: 5px; flex-shrink: 0; }}
        .control-btn {{ background: none; border: none; color: var(--color-text-muted); font-size: 16px; cursor: pointer; padding: 5px; transition: color 0.2s ease; text-shadow: var(--player-text-shadow); }}
        .control-btn:hover {{ color: var(--color-accent); }}
        .control-btn#play-pause-btn i.fa-pause {{ display: none; }}
        .playing .control-btn#play-pause-btn i.fa-play {{ display: none; }}
        .playing .control-btn#play-pause-btn i.fa-pause {{ display: inline-block; }}
        .player-bottom-row {{ display: flex; align-items: center; gap: 8px; width: 100%; margin-top: 5px; }}
        #progress-container {{ flex-grow: 1; height: 4px; background-color: rgba(255, 255, 255, 0.2); border-radius: 2px; cursor: pointer; overflow: hidden; position: relative; }}
        #progress-bar {{ width: 0%; height: 100%; background-color: var(--color-accent); border-radius: 2px; transition: width 0.1s linear; }}
        #volume-container {{ display: flex; align-items: center; gap: 5px; position: relative; }}
        #volume-icon {{ color: var(--color-text-muted); font-size: 14px; width: 15px; text-align: center; cursor: pointer; transition: color 0.2s ease; text-shadow: var(--player-text-shadow); }}
        #volume-icon:hover {{ color: var(--color-accent); }}
        #volume-slider {{
            width: 0; opacity: 0; overflow: hidden; height: 4px; cursor: pointer;
            appearance: none; -webkit-appearance: none;
            background: rgba(255, 255, 255, 0.2); border-radius: 2px; outline: none;
            transition: width 0.3s ease, opacity 0.3s ease;
            margin-left: 5px;
        }}
        #volume-container:hover #volume-slider {{ width: 60px; opacity: 1; }}
        #volume-slider::-webkit-slider-thumb {{ appearance: none; -webkit-appearance: none; width: 10px; height: 10px; background: var(--color-accent); border-radius: 50%; cursor: pointer; }}
        #volume-slider::-moz-range-thumb {{ width: 10px; height: 10px; background: var(--color-accent); border-radius: 50%; cursor: pointer; border: none; }}

        /* --- Panel Lateral --- */
        #side-panel {{ position: fixed; top: 0; left: 0; width: var(--panel-width); height: 100%; background-color: var(--panel-bg); border-right: 1px solid var(--color-bg-lighter); box-shadow: 5px 0 15px rgba(0,0,0,0.3); transform: translateX(-100%); transition: transform 0.3s ease-in-out; z-index: 1000; padding-top: 80px; display: flex; flex-direction: column; gap: 10px; padding-left: 15px; padding-right: 15px; }}
        #side-panel.panel-open {{ transform: translateX(0); }}
        .panel-button {{ display: flex; align-items: center; gap: 15px; padding: 15px; background-color: var(--color-bg-lighter); color: var(--color-text); border: none; border-radius: var(--radius-md); cursor: pointer; transition: background-color 0.2s ease; text-align: left; font-size: 16px; }}
        .panel-button:hover {{ background-color: #3a3a3a; }}
        .panel-button i {{ font-size: 18px; width: 20px; text-align: center; color: var(--color-text-muted); }}
        #panel-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 999; opacity: 0; visibility: hidden; transition: opacity 0.3s ease, visibility 0s 0.3s linear; }}
        #panel-overlay.visible {{ opacity: 1; visibility: visible; transition: opacity 0.3s ease; }}

        /* --- Pantalla de Progreso (Overlay) --- */
        #screen-progress {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; display: none; align-items: center; justify-content: center; background-color: rgba(0, 0, 0, 0.85); backdrop-filter: blur(4px); z-index: 101; padding: 20px; }}
        #screen-progress.active {{ display: flex; flex-direction: column; }}
        .progress-content-wrapper {{ position: relative; width: 100%; max-width: 900px; background-color: var(--color-bg-light); border-radius: var(--radius-lg); box-shadow: var(--shadow); padding: 24px 32px; border: 1px solid var(--color-bg-lighter); }}
        
        #minimize-progress-btn {{
            position: absolute; top: 16px; right: 16px; width: 32px; height: 32px;
            background-color: var(--color-bg-lighter); border: none; border-radius: 50%;
            color: var(--color-text-muted); font-size: 16px; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            transition: all 0.2s ease; z-index: 10;
        }}
        #minimize-progress-btn:hover {{ background-color: #3a3a3a; color: var(--color-text); transform: scale(1.1); }}
        #minimize-progress-btn i {{ font-weight: 900; }}

        #progress-title {{ text-align: center; font-weight: 500; font-size: 20px; margin-bottom: 15px; color: var(--color-text); }}
        .progress-columns {{ display: flex; gap: 16px; margin-top: 16px; }}
        #console-container {{ flex: 2; display: flex; flex-direction: column; min-width: 0; position: relative; }}
        #changelog-container {{ flex: 1; min-width: 0; background-color: var(--color-bg); border-radius: var(--radius-md); border: 1px solid var(--color-bg-lighter); height: 300px; display: flex; flex-direction: column; }}
        #changelog-container h3 {{ font-size: 14px; font-weight: 500; color: var(--color-text-muted); padding: 12px; border-bottom: 1px solid var(--color-bg-lighter); text-align: center; }}
        #changelog-content {{ overflow-y: auto; flex-grow: 1; padding: 8px; }}
        .changelog-item {{ display: flex; align-items: center; gap: 10px; padding: 8px; border-radius: var(--radius-md); transition: background-color 0.2s ease; }}
        .changelog-item:hover {{ background-color: var(--color-bg-lighter); }}
        .changelog-item img {{ width: 32px; height: 32px; border-radius: 4px; background-color: var(--color-bg-lighter); flex-shrink: 0; object-fit: cover; }}
        .changelog-item div {{ overflow: hidden; }}
        .changelog-item h4 {{ font-size: 14px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .changelog-item h4 .status {{ font-size: 11px; font-weight: bold; margin-right: 5px; vertical-align: middle; }}
        .changelog-item h4 .status-updated {{ color: var(--color-success); }}
        .changelog-item h4 .status-removed {{ color: var(--color-danger); }}
        .changelog-item h4 a {{ color: var(--color-text); text-decoration: none; vertical-align: middle; }}
        .changelog-item h4 a:hover {{ color: var(--color-accent); text-decoration: underline; }}
        .changelog-item h4 span.no-link {{ color: var(--color-text); vertical-align: middle; }}
        .changelog-item p {{ font-size: 12px; color: var(--color-text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .progress-bar {{ width: 100%; height: 16px; background-color: var(--color-bg); border-radius: 10px; overflow: hidden; }}
        #progress-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, var(--color-accent-dark), var(--color-accent)); border-radius: 10px; transition: width 0.3s ease; }}
        #progress-label {{ font-size: 12px; color: var(--color-text-muted); text-align: center; margin-top: 8px; height: 16px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        #console {{ height: 300px; background-color: var(--color-bg); border-radius: var(--radius-md); border: 1px solid var(--color-bg-lighter); padding: 12px; overflow-y: auto; font-family: 'Menlo', 'Courier New', monospace; font-size: 12px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; scrollbar-width: thin; scrollbar-color: var(--color-bg-lighter) var(--color-bg); user-select: text; cursor: text; }}
        #console::-webkit-scrollbar {{ width: 8px; }}
        #console::-webkit-scrollbar-track {{ background: var(--color-bg); border-radius: 4px; }}
        #console::-webkit-scrollbar-thumb {{ background-color: var(--color-bg-lighter); border-radius: 4px; border: 2px solid var(--color-bg); }}
        #console p {{ margin-bottom: 4px; word-break: break-all; user-select: text; }}
        #console p:last-child {{ margin-bottom: 0; }}
        #console p.highlight {{ color: var(--color-success); font-weight: 500; background-color: rgba(67, 160, 71, 0.1); border-radius: 4px; padding: 2px 4px; }}
        #scroll-bottom-btn {{ display: none; position: absolute; bottom: 20px; right: 20px; z-index: 10; background-color: var(--color-accent); color: white; border: none; border-radius: 50px; padding: 8px 16px; font-size: 12px; font-weight: 500; cursor: pointer; opacity: 0.8; transition: all 0.2s ease; }}
        #scroll-bottom-btn:hover {{ opacity: 1; transform: scale(1.05); }}
        #scroll-bottom-btn.visible {{ display: block; }}

        /* --- Widget de Progreso Minimizado --- */
        #minimized-progress-widget {{
            display: none; flex-direction: column; gap: 5px;
            position: fixed; bottom: 20px; right: 20px;
            width: 250px; background-color: transparent;
            border: 1px solid var(--color-bg-lighter); border-radius: var(--radius-md);
            padding: 12px; box-shadow: var(--shadow);
            z-index: 101; animation: fadeIn 0.3s ease;
            cursor: pointer; transition: background-color 0.2s ease;
        }}
        #minimized-progress-widget:hover {{ background-color: rgba(42, 42, 42, 0.5); }}
        .minimized-progress-text {{ display: flex; justify-content: space-between; align-items: center; width: 100%; }}
        #minimized-progress-label {{ font-size: 13px; font-weight: 500; color: var(--color-text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 10px; }}
        #minimized-progress-percent {{ font-size: 14px; font-weight: 700; color: var(--color-accent); flex-shrink: 0; }}
        .minimized-progress-bar-container {{ width: 100%; height: 6px; background-color: var(--color-bg); border-radius: 3px; overflow: hidden; }}
        #minimized-progress-bar-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, var(--color-accent-dark), var(--color-accent)); border-radius: 3px; transition: width 0.3s ease; }}

        /* --- (NUEVO) Panel de Depuración --- */
        #debug-panel {{
            display: none; /* Oculto por defecto */
            position: fixed;
            bottom: calc(var(--player-height) + 25px); /* Justo encima del reproductor */
            left: 15px;
            width: var(--player-width);
            background-color: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: var(--radius-md);
            padding: 10px;
            font-family: 'Menlo', 'Courier New', monospace;
            font-size: 12px;
            color: #a7a7a7;
            z-index: 2001; /* Encima del reproductor */
            box-shadow: var(--shadow);
            user-select: none;
        }}
        #debug-panel.visible {{
            display: block;
            animation: fadeIn 0.3s ease;
        }}
        #debug-panel h4 {{
            margin: 0 0 8px 0;
            font-size: 13px;
            color: var(--color-accent);
            border-bottom: 1px solid var(--color-bg-lighter);
            padding-bottom: 5px;
        }}
        #debug-panel div {{
            display: flex;
            justify-content: space-between;
        }}
        #debug-panel div span:last-child {{
            font-weight: bold;
            color: #fff;
        }}

        /* --- Botones Generales --- */
        .btn {{ font-family: var(--font-family-sans); font-size: 14px; font-weight: 500; padding: 12px 16px; border: none; border-radius: var(--radius-md); cursor: pointer; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; gap: 8px; outline: none; }}
        .btn:focus-visible {{ box-shadow: 0 0 0 3px rgba(182, 80, 9, 0.4); }}
        .btn:disabled {{ opacity: 0.5; cursor: not-allowed; background: var(--color-bg-lighter) !important; box-shadow: none !important; transform: none !important; }}
        .btn:not(:disabled):hover {{ transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); }}
        .btn:not(:disabled):active {{ transform: translateY(0) scale(0.98); box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15); }}
        .btn-primary {{ background: linear-gradient(90deg, var(--color-accent-dark), var(--color-accent)); color: white; width: 100%; }}
        .btn-secondary {{ background-color: var(--color-bg-lighter); color: var(--color-text); }}
        .btn-secondary:not(:disabled):hover {{ background-color: #3a3a3a; }}
        .btn-danger {{ background: linear-gradient(90deg, var(--color-danger-dark), var(--color-danger)); color: white; width: 100%; }}

        /* --- Modal de Resultado --- */
        #result-modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0, 0, 0, 0.7); backdrop-filter: blur(3px); align-items: center; justify-content: center; animation: fadeIn 0.3s ease; }}
        .modal-content {{ background-color: var(--color-bg-light); margin: auto; padding: 32px; border: 1px solid var(--color-bg-lighter); width: 90%; max-width: 450px; border-radius: var(--radius-lg); box-shadow: var(--shadow); text-align: center; animation: modalSlideIn 0.4s ease-out; z-index: 1001; }}
        #result-icon {{ font-size: 48px; margin-bottom: 16px; }}
        #result-title {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; color: var(--color-text); }}
        #result-details {{ font-size: 14px; color: var(--color-text-muted); margin-bottom: 24px; max-height: 150px; overflow-y: auto; text-align: left; background: var(--color-bg); padding: 10px; border-radius: var(--radius-md); white-space: pre-wrap; word-wrap: break-word; border: 1px solid var(--color-bg-lighter); user-select: text; cursor: text; }}

    </style>
</head>
<body>
    <!-- Overlay de Carga Inicial -->
    <div class="loading-overlay" id="loading-overlay">
        <div class="spinner" id="loading-spinner"></div>
        <h1 id="loading-title" style="display: none;"></h1>
        <p id="loading-details"></p>
    </div>

    <!-- Pantalla Principal (Jugar) -->
    <div class="screen" id="screen-play">
        <!-- Iframe de Vimeo -->
        <iframe id="vimeo-bg"
                src="{VIMEO_EMBED_SRC}"
                frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen>
        </iframe>
        <!-- Video Overlay (Para Fade In) -->
        <div id="video-overlay"></div>

        <!-- Logo Minecraft -->
        <img src="{LOGO_URL}" alt="Minecraft Logo" id="minecraft-logo">

        <!-- Gradiente Inferior -->
        <div id="bottom-gradient"></div>

        <!-- Botón Jugar -->
        <button id="play-btn">JUGAR</button>

        <!-- Botón Menú Hamburguesa -->
        <button id="menu-btn" title="Menú">
            <span class="menu-line"></span>
            <span class="menu-line"></span>
            <span class="menu-line"></span>
        </button>

    </div>

    <!-- Panel Lateral Deslizable -->
    <div id="side-panel">
        <button class="panel-button" id="panel-settings-btn">
            <i class="fas fa-cog"></i>
            <span>Configuración</span>
        </button>
        <button class="panel-button" id="panel-quit-btn">
            <i class="fas fa-sign-out-alt"></i>
            <span>Salir del Launcher</span>
        </button>
    </div>
    <div id="panel-overlay"></div>

    <!-- Pantalla de Progreso (Overlay) -->
    <div class="screen" id="screen-progress">
        <div class="progress-content-wrapper">
            <button id="minimize-progress-btn" title="Minimizar">
                <i class="fas fa-minus"></i>
            </button>
            <h2 id="progress-title">Actualizando...</h2>
            <div class="progress-bar">
                 <div id="progress-fill"></div>
            </div>
            <div id="progress-label">Iniciando...</div>
            <div class="progress-columns">
                 <div id="console-container">
                      <div id="console"></div>
                      <button id="scroll-bottom-btn">Ir al Fondo</button>
                 </div>
                 <div id="changelog-container">
                      <h3>Changelog de Mods</h3>
                      <div id="changelog-content"></div>
                 </div>
            </div>
            <button class="btn btn-danger" id="cancel-btn">Cancelar</button>
        </div>
    </div>

    <!-- Widget de Progreso Minimizado -->
    <div id="minimized-progress-widget">
         <div class="minimized-progress-text">
              <span id="minimized-progress-label">Cargando Modpack</span>
              <span id="minimized-progress-percent">0%</span>
         </div>
         <div class="minimized-progress-bar-container">
              <div id="minimized-progress-bar-fill"></div>
         </div>
    </div>

    <!-- Contenedor para Setup / Settings -->
    <div class="container" id="main-container">

        <!-- (NUEVO) Asistente de Configuración Inicial -->
        <div class="screen" id="screen-initial-setup">
            
            <!-- Paso 1: Comprobando... -->
            <div class="wizard-step active" data-step="start">
                <div class="header">
                    <h1>Bienvenido</h1>
                    <p>Comprobando tu sistema...</p>
                </div>
                <div class="wizard-spinner"></div>
            </div>

            <!-- Paso 2: Preguntar si tiene Prism -->
            <div class="wizard-step" data-step="ask-installed">
                <div class="header">
                    <h1>Prism Launcher</h1>
                    <p>No hemos detectado Prism Launcher en la ruta por defecto.</p>
                </div>
                <div class="wizard-step-content">
                    <p>¿Ya tienes Prism Launcher instalado en tu PC?</p>
                    <div class="wizard-buttons-horizontal">
                        <button class="btn btn-primary" id="wizard-btn-ask-yes">
                            <i class="fas fa-check"></i>
                            <span>Sí, lo tengo</span>
                        </button>
                        <button class="btn btn-secondary" id="wizard-btn-ask-no">
                            <i class="fas fa-times"></i>
                            <span>No, necesito instalarlo</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Paso 3a: Buscar Manualmente -->
            <div class="wizard-step" data-step="find-manual">
                <div class="header">
                    <h1>Buscar Prism Launcher</h1>
                    <p>Por favor, localiza tu archivo `prismlauncher.exe`.</p>
                </div>
                <div class="wizard-step-content">
                    <button class="btn btn-primary" id="wizard-btn-find-manual">
                        <i class="fas fa-search"></i>
                        <span>Examinar...</span>
                    </button>
                </div>
            </div>

            <!-- Paso 3b: Elegir dónde instalar -->
            <div class="wizard-step" data-step="install-location">
                <div class="header">
                    <h1>Instalar Prism Launcher</h1>
                    <p>Selecciona una carpeta donde deseas instalar Prism Launcher.</p>
                </div>
                <div class="wizard-step-content">
                     <p style="font-size: 13px; color: var(--color-text-muted);">Esto descargará la versión portable más reciente de Prism Launcher y la instalará en la carpeta que elijas.</p>
                    <button class="btn btn-primary" id="wizard-btn-install-location">
                        <i class="fas fa-folder-open"></i>
                        <span>Elegir Carpeta de Instalación</span>
                    </button>
                </div>
            </div>

            <!-- Paso 3c / 5a: Progreso de Instalación (Prism o Modpack) -->
            <div class="wizard-step" data-step="install-progress">
                <div class="header">
                    <h1 id="wizard-install-title">Instalando...</h1>
                    <p id="wizard-install-subtitle">Esto puede tardar unos minutos.</p>
                </div>
                <div class="wizard-step-content">
                    <div id="wizard-progress-container">
                        <div id="wizard-progress-bar-container">
                            <div id="wizard-progress-bar-fill" style="width: 0%;"></div>
                        </div>
                        <div id="wizard-progress-label">Iniciando...</div>
                        <div id="wizard-console"></div>
                    </div>
                    <button class="btn btn-danger" id="wizard-btn-cancel-install">Cancelar</button>
                </div>
            </div>

            <!-- Paso 4: Comprobando Modpack... -->
            <div class="wizard-step" data-step="check-modpack">
                <div class="header">
                    <h1>Instancia del Modpack</h1>
                    <p>Buscando "Kewz's Vanilla+ True" en tus instancias...</p>
                </div>
                <div class="wizard-spinner"></div>
            </div>

            <!-- Paso 6: Iniciar Sesión -->
            <div class="wizard-step" data-step="login">
                <div class="header">
                    <h1>¡Casi Listo!</h1>
                    <p>¡El modpack está instalado!</p>
                </div>
                <div class="wizard-step-content">
                    <p>El último paso es asegurarte de que has iniciado sesión con tu cuenta de Microsoft dentro de Prism Launcher.</p>
                    <p style="font-size: 13px; color: var(--color-text-muted);">Si ya lo has hecho, puedes finalizar. Si no, haz clic en "Abrir Prism" para añadir tu cuenta.</p>
                    <div class="wizard-buttons-horizontal">
                        <button class="btn btn-secondary" id="wizard-btn-login-open">
                            <i class="fas fa-user-plus"></i>
                            <span>Abrir Prism para Iniciar Sesión</span>
                        </button>
                        <button class="btn btn-primary" id="wizard-btn-login-finish">
                            <i class="fas fa-flag-checkered"></i>
                            <span>Finalizar</span>
                        </button>
                    </div>
                </div>
            </div>

        </div>

        <!-- (RENOMBRADO) Pantalla de Ajustes (Post-Setup) -->
        <div class="screen" id="screen-settings">
             <div class="header">
                  <h1>Configuración</h1>
                  <p>Aquí puedes cambiar las rutas de tus archivos.</p>
             </div>
             <label class="setup-label">1. Ejecutable de Prism Launcher</label>
             <div class="folder-display" id="settings-prism-exe-display" title="Arrastra tu 'prismlauncher.exe' o la carpeta que lo contiene aquí">
                  <span id="settings-prism-exe-text" class="placeholder">Arrastra o selecciona tu 'prismlauncher.exe'...</span>
             </div>
             <div class="folder-buttons">
                  <button class="btn btn-secondary" id="settings-browse-prism-btn">Examinar Ejecutable...</button>
             </div>
             <label class="setup-label">2. Carpeta de la Instancia ('minecraft')</label>
             <div class="folder-display" id="settings-instance-folder-display" title="Arrastra la carpeta 'minecraft' de tu instancia, o la carpeta que la contiene">
                  <span id="settings-instance-folder-text" class="placeholder">Arrastra o selecciona tu carpeta '.../minecraft'</span>
             </div>
             <div class="folder-buttons">
                  <button class="btn btn-secondary" id="settings-browse-instance-btn">Examinar Carpeta...</button>
             </div>
             <button class="btn btn-primary" id="save-settings-btn" disabled>Guardar y Volver</button>
        </div>
    </div>

    <!-- Modal de Resultado -->
    <div id="result-modal">
        <div class="modal-content">
            <div id="result-icon"></div>
            <h2 id="result-title"></h2>
            <p id="result-details"></p>
            <button class="btn btn-primary" id="close-modal-btn" style="width: 100px;">Cerrar</button>
        </div>
    </div>

    <script>
        // --- Puente JS <-> Python ---
        let osSep = '/';
        let lastUpdateWasSuccess = false;
        let isScrolledToBottom = true;
        let loadingAnimationId = null;
        let isProgressMinimized = false;
        
        // (ACTUALIZADO) setupState ahora se usa para ambos flujos
        let setupState = {{ prismPath: null, instancePath: null }};
        
        // (CORREGIDO) Declarar variables aquí, pero asignarlas dentro de DOMContentLoaded
        let domPlayer;
        let dom;

        // --- Lógica del Reproductor de Música ---
        let playlist = [];
        let currentTrackIndex = 0;
        let isPlaying = false;

        function loadTrack(index) {{
            if (!playlist || playlist.length === 0 || index < 0 || index >= playlist.length) {{
                console.error("loadTrack: Playlist inválida o índice fuera de rango.");
                domPlayer.title.textContent = "Error de Playlist";
                domPlayer.artist.textContent = "No hay canciones.";
                return;
            }}
            const track = playlist[index];
            domPlayer.audio.src = track.src;
            domPlayer.title.textContent = track.title;
            domPlayer.artist.textContent = track.artist;
            domPlayer.cover.src = track.cover;
            domPlayer.cover.onerror = () => {{ domPlayer.cover.src = 'https://placehold.co/50x50/1e1e1e/888?text=MC'; }};
            currentTrackIndex = index;
            domPlayer.progressBar.style.width = '0%';
            if (!isPlaying) {{
                domPlayer.player.classList.remove('playing');
            }}
            console.log('Track loaded: ' + track.title);
        }}

        function playTrack() {{
            if (!playlist || playlist.length === 0) {{
                console.warn("playTrack: No hay playlist para reproducir.");
                return;
            }}
            const playPromise = domPlayer.audio.play();
            if (playPromise !== undefined) {{
                playPromise.then(_ => {{
                    isPlaying = true;
                    domPlayer.player.classList.add('playing');
                    console.log('Playing: ' + playlist[currentTrackIndex].title);
                }})
                .catch(error => {{
                    console.error("Error starting playback:", error);
                    isPlaying = false;
                    domPlayer.player.classList.remove('playing');
                }});
            }} else {{
                 if (!domPlayer.audio.paused) {{
                      isPlaying = true;
                      domPlayer.player.classList.add('playing');
                      console.log('Playing (legacy): ' + playlist[currentTrackIndex].title);
                 }} else {{
                      console.error("Playback failed (legacy).");
                      isPlaying = false;
                      domPlayer.player.classList.remove('playing');
                 }}
            }}
        }}

        function pauseTrack() {{
            domPlayer.audio.pause();
            isPlaying = false;
            domPlayer.player.classList.remove('playing');
            console.log('Paused: ' + playlist[currentTrackIndex].title);
        }}

        function nextTrack() {{
            if (!playlist || playlist.length === 0) {{
                console.warn("nextTrack: No hay playlist.");
                return;
            }}
            const wasPlaying = isPlaying;
            const nextIndex = (currentTrackIndex + 1) % playlist.length;
            loadTrack(nextIndex);
            if (wasPlaying) {{
                setTimeout(playTrack, 150);
            }}
        }}

        function updateProgressUI() {{
            if (domPlayer.audio.duration && isFinite(domPlayer.audio.duration)) {{
                const percentage = (domPlayer.audio.currentTime / domPlayer.audio.duration) * 100;
                domPlayer.progressBar.style.width = percentage + '%';
            }} else {{
                domPlayer.progressBar.style.width = '0%';
            }}
        }}

        function setProgress(e) {{
            if (!domPlayer.audio.duration || !isFinite(domPlayer.audio.duration)) return;
            const rect = domPlayer.progressContainer.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const width = rect.width;
            const duration = domPlayer.audio.duration;
            const seekTime = Math.max(0, Math.min(duration, (clickX / width) * duration));
            domPlayer.audio.currentTime = seekTime;
            updateProgressUI();
        }}

        function setVolume() {{
            const volume = domPlayer.volumeSlider.value;
            domPlayer.audio.volume = volume;
            if (volume == 0) {{
                domPlayer.volumeIcon.className = 'fas fa-volume-xmark';
            }} else if (volume < 0.5) {{
                domPlayer.volumeIcon.className = 'fas fa-volume-low';
            }} else {{
                domPlayer.volumeIcon.className = 'fas fa-volume-high';
            }}
        }}
        // --- Fin Lógica Reproductor ---

        // --- Funciones UI ---
        function showLoadingError(title, details) {{ console.error("Loading Error:", title, details); if (dom.loadingSpinner) dom.loadingSpinner.style.display = 'none'; if (dom.loadingTitle) {{ dom.loadingTitle.textContent = title; dom.loadingTitle.style.display = 'block'; }} if (dom.loadingDetails) dom.loadingDetails.textContent = details; if (dom.loadingOverlay) dom.loadingOverlay.style.display = 'flex'; }}
        
        // (ACTUALIZADO) switchScreen para manejar todas las pantallas
        function switchScreen(screenName) {{
            console.log("Switching screen to:", screenName);
            // Ocultar todo primero
            dom.screens.progress.style.display = 'none';
            dom.screens.progress.classList.remove('active');
            dom.mainContainer.classList.remove('visible');
            dom.screens.initialSetup.classList.remove('active');
            dom.screens.settings.classList.remove('active');
            dom.screens.play.classList.remove('active');
            dom.minimizedWidget.style.display = 'none';
            isProgressMinimized = false;
            closeSidePanel();
            if (loadingAnimationId) {{ cancelAnimationFrame(loadingAnimationId); loadingAnimationId = null; }}

            // Mostrar reproductor si NO estamos en una pantalla de setup/settings
            domPlayer.player.classList.add('visible');

            // Mostrar pantalla de juego (fondo)
            dom.screens.play.style.display = 'flex';
            dom.screens.play.classList.add('active');

            if (screenName === 'play') {{
                if (dom.loadingOverlay.style.display !== 'none' && !dom.loadingTitle.textContent) {{
                    dom.loadingOverlay.style.display = 'none';
                }}
                dom.playBtn.textContent = "JUGAR";
                dom.playBtn.classList.remove('cancel-mode');
            }} else if (screenName === 'initial-setup') {{
                dom.mainContainer.classList.add('visible');
                dom.screens.initialSetup.style.display = 'block';
                dom.screens.initialSetup.classList.add('active');
                if (dom.loadingOverlay.style.display !== 'none' && !dom.loadingTitle.textContent) {{
                    dom.loadingOverlay.style.display = 'none';
                }}
            }} else if (screenName === 'settings') {{
                dom.mainContainer.classList.add('visible');
                dom.screens.settings.style.display = 'block';
                dom.screens.settings.classList.add('active');
                if (dom.loadingOverlay.style.display !== 'none' && !dom.loadingTitle.textContent) {{
                    dom.loadingOverlay.style.display = 'none';
                }}
            }} else if (screenName === 'progress') {{
                if (isProgressMinimized) {{
                    dom.minimizedWidget.style.display = 'flex';
                }} else {{
                    dom.screens.progress.style.display = 'flex';
                    dom.screens.progress.classList.add('active');
                }}
            }} else {{
                console.warn("Intento de cambiar a pantalla desconocida:", screenName);
                dom.playBtn.textContent = "JUGAR";
                dom.playBtn.classList.remove('cancel-mode');
            }}
        }}

        // (RENOMBRADO) validateSettings para la pantalla de Ajustes
        function validateSettings() {{
            try {{
                const isPrismPathPresent = !!setupState.prismPath; 
                let instanceValidPromise = setupState.instancePath ? pywebview.api.py_validate_instance_path(setupState.instancePath) : Promise.resolve(false); 
                instanceValidPromise.then(isInstanceValid => {{
                    const isPrismValid = isPrismPathPresent; 
                    dom.settings.prismDisplay.classList.toggle('valid', isPrismValid); 
                    dom.settings.prismDisplay.classList.toggle('invalid', !isPrismValid && !!setupState.prismPath); 
                    dom.settings.prismText.textContent = isPrismValid ? setupState.prismPath : "Arrastra o selecciona tu 'prismlauncher.exe'..."; 
                    dom.settings.prismText.classList.toggle('placeholder', !isPrismValid); 
                    dom.settings.instanceDisplay.classList.toggle('valid', isInstanceValid); 
                    dom.settings.instanceDisplay.classList.toggle('invalid', !isInstanceValid && !!setupState.instancePath); 
                    if (isInstanceValid) {{
                        dom.settings.instanceText.textContent = setupState.instancePath; 
                        dom.settings.instanceText.classList.remove('placeholder'); 
                    }} else if (!setupState.instancePath) {{
                        dom.settings.instanceText.textContent = "Arrastra o selecciona tu carpeta '.../minecraft'"; 
                        dom.settings.instanceText.classList.add('placeholder'); 
                    }} else {{
                        dom.settings.instanceText.textContent = setupState.instancePath + " (Inválido)"; 
                        dom.settings.instanceText.classList.remove('placeholder'); 
                    }}
                    dom.settings.saveBtn.disabled = !(isPrismValid && isInstanceValid); 
                }}).catch(err => {{ console.error("Error validación JS:", err); dom.settings.saveBtn.disabled = true; }});
            }} catch (e) {{ console.error("Error crítico API en validateSettings:", e); showLoadingError("Error Validación", "Fallo comunicación Python: " + e); dom.settings.saveBtn.disabled = true; }}
        }}
        
        function logToConsole(message) {{
            try {{
                const lines = message.split('\\n'); 
                for (const line of lines) {{
                    if (!line) continue; 
                    const p = document.createElement('p'); 
                    let textContent = line; 
                    if (line.startsWith('[LOG_PASSTHROUGH] ')) {{ textContent = line.substring(18); }}
                    else if (line.startsWith('[LOG_TRIGGER] ')) {{ textContent = line.substring(14); p.classList.add('highlight'); }}
                    else {{ textContent = '> ' + line; }}
                    p.appendChild(document.createTextNode(textContent)); 
                    dom.console.appendChild(p); 
                }}
                if (isScrolledToBottom) {{ dom.console.scrollTop = dom.console.scrollHeight; }}
            }} catch (e) {{ console.error("Error en logToConsole:", e); }}
        }}
        
        // (ACTUALIZADO) updateProgress ahora actualiza AMBOS (principal y minimizado)
        function updateProgress(percentage, label) {{
            try {{
                const validPercentage = Math.max(0, Math.min(1, parseFloat(percentage) || 0));
                const percentText = Math.round(validPercentage * 100) + '%';
                
                // Actualizar barra grande (pantalla de progreso)
                dom.progressBar.style.width = (validPercentage * 100) + '%'; 
                dom.progressLabel.textContent = label || ''; 
                
                // Actualizar widget minimizado
                dom.minimizedProgressBarFill.style.width = (validPercentage * 100) + '%';
                dom.minimizedProgressPercent.textContent = percentText;
                if (label) {{
                    dom.minimizedProgressLabel.textContent = label;
                }}
                
                // (NUEVO) Actualizar barra del asistente (si está visible)
                if (dom.screens.initialSetup.classList.contains('active')) {{
                    dom.wizard.progressBar.style.width = (validPercentage * 100) + '%';
                    dom.wizard.progressLabel.textContent = label || '';
                }}

            }} catch (e) {{ console.error("Error en updateProgress:", e); }}
        }}
        
        function setLoadScreen(title, progressLabel) {{
            try {{
                dom.progressTitle.textContent = title || "Procesando..."; 
                dom.progressLabel.textContent = progressLabel || "..."; 
                dom.minimizedProgressLabel.textContent = progressLabel || "...";
            }} catch(e) {{ console.error("Error en setLoadScreen:", e); }}
        }}
        
        function startLoadingAnimation(durationSeconds) {{
            if (loadingAnimationId) {{
                cancelAnimationFrame(loadingAnimationId);
            }}
            const startTime = performance.now();
            const durationMs = (durationSeconds || 400) * 1000;

            // Resetear estilos y eliminar transiciones CSS para un control total.
            dom.progressBar.style.transition = 'none';
            dom.progressBar.style.width = '0%';
            dom.minimizedProgressBarFill.style.transition = 'none';
            dom.minimizedProgressBarFill.style.width = '0%';
            dom.progressLabel.textContent = "Cargando el Modpack...";
            dom.minimizedProgressLabel.textContent = "Cargando el Modpack...";

            function animateProgress(currentTime) {{
                const elapsedTime = currentTime - startTime;
                // Calcular el progreso, asegurando que no exceda el 99% para esperar la señal final.
                const progress = Math.min(0.99, elapsedTime / durationMs);
                const percent = progress * 100;
                const percentText = Math.round(percent) + '%';

                // Actualizar ambas barras de progreso simultáneamente.
                dom.progressBar.style.width = percent + '%';
                dom.minimizedProgressBarFill.style.width = percent + '%';
                dom.minimizedProgressPercent.textContent = percentText;

                // Continuar la animación si el tiempo no ha transcurrido.
                if (elapsedTime < durationMs) {{
                    loadingAnimationId = requestAnimationFrame(animateProgress);
                }} else {{
                    // La animación ha terminado, asegurar que se detenga en 99%.
                    dom.progressBar.style.width = '99%';
                    dom.minimizedProgressBarFill.style.width = '99%';
                    dom.minimizedProgressPercent.textContent = '99%';
                    loadingAnimationId = null;
                }}
            }}
            
            // Iniciar el bucle de animación.
            loadingAnimationId = requestAnimationFrame(animateProgress);
        }}

        function showResult(success, title, details) {{ try {{ lastUpdateWasSuccess = !!success; dom.modal.icon.textContent = success ? '✅' : '❌'; dom.modal.title.textContent = title || (success ? 'Éxito' : 'Error'); dom.modal.details.innerHTML = details || (success ? "Proceso completado." : "Ocurrió un error."); dom.modal.element.style.display = 'flex'; }} catch (e) {{ console.error("Error en showResult:", e); }} }}
        
        function fadeLauncherOut() {{
            try {{
                if (loadingAnimationId) {{ cancelAnimationFrame(loadingAnimationId); loadingAnimationId = null; }}
                
                dom.progressBar.style.transition = 'width 0.3s ease'; 
                dom.progressBar.style.width = '100%'; 
                dom.minimizedProgressBarFill.style.transition = 'width 0.3s ease';
                dom.minimizedProgressBarFill.style.width = '100%';
                dom.minimizedProgressPercent.textContent = '100%';
                dom.minimizedWidget.style.display = 'none';
                isProgressMinimized = false;

                document.body.style.animation = 'fadeOut 1s forwards'; 
                document.body.addEventListener('animationend', function handler(event) {{ if (event.animationName === 'fadeOut') {{ if (!window.quitting) {{ window.quitting = true; pywebview.api.py_quit_launcher(); }} document.body.removeEventListener('animationend', handler); }} }}, {{once: true}});
                setTimeout(() => {{ if (!window.quitting) {{ window.quitting = true; pywebview.api.py_quit_launcher(); }} }}, 1200);
            }} catch (e) {{ console.error("Error en fadeLauncherOut:", e); }}
        }}

        // (ACTUALIZADO) forceShowSetupScreen ahora muestra la pantalla de AJUSTES
        function forceShowSetupScreen() {{
            validateSettings(); // Cargar datos actuales en la pantalla de ajustes
            switchScreen('settings'); 
            dom.loadingOverlay.style.display = 'none'; 
            dom.mainContainer.classList.add('visible'); 
        }}
        
        function returnToPlayScreen() {{
            console.log("Returning to play screen (hiding progress/modal)."); 
            dom.modal.element.style.display = 'none'; 
            dom.screens.progress.style.display = 'none'; 
            dom.screens.progress.classList.remove('active'); 
            
            dom.minimizedWidget.style.display = 'none';
            isProgressMinimized = false;

            dom.cancelBtn.disabled = false; 
            dom.cancelBtn.textContent = "Cancelar"; 
            updateProgress(0, ""); 
            dom.progressTitle.textContent = "Actualizando..."; 
            
            dom.playBtn.textContent = "JUGAR";
            dom.playBtn.classList.remove('cancel-mode');
            dom.playBtn.disabled = false;

            switchScreen('play'); 
        }}
        
        function cancelCurrentProcess() {{
            console.log("Cancelación manual iniciada.");
            dom.cancelBtn.disabled = true; 
            dom.cancelBtn.textContent = "Cancelando..."; 
            dom.playBtn.disabled = true; 

            // (NUEVO) Cancelar también el botón del asistente
            dom.wizard.btnCancelInstall.disabled = true;
            dom.wizard.btnCancelInstall.textContent = "Cancelando...";

            try {{
                pywebview.api.py_cancel_update(); 
            }} catch (e) {{
                console.error("Error calling py_cancel_update:", e);
            }}
            
            // Si estamos en el asistente, volver al paso de pregunta
            if (dom.screens.initialSetup.classList.contains('active')) {{
                showWizardStep('ask-installed');
                // Re-habilitar botones del asistente
                dom.wizard.btnCancelInstall.disabled = false;
                dom.wizard.btnCancelInstall.textContent = "Cancelar";
            }} else {{
                // Si estábamos en el juego, volver a la pantalla de juego
                returnToPlayScreen();
            }}
            
            // Re-habilitar botón principal
            setTimeout(() => {{
                dom.playBtn.disabled = false;
                dom.playBtn.classList.remove('cancel-mode');
                dom.playBtn.textContent = "JUGAR";
            }}, 500);
        }}

        function addChangelogItem(title, description, icon_url, url, status) {{ try {{ const item = document.createElement('div'); item.className = 'changelog-item'; const img = document.createElement('img'); img.src = (icon_url && status !== 'Removed') ? icon_url : 'https://placehold.co/32x32/2a2a2a/888?text=?'; img.alt = title + ' icon'; img.onerror = () => {{ img.src = 'https://placehold.co/32x32/2a2a2a/888?text=?'; }}; const textDiv = document.createElement('div'); const titleHeader = document.createElement('h4'); const statusSpan = document.createElement('span'); statusSpan.classList.add('status'); if (status === 'Updated') {{ statusSpan.textContent = '[UPD]'; statusSpan.classList.add('status-updated'); }} else if (status === 'Removed') {{ statusSpan.textContent = '[REM]'; statusSpan.classList.add('status-removed'); }} titleHeader.appendChild(statusSpan); if (status !== 'Removed' && url) {{ const link = document.createElement('a'); link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer'; link.textContent = title || 'Mod desconocido'; titleHeader.appendChild(link); }} else {{ const nameSpan = document.createElement('span'); nameSpan.classList.add('no-link'); nameSpan.textContent = title || 'Mod desconocido'; titleHeader.appendChild(nameSpan); }} const descP = document.createElement('p'); descP.textContent = (status !== 'Removed' && description) ? description : (status === 'Removed' ? 'Eliminado' : 'Actualizado/Añadido'); textDiv.appendChild(titleHeader); textDiv.appendChild(descP); item.appendChild(img); item.appendChild(textDiv); dom.changelogContent.appendChild(item); }} catch(e) {{ console.error("Error adding changelog item:", e); }} }}
        function openSidePanel() {{ dom.sidePanel.classList.add('panel-open'); dom.panelOverlay.classList.add('visible'); }}
        function closeSidePanel() {{ dom.sidePanel.classList.remove('panel-open'); dom.panelOverlay.classList.remove('visible'); }}

        // --- (NUEVO) Lógica del Asistente de Configuración ---

        // Muestra un paso específico del asistente
        function showWizardStep(stepName) {{
            console.log("Mostrando paso del asistente:", stepName);
            dom.wizard.steps.forEach(step => {{
                if (step.getAttribute('data-step') === stepName) {{
                    step.classList.add('active');
                }} else {{
                    step.classList.remove('active');
                }}
            }});
            // Resetear consola y progreso al mostrar un paso de instalación
            if (stepName === 'install-progress') {{
                dom.wizard.console.innerHTML = '';
                dom.wizard.progressBar.style.width = '0%';
                dom.wizard.progressLabel.textContent = 'Iniciando...';
                dom.wizard.btnCancelInstall.disabled = false;
                dom.wizard.btnCancelInstall.textContent = "Cancelar";
            }}
        }}

        // Inicia el flujo del asistente
        function startInitialSetupWizard() {{
            console.log("Iniciando Asistente de Configuración Inicial...");
            switchScreen('initial-setup');
            showWizardStep('start');
            try {{
                // (MODIFICADO) La llamada a la API ahora está dentro del setTimeout
                // de pywebviewready, por lo que no necesitamos otro aquí.
                pywebview.api.py_setup_check_prism_default_path().then(result => {{
                    if (result.status === 'prism_detected') {{
                        handlePrismPathFound(result.path); // Prism encontrado, comprobar modpack
                    }} else {{
                        showWizardStep('ask-installed'); // No detectado, preguntar al usuario
                    }}
                }}).catch(err => {{
                    console.error("Error en py_setup_check_prism_default_path:", err);
                    showResult(false, "Error de Detección", "No se pudo comprobar la ruta por defecto: " + err);
                    showWizardStep('ask-installed'); // Fallback a preguntar
                }});
            }} catch (e) {{
                // Este catch probablemente no se disparará por el error de "not a function"
                // porque la llamada está dentro de un .then()
                showLoadingError("Error Fatal", "API Python no disponible (catch pre-llamada): " + e);
            }}
        }}

        // Llamado cuando se encuentra una ruta de Prism válida (detectada o manual)
        function handlePrismPathFound(prismPath) {{
            console.log("Ruta de Prism válida encontrada:", prismPath);
            setupState.prismPath = prismPath;
            showWizardStep('check-modpack');
            try {{
                pywebview.api.py_setup_check_modpack_installed(prismPath).then(result => {{
                    if (result.status === 'modpack_installed') {{
                        console.log("Modpack ya instalado en:", result.instance_path);
                        setupState.instancePath = result.instance_path;
                        // Guardar rutas en config.json
                        pywebview.api.py_save_paths(result.prism_path, result.instance_path);
                        showWizardStep('login'); // Avanzar al paso de login
                    }} else if (result.status === 'modpack_not_installed') {{
                        console.log("Modpack no instalado. Iniciando instalación...");
                        showWizardStep('install-progress');
                        dom.wizard.installTitle.textContent = "Instalando Modpack";
                        dom.wizard.installSubtitle.textContent = "Descargando y extrayendo archivos...";
                        pywebview.api.py_start_threaded_task('install_modpack', result.prism_path, result.instance_base_path);
                    }} else {{
                        throw new Error(result.error || "Respuesta desconocida al comprobar modpack.");
                    }}
                }}).catch(err => {{
                    console.error("Error en py_setup_check_modpack_installed:", err);
                    showResult(false, "Error de Modpack", "No se pudo comprobar la instancia del modpack: " + err);
                    showWizardStep('ask-installed'); // Volver al inicio del flujo
                }});
            }} catch (e) {{
                 showLoadingError("Error Fatal", "API Python no disponible (catch pre-llamada): " + e);
            }}
        }}

        // --- (NUEVO) Callbacks Globales desde Python (Hilos) ---
        
        function updateInstallStatus(message) {{
            // Esta función es llamada por Python para CUALQUIER tarea en hilo
            try {{
                const p = document.createElement('p');
                p.appendChild(document.createTextNode(message));
                dom.wizard.console.appendChild(p);
                dom.wizard.console.scrollTop = dom.wizard.console.scrollHeight;
                
                // También actualizar la etiqueta de progreso
                dom.wizard.progressLabel.textContent = message;
            }} catch (e) {{ console.error("Error en updateInstallStatus:", e); }}
        }}

        function onPrismInstallComplete(success, path, error) {{
            if (success) {{
                console.log("Instalación de Prism completada, ruta:", path);
                handlePrismPathFound(path); // Continuar al siguiente paso
            }} else {{
                console.error("Instalación de Prism fallida:", error);
                showResult(false, "Error de Instalación", "No se pudo instalar Prism Launcher: " + error);
                showWizardStep('ask-installed'); // Volver a preguntar
            }}
        }}

        function onModpackInstallComplete(success, prismPath, instancePath, error) {{
            if (success) {{
                console.log("Instalación de Modpack completada, ruta:", instancePath);
                setupState.prismPath = prismPath;
                setupState.instancePath = instancePath;
                // Guardar rutas en config.json
                pywebview.api.py_save_paths(prismPath, instancePath);
                showWizardStep('login'); // Avanzar al paso de login
            }} else {{
                console.error("Instalación de Modpack fallida:", error);
                showResult(false, "Error de Instalación", "No se pudo instalar el modpack: " + error);
                showWizardStep('ask-installed'); // Volver al inicio del flujo
            }}
        }}
        
        function onTaskError(taskName, error) {{
            console.error("Error en tarea '" + taskName + "':", error);
            showResult(false, 'Error en ' + taskName, error);
            showWizardStep('ask-installed'); // Volver al inicio
        }}


        // --- Event Listeners ---
        // (CORREGIDO) Separar la lógica de pywebviewready y DOMContentLoaded

        // 1. Esperar a que la API de Python esté lista
        window.addEventListener('pywebviewready', () => {{
            console.log("pywebviewready: La API de Python está lista.");
            window.pywebview.apiReady = true; // Establecer una bandera global

            // Adjuntar listeners que dependen únicamente de la API y no del DOM
            // (Ninguno en este caso, pero es buena práctica tenerlo aquí)
        }});

        // 2. Esperar a que el DOM esté completamente cargado
        document.addEventListener('DOMContentLoaded', () => {{
            console.log("DOMContentLoaded: El DOM está completamente cargado.");

            // (CORREGIDO) Asignar las constantes del DOM aquí, ahora que el HTML está cargado.
            domPlayer = {{
                player: document.getElementById('music-player'),
                cover: document.getElementById('album-cover'),
                title: document.getElementById('track-title'),
                artist: document.getElementById('track-artist'),
                audio: document.getElementById('audio-element'),
                playPauseBtn: document.getElementById('play-pause-btn'),
                nextBtn: document.getElementById('next-btn'),
                progressContainer: document.getElementById('progress-container'),
                progressBar: document.getElementById('progress-bar'),
                volumeContainer: document.getElementById('volume-container'),
                volumeIcon: document.getElementById('volume-icon'),
                volumeSlider: document.getElementById('volume-slider')
            }};

            dom = {{
                loadingOverlay: document.getElementById('loading-overlay'), loadingSpinner: document.getElementById('loading-spinner'), loadingTitle: document.getElementById('loading-title'), loadingDetails: document.getElementById('loading-details'),
                mainContainer: document.getElementById('main-container'),
                screens: {{
                    initialSetup: document.getElementById('screen-initial-setup'),
                    settings: document.getElementById('screen-settings'),
                    play: document.getElementById('screen-play'),
                    progress: document.getElementById('screen-progress'),
                }},
                wizard: {{
                    steps: document.querySelectorAll('#screen-initial-setup .wizard-step'),
                    btnAskYes: document.getElementById('wizard-btn-ask-yes'),
                    btnAskNo: document.getElementById('wizard-btn-ask-no'),
                    btnFindManual: document.getElementById('wizard-btn-find-manual'),
                    btnInstallLocation: document.getElementById('wizard-btn-install-location'),
                    btnCancelInstall: document.getElementById('wizard-btn-cancel-install'),
                    btnLoginOpen: document.getElementById('wizard-btn-login-open'),
                    btnLoginFinish: document.getElementById('wizard-btn-login-finish'),
                    installTitle: document.getElementById('wizard-install-title'),
                    installSubtitle: document.getElementById('wizard-install-subtitle'),
                    progressBar: document.getElementById('wizard-progress-bar-fill'),
                    progressLabel: document.getElementById('wizard-progress-label'),
                    console: document.getElementById('wizard-console'),
                }},
                settings: {{
                    prismDisplay: document.getElementById('settings-prism-exe-display'),
                    prismText: document.getElementById('settings-prism-exe-text'),
                    browsePrismBtn: document.getElementById('settings-browse-prism-btn'),
                    instanceDisplay: document.getElementById('settings-instance-folder-display'),
                    instanceText: document.getElementById('settings-instance-folder-text'),
                    browseInstanceBtn: document.getElementById('settings-browse-instance-btn'),
                    saveBtn: document.getElementById('save-settings-btn')
                }},
                playBtn: document.getElementById('play-btn'),
                menuBtn: document.getElementById('menu-btn'),
                sidePanel: document.getElementById('side-panel'), panelOverlay: document.getElementById('panel-overlay'),
                panelSettingsBtn: document.getElementById('panel-settings-btn'),
                panelQuitBtn: document.getElementById('panel-quit-btn'),
                cancelBtn: document.getElementById('cancel-btn'),
                progressTitle: document.getElementById('progress-title'),
                progressBar: document.getElementById('progress-fill'),
                progressLabel: document.getElementById('progress-label'),
                console: document.getElementById('console'),
                scrollBottomBtn: document.getElementById('scroll-bottom-btn'),
                changelogContent: document.getElementById('changelog-content'),
                modal: {{ element: document.getElementById('result-modal'), icon: document.getElementById('result-icon'), title: document.getElementById('result-title'), details: document.getElementById('result-details'), closeBtn: document.getElementById('close-modal-btn') }},
                minimizeProgressBtn: document.getElementById('minimize-progress-btn'),
                minimizedWidget: document.getElementById('minimized-progress-widget'),
                minimizedProgressLabel: document.getElementById('minimized-progress-label'),
                minimizedProgressPercent: document.getElementById('minimized-progress-percent'),
                minimizedProgressBarFill: document.getElementById('minimized-progress-bar-fill')
            }};

            // Función para iniciar la aplicación una vez que AMBOS eventos han ocurrido
            function initializeApp() {{
                if (!window.pywebview || !window.pywebview.apiReady) {{
                    console.log("La API de pywebview no está lista todavía, esperando...");
                    setTimeout(initializeApp, 50); // Volver a comprobar en 50ms
                    return;
                }}

                console.log("¡DOM y API listos! Inicializando la aplicación...");
                window.quitting = false;

                try {{
                    // 1. Iniciar la cadena de llamadas a la API
                    pywebview.api.py_get_os_sep().then(sep => {{
                        osSep = sep || '/';
                        return pywebview.api.py_load_saved_paths();
                    }}).then(pathsAreValid => {{
                        // 2. Cargar la música (paralelamente)
                        pywebview.api.py_get_playlist().then(newPlaylist => {{
                            if (newPlaylist && newPlaylist.length > 0) {{
                                console.log('Playlist cargada desde Python con ' + newPlaylist.length + ' canciones.');
                                playlist = newPlaylist;
                                loadTrack(0);
                                domPlayer.audio.play().then(() => {{
                                    isPlaying = true;
                                    domPlayer.player.classList.add('playing');
                                }}).catch(error => {{
                                    console.warn('Autoplay bloqueado o fallido:', error);
                                }});
                            }} else {{
                                console.error("No se pudo cargar la playlist desde Python o está vacía.");
                                domPlayer.title.textContent = "Error al Cargar";
                                domPlayer.artist.textContent = "No se encontró playlist.";
                            }}
                        }}).catch(err => {{
                             console.error("Error fatal al llamar a py_get_playlist:", err);
                             domPlayer.title.textContent = "Error de API";
                             domPlayer.artist.textContent = "Fallo al conectar con Python.";
                        }});
                        
                        // 3. Setear volumen inicial (AHORA SEGURO)
                        setVolume();

                        // 4. Decidir qué pantalla mostrar
                        if (pathsAreValid) {{
                            console.log("Rutas válidas encontradas. Yendo a 'play'.");
                            pywebview.api.py_toggle_fullscreen();
                            dom.loadingOverlay.style.display = 'none';
                            switchScreen('play');
                        }} else {{
                             console.log("Rutas no válidas. Iniciando asistente.");
                             pywebview.api.py_toggle_fullscreen();
                             startInitialSetupWizard();
                        }}
                    }}).catch(e => {{
                        // Error en la cadena py_get_os_sep o py_load_saved_paths
                        console.error("Error en la cadena de carga inicial:", e);
                        showLoadingError("Error de Carga Inicial", "No se pudo cargar la configuración: " + e); 
                        // Forzar el asistente como fallback
                        pywebview.api.py_toggle_fullscreen();
                        startInitialSetupWizard();
                    }});
                }} catch (e) {{
                    showLoadingError("Error Fatal", "API Python no disponible (catch principal): " + e); 
                }}
            }}

            // Iniciar el proceso de inicialización
            initializeApp();


            // --- Adjuntar todos los listeners de UI aquí ---
            // (Ahora es seguro porque el DOM está cargado)

            // --- Asistente Listeners ---
            dom.wizard.btnAskYes.addEventListener('click', () => showWizardStep('find-manual'));
            dom.wizard.btnAskNo.addEventListener('click', () => showWizardStep('install-location'));
            
            dom.wizard.btnFindManual.addEventListener('click', () => {{
                pywebview.api.py_setup_ask_for_prism_path().then(result => {{
                    if (result.status === 'path_valid') {{
                        handlePrismPathFound(result.path);
                    }} else if (result.status === 'path_invalid') {{
                        showResult(false, "Ruta Inválida", result.error);
                    }}
                    // Si 'cancelled', no hacer nada
                }}).catch(err => showResult(false, "Error", "No se pudo abrir diálogo: " + err));
            }});
            
            dom.wizard.btnInstallLocation.addEventListener('click', () => {{
                pywebview.api.py_setup_ask_for_install_location().then(result => {{
                    if (result.status === 'path_valid') {{
                        showWizardStep('install-progress');
                        dom.wizard.installTitle.textContent = "Instalando Prism Launcher";
                        dom.wizard.installSubtitle.textContent = "Ejecutando Winget... Esto puede tardar.";
                        pywebview.api.py_start_threaded_task('install_prism', result.path);
                    }}
                    // Si 'cancelled', no hacer nada
                }}).catch(err => showResult(false, "Error", "No se pudo abrir diálogo: " + err));
            }});
            
            dom.wizard.btnCancelInstall.addEventListener('click', cancelCurrentProcess);

            dom.wizard.btnLoginOpen.addEventListener('click', () => {{
                pywebview.api.py_setup_open_prism_for_login(setupState.prismPath)
                    .catch(e => showResult(false, "Error", "No se pudo abrir Prism: " + e));
            }});

            dom.wizard.btnLoginFinish.addEventListener('click', () => {{
                // Guardar por si acaso (aunque ya debería estar guardado)
                pywebview.api.py_save_paths(setupState.prismPath, setupState.instancePath).then(() => {{
                    switchScreen('play'); // ¡Terminado!
                }});
            }});


            // --- (ACTUALIZADO) Settings Screen Listeners ---
            dom.settings.browsePrismBtn.addEventListener('click', () => {{ pywebview.api.py_browse_for_prism_exe().then(data => {{ if (data && data.is_valid) {{ setupState.prismPath = data.prism_path; setupState.instancePath = data.instance_path; }} else {{ setupState.prismPath = null; setupState.instancePath = null; }} validateSettings(); }}).catch(err => {{ showResult(false, "Error Examinar", "No se pudo abrir diálogo: " + err); }}); }});
            dom.settings.browseInstanceBtn.addEventListener('click', () => {{ pywebview.api.py_browse_for_instance_folder().then(path => {{ setupState.instancePath = path; validateSettings(); }}).catch(err => {{ showResult(false, "Error Examinar", "No se pudo abrir diálogo: " + err); }}); }});
            [dom.settings.prismDisplay, dom.settings.instanceDisplay].forEach(el => {{
                el.addEventListener('dragenter', (e) => {{ e.preventDefault(); e.stopPropagation(); el.classList.add('dragover'); }}, false);
                el.addEventListener('dragover', (e) => {{ e.preventDefault(); e.stopPropagation(); el.classList.add('dragover'); }}, false);
                el.addEventListener('dragleave', (e) => {{ e.preventDefault(); e.stopPropagation(); el.classList.remove('dragover'); }}, false);
                el.addEventListener('drop', (e) => {{
                    e.preventDefault(); e.stopPropagation(); el.classList.remove('dragover'); 
                    if (e.dataTransfer.items && e.dataTransfer.items.length > 0 && e.dataTransfer.items[0].kind === 'file') {{
                        const droppedPath = e.dataTransfer.files[0].path; if (!droppedPath) return; 
                        if (el === dom.settings.prismDisplay) {{
                            pywebview.api.py_process_prism_path_drop(droppedPath).then(data => {{ setupState.prismPath = data.prism_path; setupState.instancePath = data.instance_path; validateSettings(); }}).catch(err => console.error("Error Prism drop:", err));
                        }} else {{
                            pywebview.api.py_process_instance_path_drop(droppedPath).then(data => {{ setupState.instancePath = data.path; validateSettings(); }}).catch(err => console.error("Error Instance drop:", err));
                        }}
                    }}
                }}, false);
            }});
            dom.settings.saveBtn.addEventListener('click', () => {{
                if (dom.settings.saveBtn.disabled) return; 
                if (setupState.prismPath && setupState.instancePath) {{
                    pywebview.api.py_save_paths(setupState.prismPath, setupState.instancePath).then(didSave => {{
                        if (didSave) {{ switchScreen('play'); }}
                        else {{ showResult(false, "Error Guardar", "No se pudieron guardar rutas."); }}
                    }}).catch(err => {{ showResult(false, "Error Inesperado", "No se pudo guardar config: " + err); }});
                }} else {{ showResult(false, "Error Interno", "Faltan rutas válidas."); }}
            }});

            // --- Play Screen Listeners ---
            dom.playBtn.addEventListener('click', () => {{
                if (dom.playBtn.classList.contains('cancel-mode')) {{
                    cancelCurrentProcess();
                }} else {{
                    dom.playBtn.textContent = "CANCELAR";
                    dom.playBtn.classList.add('cancel-mode');
                    switchScreen('progress');
                    dom.console.innerHTML = '';
                    dom.changelogContent.innerHTML = '';
                    logToConsole("Iniciando proceso...");
                    dom.cancelBtn.disabled = false;
                    dom.cancelBtn.textContent = "Cancelar";
                    updateProgress(0, "Iniciando...");
                    setLoadScreen("Actualizando...", "Comprobando versiones...");
                    
                    try {{
                        pywebview.api.py_start_game();
                    }} catch(e) {{
                        console.error("Error calling py_start_game:", e);
                        showResult(false, "Error de API", "No se pudo llamar a py_start_game: " + e);
                        returnToPlayScreen();
                    }}
                }}
             }});
            dom.menuBtn.addEventListener('click', openSidePanel);

            // --- Side Panel Listeners ---
            dom.panelOverlay.addEventListener('click', closeSidePanel);
            dom.panelSettingsBtn.addEventListener('click', () => {{
                closeSidePanel();
                switchScreen('settings');
                validateSettings();
             }});
            dom.panelQuitBtn.addEventListener('click', () => {{ if (!window.quitting) {{ window.quitting = true; pywebview.api.py_quit_launcher(); }} }});

            // --- Progress Screen Listeners ---
            dom.cancelBtn.addEventListener('click', () => {{
                cancelCurrentProcess();
            }});
            dom.console.addEventListener('scroll', () => {{ const atBottom = (dom.console.scrollHeight - dom.console.scrollTop - dom.console.clientHeight) < 30; isScrolledToBottom = atBottom; dom.scrollBottomBtn.classList.toggle('visible', !atBottom); }});
            dom.scrollBottomBtn.addEventListener('click', () => {{ dom.console.scrollTop = dom.console.scrollHeight; isScrolledToBottom = true; dom.scrollBottomBtn.classList.remove('visible'); }});

            dom.minimizeProgressBtn.addEventListener('click', () => {{
                isProgressMinimized = true;

                // (CORREGIDO) Sincronizar la barra minimizada con la principal ANTES de mostrarla
                const currentMainWidth = dom.progressBar.style.width;
                dom.minimizedProgressBarFill.style.transition = 'none';
                dom.minimizedProgressBarFill.style.width = currentMainWidth;
                setTimeout(() => {{ dom.minimizedProgressBarFill.style.transition = 'width 0.3s ease'; }}, 50);

                dom.screens.progress.style.display = 'none';
                dom.screens.progress.classList.remove('active');
                dom.minimizedWidget.style.display = 'flex';
            }});
             dom.minimizedWidget.addEventListener('click', () => {{
                 isProgressMinimized = false;
                 dom.minimizedWidget.style.display = 'none';
                 dom.screens.progress.style.display = 'flex';
                 dom.screens.progress.classList.add('active');
             }});

            // --- Modal Listeners ---
            dom.modal.closeBtn.addEventListener('click', () => {{
                 returnToPlayScreen();
             }});

             // --- Music Player Listeners ---
             domPlayer.playPauseBtn.addEventListener('click', () => {{
                 if (isPlaying) {{ pauseTrack(); }} else {{ playTrack(); }}
             }});
             domPlayer.nextBtn.addEventListener('click', nextTrack);
             domPlayer.audio.addEventListener('ended', nextTrack);
             domPlayer.audio.addEventListener('error', (e) => {{
                 console.error("Audio error:", domPlayer.audio.error);
                 domPlayer.title.textContent = "Error al cargar";
                 domPlayer.artist.textContent = playlist[currentTrackIndex]?.src || "URL inválida";
                 domPlayer.progressBar.style.width = '0%';
             }});
             domPlayer.audio.addEventListener('timeupdate', updateProgressUI);
             domPlayer.progressContainer.addEventListener('click', setProgress);
             domPlayer.volumeSlider.addEventListener('input', setVolume);

            console.log("Initial event listeners attached.");
        }});
    </script>
        <!-- Reproductor de Música -->
        <div id="music-player">
            <div class="player-top-row">
                <img id="album-cover" src="{URL_ALBUM_COVER}" alt="Album Cover">
                <div class="track-info">
                    <span id="track-title">Cargando...</span>
                    <span id="track-artist">...</span>
                </div>
                <div class="controls">
                    <button id="play-pause-btn" class="control-btn" title="Play/Pause">
                        <i class="fas fa-play"></i>
                        <i class="fas fa-pause"></i>
                    </button>
                    <button id="next-btn" class="control-btn" title="Siguiente">
                        <i class="fas fa-forward-step"></i>
                    </button>
                </div>
            </div>
            <div class="player-bottom-row">
                 <div id="progress-container">
                      <div id="progress-bar"></div>
                 </div>
                 <div id="volume-container">
                      <i id="volume-icon" class="fas fa-volume-high"></i>
                      <input type="range" id="volume-slider" min="0" max="1" step="0.01" value="1">
                 </div>
            </div>
        </div>
        <!-- (NUEVO) Panel de Depuración -->
        <div id="debug-panel">
            <h4>Debug Info</h4>
            <div><span>Unmute Trigger Count:</span><span id="debug-unmute-count">0</span></div>
            <div><span>Game Ready Event:</span><span id="debug-gameready-event">false</span></div>
            <div><span>Unmute Event:</span><span id="debug-unmute-event">false</span></div>
        </div>
        <!-- Elemento Audio (oculto) -->
        <audio id="audio-element" preload="metadata"></audio>
</body>
</html>
"""
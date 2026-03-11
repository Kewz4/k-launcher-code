import os
import sys

# --- HTML Content Definition ---

FONT_IMPORT_URL = "https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&family=Montserrat:wght@900&display=swap"
FONT_AWESOME_URL = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
UNIFIED_REPO_RAW_URL = "https://raw.githubusercontent.com/Kewz4/kewz-cobblemon/main"
LOGO_URL = f"{UNIFIED_REPO_RAW_URL}/minecraftlogo.png"
URL_ALBUM_COVER = ""  # Each song provides its own cover.jpg inside its songs/<folder>/ directory


# (CORREGIDO) HTML_CONTENT es ahora un f-string para inyectar variables directamente.
# Todas las llaves literales de CSS/JS deben escaparse con {{ y }}.
HTML_CONTENT = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kewz's Cobblemon Launcher</title>
    <link rel="stylesheet" href="{FONT_IMPORT_URL}">
    <link rel="stylesheet" href="{FONT_AWESOME_URL}">
    <style>
        /* --- Reset & Fonts --- */
        :root {{
            --font-family-sans: 'Roboto', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            --font-family-display: 'Montserrat', sans-serif;
            --color-bg: #000000;
            --color-bg-light: #0d1117;
            --color-bg-lighter: #161b22;
            --color-text: #e0e0e0;
            --color-text-muted: #7a8fa6;
            /* Aqua accent palette */
            --color-accent: #00cfaa;
            --color-accent-dark: #007a65;
            --color-danger: #e53935;
            --color-danger-dark: #b71c1c;
            --color-success: #00e676;
            --color-success-dark: #00c853;
            --radius-md: 8px;
            --radius-lg: 12px;
            --radius-btn: 11px;
            --shadow: 0 4px 20px rgba(0, 207, 170, 0.08);
            /* Button colors */
            --play-btn-grad-start: #007a65;
            --play-btn-grad-end: #00cfaa;
            --cancel-btn-grad-start: #b71c1c;
            --cancel-btn-grad-end: #e53935;

            --menu-btn-fill-start: #000000;
            --menu-btn-fill-end: #0d1117;
            --menu-btn-stroke-start: #004840;
            --menu-btn-stroke-end: #00cfaa;
            /* Side panel */
            --panel-bg: #080d13;
            --panel-width: 280px;
            /* Music player dimensions */
            --player-height: 80px;
            --player-width: 300px;
            /* Text shadow for player */
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

        /* --- (NUEVO) Pantalla de Auto-Actualización --- */
        #screen-updater {{
            display: flex; /* Se muestra por defecto */
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: var(--color-bg);
            align-items: center; justify-content: center;
            flex-direction: column; z-index: 10000;
            padding: 20px; text-align: center;
            transition: opacity 0.5s ease;
        }}
        #screen-updater.hidden {{
            opacity: 0;
            pointer-events: none;
        }}
        #updater-container {{
            width: 100%; max-width: 450px;
        }}
        #updater-container h1 {{
            font-size: 24px; font-weight: 700;
            color: var(--color-accent); margin-bottom: 20px;
        }}
        #updater-progress-bar-container {{
            width: 100%; height: 8px; background-color: var(--color-bg-lighter);
            border-radius: 4px; overflow: hidden; margin-bottom: 10px;
        }}
        #updater-progress-bar {{
            width: 0%; height: 100%; background-color: var(--color-accent);
            border-radius: 4px; transition: width 0.3s ease;
        }}
        #updater-console {{
            height: 120px; background-color: var(--color-bg-lighter);
            border-radius: var(--radius-md); border: 1px solid #333;
            padding: 10px; overflow-y: auto; text-align: left;
            font-family: 'Menlo', 'Courier New', monospace; font-size: 11px;
            color: var(--color-text-muted);
            margin-bottom: 20px;
        }}
        #updater-console p {{ margin: 0; margin-bottom: 4px; }}
        #updater-buttons {{
            display: flex; gap: 16px; justify-content: center;
        }}


        /* --- Contenedor Principal (Setup / Settings) --- */
        .container {{ width: 100%; max-width: 650px; background-color: var(--color-bg-light); border-radius: var(--radius-lg); box-shadow: var(--shadow); padding: 24px 32px; border: 1px solid var(--color-bg-lighter); transition: opacity 0.3s ease; position: relative; z-index: 101; display: none; }}
        .container.visible {{ display: block; animation: fadeIn 0.25s ease; }}
        .header {{ text-align: center; margin-bottom: 24px; }}
        .header h1 {{ font-size: 28px; font-weight: 700; background: linear-gradient(90deg, var(--color-accent-dark), var(--color-accent)); -webkit-background-clip: text; background-clip: text; color: transparent; -webkit-text-fill-color: transparent; margin-bottom: 4px; }}
        .header p {{ font-size: 14px; color: var(--color-text-muted); }}

        /* --- Pantallas (Contenedores generales) --- */
        .screen {{ display: none; }}
        .screen.active {{ /* display set dynamically */ animation: fadeIn 0.5s ease; }}

        /* --- (RENOMBRADO) Pantalla de Ajustes (Post-Setup) --- */
        #screen-settings .setup-label {{ font-size: 16px; font-weight: 500; margin-bottom: 8px; margin-top: 16px; display: block; }}
        #screen-settings .folder-display {{ display: flex; align-items: center; background-color: var(--color-bg); border-radius: var(--radius-md); padding: 12px 16px; border: 2px dashed var(--color-bg-lighter); margin-bottom: 12px; transition: all 0.3s ease; min-height: 48px; cursor: default; }}
        #screen-settings .folder-display.dragover {{ border-color: var(--color-accent); background-color: rgba(0, 207, 170, 0.07); }}
        #screen-settings .folder-display.valid {{ border-style: solid; border-color: var(--color-success-dark); background-color: rgba(0, 230, 118, 0.07); }}
        #screen-settings .folder-display.invalid {{ border-style: solid; border-color: var(--color-danger-dark); background-color: rgba(229, 57, 53, 0.07); }}
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
        #screen-initial-setup .wizard-spinner {{ width: 40px; height: 40px; border: 4px solid var(--color-bg-lighter); border-top-color: var(--color-accent); border-radius: 50%; animation: spin 1s linear infinite; margin: 10px auto 20px auto; box-shadow: 0 0 12px rgba(0, 207, 170, 0.3); }}
        
        /* (NUEVO) Consola y progreso para el asistente */
        #wizard-progress-container {{ display: flex; flex-direction: column; gap: 12px; margin-top: 20px; }}
        #wizard-console {{ height: 250px; background-color: var(--color-bg); border-radius: var(--radius-md); border: 1px solid var(--color-bg-lighter); padding: 12px; overflow-y: auto; font-family: 'Menlo', 'Courier New', monospace; font-size: 12px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; scrollbar-width: thin; scrollbar-color: var(--color-bg-lighter) var(--color-bg); user-select: text; cursor: text; text-align: left; }}
        #wizard-console p {{ margin-bottom: 4px; word-break: break-all; user-select: text; font-size: 12px !important; color: var(--color-text-muted) !important; }}
        #wizard-console p:last-child {{ margin-bottom: 0; }}
        
        #wizard-progress-bar-container {{ width: 100%; height: 10px; background-color: var(--color-bg); border-radius: 5px; overflow: hidden; }}
        #wizard-progress-bar-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, var(--color-accent-dark), var(--color-accent)); border-radius: 5px; transition: width 0.3s ease; }}
        #wizard-progress-label {{ font-size: 12px; color: var(--color-text-muted); text-align: center; height: 16px; }}
        #wizard-step-install-progress .btn, #wizard-step-install-modpack .btn {{ margin-top: 16px; }}


        /* --- Play Screen --- */
        #screen-play {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
            z-index: 50; overflow: hidden; background-color: #000;
            padding: 40px 20px; padding-bottom: calc(var(--player-height) + 30px);
        }}
        #screen-play.active {{ z-index: 100; }}

        #bg-video {{
            position: absolute; top: 50%; left: 50%;
            width: 100vw; height: 56.25vw; /* 16:9 ratio */
            min-height: 100vh; min-width: 177.77vh; /* 16:9 ratio */
            transform: translate(-50%, -50%);
            z-index: -1; pointer-events: none; border: none;
            object-fit: cover;
        }}
        #video-overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-color: var(--color-bg);
            z-index: 0; pointer-events: none;
            animation: fadeOutOverlay 3s ease-out forwards;
        }}

        #minecraft-logo {{
            position: absolute; top: 16px; right: 16px;
            width: 160px; height: auto;
            object-fit: contain; z-index: 2; pointer-events: none;
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
            border: none; box-shadow: 0 5px 25px rgba(0, 207, 170, 0.3);
            color: #000; font-weight: 900;
        }}
        #play-btn::before {{ content: ''; position: absolute; inset: -6px; border-radius: calc(var(--radius-btn) + 6px); background-image: linear-gradient(90deg, var(--play-btn-grad-start), var(--play-btn-grad-end)); z-index: -1; padding: 6px; -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); -webkit-mask-composite: xor; mask-composite: exclude; transition: background-image 0.3s ease; }}
        #play-btn:hover {{ transform: translateX(-50%) scale(1.04); box-shadow: 0 10px 35px rgba(0, 207, 170, 0.45); }}
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

        /* --- (NUEVO) Display de Versión --- */
        #launcher-version {{
            position: fixed;
            bottom: 5px;
            right: 10px;
            font-size: 11px;
            color: var(--color-text-muted);
            opacity: 0.5;
            z-index: 500;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            pointer-events: none;
        }}

        /* --- Panel Lateral --- */
        #side-panel {{ position: fixed; top: 0; left: 0; width: var(--panel-width); height: 100%; background-color: var(--panel-bg); border-right: 1px solid rgba(0,207,170,0.12); box-shadow: 5px 0 30px rgba(0,207,170,0.06); transform: translateX(-100%); transition: transform 0.3s ease-in-out; z-index: 1000; padding: 24px 15px 24px 15px; display: flex; flex-direction: column; gap: 10px; }}
        #side-panel.panel-open {{ transform: translateX(0); }}
        .panel-button {{ display: flex; align-items: center; gap: 15px; padding: 15px; background-color: var(--color-bg-lighter); color: var(--color-text); border: none; border-radius: var(--radius-md); cursor: pointer; transition: all 0.2s ease; text-align: left; font-size: 16px; border: 1px solid transparent; }}
        .panel-button:hover {{ background-color: rgba(0, 207, 170, 0.07); border-color: rgba(0, 207, 170, 0.2); color: var(--color-accent); }}
        .panel-button:hover i {{ color: var(--color-accent); }}
        .panel-button i {{ font-size: 18px; width: 20px; text-align: center; color: var(--color-text-muted); transition: color 0.2s ease; }}
        #panel-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 999; opacity: 0; visibility: hidden; transition: opacity 0.3s ease, visibility 0s 0.3s linear; }}
        #panel-overlay.visible {{ opacity: 1; visibility: visible; transition: opacity 0.3s ease; }}

        /* --- Pantalla de Progreso (Overlay) --- */
        #screen-progress {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; display: none; align-items: center; justify-content: center; background-color: rgba(0, 0, 0, 0.85); backdrop-filter: blur(4px); z-index: 101; padding: 20px; }}
        #screen-progress.active {{ display: flex; flex-direction: column; }}
        .progress-content-wrapper {{ position: relative; width: 100%; max-width: 900px; background-color: var(--color-bg-light); border-radius: var(--radius-lg); box-shadow: var(--shadow); padding: 24px 32px; border: 1px solid var(--color-bg-lighter); }}
        
        #minimize-progress-btn {{ position: absolute; top: 16px; right: 16px; width: 32px; height: 32px; background-color: var(--color-bg-lighter); border: none; border-radius: 50%; color: var(--color-text-muted); font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease; z-index: 10; }}
        #minimize-progress-btn:hover {{ background-color: #3a3a3a; color: var(--color-text); transform: scale(1.1); }}
        #minimize-progress-btn i {{ font-weight: 900; }}

        /* --- Wizard minimize button (overlaid on main container) --- */
        #wizard-minimize-btn {{
            position: absolute; top: 12px; right: 12px;
            width: 32px; height: 32px;
            background-color: var(--color-bg-lighter); border: none; border-radius: 50%;
            color: var(--color-text-muted); font-size: 14px; cursor: pointer;
            display: none; align-items: center; justify-content: center;
            transition: all 0.2s ease; z-index: 10;
        }}
        #wizard-minimize-btn:hover {{ background-color: #3a3a3a; color: var(--color-text); transform: scale(1.1); }}

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
        .changelog-item h4 a:hover {{ color: var(--color-accent); text-decoration: underline; text-shadow: 0 0 8px rgba(0, 207, 170, 0.4); }}
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
        #console p.highlight {{ color: var(--color-accent); font-weight: 500; background-color: rgba(0, 207, 170, 0.08); border-radius: 4px; padding: 2px 4px; }}

        /* --- Widget de Progreso Minimizado --- */
        #minimized-progress-widget {{
            display: none; flex-direction: column; gap: 5px;
            position: fixed; bottom: 20px; right: 20px;
            width: 250px;
            background-color: rgba(10, 14, 20, 0.94);
            backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(0,207,170,0.18); border-radius: var(--radius-md);
            padding: 12px; box-shadow: var(--shadow);
            z-index: 101; animation: fadeIn 0.3s ease;
            cursor: pointer; transition: background-color 0.2s ease;
        }}
        #minimized-progress-widget:hover {{ background-color: rgba(20, 28, 38, 0.97); }}
        .minimized-progress-text {{ display: flex; justify-content: space-between; align-items: center; width: 100%; }}
        #minimized-progress-label {{ font-size: 13px; font-weight: 500; color: var(--color-text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 10px; }}
        #minimized-progress-percent {{ font-size: 14px; font-weight: 700; color: var(--color-accent); flex-shrink: 0; text-shadow: 0 0 8px rgba(0, 207, 170, 0.4); }}
        .minimized-progress-bar-container {{ width: 100%; height: 6px; background-color: var(--color-bg); border-radius: 3px; overflow: hidden; }}
        #minimized-progress-bar-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, var(--color-accent-dark), var(--color-accent)); border-radius: 3px; transition: width 0.3s ease; }}

        /* --- Panel de Depuración --- */
        #debug-panel {{
            position: fixed;
            top: 20px;
            right: 20px;
            width: 280px;
            background-color: rgba(26, 26, 26, 0.8);
            backdrop-filter: blur(5px);
            border-radius: var(--radius-md);
            border: 1px solid var(--color-bg-lighter);
            box-shadow: var(--shadow);
            z-index: 5000;
            color: var(--color-text);
            padding: 12px;
            display: none; /* Oculto por defecto */
            font-size: 12px;
        }}
        #debug-panel h3 {{
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 10px;
            text-align: center;
            color: var(--color-accent);
        }}
        .debug-trigger {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid var(--color-bg-lighter);
        }}
        .debug-trigger:last-child {{
            border-bottom: none;
        }}
        .debug-trigger-name {{
            font-weight: 500;
        }}
        .debug-trigger-status {{
            font-weight: 700;
            padding: 3px 6px;
            border-radius: 4px;
        }}
        .debug-trigger-status.pending {{
            color: #fdd835; /* Amarillo */
            background-color: rgba(253, 216, 53, 0.1);
        }}
        .debug-trigger-status.triggered {{
            color: var(--color-success);
            background-color: rgba(67, 160, 71, 0.1);
        }}

        /* --- Botones Generales --- */
        .btn {{ font-family: var(--font-family-sans); font-size: 14px; font-weight: 500; padding: 12px 16px; border: none; border-radius: var(--radius-md); cursor: pointer; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; gap: 8px; outline: none; }}
        .btn:focus-visible {{ box-shadow: 0 0 0 3px rgba(0, 207, 170, 0.35); }}
        .btn:disabled {{ opacity: 0.5; cursor: not-allowed; background: var(--color-bg-lighter) !important; box-shadow: none !important; transform: none !important; }}
        .btn:not(:disabled):hover {{ transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); }}
        .btn:not(:disabled):active {{ transform: translateY(0) scale(0.98); box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15); }}
        .btn-primary {{ background: linear-gradient(90deg, var(--color-accent-dark), var(--color-accent)); color: #000; font-weight: 700; width: 100%; }}
        .btn-secondary {{ background-color: var(--color-bg-lighter); color: var(--color-text); border: 1px solid rgba(0,207,170,0.1); }}
        .btn-secondary:not(:disabled):hover {{ background-color: rgba(0,207,170,0.08); border-color: rgba(0,207,170,0.3); color: var(--color-accent); }}
        .btn-danger {{ background: linear-gradient(90deg, var(--color-danger-dark), var(--color-danger)); color: white; width: 100%; }}

        /* --- Modal de Resultado --- */
        #result-modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0, 0, 0, 0.7); backdrop-filter: blur(3px); align-items: center; justify-content: center; animation: fadeIn 0.3s ease; }}
        .modal-content {{ background-color: var(--color-bg-light); margin: auto; padding: 32px; border: 1px solid var(--color-bg-lighter); width: 90%; max-width: 450px; border-radius: var(--radius-lg); box-shadow: var(--shadow); text-align: center; animation: modalSlideIn 0.4s ease-out; z-index: 1001; }}
        #result-icon {{ font-size: 48px; margin-bottom: 16px; }}
        #result-title {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; color: var(--color-text); }}
        #result-details {{ font-size: 14px; color: var(--color-text-muted); margin-bottom: 24px; max-height: 150px; overflow-y: auto; text-align: left; background: var(--color-bg); padding: 10px; border-radius: var(--radius-md); white-space: pre-wrap; word-wrap: break-word; border: 1px solid var(--color-bg-lighter); user-select: text; cursor: text; }}
        #close-modal-btn {{ width: auto; min-width: 120px; margin: 0 auto; }}

        /* --- Updater Screen Logo --- */
        #updater-logo {{
            max-width: 360px; width: 85%; height: auto;
            margin-bottom: 32px; opacity: 0.92;
        }}

        /* --- Top Gradient (play screen) --- */
        #top-gradient {{
            position: absolute; top: 0; left: 0; width: 100%; height: 140px;
            background: linear-gradient(to bottom, rgba(0,0,0,0.75) 0%, transparent 100%);
            z-index: 0; pointer-events: none;
        }}

        /* --- Container: animate on show --- */
        /* --- Side Panel Header --- */
        #panel-header {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 0 2px 16px 2px;
            border-bottom: 1px solid rgba(0,207,170,0.12);
            margin-bottom: 8px;
        }}
        #panel-title {{
            font-size: 13px; font-weight: 700;
            color: var(--color-accent);
            letter-spacing: 0.5px; text-transform: uppercase;
        }}
        #panel-close-btn {{
            background: none; border: none;
            color: var(--color-text-muted); cursor: pointer;
            font-size: 16px; padding: 4px 6px;
            border-radius: var(--radius-md);
            transition: color 0.2s ease, background 0.2s ease;
            line-height: 1;
        }}
        #panel-close-btn:hover {{ color: var(--color-text); background: var(--color-bg-lighter); }}

        /* Push Quit to bottom, style it as a soft-danger action */
        .panel-spacer {{ flex-grow: 1; min-height: 16px; }}
        #panel-quit-btn {{ color: #d45e5e; border-color: transparent; }}
        #panel-quit-btn i {{ color: #d45e5e; }}
        #panel-quit-btn:hover {{ background-color: rgba(229, 57, 53, 0.08); border-color: rgba(229, 57, 53, 0.25); color: #e57373; }}
        #panel-quit-btn:hover i {{ color: #e57373; }}

        /* --- Settings folder display improvements --- */
        #screen-settings .folder-display .folder-type-icon {{
            font-size: 15px; color: var(--color-text-muted);
            margin-right: 10px; flex-shrink: 0; transition: color 0.2s ease;
        }}
        #screen-settings .folder-display.valid .folder-type-icon {{ color: var(--color-success-dark); }}
        #screen-settings .folder-display.invalid .folder-type-icon {{ color: var(--color-danger); }}
        #screen-settings .folder-display .folder-browse-arrow {{
            font-size: 11px; color: var(--color-text-muted); opacity: 0.45;
            flex-shrink: 0; margin-left: 8px;
        }}
        #screen-settings .setup-label {{
            font-size: 13px; font-weight: 600; letter-spacing: 0.3px;
            color: var(--color-text-muted); text-transform: uppercase;
            margin-bottom: 8px; margin-top: 20px; display: block;
        }}

        /* --- Changelog status icon pills --- */
        .changelog-item h4 .status {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 20px; height: 20px; border-radius: 50%;
            font-size: 9px; margin-right: 6px; vertical-align: middle;
            flex-shrink: 0;
        }}
        .changelog-item h4 .status-updated {{
            color: var(--color-success); background-color: rgba(0, 230, 118, 0.12);
        }}
        .changelog-item h4 .status-removed {{
            color: var(--color-danger); background-color: rgba(229, 57, 53, 0.12);
        }}

        /* --- Scroll-to-bottom button (icon only) --- */
        #scroll-bottom-btn {{
            display: none; position: absolute; bottom: 12px; right: 12px; z-index: 10;
            background-color: rgba(0,207,170,0.85); color: #000; border: none;
            border-radius: 50%; width: 32px; height: 32px;
            font-size: 13px; font-weight: 700; cursor: pointer;
            opacity: 0.9; transition: all 0.2s ease;
            align-items: center; justify-content: center;
        }}
        #scroll-bottom-btn:hover {{ opacity: 1; transform: scale(1.1); }}
        #scroll-bottom-btn.visible {{ display: flex; }}

        /* --- Download banner (replaces inline styles) --- */
        .download-banner {{
            display: none; margin-bottom: 10px; padding: 10px 14px;
            background: rgba(0,207,170,0.06); border: 1px solid rgba(0,207,170,0.18);
            border-radius: var(--radius-md); align-items: center; gap: 12px; flex-wrap: wrap;
            animation: fadeIn 0.3s ease;
        }}
        .download-banner.visible {{ display: flex; }}
        .download-banner-icon {{ color: var(--color-accent); flex-shrink: 0; }}
        .download-banner-name {{
            font-weight: 600; color: var(--color-text); flex-shrink: 0;
            max-width: 240px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }}
        .download-banner-name.narrow {{ max-width: 200px; }}
        .download-banner-size {{ font-size: 13px; color: var(--color-text-muted); flex-grow: 1; }}
        .download-banner-size.narrow {{ font-size: 12px; }}
        .paused-badge {{
            display: none; font-size: 11px; font-weight: 700;
            color: #ffb300; background: rgba(255,179,0,0.12);
            padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(255,179,0,0.3);
        }}
        .paused-badge.visible {{ display: inline-block; }}

        /* --- Settings Drawer (right-side slide-in) --- */
        #settings-drawer-overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.55); z-index: 599;
            opacity: 0; visibility: hidden;
            transition: opacity 0.35s ease, visibility 0s 0.35s linear;
        }}
        #settings-drawer-overlay.visible {{
            opacity: 1; visibility: visible;
            transition: opacity 0.35s ease;
        }}
        #settings-drawer {{
            position: fixed; top: 0; right: 0;
            width: 400px; height: 100%;
            background-color: var(--panel-bg);
            border-left: 1px solid rgba(0,207,170,0.15);
            box-shadow: -8px 0 40px rgba(0,207,170,0.1);
            transform: translateX(100%);
            transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 600; display: flex; flex-direction: column;
            overflow: hidden;
        }}
        #settings-drawer.open {{ transform: translateX(0); }}
        #settings-drawer-header {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 20px 24px 16px; flex-shrink: 0;
            border-bottom: 1px solid rgba(0,207,170,0.12);
        }}
        #settings-drawer-title {{
            font-size: 17px; font-weight: 700;
            background: linear-gradient(90deg, var(--color-accent-dark), var(--color-accent));
            -webkit-background-clip: text; background-clip: text;
            color: transparent; -webkit-text-fill-color: transparent;
        }}
        #settings-drawer-close-btn {{
            background: none; border: none; color: var(--color-text-muted);
            cursor: pointer; font-size: 18px; padding: 6px 8px;
            border-radius: var(--radius-md); line-height: 1;
            transition: color 0.2s ease, background 0.2s ease;
        }}
        #settings-drawer-close-btn:hover {{ color: var(--color-text); background: var(--color-bg-lighter); }}
        #settings-drawer-body {{
            padding: 4px 24px 24px; flex-grow: 1; overflow-y: auto;
        }}

        /* --- Resume Modal --- */
        #resume-modal {{
            display: none; position: fixed; z-index: 1001; left: 0; top: 0;
            width: 100%; height: 100%; background-color: rgba(0,0,0,0.75);
            backdrop-filter: blur(4px); align-items: center; justify-content: center;
        }}
        #resume-modal.visible {{ display: flex; animation: fadeIn 0.3s ease; }}
        #resume-modal-content {{
            background-color: var(--color-bg-light); margin: auto; padding: 32px;
            border: 1px solid rgba(0,207,170,0.2); width: 90%; max-width: 460px;
            border-radius: var(--radius-lg); box-shadow: 0 8px 40px rgba(0,207,170,0.15);
            text-align: center; animation: modalSlideIn 0.4s ease-out;
        }}
        #resume-modal-icon {{ font-size: 42px; margin-bottom: 14px; color: var(--color-accent); }}
        #resume-modal-title {{ font-size: 22px; font-weight: 700; margin-bottom: 8px; }}
        #resume-modal-details {{ font-size: 14px; color: var(--color-text-muted); margin-bottom: 24px; line-height: 1.6; }}
        #resume-modal-buttons {{ display: flex; gap: 12px; }}
        #resume-modal-buttons .btn {{ flex: 1; }}

        /* --- New Animations --- */
        /* Shimmer: background-size 200% so the highlight sweeps left→right */
        @keyframes shimmer {{
            0% {{ background-position: 100% center; }}
            100% {{ background-position: 0% center; }}
        }}
        @keyframes floatUpDown {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-14px); }}
        }}
        @keyframes slideInFromRight {{
            from {{ opacity: 0; transform: translateX(30px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        @keyframes pulseGlow {{
            0%, 100% {{ box-shadow: 0 5px 25px rgba(0,207,170,0.3); }}
            50% {{ box-shadow: 0 8px 45px rgba(0,207,170,0.65); }}
        }}
        @keyframes staggerFadeIn {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Apply shimmer to all progress bars */
        #progress-fill, #wizard-progress-bar-fill, #minimized-progress-bar-fill {{
            background: linear-gradient(90deg,
                var(--color-accent-dark) 0%,
                var(--color-accent) 40%,
                rgba(180,255,240,0.45) 50%,
                var(--color-accent) 60%,
                var(--color-accent-dark) 100%);
            background-size: 200% 100%;
            animation: shimmer 2s linear infinite;
        }}

        /* Float animation on logo */
        #minecraft-logo {{ animation: floatUpDown 6s ease-in-out infinite; }}

        /* Pulse glow on play button (only when not in cancel mode) */
        #play-btn:not(.cancel-mode) {{ animation: pulseGlow 3s ease-in-out infinite; }}
        #play-btn:hover, #play-btn:active {{ animation: none !important; }}

        /* Slide-in for wizard steps */
        #screen-initial-setup .wizard-step.active {{
            animation: slideInFromRight 0.3s ease-out;
        }}

        /* Staggered entrance for wizard horizontal buttons */
        .wizard-buttons-horizontal .btn:nth-child(1) {{ animation: staggerFadeIn 0.3s ease-out 0.05s both; }}
        .wizard-buttons-horizontal .btn:nth-child(2) {{ animation: staggerFadeIn 0.3s ease-out 0.15s both; }}

    </style>
</head>
<body>
    <!-- Auto-Update Screen -->
    <div id="screen-updater">
        <div id="updater-container">
            <img src="{LOGO_URL}" alt="Kewz's Cobblemon" id="updater-logo">
            <h1 id="updater-title">Checking for Updates...</h1>
            <div id="updater-progress-bar-container">
                <div id="updater-progress-bar" style="width: 5%;"></div>
            </div>
            <div id="updater-console">
                <p>Initializing...</p>
            </div>
            <div id="updater-buttons">
                 <!-- Buttons added dynamically -->
            </div>
        </div>
    </div>

    <!-- Pantalla Principal (Jugar) -->
    <div class="screen" id="screen-play" style="display: none;">
        <!-- Iframe de Vimeo -->
        <video id="bg-video" autoplay muted playsinline></video>
        <!-- Video Overlay (Para Fade In) -->
        <div id="video-overlay"></div>

        <!-- Top & Bottom Gradients -->
        <div id="top-gradient"></div>
        <div id="bottom-gradient"></div>

        <!-- Logo -->
        <img src="{LOGO_URL}" alt="Kewz's Cobblemon" id="minecraft-logo">

        <!-- Play Button -->
        <button id="play-btn">PLAY</button>

        <!-- Hamburger Menu Button -->
        <button id="menu-btn" title="Menu">
            <span class="menu-line"></span>
            <span class="menu-line"></span>
            <span class="menu-line"></span>
        </button>

    </div>

    <!-- Slide-out Side Panel -->
    <div id="side-panel">
        <div id="panel-header">
            <span id="panel-title">Kewz's Cobblemon</span>
            <button id="panel-close-btn" title="Close menu"><i class="fas fa-times"></i></button>
        </div>
        <button class="panel-button" id="panel-settings-btn">
            <i class="fas fa-cog"></i>
            <span>Settings</span>
        </button>
        <button class="panel-button" id="panel-debug-btn">
            <i class="fas fa-bug"></i>
            <span>Debug</span>
        </button>
        <div class="panel-spacer"></div>
        <button class="panel-button" id="panel-quit-btn">
            <i class="fas fa-sign-out-alt"></i>
            <span>Quit Launcher</span>
        </button>
    </div>
    <div id="panel-overlay"></div>

    <!-- Progress Screen (Overlay) -->
    <div class="screen" id="screen-progress">
        <div class="progress-content-wrapper">
            <button id="minimize-progress-btn" title="Minimize">
                <i class="fas fa-minus"></i>
            </button>
            <h2 id="progress-title">Updating...</h2>
            <!-- Download Details Banner -->
            <div id="download-details-banner" class="download-banner">
                <i class="fas fa-download download-banner-icon"></i>
                <span id="download-filename" class="download-banner-name"></span>
                <span id="download-size-label" class="download-banner-size"></span>
                <span id="download-paused-badge" class="paused-badge">PAUSED</span>
                <button id="pause-resume-btn" class="btn btn-secondary" style="padding:6px 14px; font-size:13px; min-width:90px;" onclick="togglePauseDownload()">
                    <i class="fas fa-pause" id="pause-icon"></i> <span id="pause-label">Pause</span>
                </button>
            </div>
            <div class="progress-bar">
                 <div id="progress-fill"></div>
            </div>
            <div id="progress-label">Starting...</div>
            <div class="progress-columns">
                 <div id="console-container">
                      <div id="console"></div>
                      <button id="scroll-bottom-btn" title="Scroll to bottom"><i class="fas fa-arrow-down"></i></button>
                 </div>
                 <div id="changelog-container">
                      <h3>Mod Changelog</h3>
                      <div id="changelog-content"></div>
                 </div>
            </div>
            <button class="btn btn-danger" id="cancel-btn">Cancel</button>
        </div>
    </div>

    <!-- Minimized Progress Widget -->
    <div id="minimized-progress-widget">
         <div class="minimized-progress-text">
              <span id="minimized-progress-label">Loading Modpack</span>
              <span id="minimized-progress-percent">0%</span>
         </div>
         <div class="minimized-progress-bar-container">
              <div id="minimized-progress-bar-fill"></div>
         </div>
    </div>

    <!-- Contenedor para Setup Wizard -->
    <div class="container" id="main-container">

        <!-- Overlay buttons (shown conditionally) -->
        <button id="wizard-minimize-btn" title="Minimize"><i class="fas fa-minus"></i></button>

        <!-- (NUEVO) Asistente de Configuración Inicial -->
        <div class="screen" id="screen-initial-setup">
            
            <!-- Step 1: Checking... -->
            <div class="wizard-step active" data-step="start">
                <div class="header">
                    <h1>Welcome</h1>
                    <p>Checking your system...</p>
                </div>
                <div class="wizard-spinner"></div>
            </div>

            <!-- Step 2: Ask if Prism is installed -->
            <div class="wizard-step" data-step="ask-installed">
                <div class="header">
                    <h1>Prism Launcher</h1>
                    <p>Prism Launcher was not found at the default location.</p>
                </div>
                <div class="wizard-step-content">
                    <p>Do you already have Prism Launcher installed?</p>
                    <div class="wizard-buttons-horizontal">
                        <button class="btn btn-primary" id="wizard-btn-ask-yes">
                            <i class="fas fa-check"></i>
                            <span>Yes, I have it</span>
                        </button>
                        <button class="btn btn-secondary" id="wizard-btn-ask-no">
                            <i class="fas fa-times"></i>
                            <span>No, install it for me</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Step 3a: Find Manually -->
            <div class="wizard-step" data-step="find-manual">
                <div class="header">
                    <h1>Locate Prism Launcher</h1>
                    <p>Please find your <code>prismlauncher.exe</code> file.</p>
                </div>
                <div class="wizard-step-content">
                    <button class="btn btn-primary" id="wizard-btn-find-manual">
                        <i class="fas fa-search"></i>
                        <span>Browse...</span>
                    </button>
                </div>
            </div>

            <!-- Step 3b: Choose install location -->
            <div class="wizard-step" data-step="install-location">
                <div class="header">
                    <h1>Install Prism Launcher</h1>
                    <p>Choose a folder where Prism Launcher will be installed.</p>
                </div>
                <div class="wizard-step-content">
                     <p style="font-size: 13px; color: var(--color-text-muted);">This will download the latest portable version of Prism Launcher (v10.0.5) and install it to the folder you choose.</p>
                    <button class="btn btn-primary" id="wizard-btn-install-location">
                        <i class="fas fa-folder-open"></i>
                        <span>Choose Install Folder</span>
                    </button>
                </div>
            </div>

            <!-- Paso 3c / 5a: Progreso de Instalación (Prism o Modpack) -->
            <div class="wizard-step" data-step="install-progress">
                <div class="header">
                    <h1 id="wizard-install-title">Installing...</h1>
                    <p id="wizard-install-subtitle">This may take a few minutes. Large files can be paused and resumed.</p>
                </div>
                <div class="wizard-step-content">
                    <!-- Wizard Download Details -->
                    <div id="wizard-download-details" class="download-banner">
                        <i class="fas fa-download download-banner-icon"></i>
                        <span id="wizard-dl-filename" class="download-banner-name narrow"></span>
                        <span id="wizard-dl-size" class="download-banner-size narrow"></span>
                        <span id="wizard-paused-badge" class="paused-badge">PAUSED</span>
                        <button id="wizard-pause-resume-btn" class="btn btn-secondary" style="padding:5px 12px; font-size:12px; min-width:80px;" onclick="togglePauseDownload()">
                            <i class="fas fa-pause" id="wizard-pause-icon"></i> <span id="wizard-pause-label">Pause</span>
                        </button>
                    </div>
                    <div id="wizard-progress-container">
                        <div id="wizard-progress-bar-container">
                            <div id="wizard-progress-bar-fill" style="width: 0%;"></div>
                        </div>
                        <div id="wizard-progress-label">Starting...</div>
                        <div id="wizard-console"></div>
                    </div>
                    <button class="btn btn-danger" id="wizard-btn-cancel-install">Cancel</button>
                </div>
            </div>

            <!-- Step 4: Checking Modpack... -->
            <div class="wizard-step" data-step="check-modpack">
                <div class="header">
                    <h1>Modpack Instance</h1>
                    <p>Looking for "Kewz's Cobblemon" in your instances...</p>
                </div>
                <div class="wizard-spinner"></div>
            </div>

            <!-- Step 6: Login -->
            <div class="wizard-step" data-step="login">
                <div class="header">
                    <h1>Almost Ready!</h1>
                    <p>The modpack is installed!</p>
                </div>
                <div class="wizard-step-content">
                    <p>The last step is to make sure you're logged in with your Microsoft account inside Prism Launcher.</p>
                    <p style="font-size: 13px; color: var(--color-text-muted);">If you've already done this, click Finish. Otherwise, click "Open Prism" to add your account.</p>
                    <div class="wizard-buttons-horizontal">
                        <button class="btn btn-secondary" id="wizard-btn-login-open">
                            <i class="fas fa-user-plus"></i>
                            <span>Open Prism to Sign In</span>
                        </button>
                        <button class="btn btn-primary" id="wizard-btn-login-finish">
                            <i class="fas fa-flag-checkered"></i>
                            <span>Finish</span>
                        </button>
                    </div>
                </div>
            </div>

        </div>

    </div>

    <!-- Result Modal -->
    <div id="result-modal">
        <div class="modal-content">
            <div id="result-icon"></div>
            <h2 id="result-title"></h2>
            <p id="result-details"></p>
            <button class="btn btn-primary" id="close-modal-btn" style="width: 100px;">Close</button>
        </div>
    </div>

    <!-- Resume Interrupted Download Modal -->
    <div id="resume-modal">
        <div id="resume-modal-content">
            <div id="resume-modal-icon"><i class="fas fa-download"></i></div>
            <h2 id="resume-modal-title">Download Interrupted</h2>
            <p id="resume-modal-details">A previous modpack download was interrupted.</p>
            <div id="resume-modal-buttons">
                <button class="btn btn-secondary" id="resume-discard-btn"><i class="fas fa-trash"></i> Discard</button>
                <button class="btn btn-primary" id="resume-continue-btn"><i class="fas fa-play"></i> Resume</button>
            </div>
        </div>
    </div>

    <!-- Settings Drawer -->
    <div id="settings-drawer-overlay"></div>
    <div id="settings-drawer">
        <div id="settings-drawer-header">
            <span id="settings-drawer-title">Settings</span>
            <button id="settings-drawer-close-btn" title="Close settings"><i class="fas fa-times"></i></button>
        </div>
        <div id="settings-drawer-body">
            <div id="screen-settings">
                <label class="setup-label">Prism Launcher</label>
                <div class="folder-display" id="settings-prism-exe-display" title="Drag your 'prismlauncher.exe' here, or click Browse">
                    <i class="fas fa-rocket folder-type-icon"></i>
                    <span id="settings-prism-exe-text" class="placeholder">Drag or browse for 'prismlauncher.exe'...</span>
                    <i class="fas fa-chevron-right folder-browse-arrow"></i>
                </div>
                <div class="folder-buttons">
                    <button class="btn btn-secondary" id="settings-browse-prism-btn"><i class="fas fa-search"></i> Browse Executable...</button>
                </div>
                <label class="setup-label">Modpack Folder</label>
                <div class="folder-display" id="settings-instance-folder-display" title="Drag the 'minecraft' folder of your Kewz's Cobblemon instance here">
                    <i class="fas fa-folder-open folder-type-icon"></i>
                    <span id="settings-instance-folder-text" class="placeholder">Drag or browse for your '.../minecraft' folder</span>
                    <i class="fas fa-chevron-right folder-browse-arrow"></i>
                </div>
                <div class="folder-buttons">
                    <button class="btn btn-secondary" id="settings-browse-instance-btn"><i class="fas fa-folder-open"></i> Browse Folder...</button>
                </div>
                <button class="btn btn-primary" id="save-settings-btn" style="margin-top: 24px;" disabled>Save & Close</button>
                <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid rgba(0,207,170,0.12);">
                    <button class="btn" id="settings-quit-btn" style="width:100%; background: none; border: 1px solid rgba(229,57,53,0.25); color: #d45e5e; gap: 10px;">
                        <i class="fas fa-power-off"></i> Quit Launcher
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Debug Panel -->
    <div id="debug-panel">
        <h3>Debug Triggers</h3>
        <div class="debug-trigger">
            <span class="debug-trigger-name">Close Launcher</span>
            <span id="debug-close-status" class="debug-trigger-status pending">PENDING</span>
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
        let setupState = {{ prismPath: null, instancePath: null, modpackInstalled: false }};
        
        // (CORREGIDO) Declarar variables aquí, pero asignarlas dentro de DOMContentLoaded
        let domPlayer;
        let dom;

        // --- Background Video Slideshow (outer scope so Python evaluate_js can reach these) ---
        let bgVideoList = [];
        let bgVideoIndex = 0;
        let bgVideoPlaying = false;

        function _randomNextIndex() {{
            if (bgVideoList.length <= 1) return 0;
            let next;
            do {{ next = Math.floor(Math.random() * bgVideoList.length); }}
            while (next === bgVideoIndex);
            return next;
        }}

        function _loadBgVideo(index) {{
            const vid = dom && dom.bgVideo;
            if (!vid || bgVideoList.length === 0) return;
            vid.src = bgVideoList[index];
            vid.load();
            vid.play().catch(() => {{}});
        }}

        // Called by Python during a video download — updates progress bar + status line.
        function onBgVideoProgress(videoIdx, totalVideos, pct) {{
            if (dom && dom.updater.title) {{
                dom.updater.title.textContent = `Downloading Launcher Assets (${{videoIdx}}/${{totalVideos}})...`;
            }}
            const overall = Math.round(((videoIdx - 1) / totalVideos + pct / 100 / totalVideos) * 100);
            updateUpdaterProgress(overall);
        }}

        // Called by Python at each LFS resolution step with a stage label and detail string.
        function onBgVideoStatus(videoIdx, totalVideos, stage, detail) {{
            if (dom && dom.updater.title) {{
                dom.updater.title.textContent = `${{stage}} (${{videoIdx}}/${{totalVideos}})...`;
            }}
            if (dom && dom.updater.console) {{
                let line = dom.updater.console.querySelector('p[data-bg-progress]');
                if (!line) {{
                    line = document.createElement('p');
                    line.setAttribute('data-bg-progress', '1');
                    dom.updater.console.appendChild(line);
                }}
                line.textContent = detail ? `${{stage}}: ${{detail}}` : stage;
                dom.updater.console.scrollTop = dom.updater.console.scrollHeight;
            }}
        }}

        // Gate variables removed — videos load in background, app starts after update check only.
        let _firstVideoReady = false;

        // Called by Python each time a video becomes ready (downloaded or already cached).
        function onBgVideoReady(url) {{
            bgVideoList.push(url);
            if (!_firstVideoReady) {{
                _firstVideoReady = true;
                bgVideoIndex = Math.floor(Math.random() * bgVideoList.length);
                _loadBgVideo(bgVideoIndex);
            }}
        }}

        // Called by Python if the download fails for the first video.
        function onBgVideoError(msg) {{
            console.warn("Background video error:", msg);
        }}

        // --- Lógica del Panel de Depuración ---
        function toggleDebugPanel(visible) {{
            if (dom && dom.debugPanel) {{
                dom.debugPanel.style.display = visible ? 'block' : 'none';
            }}
        }}

        function updateDebugPanel(close_status) {{
            if (dom && dom.debugCloseStatus) {{
                // Actualizar estado de Cerrar Launcher
                dom.debugCloseStatus.textContent = close_status;
                dom.debugCloseStatus.className = 'debug-trigger-status'; // Reset class
                if (close_status === 'TRIGGERED') {{
                    dom.debugCloseStatus.classList.add('triggered');
                }} else {{
                    dom.debugCloseStatus.classList.add('pending');
                }}
            }}
        }}

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
            // (NUEVO) Guardar el volumen con debounce
            saveVolumeDebounced(volume);
        }}

        // --- (NUEVO) Debounce para guardar el volumen ---
        let saveVolumeTimeout;
        function saveVolumeDebounced(volume) {{
            clearTimeout(saveVolumeTimeout);
            saveVolumeTimeout = setTimeout(() => {{
                try {{
                    if (window.pywebview && window.pywebview.api) {{
                        console.log(`Guardando volumen: ${{volume}}`);
                        pywebview.api.py_save_music_volume(volume);
                    }}
                }} catch(e) {{
                    console.error("Error guardando el volumen:", e);
                }}
            }}, 300); // Guardar 300ms después de que el usuario deje de mover el slider
        }}
        // --- Fin Lógica Reproductor ---

        // --- (NUEVO) Flujo de Inicio y Actualización ---

        function logToUpdaterConsole(message) {{
            if (dom && dom.updater.console) {{
                const p = document.createElement('p');
                p.textContent = message;
                dom.updater.console.appendChild(p);
                dom.updater.console.scrollTop = dom.updater.console.scrollHeight;
            }}
        }}

        function updateUpdaterProgress(percentage) {{ // percentage es 0-100
            if (dom && dom.updater.progressBar) {{
                dom.updater.progressBar.style.width = `${{Math.max(0, Math.min(100, percentage))}}%`;
            }}
        }}

        function onUpdateCheckComplete(update_available, details_json) {{
            console.log(`onUpdateCheckComplete: available=${{update_available}}`);

            if (!update_available) {{
                // No update — hide updater and launch main app
                logToUpdaterConsole("You're up to date. Loading launcher...");
                updateUpdaterProgress(100);
                setTimeout(() => {{
                    if (dom.updater && dom.updater.screen) dom.updater.screen.classList.add('hidden');
                    startMainApp();
                }}, 1200);
                return;
            }}

            // Update available — keep updater visible, start countdown
            const details = JSON.parse(details_json);
            logToUpdaterConsole(`New version available: ${{details.version}}!`);
            dom.updater.title.textContent = `Update Available`;

            const notes = document.createElement('p');
            notes.innerHTML = `<strong>Release notes:</strong><br>${{details.notes || 'No notes available.'}}`;
            dom.updater.console.appendChild(notes);

            logToUpdaterConsole('This update is required and will start in 5 seconds...');

            let countdown = 5;
            const countdownInterval = setInterval(() => {{
                countdown--;
                if (countdown > 0) {{
                    logToUpdaterConsole(`Starting in ${{countdown}}...`);
                }} else {{
                    clearInterval(countdownInterval);
                    logToUpdaterConsole('Starting download...');
                    dom.updater.title.textContent = 'Downloading Update...';
                    dom.updater.buttons.innerHTML = '';
                    try {{
                        pywebview.api.py_download_and_apply_update();
                    }} catch (e) {{
                        onUpdateError("Could not start download: " + e.message);
                    }}
                }}
            }}, 1000);
        }}

        function onUpdateError(error_message) {{
            console.error("onUpdateError:", error_message);
            logToUpdaterConsole(`Warning: ${{error_message}}`);
            dom.updater.title.textContent = 'Update Check Failed';
            dom.updater.buttons.innerHTML = '';
            const skipButton = document.createElement('button');
            skipButton.textContent = 'Continue Anyway';
            skipButton.className = 'btn btn-secondary';
            skipButton.onclick = () => {{
                if (dom.updater && dom.updater.screen) dom.updater.screen.classList.add('hidden');
                startMainApp();
            }};
            dom.updater.buttons.appendChild(skipButton);
        }}

        // --- Funciones UI ---
        
        // --- Settings Drawer ---
        function openSettingsDrawer() {{
            validateSettings();
            dom.settingsDrawer.classList.add('open');
            dom.settingsDrawerOverlay.classList.add('visible');
        }}
        function closeSettingsDrawer() {{
            dom.settingsDrawer.classList.remove('open');
            dom.settingsDrawerOverlay.classList.remove('visible');
        }}

        // (ACTUALIZADO) switchScreen para manejar todas las pantallas
        function switchScreen(screenName) {{
            console.log("Switching screen to:", screenName);
            // Ocultar todo primero
            if (dom.updater && dom.updater.screen) dom.updater.screen.classList.add('hidden'); // Ocultar pantalla de actualización
            dom.screens.progress.style.display = 'none';
            dom.screens.progress.classList.remove('active');
            dom.mainContainer.classList.remove('visible');
            dom.screens.initialSetup.classList.remove('active');
            dom.screens.play.classList.remove('active');
            dom.minimizedWidget.style.display = 'none';
            isProgressMinimized = false;
            closeSidePanel();
            if (loadingAnimationId) {{ cancelAnimationFrame(loadingAnimationId); loadingAnimationId = null; }}

            // Ocultar reproductor y pantalla de juego en pantallas de configuración
            const isSetupScreen = (screenName === 'initial-setup' || screenName === 'settings');
            domPlayer.player.style.display = isSetupScreen ? 'none' : 'flex';
            domPlayer.player.classList.toggle('visible', !isSetupScreen);

            const showPlayBackground = (screenName !== 'initial-setup' && screenName !== 'settings');
            dom.screens.play.style.display = showPlayBackground ? 'flex' : 'none';
            dom.screens.play.classList.toggle('active', showPlayBackground);
            resumeBgVideoIfReady();

            // wizardMinimizeBtn shown/hidden by showWizardStep
            dom.wizardMinimizeBtn.style.display = 'none';

            if (screenName === 'play') {{
                // Determinar el estado del botón JUGAR/DESCARGAR/INSTALAR
                refreshPlayBtnLabel();
                dom.playBtn.classList.remove('cancel-mode');
            }} else if (screenName === 'initial-setup') {{
                dom.mainContainer.classList.add('visible');
                dom.screens.initialSetup.style.display = 'block';
                dom.screens.initialSetup.classList.add('active');
            }} else if (screenName === 'progress') {{
                if (isProgressMinimized) {{
                    dom.minimizedWidget.style.display = 'flex';
                }} else {{
                    dom.screens.progress.style.display = 'flex';
                    dom.screens.progress.classList.add('active');
                }}
            }} else if (screenName !== 'updater') {{
                console.warn("Attempt to switch to unknown screen:", screenName);
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
                    dom.settings.prismText.textContent = isPrismValid ? setupState.prismPath : "Drag or browse for 'prismlauncher.exe'...";
                    dom.settings.prismText.classList.toggle('placeholder', !isPrismValid);
                    dom.settings.instanceDisplay.classList.toggle('valid', isInstanceValid);
                    dom.settings.instanceDisplay.classList.toggle('invalid', !isInstanceValid && !!setupState.instancePath);
                    if (isInstanceValid) {{
                        dom.settings.instanceText.textContent = setupState.instancePath;
                        dom.settings.instanceText.classList.remove('placeholder');
                    }} else if (!setupState.instancePath) {{
                        dom.settings.instanceText.textContent = "Drag or browse for your '.../minecraft' folder";
                        dom.settings.instanceText.classList.add('placeholder');
                    }} else {{
                        dom.settings.instanceText.textContent = setupState.instancePath + " (Invalid)";
                        dom.settings.instanceText.classList.remove('placeholder');
                    }}
                    dom.settings.saveBtn.disabled = !(isPrismValid && isInstanceValid); 
                }}).catch(err => {{ console.error("Error validación JS:", err); dom.settings.saveBtn.disabled = true; }});
            }} catch (e) {{ console.error("Error crítico API en validateSettings:", e); showResult(false, "Error Validación", "Fallo comunicación Python: " + e); dom.settings.saveBtn.disabled = true; }}
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

                    // Forward to Updater Console if visible
                    if (dom.updater && dom.updater.screen && !dom.updater.screen.classList.contains('hidden')) {{
                        let cleanMsg = line;
                        if (line.startsWith('[LOG_PASSTHROUGH] ')) cleanMsg = line.substring(18);
                        else if (line.startsWith('[LOG_TRIGGER] ')) cleanMsg = line.substring(14);
                        logToUpdaterConsole(cleanMsg);
                    }}
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
        
        // --- Download Manager UI ---
        let downloadIsPaused = false;

        function _applyBannerState(ids, filename, label, paused) {{
            const {{ banner, name, size, badge, icon, lbl }} = ids;
            if (!banner) return;
            banner.classList.add('visible');
            if (name) name.textContent = filename;
            if (size) size.textContent = label;
            if (badge) badge.classList.toggle('visible', !!paused);
            if (icon) icon.className = paused ? 'fas fa-play' : 'fas fa-pause';
            if (lbl) lbl.textContent = paused ? 'Resume' : 'Pause';
        }}

        function updateDownloadDetails(filename, pct, label, paused) {{
            try {{
                downloadIsPaused = !!paused;
                _applyBannerState({{
                    banner: document.getElementById('download-details-banner'),
                    name: document.getElementById('download-filename'),
                    size: document.getElementById('download-size-label'),
                    badge: document.getElementById('download-paused-badge'),
                    icon: document.getElementById('pause-icon'),
                    lbl: document.getElementById('pause-label')
                }}, filename, label, paused);
                _applyBannerState({{
                    banner: document.getElementById('wizard-download-details'),
                    name: document.getElementById('wizard-dl-filename'),
                    size: document.getElementById('wizard-dl-size'),
                    badge: document.getElementById('wizard-paused-badge'),
                    icon: document.getElementById('wizard-pause-icon'),
                    lbl: document.getElementById('wizard-pause-label')
                }}, filename, label, paused);
                if (dom.minimizedProgressLabel) {{
                    dom.minimizedProgressLabel.textContent = filename || 'Downloading...';
                }}
            }} catch(e) {{ console.error("Error in updateDownloadDetails:", e); }}
        }}

        function togglePauseDownload() {{
            try {{
                if (downloadIsPaused) {{
                    pywebview.api.py_resume_download();
                    downloadIsPaused = false;
                }} else {{
                    pywebview.api.py_pause_download();
                    downloadIsPaused = true;
                }}
            }} catch(e) {{ console.error("Error toggling pause:", e); }}
        }}

        function hideDownloadDetails() {{
            const banner = document.getElementById('download-details-banner');
            if (banner) banner.classList.remove('visible');
            const wizardDetails = document.getElementById('wizard-download-details');
            if (wizardDetails) wizardDetails.classList.remove('visible');
            downloadIsPaused = false;
        }}
        // --- End Download Manager UI ---

        function setLoadScreen(title, progressLabel) {{
            try {{
                dom.progressTitle.textContent = title || "Processing...";
                dom.progressLabel.textContent = progressLabel || "...";
                dom.minimizedProgressLabel.textContent = progressLabel || "...";
                updateDebugPanel("PENDING");
                hideDownloadDetails();
            }} catch(e) {{ console.error("Error in setLoadScreen:", e); }}
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
            dom.progressLabel.textContent = "Loading Modpack...";
            dom.minimizedProgressLabel.textContent = "Loading Modpack...";

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

        function showResult(success, title, details) {{ try {{ lastUpdateWasSuccess = !!success; dom.modal.icon.innerHTML = success ? '<i class="fas fa-check-circle" style="color: var(--color-success);"></i>' : '<i class="fas fa-times-circle" style="color: var(--color-danger);"></i>'; dom.modal.title.textContent = title || (success ? 'Success' : 'Error'); dom.modal.details.innerHTML = details || (success ? "Process completed." : "An error occurred."); dom.modal.element.style.display = 'flex'; }} catch (e) {{ console.error("Error in showResult:", e); }} }}
        
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

        // (ACTUALIZADO) forceShowSetupScreen ahora abre el settings drawer
        function forceShowSetupScreen() {{
            openSettingsDrawer();
        }}

        // Refresh play button label from Python (async, updates when resolved)
        function refreshPlayBtnLabel() {{
            if (!setupState.prismPath || !setupState.instancePath) {{
                dom.playBtn.textContent = "DOWNLOAD";
                return;
            }}
            pywebview.api.py_is_modpack_installed().then(installed => {{
                setupState.modpackInstalled = installed;
                dom.playBtn.textContent = installed ? "PLAY" : "INSTALL";
            }}).catch(() => {{
                dom.playBtn.textContent = setupState.modpackInstalled ? "PLAY" : "INSTALL";
            }});
        }}

        function returnToPlayScreen() {{
            console.log("Returning to play screen (hiding progress/modal)."); 
            dom.modal.element.style.display = 'none'; 
            dom.screens.progress.style.display = 'none'; 
            dom.screens.progress.classList.remove('active'); 
            
            dom.minimizedWidget.style.display = 'none';
            isProgressMinimized = false;

            dom.cancelBtn.disabled = false; 
            dom.cancelBtn.textContent = "Cancel";
            updateProgress(0, ""); 
            dom.progressTitle.textContent = "Updating...";
            
            dom.playBtn.classList.remove('cancel-mode');
            dom.playBtn.disabled = false;
            refreshPlayBtnLabel();

            switchScreen('play'); 
        }}
        
        function cancelCurrentProcess() {{
            console.log("Manual cancellation initiated.");
            dom.cancelBtn.disabled = true; 
            dom.cancelBtn.textContent = "Cancelling..."; 
            dom.playBtn.disabled = true; 

            // (NUEVO) Cancelar también el botón del asistente
            dom.wizard.btnCancelInstall.disabled = true;
            dom.wizard.btnCancelInstall.textContent = "Cancelling...";

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
                dom.wizard.btnCancelInstall.textContent = "Cancel";
            }} else {{
                // Si estábamos en el juego, volver a la pantalla de juego
                returnToPlayScreen();
            }}
            
            // Re-habilitar botón principal
            setTimeout(() => {{
                dom.playBtn.disabled = false;
                dom.playBtn.classList.remove('cancel-mode');
                dom.playBtn.textContent = (setupState.prismPath && setupState.instancePath) ? "PLAY" : "DOWNLOAD";
            }}, 500);
        }}

        function addChangelogItem(title, description, icon_url, url, status) {{
            try {{
                const item = document.createElement('div');
                item.className = 'changelog-item';

                const img = document.createElement('img');
                img.src = (icon_url && status !== 'Removed') ? icon_url : 'https://placehold.co/32x32/2a2a2a/888?text=?';
                img.alt = title + ' icon';
                img.onerror = () => {{ img.src = 'https://placehold.co/32x32/2a2a2a/888?text=?'; }};

                const textDiv = document.createElement('div');
                const titleHeader = document.createElement('h4');

                const statusSpan = document.createElement('span');
                statusSpan.classList.add('status');
                if (status === 'Updated') {{
                    statusSpan.innerHTML = '<i class="fas fa-arrow-up"></i>';
                    statusSpan.classList.add('status-updated');
                    statusSpan.title = 'Updated';
                }} else if (status === 'Removed') {{
                    statusSpan.innerHTML = '<i class="fas fa-trash"></i>';
                    statusSpan.classList.add('status-removed');
                    statusSpan.title = 'Removed';
                }}
                titleHeader.appendChild(statusSpan);

                if (status !== 'Removed' && url) {{
                    const link = document.createElement('a');
                    link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer';
                    link.textContent = title || 'Unknown mod';
                    titleHeader.appendChild(link);
                }} else {{
                    const nameSpan = document.createElement('span');
                    nameSpan.classList.add('no-link');
                    nameSpan.textContent = title || 'Unknown mod';
                    titleHeader.appendChild(nameSpan);
                }}

                const descP = document.createElement('p');
                descP.textContent = (status !== 'Removed' && description) ? description : (status === 'Removed' ? 'Removed from modpack' : 'Updated / Added');

                textDiv.appendChild(titleHeader);
                textDiv.appendChild(descP);
                item.appendChild(img);
                item.appendChild(textDiv);
                dom.changelogContent.appendChild(item);
            }} catch(e) {{ console.error("Error adding changelog item:", e); }}
        }}
        function openSidePanel() {{ dom.sidePanel.classList.add('panel-open'); dom.panelOverlay.classList.add('visible'); }}
        function closeSidePanel() {{ dom.sidePanel.classList.remove('panel-open'); dom.panelOverlay.classList.remove('visible'); }}

        // Called by Python when a duplicate task start is attempted.
        // Instead of an error, we just bring whatever is running back into view.
        function restoreRunningTaskView() {{
            console.log("restoreRunningTaskView: bringing active task back into view.");
            isProgressMinimized = false;
            dom.minimizedWidget.style.display = 'none';
            if (dom.screens.initialSetup.classList.contains('active')) {{
                // Wizard was running — restore container and make sure install-progress step shows
                dom.mainContainer.classList.add('visible');
                const activeStep = document.querySelector('#screen-initial-setup .wizard-step.active');
                if (!activeStep || activeStep.getAttribute('data-step') !== 'install-progress') {{
                    showWizardStep('install-progress');
                }}
            }} else {{
                // Regular progress screen was running
                dom.screens.progress.style.display = 'flex';
                dom.screens.progress.classList.add('active');
            }}
        }}

        // --- Setup Wizard Logic ---

        function showWizardStep(stepName) {{
            console.log("Showing wizard step:", stepName);
            dom.wizard.steps.forEach(step => {{
                if (step.getAttribute('data-step') === stepName) {{
                    step.classList.add('active');
                }} else {{
                    step.classList.remove('active');
                }}
            }});
            // Show minimize button only during active download/install
            dom.wizardMinimizeBtn.style.display = (stepName === 'install-progress') ? 'flex' : 'none';
            // Resetear consola y progreso al mostrar un paso de instalación
            if (stepName === 'install-progress') {{
                dom.wizard.console.innerHTML = '';
                dom.wizard.progressBar.style.width = '0%';
                dom.wizard.progressLabel.textContent = 'Starting...';
                dom.wizard.btnCancelInstall.disabled = false;
                dom.wizard.btnCancelInstall.textContent = "Cancel";
            }}
        }}

        function startInitialSetupWizard() {{
            console.log("Starting initial setup wizard...");
            switchScreen('initial-setup');
            showWizardStep('start');
            try {{
                pywebview.api.py_setup_check_prism_default_path().then(result => {{
                    if (result.status === 'prism_detected') {{
                        handlePrismPathFound(result.path);
                    }} else {{
                        showWizardStep('ask-installed');
                    }}
                }}).catch(err => {{
                    console.error("Error in py_setup_check_prism_default_path:", err);
                    showResult(false, "Detection Error", "Could not check default path: " + err);
                    showWizardStep('ask-installed');
                }});
            }} catch (e) {{
                showResult(false, "Fatal Error", "Python API not available: " + e);
            }}
        }}

        function handlePrismPathFound(prismPath) {{
            console.log("Valid Prism path found:", prismPath);
            setupState.prismPath = prismPath;
            showWizardStep('check-modpack');
            try {{
                pywebview.api.py_setup_check_modpack_installed(prismPath).then(result => {{
                    if (result.status === 'modpack_installed') {{
                        console.log("Modpack already installed at:", result.instance_path);
                        setupState.instancePath = result.instance_path;
                        pywebview.api.py_save_paths(result.prism_path, result.instance_path);
                        showWizardStep('login');
                    }} else if (result.status === 'modpack_not_installed') {{
                        console.log("Modpack not installed. Starting download...");

                        if (!result.prism_path || !result.instance_base_path) {{
                             throw new Error("Incomplete data for modpack install: prism=" + result.prism_path + ", base=" + result.instance_base_path);
                        }}

                        showWizardStep('install-progress');
                        dom.wizard.installTitle.textContent = "Installing Kewz's Cobblemon";
                        dom.wizard.installSubtitle.textContent = "Downloading modpack files (10GB+). You can pause this at any time.";

                        console.log("Starting 'install_modpack' task with args:", result.prism_path, result.instance_base_path);
                        pywebview.api.py_start_threaded_task('install_modpack', result.prism_path, result.instance_base_path);
                    }} else {{
                        throw new Error(result.error || "Unknown response when checking modpack.");
                    }}
                }}).catch(err => {{
                    console.error("Error in py_setup_check_modpack_installed:", err);
                    showResult(false, "Modpack Error", "Could not check modpack instance: " + err);
                    showWizardStep('ask-installed'); // Volver al inicio del flujo
                }});
            }} catch (e) {{
                 showResult(false, "Error Fatal", "API Python no disponible: " + e);
            }}
        }}

        // --- Global Python Callbacks (from threads) ---

        function updateInstallStatus(message) {{
            try {{
                const p = document.createElement('p');
                p.appendChild(document.createTextNode(message));
                dom.wizard.console.appendChild(p);
                dom.wizard.console.scrollTop = dom.wizard.console.scrollHeight;
                dom.wizard.progressLabel.textContent = message;
            }} catch (e) {{ console.error("Error in updateInstallStatus:", e); }}
        }}

        function onPrismInstallComplete(success, path, error) {{
            if (success) {{
                console.log("Prism install complete, path:", path);
                handlePrismPathFound(path);
            }} else {{
                console.error("Prism install failed:", error);
                showResult(false, "Installation Error", "Could not install Prism Launcher: " + error);
                showWizardStep('ask-installed');
            }}
        }}

        function onModpackInstallComplete(success, prismPath, instancePath, error) {{
            if (success) {{
                console.log("Modpack install complete, path:", instancePath);
                setupState.prismPath = prismPath;
                setupState.instancePath = instancePath;
                hideDownloadDetails();
                pywebview.api.py_save_paths(prismPath, instancePath);
                showWizardStep('login');
            }} else {{
                console.error("Modpack install failed:", error);
                showResult(false, "Installation Error", "Could not install modpack: " + error);
                showWizardStep('ask-installed');
            }}
        }}

        function onTaskError(taskName, error) {{
            console.error("Error in task '" + taskName + "':", error);
            showResult(false, 'Error: ' + taskName, error);
            showWizardStep('ask-installed');
        }}


        // Helper: show progress screen and auto-start the modpack install+launch flow.
        // Called when Prism paths are saved but mods aren't installed yet.
        function _autoStartInstall(reason) {{
            console.log("Auto-starting install flow:", reason);
            dom.playBtn.textContent = "CANCEL";
            dom.playBtn.classList.add('cancel-mode');
            switchScreen('progress');
            dom.console.innerHTML = '';
            dom.changelogContent.innerHTML = '';
            logToConsole(reason);
            dom.cancelBtn.disabled = false;
            dom.cancelBtn.textContent = "Cancel";
            updateProgress(0, "Starting...");
            setLoadScreen("Installing Modpack...", "Getting things ready...");
            pywebview.api.py_start_game().catch(e => {{
                showResult(false, "Install Error", "Could not start installation: " + e);
                returnToPlayScreen();
            }});
        }}

        // Main app startup — called from onUpdateCheckComplete (no update) or onUpdateError.
        function startMainApp() {{
            console.log("startMainApp: loading config...");
            pywebview.api.py_get_os_sep().then(sep => {{
                osSep = sep || '/';
                return pywebview.api.py_load_and_migrate_config();
            }}).then(pathsAreValid => {{
                console.log("startMainApp: pathsAreValid =", pathsAreValid);

                // Load music in background (fire-and-forget)
                pywebview.api.py_get_playlist().then(p => {{
                    if (p && p.length > 0) {{ playlist = p; loadTrack(0); playTrack(); }}
                    else {{ domPlayer.title.textContent = "Playlist Error"; }}
                }}).catch(e => {{ domPlayer.title.textContent = "Playlist API Error"; console.error(e); }});
                pywebview.api.py_load_music_volume().then(vol => {{
                    domPlayer.volumeSlider.value = vol; setVolume();
                }}).catch(e => {{ domPlayer.volumeSlider.value = 1.0; setVolume(); }});

                // Show the right screen
                if (pathsAreValid) {{
                    switchScreen('play');
                }} else {{
                    startInitialSetupWizard();
                }}

                return pywebview.api.py_get_debug_status();
            }}).then(isDebug => {{
                dom.panelDebugBtn.style.display = isDebug ? 'flex' : 'none';
                return pywebview.api.py_get_launcher_version();
            }}).then(version => {{
                if (version) dom.launcherVersion.textContent = `v${{version}}`;
            }}).catch(e => {{
                console.error("startMainApp chain error:", e);
                startInitialSetupWizard();
            }});
        }}

        // --- Event Listeners ---
        window.addEventListener('pywebviewready', () => {{
            console.log("pywebviewready: Python API is ready.");
            window.pywebview.apiReady = true;
        }});

        document.addEventListener('DOMContentLoaded', () => {{
            console.log("DOMContentLoaded: DOM fully loaded.");

            // Cache all DOM elements
            domPlayer = {{
                player: document.getElementById('music-player'), cover: document.getElementById('album-cover'), title: document.getElementById('track-title'), artist: document.getElementById('track-artist'), audio: document.getElementById('audio-element'), playPauseBtn: document.getElementById('play-pause-btn'), nextBtn: document.getElementById('next-btn'), progressContainer: document.getElementById('progress-container'), progressBar: document.getElementById('progress-bar'), volumeContainer: document.getElementById('volume-container'), volumeIcon: document.getElementById('volume-icon'), volumeSlider: document.getElementById('volume-slider')
            }};
            dom = {{
                updater: {{ screen: document.getElementById('screen-updater'), title: document.getElementById('updater-title'), progressBar: document.getElementById('updater-progress-bar'), console: document.getElementById('updater-console'), buttons: document.getElementById('updater-buttons') }},
                mainContainer: document.getElementById('main-container'),
                screens: {{ initialSetup: document.getElementById('screen-initial-setup'), settings: document.getElementById('screen-settings'), play: document.getElementById('screen-play'), progress: document.getElementById('screen-progress') }},
                wizard: {{ steps: document.querySelectorAll('#screen-initial-setup .wizard-step'), btnAskYes: document.getElementById('wizard-btn-ask-yes'), btnAskNo: document.getElementById('wizard-btn-ask-no'), btnFindManual: document.getElementById('wizard-btn-find-manual'), btnInstallLocation: document.getElementById('wizard-btn-install-location'), btnCancelInstall: document.getElementById('wizard-btn-cancel-install'), btnLoginOpen: document.getElementById('wizard-btn-login-open'), btnLoginFinish: document.getElementById('wizard-btn-login-finish'), installTitle: document.getElementById('wizard-install-title'), installSubtitle: document.getElementById('wizard-install-subtitle'), progressBar: document.getElementById('wizard-progress-bar-fill'), progressLabel: document.getElementById('wizard-progress-label'), console: document.getElementById('wizard-console') }},
                settings: {{ prismDisplay: document.getElementById('settings-prism-exe-display'), prismText: document.getElementById('settings-prism-exe-text'), browsePrismBtn: document.getElementById('settings-browse-prism-btn'), instanceDisplay: document.getElementById('settings-instance-folder-display'), instanceText: document.getElementById('settings-instance-folder-text'), browseInstanceBtn: document.getElementById('settings-browse-instance-btn'), saveBtn: document.getElementById('save-settings-btn') }},
                playBtn: document.getElementById('play-btn'), menuBtn: document.getElementById('menu-btn'), sidePanel: document.getElementById('side-panel'), panelOverlay: document.getElementById('panel-overlay'), panelCloseBtn: document.getElementById('panel-close-btn'), panelSettingsBtn: document.getElementById('panel-settings-btn'), panelDebugBtn: document.getElementById('panel-debug-btn'), panelQuitBtn: document.getElementById('panel-quit-btn'), cancelBtn: document.getElementById('cancel-btn'), progressTitle: document.getElementById('progress-title'), progressBar: document.getElementById('progress-fill'), progressLabel: document.getElementById('progress-label'), console: document.getElementById('console'), scrollBottomBtn: document.getElementById('scroll-bottom-btn'), changelogContent: document.getElementById('changelog-content'),
                modal: {{ element: document.getElementById('result-modal'), icon: document.getElementById('result-icon'), title: document.getElementById('result-title'), details: document.getElementById('result-details'), closeBtn: document.getElementById('close-modal-btn') }},
                minimizeProgressBtn: document.getElementById('minimize-progress-btn'), minimizedWidget: document.getElementById('minimized-progress-widget'), minimizedProgressLabel: document.getElementById('minimized-progress-label'), minimizedProgressPercent: document.getElementById('minimized-progress-percent'), minimizedProgressBarFill: document.getElementById('minimized-progress-bar-fill'),
                wizardMinimizeBtn: document.getElementById('wizard-minimize-btn'),
                settingsDrawer: document.getElementById('settings-drawer'),
                settingsDrawerOverlay: document.getElementById('settings-drawer-overlay'),
                settingsDrawerCloseBtn: document.getElementById('settings-drawer-close-btn'),
                resumeModal: document.getElementById('resume-modal'),
                resumeDiscardBtn: document.getElementById('resume-discard-btn'),
                resumeContinueBtn: document.getElementById('resume-continue-btn'),
                debugPanel: document.getElementById('debug-panel'), debugCloseStatus: document.getElementById('debug-close-status'), launcherVersion: document.getElementById('launcher-version'),
                bgVideo: document.getElementById('bg-video')
            }};

            // --- Background Video event listeners (video list + gate managed at outer scope) ---

            if (dom.bgVideo) {{
                dom.bgVideo.addEventListener('ended', () => {{
                    if (bgVideoList.length === 0) return;
                    bgVideoIndex = _randomNextIndex();
                    _loadBgVideo(bgVideoIndex);
                }});
                dom.bgVideo.addEventListener('error', () => {{
                    if (bgVideoList.length === 0) return;
                    bgVideoIndex = _randomNextIndex();
                    setTimeout(() => _loadBgVideo(bgVideoIndex), 500);
                }});
            }}

            // Retry bg video play when the play screen becomes visible
            // (video may have been loaded while screen was display:none)
            function resumeBgVideoIfReady() {{
                const vid = dom.bgVideo;
                if (!vid || bgVideoList.length === 0) return;
                if (!vid.src || vid.src === window.location.href) {{
                    // No video loaded yet — pick a random one and start it
                    bgVideoIndex = Math.floor(Math.random() * bgVideoList.length);
                    _loadBgVideo(bgVideoIndex);
                }} else if (vid.paused && vid.readyState >= 2) {{
                    vid.play().catch(() => {{}});
                }}
            }}

            // Main entry point
            let _initRetries = 0;
            function initializeApp() {{
                if (!window.pywebview || !window.pywebview.apiReady) {{
                    if (++_initRetries > 200) {{ // 10s max wait
                        onUpdateError("Python backend did not become ready in time.");
                        return;
                    }}
                    return setTimeout(initializeApp, 50);
                }}
                console.log("DOM and API ready! Initializing app...");
                window.quitting = false;
                window.startMainApp = startMainApp;

                // Start bg video download in background (does not block startup)
                try {{ pywebview.api.py_ensure_background_videos().catch(() => {{}}); }}
                catch(e) {{ console.warn("Could not start background video download:", e); }}

                // Start update check — onUpdateCheckComplete/onUpdateError will call startMainApp
                try {{ pywebview.api.py_start_update_check(); }}
                catch(e) {{ onUpdateError(`Backend communication failed: ${{e}}`); }}
            }}

            // Iniciar la aplicación
            initializeApp();

            // --- Adjuntar Listeners de UI ---
            dom.wizard.btnAskYes.addEventListener('click', () => showWizardStep('find-manual'));
            dom.wizard.btnAskNo.addEventListener('click', () => showWizardStep('install-location'));
            
            dom.wizard.btnFindManual.addEventListener('click', () => {{
                pywebview.api.py_setup_ask_for_prism_path().then(result => {{
                    if (result.status === 'path_valid') {{ handlePrismPathFound(result.path); }}
                    else if (result.status === 'path_invalid') {{ showResult(false, "Ruta Inválida", result.error); }}
                }}).catch(err => showResult(false, "Error", "No se pudo abrir diálogo: " + err));
            }});
            
            dom.wizard.btnInstallLocation.addEventListener('click', () => {{
                pywebview.api.py_setup_ask_for_install_location().then(result => {{
                    if (result.status === 'path_valid') {{
                        showWizardStep('install-progress');
                        dom.wizard.installTitle.textContent = "Instalando Prism Launcher";
                        dom.wizard.installSubtitle.textContent = "Descargando la versión portable...";
                        console.log("Starting 'install_prism' task with path:", result.path);
                        pywebview.api.py_start_threaded_task('install_prism', result.path);
                    }}
                }}).catch(err => showResult(false, "Error", "Could not open dialog: " + err));
            }});

            dom.wizard.btnCancelInstall.addEventListener('click', cancelCurrentProcess);
            dom.wizard.btnLoginOpen.addEventListener('click', () => pywebview.api.py_setup_open_prism_for_login(setupState.prismPath).catch(e => showResult(false, "Error", "Could not open Prism: " + e)));
            dom.wizard.btnLoginFinish.addEventListener('click', () => pywebview.api.py_save_paths(setupState.prismPath, setupState.instancePath).then(() => switchScreen('play')));

            // Settings Screen Listeners
            dom.settings.browsePrismBtn.addEventListener('click', () => pywebview.api.py_browse_for_prism_exe().then(data => {{ if (data && data.is_valid) {{ setupState.prismPath = data.prism_path; setupState.instancePath = data.instance_path; }} else {{ setupState.prismPath = null; setupState.instancePath = null; }} validateSettings(); }}).catch(err => showResult(false, "Browse Error", "Could not open dialog: " + err)));
            dom.settings.browseInstanceBtn.addEventListener('click', () => pywebview.api.py_browse_for_instance_folder().then(path => {{ setupState.instancePath = path; validateSettings(); }}).catch(err => showResult(false, "Browse Error", "Could not open dialog: " + err)));
            [dom.settings.prismDisplay, dom.settings.instanceDisplay].forEach(el => {{
                el.addEventListener('dragenter', (e) => {{ e.preventDefault(); e.stopPropagation(); el.classList.add('dragover'); }}, false);
                el.addEventListener('dragover', (e) => {{ e.preventDefault(); e.stopPropagation(); el.classList.add('dragover'); }}, false);
                el.addEventListener('dragleave', (e) => {{ e.preventDefault(); e.stopPropagation(); el.classList.remove('dragover'); }}, false);
                el.addEventListener('drop', (e) => {{
                    e.preventDefault(); e.stopPropagation(); el.classList.remove('dragover');
                    if (e.dataTransfer.items && e.dataTransfer.items.length > 0 && e.dataTransfer.items[0].kind === 'file') {{
                        const droppedPath = e.dataTransfer.files[0].path; if (!droppedPath) return;
                        if (el === dom.settings.prismDisplay) pywebview.api.py_process_prism_path_drop(droppedPath).then(data => {{ setupState.prismPath = data.prism_path; setupState.instancePath = data.instance_path; validateSettings(); }}).catch(err => console.error("Prism drop error:", err));
                        else pywebview.api.py_process_instance_path_drop(droppedPath).then(data => {{ setupState.instancePath = data.path; validateSettings(); }}).catch(err => console.error("Instance drop error:", err));
                    }}
                }}, false);
            }});
            dom.settings.saveBtn.addEventListener('click', () => {{
                if (dom.settings.saveBtn.disabled) return;
                pywebview.api.py_save_paths(setupState.prismPath, setupState.instancePath).then(didSave => {{
                    if (didSave) {{
                        closeSettingsDrawer();
                        // Update play button label in case paths changed
                        if (setupState.prismPath && setupState.instancePath) {{
                            dom.playBtn.textContent = "PLAY";
                        }}
                    }} else showResult(false, "Save Error", "Could not save paths.");
                }}).catch(err => showResult(false, "Unexpected Error", "Could not save config: " + err));
            }});

            // Play Screen Listeners
            dom.playBtn.addEventListener('click', () => {{
                if (dom.playBtn.classList.contains('cancel-mode')) {{
                    cancelCurrentProcess();
                }} else {{
                    if (!setupState.prismPath || !setupState.instancePath) {{
                        // If a wizard download is already running (just minimized), restore it
                        // instead of restarting setup — which would cause a task conflict.
                        if (isProgressMinimized && dom.screens.initialSetup.classList.contains('active')) {{
                            restoreRunningTaskView();
                            return;
                        }}
                        // If the setup wizard is already visible, just scroll/pulse it into focus
                        // instead of restarting it (which would lose wizard progress).
                        if (dom.screens.initialSetup.classList.contains('active')) {{
                            dom.mainContainer.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                            dom.mainContainer.style.transition = 'box-shadow 0.2s';
                            dom.mainContainer.style.boxShadow = '0 0 0 3px var(--color-accent)';
                            setTimeout(() => {{ dom.mainContainer.style.boxShadow = ''; }}, 600);
                            return;
                        }}
                        console.log("Paths not set, starting setup wizard...");
                        startInitialSetupWizard();
                    }} else {{
                        dom.playBtn.textContent = "CANCEL"; dom.playBtn.classList.add('cancel-mode');
                        switchScreen('progress');
                        dom.console.innerHTML = ''; dom.changelogContent.innerHTML = '';
                        logToConsole("Starting process...");
                        dom.cancelBtn.disabled = false; dom.cancelBtn.textContent = "Cancel";
                        updateProgress(0, "Starting...");
                        setLoadScreen(setupState.modpackInstalled ? "Updating..." : "Installing...", "Checking versions...");
                        pywebview.api.py_start_game().catch(e => {{
                            showResult(false, "API Error", "Could not start game: " + e);
                            returnToPlayScreen();
                        }});
                    }}
                }}
             }});
            dom.menuBtn.addEventListener('click', openSidePanel);

            // Side Panel Listeners
            dom.panelOverlay.addEventListener('click', closeSidePanel);
            dom.panelCloseBtn.addEventListener('click', closeSidePanel);
            dom.panelSettingsBtn.addEventListener('click', () => {{ closeSidePanel(); openSettingsDrawer(); }});
            dom.panelDebugBtn.addEventListener('click', () => {{ const isVisible = dom.debugPanel.style.display === 'block'; toggleDebugPanel(!isVisible); closeSidePanel(); }});
            dom.panelQuitBtn.addEventListener('click', () => {{ if (!window.quitting) {{ window.quitting = true; pywebview.api.py_quit_launcher(); }} }});

            // Progress Screen Listeners
            dom.cancelBtn.addEventListener('click', cancelCurrentProcess);
            dom.console.addEventListener('scroll', () => {{ const atBottom = (dom.console.scrollHeight - dom.console.scrollTop - dom.console.clientHeight) < 30; isScrolledToBottom = atBottom; dom.scrollBottomBtn.classList.toggle('visible', !atBottom); }});
            dom.scrollBottomBtn.addEventListener('click', () => {{ dom.console.scrollTop = dom.console.scrollHeight; isScrolledToBottom = true; dom.scrollBottomBtn.classList.remove('visible'); }});

            dom.minimizeProgressBtn.addEventListener('click', () => {{
                isProgressMinimized = true;
                const currentMainWidth = dom.progressBar.style.width;
                dom.minimizedProgressBarFill.style.transition = 'none';
                dom.minimizedProgressBarFill.style.width = currentMainWidth;
                setTimeout(() => {{ dom.minimizedProgressBarFill.style.transition = 'width 0.3s ease'; }}, 50);
                dom.screens.progress.style.display = 'none';
                dom.minimizedWidget.style.display = 'flex';
            }});
             dom.minimizedWidget.addEventListener('click', () => {{
                 isProgressMinimized = false;
                 dom.minimizedWidget.style.display = 'none';
                 if (dom.screens.initialSetup.classList.contains('active')) {{
                     dom.mainContainer.classList.add('visible');
                 }} else {{
                     dom.screens.progress.style.display = 'flex';
                 }}
             }});

            // Settings drawer close button + overlay
            dom.settingsDrawerCloseBtn.addEventListener('click', closeSettingsDrawer);
            dom.settingsDrawerOverlay.addEventListener('click', closeSettingsDrawer);
            document.getElementById('settings-quit-btn').addEventListener('click', () => {{
                if (!window.quitting) {{ window.quitting = true; pywebview.api.py_quit_launcher(); }}
            }});

            // Wizard minimize button
            dom.wizardMinimizeBtn.addEventListener('click', () => {{
                isProgressMinimized = true;
                const currentWidth = dom.wizard.progressBar.style.width;
                dom.minimizedProgressBarFill.style.transition = 'none';
                dom.minimizedProgressBarFill.style.width = currentWidth || '0%';
                setTimeout(() => {{ dom.minimizedProgressBarFill.style.transition = 'width 0.3s ease'; }}, 50);
                dom.mainContainer.classList.remove('visible');
                dom.minimizedWidget.style.display = 'flex';
            }});

            // Resume modal buttons
            dom.resumeDiscardBtn.addEventListener('click', () => {{
                dom.resumeModal.classList.remove('visible');
                pywebview.api.py_discard_interrupted_download().catch(e => console.error("Error discarding download:", e));
                if (setupState.prismPath && setupState.instancePath) {{
                    switchScreen('play');
                }} else {{
                    startInitialSetupWizard();
                }}
            }});
            dom.resumeContinueBtn.addEventListener('click', () => {{
                dom.resumeModal.classList.remove('visible');
                const info = dom.resumeModal._interruptedInfo;
                if (!info || !info.extra) {{ startInitialSetupWizard(); return; }}
                const {{ prism_exe_path, instance_base_path }} = info.extra;
                if (!prism_exe_path || !instance_base_path) {{ startInitialSetupWizard(); return; }}
                // Resume the download via the wizard progress step
                switchScreen('initial-setup');
                showWizardStep('install-progress');
                dom.wizard.installTitle.textContent = "Resuming Download...";
                dom.wizard.installSubtitle.textContent = `Resuming from ${{(info.bytes_downloaded / 1048576).toFixed(1)}} MB. Large files can be paused.`;
                pywebview.api.py_start_threaded_task('install_modpack', prism_exe_path, instance_base_path);
            }});

            // Modal & Music Player Listeners
            dom.modal.closeBtn.addEventListener('click', returnToPlayScreen);
            domPlayer.playPauseBtn.addEventListener('click', () => {{ if (isPlaying) pauseTrack(); else playTrack(); }});
            domPlayer.nextBtn.addEventListener('click', nextTrack);
            domPlayer.audio.addEventListener('ended', nextTrack);
            domPlayer.audio.addEventListener('error', (e) => {{ console.error("Audio error:", domPlayer.audio.error); domPlayer.title.textContent = "Load Error"; domPlayer.artist.textContent = playlist[currentTrackIndex]?.src || "Invalid URL"; domPlayer.progressBar.style.width = '0%'; }});
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
        <!-- Elemento Audio (oculto) -->
        <audio id="audio-element" preload="metadata"></audio>

        <!-- (NUEVO) Display de Versión -->
        <div id="launcher-version"></div>
</body>
</html>
"""
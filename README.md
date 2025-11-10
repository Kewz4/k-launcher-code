# Kewz's Vanilla+ True Launcher

Este es el launcher personalizado para el modpack **Kewz's Vanilla+ True**, diseñado para ofrecer una experiencia de instalación, actualización y juego fluida y automatizada.

## ✨ Características Principales

- **Instalación Automática de Prism Launcher**: Si no detecta una instalación existente, el launcher puede descargar y configurar una versión portable de **Prism Launcher** por ti.
- **Instalación del Modpack con Un Clic**: Instala la última versión de **Kewz's Vanilla+ True** directamente desde el repositorio, creando una instancia dedicada en Prism Launcher.
- **Actualizaciones Automáticas**: Cada vez que inicias el juego, el launcher comprueba si hay una nueva versión del modpack. Si existe, descarga y aplica las actualizaciones de forma segura, respaldando tus archivos por si algo sale mal.
- **Sincronización de Opciones**: Sincroniza automáticamente las configuraciones de `options.txt` relacionadas con los resource packs para asegurar que siempre tengas la configuración visual recomendada, sin perder tus ajustes personales.
- **Reproductor de Música Integrado**: Disfruta de una selección de música curada directamente desde la interfaz del launcher, con controles de reproducción y volumen.
- **Panel de Depuración en Tiempo Real**: Ofrece un feedback visual sobre los eventos clave durante el lanzamiento del juego, como la detección de triggers para el audio y el cierre del launcher.
- **Interfaz Moderna y Personalizada**: Una interfaz de usuario limpia y fácil de usar, diseñada específicamente para el modpack.

## 🚀 Cómo Empezar

1.  **Descarga el Launcher**: Obtén la última versión del launcher (`VPlus_Launcher_vX.X.X.exe`) desde la sección de **Releases**.
2.  **Ejecuta el Launcher**: Coloca el ejecutable en una carpeta de tu elección (por ejemplo, en el escritorio o en `C:\Games\VPlusLauncher`) y ejecútalo.
3.  **Sigue el Asistente de Configuración**:
    -   El launcher buscará automáticamente una instalación de **Prism Launcher**.
    -   Si no la encuentra, te preguntará si deseas que descargue una versión portable o si prefieres localizar tu instalación existente manualmente.
    -   Una vez configurado Prism, detectará si el modpack **Kewz's Vanilla+ True** está instalado.
    -   Si no lo está, te guiará para instalarlo con un solo clic.
4.  **Inicia Sesión en Prism (Primera Vez)**: Antes de poder jugar, el asistente te pedirá que abras Prism Launcher para que **inicies sesión con tu cuenta de Minecraft**. Este es un paso único y necesario.
5.  **¡Juega!**: Una vez completada la configuración, simplemente haz clic en el botón **JUGAR**. El launcher se encargará de buscar actualizaciones y lanzar el juego.

## 🛠️ Lógica de Actualización Detallada

El sistema de actualización es una de las características más importantes de este launcher. Así es como funciona:

### Eliminación Segura de Archivos

-   Antes de aplicar una actualización, el launcher busca archivos de control como `removedshaderpacks.txt`, `removedconfigs.txt`, y `removedmods.txt` dentro de las carpetas correspondientes del paquete de actualización.
-   Estos archivos le indican al launcher qué archivos o carpetas deben ser eliminados de tu instalación local para evitar conflictos.
-   **Palabra Clave `all`**: Si uno de estos archivos contiene la palabra `all`, el launcher vaciará completamente el directorio correspondiente (por ejemplo, `shaderpacks`), asegurando una actualización limpia.
-   **Respaldo Automático**: Antes de eliminar cualquier archivo o carpeta, se crea un respaldo en un directorio temporal. Si la actualización falla por cualquier motivo, el launcher **revierte todos los cambios automáticamente**, restaurando los archivos desde el respaldo.

### Fusión de Archivos

-   Después de las eliminaciones, el launcher copia los archivos nuevos o actualizados desde el paquete de actualización a tu carpeta de instancia.
-   Si un archivo ya existe (por ej., un archivo de configuración), se respalda la versión antigua antes de ser reemplazado por la nueva.

## 🔇 Control de Audio Durante el Lanzamiento

-   Para evitar el molesto sonido de carga de recursos de Minecraft, el launcher **silencia automáticamente el proceso del juego** (`javaw.exe`) en cuanto este se inicia.
-   Una vez que el juego ha cargado completamente los recursos (detectado por la línea de log `[FANCYMENU] Minecraft resource reload: FINISHED` por segunda vez), el launcher **reactiva el sonido** para que no te pierdas nada.
-   El launcher se cerrará automáticamente solo cuando detecte que el juego está completamente cargado y listo para jugar (usando el trigger `[ModernFix/]: Game took`).

## 📄 Archivos de Configuración

-   `launcher_config.json`: Este archivo se crea en la misma carpeta que el launcher y guarda las rutas a tu ejecutable de Prism y a la instancia del modpack.
-   `options_backup.txt`: Un respaldo de tu `options.txt` que se actualiza cada vez que juegas, asegurando que tus configuraciones importantes estén a salvo.

## ❓ Preguntas Frecuentes

**¿Necesito tener Prism Launcher instalado de antemano?**
No. El launcher puede descargar una versión portable por ti, lo cual es el método recomendado para una experiencia sin complicaciones.

**¿Qué pasa si la actualización falla?**
No te preocupes. El launcher está diseñado para ser seguro. Si algo sale mal, revertirá todos los cambios y te mostrará un mensaje de error. Tu instalación del modpack quedará como estaba antes de intentar actualizar.

**¿Puedo usar mi instalación existente de Prism Launcher?**
Sí. Durante el asistente de configuración, puedes seleccionar la opción para buscar manualmente tu archivo `PrismLauncher.exe`.

**¿El launcher es de código abierto?**
Sí, puedes revisar todo el código fuente en el repositorio de GitLab para asegurarte de su funcionamiento y seguridad.

---
*Desarrollado con ❤️ para la comunidad de Vanilla+ True.*
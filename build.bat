@echo off
:: ============================================================
:: Vanilla+ Launcher — build script
:: ============================================================
:: Requirements:
::   pip install pyinstaller pywebview psutil pywin32 requests
::
:: SmartScreen note:
::   For the cleanest SmartScreen experience, sign the produced
::   exe after building:
::
::     signtool sign /fd SHA256 /tr http://timestamp.digicert.com ^
::       /td SHA256 /f YourCert.pfx /p YourPassword ^
::       dist\VanillaPlusLauncher.exe
::
::   Even without a certificate, disabling UPX and embedding
::   version info (already done in the spec) reduces AV false
::   positives significantly.
:: ============================================================

echo [Build] Cleaning old build...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

echo [Build] Running PyInstaller...
pyinstaller --clean launcher.spec

if errorlevel 1 (
    echo [Build] FAILED — check output above.
    pause
    exit /b 1
)

echo.
echo [Build] Done!  Exe is at: dist\VanillaPlusLauncher.exe
echo.
echo [Optional] To code-sign:
echo   signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 /f cert.pfx /p password dist\VanillaPlusLauncher.exe
echo.
pause

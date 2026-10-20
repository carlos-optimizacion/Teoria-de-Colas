@echo off
setlocal
cd /d "%~dp0"
echo =============================================
echo     DECISION LAB 2.0 - APLICATIVO APP
echo =============================================
if not exist ".venv-app\Scripts\python.exe" (
    echo Creando entorno Python aislado...
    py -3 -m venv .venv-app
    if errorlevel 1 (
        echo Error: instala Python 3.12 o superior.
        pause
        exit /b 1
    )
)
call ".venv-app\Scripts\activate.bat"
python -m pip install -r django_app\requirements.txt
if errorlevel 1 goto error
cd django_app
python manage.py migrate --noinput
if errorlevel 1 goto error
echo Abre http://127.0.0.1:8000/aplicativo-app/
start "" "http://127.0.0.1:8000/aplicativo-app/"
python manage.py runserver 127.0.0.1:8000
goto end
:error
echo No se pudo iniciar la aplicacion. Comprueba Python y la conexion.
pause
:end
endlocal

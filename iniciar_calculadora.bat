@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_CMD="

where py >nul 2>nul
if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>nul
    if %ERRORLEVEL%==0 (
        set "PYTHON_CMD=python"
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERRO] Python nao encontrado.
    echo Instale o Python 3 e marque a opcao "Add Python to PATH".
    pause
    exit /b 1
)

echo [OK] Python detectado: %PYTHON_CMD%

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual em .venv...
    %PYTHON_CMD% -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
)

echo Atualizando pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Falha ao atualizar o pip.
    pause
    exit /b 1
)

echo Instalando dependencias de requirements.txt...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo Iniciando aplicacao...
".venv\Scripts\python.exe" app.py

endlocal

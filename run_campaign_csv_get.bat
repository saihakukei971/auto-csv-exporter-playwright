@echo off
setlocal enabledelayedexpansion

REM ==========================================================
REM fam8キャンペーンCSV自動取得処理実行バッチ
REM 機能：埋め込みPython環境を使用してPlaywright処理を実行する
REM ==========================================================

REM 現在のバッチファイルの場所を取得
set "SCRIPT_DIR=%~dp0"
set "PYTHON_DIR=%SCRIPT_DIR%..\Python実行環境"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "SCRIPT_PATH=%SCRIPT_DIR%get_campaign_csv_auto_2mode.py"
set "LOG_DIR=%SCRIPT_DIR%log"
set "LOG_FILE=%LOG_DIR%\batch_execution_%date:~0,4%%date:~5,2%%date:~8,2%.log"

REM ログディレクトリが存在しない場合は作成
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM バッチ実行のログ開始
echo [INFO] %date% %time% - fam8キャンペーンCSV自動取得処理を開始します >> "%LOG_FILE%"

REM Pythonインタプリタの存在確認
if not exist "%PYTHON_EXE%" (
    echo [ERROR] %date% %time% - Pythonインタプリタが見つかりません: %PYTHON_EXE% >> "%LOG_FILE%"
    echo Pythonインタプリタが見つかりません: %PYTHON_EXE%
    exit /b 1
)

REM スクリプトの存在確認
if not exist "%SCRIPT_PATH%" (
    echo [ERROR] %date% %time% - Pythonスクリプトが見つかりません: %SCRIPT_PATH% >> "%LOG_FILE%"
    echo Pythonスクリプトが見つかりません: %SCRIPT_PATH%
    exit /b 1
)

REM 実行コマンドのログ
echo [INFO] %date% %time% - Pythonスクリプトを実行します: "%PYTHON_EXE%" "%SCRIPT_PATH%" >> "%LOG_FILE%"

REM コマンド実行とエラーコード取得
echo スクリプトを実行中です...しばらくお待ちください...
"%PYTHON_EXE%" "%SCRIPT_PATH%" 2>> "%LOG_FILE%"
set "EXIT_CODE=%ERRORLEVEL%"

REM 実行結果のログ
if %EXIT_CODE% equ 0 (
    echo [INFO] %date% %time% - スクリプトが正常に実行されました（終了コード: %EXIT_CODE%） >> "%LOG_FILE%"
    echo スクリプトが正常に実行されました。
) else (
    echo [ERROR] %date% %time% - スクリプトの実行中にエラーが発生しました（終了コード: %EXIT_CODE%） >> "%LOG_FILE%"
    echo スクリプトの実行中にエラーが発生しました（終了コード: %EXIT_CODE%）
)

echo [INFO] %date% %time% - fam8キャンペーンCSV自動取得処理を終了します >> "%LOG_FILE%"

REM 処理終了
exit /b %EXIT_CODE%

pause
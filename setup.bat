@echo off
setlocal enabledelayedexpansion

REM ---------------------------------------------
REM Playwrightブラウザ（Chromium）インストール専用バッチ
REM 配置場所：D:\rep05\キャンペーンレポートCSV取得\
REM ---------------------------------------------

REM このバッチのある場所を取得
set BASEDIR=%~dp0
cd /d "%BASEDIR%"

REM Python実行環境のパス
set PYTHON="%BASEDIR%Python実行環境\python.exe"

REM 実行前チェック：python.exe の存在確認
if not exist %PYTHON% (
    echo [ERROR] Python実行環境が見つかりません：%PYTHON%
    pause
    exit /b 1
)

REM Playwrightブラウザ（chromium）のインストール実行
echo [INFO] Playwright用Chromiumをインストール中...
%PYTHON% -m playwright install chromium

if errorlevel 1 (
    echo [ERROR] インストール中にエラーが発生しました。ネット接続を確認してください。
    pause
    exit /b 1
)

echo [INFO] Chromiumのインストールが完了しました。
pause

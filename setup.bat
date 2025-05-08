@echo off
setlocal enabledelayedexpansion

REM ---------------------------------------------
REM Playwright�u���E�U�iChromium�j�C���X�g�[����p�o�b�`
REM �z�u�ꏊ�FD:\rep05\�L�����y�[�����|�[�gCSV�擾\
REM ---------------------------------------------

REM ���̃o�b�`�̂���ꏊ���擾
set BASEDIR=%~dp0
cd /d "%BASEDIR%"

REM Python���s���̃p�X
set PYTHON="%BASEDIR%Python���s��\python.exe"

REM ���s�O�`�F�b�N�Fpython.exe �̑��݊m�F
if not exist %PYTHON% (
    echo [ERROR] Python���s����������܂���F%PYTHON%
    pause
    exit /b 1
)

REM Playwright�u���E�U�ichromium�j�̃C���X�g�[�����s
echo [INFO] Playwright�pChromium���C���X�g�[����...
%PYTHON% -m playwright install chromium

if errorlevel 1 (
    echo [ERROR] �C���X�g�[�����ɃG���[���������܂����B�l�b�g�ڑ����m�F���Ă��������B
    pause
    exit /b 1
)

echo [INFO] Chromium�̃C���X�g�[�����������܂����B
pause

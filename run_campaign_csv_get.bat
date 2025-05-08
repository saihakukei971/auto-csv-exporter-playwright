@echo off
setlocal enabledelayedexpansion

REM ==========================================================
REM fam8�L�����y�[��CSV�����擾�������s�o�b�`
REM �@�\�F���ߍ���Python�����g�p����Playwright���������s����
REM ==========================================================

REM ���݂̃o�b�`�t�@�C���̏ꏊ���擾
set "SCRIPT_DIR=%~dp0"
set "PYTHON_DIR=%SCRIPT_DIR%..\Python���s��"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "SCRIPT_PATH=%SCRIPT_DIR%get_campaign_csv_auto_2mode.py"
set "LOG_DIR=%SCRIPT_DIR%log"
set "LOG_FILE=%LOG_DIR%\batch_execution_%date:~0,4%%date:~5,2%%date:~8,2%.log"

REM ���O�f�B���N�g�������݂��Ȃ��ꍇ�͍쐬
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM �o�b�`���s�̃��O�J�n
echo [INFO] %date% %time% - fam8�L�����y�[��CSV�����擾�������J�n���܂� >> "%LOG_FILE%"

REM Python�C���^�v���^�̑��݊m�F
if not exist "%PYTHON_EXE%" (
    echo [ERROR] %date% %time% - Python�C���^�v���^��������܂���: %PYTHON_EXE% >> "%LOG_FILE%"
    echo Python�C���^�v���^��������܂���: %PYTHON_EXE%
    exit /b 1
)

REM �X�N���v�g�̑��݊m�F
if not exist "%SCRIPT_PATH%" (
    echo [ERROR] %date% %time% - Python�X�N���v�g��������܂���: %SCRIPT_PATH% >> "%LOG_FILE%"
    echo Python�X�N���v�g��������܂���: %SCRIPT_PATH%
    exit /b 1
)

REM ���s�R�}���h�̃��O
echo [INFO] %date% %time% - Python�X�N���v�g�����s���܂�: "%PYTHON_EXE%" "%SCRIPT_PATH%" >> "%LOG_FILE%"

REM �R�}���h���s�ƃG���[�R�[�h�擾
echo �X�N���v�g�����s���ł�...���΂炭���҂���������...
"%PYTHON_EXE%" "%SCRIPT_PATH%" 2>> "%LOG_FILE%"
set "EXIT_CODE=%ERRORLEVEL%"

REM ���s���ʂ̃��O
if %EXIT_CODE% equ 0 (
    echo [INFO] %date% %time% - �X�N���v�g������Ɏ��s����܂����i�I���R�[�h: %EXIT_CODE%�j >> "%LOG_FILE%"
    echo �X�N���v�g������Ɏ��s����܂����B
) else (
    echo [ERROR] %date% %time% - �X�N���v�g�̎��s���ɃG���[���������܂����i�I���R�[�h: %EXIT_CODE%�j >> "%LOG_FILE%"
    echo �X�N���v�g�̎��s���ɃG���[���������܂����i�I���R�[�h: %EXIT_CODE%�j
)

echo [INFO] %date% %time% - fam8�L�����y�[��CSV�����擾�������I�����܂� >> "%LOG_FILE%"

REM �����I��
exit /b %EXIT_CODE%

pause
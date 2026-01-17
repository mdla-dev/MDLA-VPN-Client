@echo off
echo ========================================
echo MDLA Android APK Builder
echo ========================================
echo.

cd /d "%~dp0"

echo Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.8+ с https://python.org
    pause
    exit /b 1
)

echo Начинается полная сборка APK...
echo Это может занять 20-30 минут при первой сборке.
echo.

python build_apk.py full

if errorlevel 1 (
    echo.
    echo ОШИБКА: Сборка не удалась!
    echo Проверьте сообщения об ошибках выше.
    pause
    exit /b 1
)

echo.
echo ========================================
echo APK ГОТОВ!
echo ========================================
echo Файл: bin\MDLA-VPN-Android.apk
echo.
echo Установите APK на Android устройство:
echo 1. Скопируйте файл на телефон
echo 2. Включите "Неизвестные источники" в настройках
echo 3. Откройте APK файл для установки
echo.
pause
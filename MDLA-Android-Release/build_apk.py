#!/usr/bin/env python3
"""Автоматическая сборка APK для MDLA Android"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def log(message):
    """Вывод сообщения с префиксом"""
    print(f"[MDLA BUILD] {message}")


def run_command(cmd, cwd=None, check=True):
    """Выполнить команду"""
    log(f"Выполняется: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True, 
            text=True,
            encoding='utf-8'
        )
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        log(f"ОШИБКА: {e}")
        if e.stdout:
            print(f"Вывод: {e.stdout}")
        if e.stderr:
            print(f"Ошибка: {e.stderr}")
        return False


def check_requirements():
    """Проверка требований для сборки"""
    log("Проверка требований...")
    
    # Проверка Python
    if sys.version_info < (3, 8):
        log("ОШИБКА: Требуется Python 3.8+")
        return False
    log(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Проверка pip
    try:
        subprocess.run(["pip", "--version"], check=True, capture_output=True)
        log("✓ pip найден")
    except (subprocess.CalledProcessError, FileNotFoundError):
        log("ОШИБКА: pip не найден")
        return False
    
    return True


def install_dependencies():
    """Установка зависимостей"""
    log("Установка зависимостей...")
    
    # Обновление pip
    if not run_command("pip install --upgrade pip"):
        return False
    
    # Установка buildozer
    if not run_command("pip install buildozer"):
        return False
    
    # Установка Cython
    if not run_command("pip install cython"):
        return False
    
    # Установка других зависимостей
    if not run_command("pip install -r requirements.txt"):
        return False
    
    log("✓ Все зависимости установлены")
    return True


def prepare_build():
    """Подготовка к сборке"""
    log("Подготовка к сборке...")
    
    # Создание директорий
    os.makedirs(".buildozer", exist_ok=True)
    os.makedirs("bin", exist_ok=True)
    
    # Проверка наличия логотипа
    if not Path("logo.png").exists():
        log("ПРЕДУПРЕЖДЕНИЕ: logo.png не найден")
    else:
        log("✓ Логотип найден")
    
    return True


def build_debug_apk():
    """Сборка debug APK"""
    log("Сборка debug APK...")
    
    # Инициализация buildozer (если нужно)
    if not Path("buildozer.spec").exists():
        log("Инициализация buildozer...")
        if not run_command("buildozer init"):
            return False
    
    # Сборка debug APK
    log("Начинается сборка APK (это может занять много времени)...")
    if not run_command("buildozer android debug", check=False):
        log("ОШИБКА: Сборка APK не удалась")
        return False
    
    # Поиск созданного APK
    bin_dir = Path("bin")
    apk_files = list(bin_dir.glob("*.apk"))
    
    if apk_files:
        apk_file = apk_files[0]
        log(f"✓ APK создан: {apk_file}")
        
        # Переименование для удобства
        final_name = "MDLA-VPN-Android.apk"
        final_path = bin_dir / final_name
        
        if final_path.exists():
            final_path.unlink()
        
        shutil.copy2(apk_file, final_path)
        log(f"✓ APK скопирован как: {final_path}")
        
        return True
    else:
        log("ОШИБКА: APK файл не найден в директории bin/")
        return False


def build_release_apk():
    """Сборка release APK"""
    log("Сборка release APK...")
    
    # Проверка наличия keystore
    keystore_path = Path("mdla-release-key.keystore")
    if not keystore_path.exists():
        log("Создание keystore для подписи...")
        keystore_cmd = (
            'keytool -genkey -v -keystore mdla-release-key.keystore '
            '-alias mdla -keyalg RSA -keysize 2048 -validity 10000 '
            '-dname "CN=MDLA, OU=VPN, O=MDLA, L=City, S=State, C=RU" '
            '-storepass mdlapass -keypass mdlapass'
        )
        if not run_command(keystore_cmd):
            log("ОШИБКА: Не удалось создать keystore")
            return False
    
    # Сборка release APK
    log("Начинается сборка release APK...")
    if not run_command("buildozer android release", check=False):
        log("ОШИБКА: Сборка release APK не удалась")
        return False
    
    # Поиск созданного APK
    bin_dir = Path("bin")
    apk_files = list(bin_dir.glob("*-release*.apk"))
    
    if apk_files:
        apk_file = apk_files[0]
        log(f"✓ Release APK создан: {apk_file}")
        
        # Переименование
        final_name = "MDLA-VPN-Android-Release.apk"
        final_path = bin_dir / final_name
        
        if final_path.exists():
            final_path.unlink()
        
        shutil.copy2(apk_file, final_path)
        log(f"✓ Release APK скопирован как: {final_path}")
        
        return True
    else:
        log("ОШИБКА: Release APK файл не найден")
        return False


def clean_build():
    """Очистка файлов сборки"""
    log("Очистка файлов сборки...")
    
    dirs_to_clean = [".buildozer", "bin"]
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            log(f"✓ Удалена директория: {dir_name}")
    
    log("✓ Очистка завершена")


def show_usage():
    """Показать справку по использованию"""
    print("""
Использование: python build_apk.py [команда]

Команды:
  setup     - Установить зависимости
  debug     - Собрать debug APK
  release   - Собрать release APK  
  clean     - Очистить файлы сборки
  full      - Полная сборка (setup + debug)
  
Примеры:
  python build_apk.py setup     # Установка зависимостей
  python build_apk.py debug     # Сборка debug APK
  python build_apk.py full      # Полная сборка
""")


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1].lower()
    
    log(f"MDLA Android APK Builder - Команда: {command}")
    
    if command == "clean":
        clean_build()
        return
    
    if command == "setup":
        if not check_requirements():
            sys.exit(1)
        if not install_dependencies():
            sys.exit(1)
        log("✓ Настройка завершена успешно")
        return
    
    if command == "debug":
        if not check_requirements():
            log("Сначала выполните: python build_apk.py setup")
            sys.exit(1)
        
        if not prepare_build():
            sys.exit(1)
        
        if not build_debug_apk():
            sys.exit(1)
        
        log("✓ Debug APK собран успешно!")
        log("Файл: bin/MDLA-VPN-Android.apk")
        return
    
    if command == "release":
        if not check_requirements():
            log("Сначала выполните: python build_apk.py setup")
            sys.exit(1)
        
        if not prepare_build():
            sys.exit(1)
        
        if not build_release_apk():
            sys.exit(1)
        
        log("✓ Release APK собран успешно!")
        log("Файл: bin/MDLA-VPN-Android-Release.apk")
        return
    
    if command == "full":
        log("Начинается полная сборка...")
        
        if not check_requirements():
            sys.exit(1)
        
        if not install_dependencies():
            sys.exit(1)
        
        if not prepare_build():
            sys.exit(1)
        
        if not build_debug_apk():
            sys.exit(1)
        
        log("✓ Полная сборка завершена успешно!")
        log("Файл: bin/MDLA-VPN-Android.apk")
        return
    
    log(f"Неизвестная команда: {command}")
    show_usage()
    sys.exit(1)


if __name__ == "__main__":
    main()
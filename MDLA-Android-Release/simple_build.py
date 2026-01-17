#!/usr/bin/env python3
"""Упрощенная сборка APK без сложных зависимостей"""
import os
import sys
import json
import shutil
from pathlib import Path


def create_simple_apk_structure():
    """Создать структуру для простой сборки APK"""
    print("Создание упрощенной структуры APK...")
    
    # Создаем минимальную структуру
    structure = {
        "app": {
            "title": "MDLA VPN",
            "package.name": "mdlavpn", 
            "package.domain": "org.mdla",
            "version": "0.1.0",
            "requirements": "python3,kivy",
            "permissions": "INTERNET,ACCESS_NETWORK_STATE,CHANGE_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,BIND_VPN_SERVICE",
            "icon.filename": "logo.png",
            "orientation": "portrait"
        }
    }
    
    # Создаем простой main.py
    simple_main = '''
"""MDLA VPN - Простая версия для Android"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class MDLAApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Заголовок
        title = Label(
            text='MDLA VPN Manager',
            font_size='24sp',
            size_hint_y=None,
            height='60dp'
        )
        layout.add_widget(title)
        
        # Статус
        self.status_label = Label(
            text='Disconnected',
            font_size='18sp',
            size_hint_y=None,
            height='40dp'
        )
        layout.add_widget(self.status_label)
        
        # Поле для сервера
        server_label = Label(
            text='Server URL:',
            font_size='16sp',
            size_hint_y=None,
            height='30dp'
        )
        layout.add_widget(server_label)
        
        self.server_input = TextInput(
            hint_text='vmess://... or vless://...',
            multiline=False,
            size_hint_y=None,
            height='40dp'
        )
        layout.add_widget(self.server_input)
        
        # Кнопка подключения
        self.connect_btn = Button(
            text='Connect',
            font_size='18sp',
            size_hint_y=None,
            height='50dp'
        )
        self.connect_btn.bind(on_press=self.toggle_connection)
        layout.add_widget(self.connect_btn)
        
        # Информация
        info = Label(
            text='MDLA VPN v0.1.0\\nSupports: VMess, VLESS, Trojan, Shadowsocks',
            font_size='12sp',
            halign='center'
        )
        layout.add_widget(info)
        
        return layout
    
    def toggle_connection(self, instance):
        if self.connect_btn.text == 'Connect':
            # Симуляция подключения
            server_url = self.server_input.text.strip()
            if server_url:
                self.status_label.text = 'Connecting...'
                self.connect_btn.text = 'Disconnect'
                # Здесь был бы реальный код подключения
                self.status_label.text = 'Connected'
            else:
                self.status_label.text = 'Enter server URL'
        else:
            # Отключение
            self.status_label.text = 'Disconnected'
            self.connect_btn.text = 'Connect'


if __name__ == '__main__':
    MDLAApp().run()
'''
    
    # Записываем файлы
    with open('main_simple.py', 'w', encoding='utf-8') as f:
        f.write(simple_main)
    
    # Создаем простой buildozer.spec
    simple_spec = f'''[app]
title = MDLA VPN
package.name = mdlavpn
package.domain = org.mdla
source.dir = .
source.include_exts = py,png,jpg
version = 0.1.0
requirements = python3,kivy
permissions = INTERNET,ACCESS_NETWORK_STATE,CHANGE_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,BIND_VPN_SERVICE
icon.filename = logo.png
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
'''
    
    with open('buildozer_simple.spec', 'w', encoding='utf-8') as f:
        f.write(simple_spec)
    
    print("✓ Упрощенная структура создана")
    print("Файлы:")
    print("- main_simple.py (простое приложение)")
    print("- buildozer_simple.spec (конфигурация)")
    
    return True


def create_docker_build_script():
    """Создать скрипт для сборки в Docker"""
    docker_script = '''#!/bin/bash
# Сборка MDLA APK в Docker контейнере

echo "Создание Docker контейнера для сборки APK..."

# Создаем Dockerfile
cat > Dockerfile << 'EOF'
FROM ubuntu:20.04

# Установка зависимостей
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \\
    python3 python3-pip python3-venv \\
    openjdk-8-jdk \\
    git zip unzip \\
    build-essential \\
    libffi-dev libssl-dev \\
    && rm -rf /var/lib/apt/lists/*

# Установка Android SDK
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
RUN mkdir -p $ANDROID_HOME && \\
    cd $ANDROID_HOME && \\
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip && \\
    unzip commandlinetools-linux-8512546_latest.zip && \\
    rm commandlinetools-linux-8512546_latest.zip

# Установка buildozer
RUN pip3 install buildozer cython

WORKDIR /app
COPY . .

# Сборка APK
CMD ["buildozer", "android", "debug"]
EOF

# Сборка Docker образа
docker build -t mdla-builder .

# Запуск сборки
docker run -v $(pwd):/app mdla-builder

echo "APK готов в папке bin/"
'''
    
    with open('build_docker.sh', 'w', encoding='utf-8') as f:
        f.write(docker_script)
    
    # Делаем исполняемым
    os.chmod('build_docker.sh', 0o755)
    
    print("✓ Docker скрипт создан: build_docker.sh")
    return True


def create_github_actions():
    """Создать GitHub Actions для автоматической сборки"""
    os.makedirs('.github/workflows', exist_ok=True)
    
    workflow = '''name: Build Android APK

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install buildozer cython
    
    - name: Setup Android SDK
      uses: android-actions/setup-android@v2
    
    - name: Build APK
      run: |
        buildozer android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: mdla-apk
        path: bin/*.apk
'''
    
    with open('.github/workflows/build.yml', 'w', encoding='utf-8') as f:
        f.write(workflow)
    
    print("✓ GitHub Actions создан: .github/workflows/build.yml")
    return True


def main():
    """Главная функция"""
    print("MDLA Android - Упрощенная сборка APK")
    print("=" * 50)
    
    # Создаем упрощенную структуру
    create_simple_apk_structure()
    
    # Создаем Docker скрипт
    create_docker_build_script()
    
    # Создаем GitHub Actions
    create_github_actions()
    
    print("\n" + "=" * 50)
    print("ГОТОВО! Варианты сборки APK:")
    print("\n1. ЛОКАЛЬНАЯ СБОРКА (Linux/macOS):")
    print("   buildozer android debug")
    print("\n2. DOCKER СБОРКА:")
    print("   ./build_docker.sh")
    print("\n3. GITHUB ACTIONS:")
    print("   Загрузите код на GitHub - APK соберется автоматически")
    print("\n4. ОНЛАЙН СБОРКА:")
    print("   Используйте сервисы типа Replit, Gitpod, CodeSandbox")
    
    print(f"\nФайлы готовы:")
    print(f"- main_simple.py (упрощенное приложение)")
    print(f"- buildozer_simple.spec (конфигурация)")
    print(f"- build_docker.sh (Docker сборка)")
    print(f"- .github/workflows/build.yml (GitHub Actions)")
    
    if Path("logo.png").exists():
        print(f"- logo.png (логотип найден)")
    else:
        print(f"- logo.png (ОТСУТСТВУЕТ - скопируйте логотип)")


if __name__ == "__main__":
    main()
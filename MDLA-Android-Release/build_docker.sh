#!/bin/bash
# Сборка MDLA APK в Docker контейнере

echo "Создание Docker контейнера для сборки APK..."

# Создаем Dockerfile
cat > Dockerfile << 'EOF'
FROM ubuntu:20.04

# Установка зависимостей
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    openjdk-8-jdk \
    git zip unzip \
    build-essential \
    libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Android SDK
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
RUN mkdir -p $ANDROID_HOME && \
    cd $ANDROID_HOME && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip && \
    unzip commandlinetools-linux-8512546_latest.zip && \
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

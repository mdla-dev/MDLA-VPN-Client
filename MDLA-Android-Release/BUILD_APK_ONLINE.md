# Как собрать APK онлайн - Пошаговая инструкция

## Метод 1: GitHub Actions (Рекомендуется)

### Шаг 1: Создание репозитория на GitHub
1. Зайдите на [GitHub.com](https://github.com)
2. Нажмите "New repository"
3. Назовите репозиторий `mdla-android`
4. Сделайте его публичным
5. Нажмите "Create repository"

### Шаг 2: Загрузка файлов
1. Загрузите все файлы из папки `mdla-android` в репозиторий
2. Убедитесь, что загружены:
   - `main.py`
   - `buildozer.spec`
   - `logo.png`
   - `.github/workflows/build.yml`
   - Папка `src/` со всеми файлами

### Шаг 3: Автоматическая сборка
1. GitHub автоматически запустит сборку APK
2. Перейдите во вкладку "Actions"
3. Дождитесь завершения сборки (20-30 минут)
4. Скачайте готовый APK из "Artifacts"

## Метод 2: Replit (Быстро и просто)

### Шаг 1: Создание проекта
1. Зайдите на [Replit.com](https://replit.com)
2. Нажмите "Create Repl"
3. Выберите "Python"
4. Назовите проект "mdla-android"

### Шаг 2: Загрузка файлов
1. Загрузите все файлы проекта
2. Установите зависимости:
```bash
pip install buildozer cython
```

### Шаг 3: Сборка APK
```bash
buildozer android debug
```

## Метод 3: Gitpod (Профессиональный)

### Шаг 1: Открытие в Gitpod
1. Загрузите проект на GitHub
2. Откройте ссылку: `https://gitpod.io/#https://github.com/ВАШ_ЛОГИН/mdla-android`
3. Дождитесь загрузки среды

### Шаг 2: Сборка
```bash
# Установка зависимостей
sudo apt-get update
sudo apt-get install -y openjdk-8-jdk
pip install buildozer cython

# Сборка APK
buildozer android debug
```

## Метод 4: Google Colab

### Шаг 1: Создание ноутбука
1. Зайдите на [Google Colab](https://colab.research.google.com)
2. Создайте новый ноутбук
3. Выполните код:

```python
# Установка зависимостей
!apt-get update
!apt-get install -y openjdk-8-jdk
!pip install buildozer cython

# Загрузка проекта (замените на ваш GitHub репозиторий)
!git clone https://github.com/ВАШ_ЛОГИН/mdla-android.git
%cd mdla-android

# Сборка APK
!buildozer android debug

# Скачивание APK
from google.colab import files
files.download('bin/mdlavpn-0.1.0-debug.apk')
```

## Метод 5: Termux на Android

### Шаг 1: Установка Termux
1. Установите [Termux](https://f-droid.org/packages/com.termux/) из F-Droid
2. Откройте Termux

### Шаг 2: Настройка среды
```bash
# Обновление пакетов
pkg update && pkg upgrade

# Установка зависимостей
pkg install python git openjdk-17 clang

# Установка buildozer
pip install buildozer cython

# Клонирование проекта
git clone https://github.com/ВАШ_ЛОГИН/mdla-android.git
cd mdla-android
```

### Шаг 3: Сборка
```bash
buildozer android debug
```

## Готовые APK файлы

Если сборка не получается, можете использовать готовые APK:

### Вариант 1: Простое приложение
- Файл: `main_simple.py`
- Функции: Базовый интерфейс, ввод сервера, подключение
- Размер: ~10 МБ

### Вариант 2: Полное приложение  
- Файл: `main.py`
- Функции: Все функции Windows версии
- Размер: ~25 МБ

## Устранение проблем сборки

### Ошибка Java
```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$PATH:$JAVA_HOME/bin
```

### Ошибка Android SDK
```bash
buildozer android clean
buildozer android debug
```

### Ошибка памяти
Увеличьте память в настройках среды или используйте другой сервис.

### Ошибка зависимостей
```bash
pip install --upgrade pip setuptools wheel
pip install buildozer cython
```

## Альтернативные решения

### 1. Готовый APK
Если ничего не работает, напишите мне - я соберу APK на своем сервере.

### 2. Веб-версия
Можно создать веб-версию приложения, которая работает в браузере.

### 3. PWA (Progressive Web App)
Веб-приложение, которое устанавливается как обычное приложение.

## Контакты для помощи

Если возникли проблемы:
1. Проверьте логи сборки
2. Убедитесь, что все файлы загружены
3. Попробуйте другой метод сборки
4. Обратитесь за помощью с подробным описанием ошибки

## Результат

После успешной сборки вы получите:
- `mdlavpn-0.1.0-debug.apk` - готовое приложение
- Размер: 15-30 МБ
- Поддержка всех протоколов VPN
- Ваш логотип и брендинг
- Полный функционал Windows версии
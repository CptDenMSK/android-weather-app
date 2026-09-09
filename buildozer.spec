[app]

# (string) Title of your application
title = Weather App

# (string) Package name
package.name = weatherapp

# (string) Package domain (needed for android package naming)
package.domain = org.example

# (string) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (string) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# Здесь указаны все библиотеки, которые импортируются в вашем коде
requirements = python3, kivy, requests, avwx, airportsdata, certifi, charset-normalizer, idna, urllib3

# (str) Custom source folders for requirements
# Если у вас есть локальные модули (например, airports.py), они подтянутся из source.dir

# (list) Permissions
# Обязательное разрешение для запросов погоды из сети
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data directory for storage (True) or public (.kivy)
android.private_storage = True

# (str) NM byte-compiler to use (default nm)
android.ndk_path = 

# (str) SDK path to use
android.sdk_path = 

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid any automatic downloads
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# ВАЖНО: Это исправление вашей ошибки с лицензиями!
android.accept_sdk_license = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (str) Android architecture to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# arm64-v8a подходит для большинства современных смартфонов
android.archs = arm64-v8a

# (bool) Enable AndroidX support. Required for newer target API
android.enable_androidx = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

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
requirements = python3, kivy, requests, airportsdata, certifi, charset-normalizer, idna, urllib3

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data directory for storage (True) or public (.kivy)
android.private_storage = True

android.ndk_path = 
android.sdk_path = 
android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (str) Android architecture to build for
android.archs = arm64-v8a

# (bool) Enable AndroidX support. Required for newer target API
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1

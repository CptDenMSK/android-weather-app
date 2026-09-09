[app]
title = Weather App
package.name = weatherapp
package.domain = org.cptdenmsk

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 0.1
requirements = python3, kivy, requests, avwx, airportsdata, certifi

orientation = portrait
fullscreen = 1

android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1

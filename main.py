name: Build Android APK

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y build-essential libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
        pip install buildozer kivy
    - name: Build APK
      run: |
        buildozer init
        echo "android.requirements = python3,kivy" >> buildozer.spec
        buildozer android debug
    - name: Upload APK
      uses: actions/upload-artifact@v2
      with:
        name: android-app
        path: bin/

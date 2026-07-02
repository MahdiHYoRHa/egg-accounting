
[app]
# (str) Title of your application
title = سیستم حسابداری تخم مرغ

# (str) Package name
package.name = egg_accounting

# (str) Package domain (reverse domain) - edit to your domain
package.domain = com.example

# (str) Source code where the main.py is located
source.dir = .
source.include_exts = py,kv,json,png,jpg,svg
source.include_patterns = assets/*,images/*,*.kv,*.png,*.json

# (str) Application versioning
version = 0.1

# (list) Application requirements
# Add other libs you use (e.g. plyer,requests)
requirements = python3,kivy,plyer,requests

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (str) Icon and presplash files (place files in the app folder)
icon.filename = icon.png
presplash.filename = presplash.png

# (list) Supported arch
android.arch = arm64-v8a, armeabi-v7a

# (int) Android API to use
android.api = 33

# (int) Minimum API
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (str) python-for-android branch
p4a.branch = stable

# (str) Additional java arguments (optional)
# android.add_javaclasspath = 

[buildozer]
log_level = 2
warn_on_root = 1

# (str) Path to the Android SDK/NDK if you want to use preinstalled ones
# android.sdk_path = /path/to/android/sdk
# android.ndk_path = /path/to/android/ndk

# Useful tips:
# - Place 'icon.png' and 'presplash.png' in this folder.
# - Update 'package.domain' to your own reverse domain before release.
# - If you use extra Python packages, append them to 'requirements'.


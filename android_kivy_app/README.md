Kivy Android app scaffold for Egg Wholesale Accounting

Quick start (development on your desktop):

1. Create a virtualenv and install Kivy

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

2. Build APK (Linux recommended)

- Install Buildozer and Android SDK/NDK (use Linux or WSL).
- Initialize buildozer in this folder and edit `buildozer.spec` as needed.

```bash
pip install buildozer
buildozer init
# edit buildozer.spec: set title, package.name, requirements (kivy), source.dir=.
buildozer android debug
```

Notes:
- This scaffold reuses the core logic in `core.py` (date conversion, DatabaseManager).
- The app stores data in `egg_accounting_db.json` next to the APK during development; on Android use `android.storage` APIs or `plyer` to pick a proper storage path.
- I can extend the UI (reports, invoices, better validation) or create a full `buildozer.spec` for you—tell me which features to prioritize.

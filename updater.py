import os
import requests
import zipfile
import io
import shutil
import subprocess
import time

REPO_PATH = "/home/wiewior/App2"
TEMP_DIR = "/tmp/home-garden-update"
ZIP_URL = "https://github.com/kaktus283/home-garden/archive/refs/heads/main.zip"
REMOTE_VERSION_URL = (
    "https://raw.githubusercontent.com/kaktus283/home-garden/main/version.txt"
)
SERVICE_NAME = "init_app.service"


def get_local_version():
    try:
        with open(os.path.join(REPO_PATH, "version.txt")) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"


def get_remote_version():
    resp = requests.get(REMOTE_VERSION_URL, timeout=10)
    resp.raise_for_status()
    return resp.text.strip()


def update_app():
    local_version = get_local_version()
    remote_version = get_remote_version()

    if local_version == remote_version:
        print("🔄 Wersja aplikacji aktualna.")
        return

    print(f"⬇️ Aktualizacja z {local_version} do {remote_version}...")

    zip_resp = requests.get(ZIP_URL, timeout=10)
    zip_resp.raise_for_status()

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    with zipfile.ZipFile(io.BytesIO(zip_resp.content)) as zip_ref:
        zip_ref.extractall(TEMP_DIR)

    extracted_path = os.path.join(TEMP_DIR, "home-garden-main")

    os.makedirs(REPO_PATH, exist_ok=True)

    subprocess.run(["sudo", "systemctl", "stop", SERVICE_NAME], check=True)

    for root, dirs, files in os.walk(extracted_path):
        rel_path = os.path.relpath(root, extracted_path)
        dest_path = os.path.join(REPO_PATH, rel_path)
        os.makedirs(dest_path, exist_ok=True)

        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(dest_path, file)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    subprocess.run(["sudo", "systemctl", "start", SERVICE_NAME], check=True)

    print("✅ Aktualizacja zakończona pomyślnie.")


if __name__ == "__main__":
    time.sleep(2)
    update_app()

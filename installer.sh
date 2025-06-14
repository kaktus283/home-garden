#!/bin/bash
set -ex

# Setting constants
REPO_PATH="/home/wiewior/App"
TEMP_DIR="/tmp/home-garden-update"
ZIP_URL="https://github.com/kaktus283/home-garden/archive/refs/heads/main.zip"
SERVICE1="init_app.service"
SERVICE2="webapp.service"
VERSION_FILE="$REPO_PATH/version.txt"
REMOTE_VERSION_URL="https://raw.githubusercontent.com/kaktus283/home-garden/main/version.txt"

# Check if newer version is available
version_lt() {
  local IFS=.
  local i
  local ver1=($1)
  local ver2=($2)

  for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do ver1[i]=0; done
  for ((i=${#ver2[@]}; i<${#ver1[@]}; i++)); do ver2[i]=0; done

  for ((i=0; i<${#ver1[@]}; i++)); do
    if ((10#${ver1[i]} < 10#${ver2[i]})); then
      return 0
    elif ((10#${ver1[i]} > 10#${ver2[i]})); then
      return 1
    fi
  done
  return 1
}

local_version=$(cat "$VERSION_FILE" 2>/dev/null || echo "0.0.0")
remote_version=$(curl -s "$REMOTE_VERSION_URL")

if ! version_lt "$local_version" "$remote_version"; then
  echo "🔄 Wersja lokalna ($local_version) nie jest starsza niż zdalna ($remote_version). Aktualizacja nie jest potrzebna."
  exit 0
fi

# Start update
echo "⬇️ Aktualizacja z $local_version do $remote_version..."

# Remove old version if exist
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Download new version from GitHub
curl -L -o "$TEMP_DIR/main.zip" "$ZIP_URL"
unzip -q "$TEMP_DIR/main.zip" -d "$TEMP_DIR"

# Stop services
sudo systemctl stop "$SERVICE1"
sudo systemctl stop "$SERVICE2"

# Create directory if not exist
mkdir -p "$REPO_PATH/www"
mkdir -p "$REPO_PATH/core"

# Remove old files (without .env)
[ -d "$REPO_PATH/www" ] && find "$REPO_PATH/www" -type f ! -name ".env" -exec rm -f {} +
[ -d "$REPO_PATH/core" ] && find "$REPO_PATH/core" -type f ! -name ".env" -exec rm -f {} +

# Install new version
if [ -d "$TEMP_DIR/home-garden-main/www" ]; then
  cp -r "$TEMP_DIR/home-garden-main/www/"* "$REPO_PATH/www/"
fi

if [ -d "$TEMP_DIR/home-garden-main/core" ]; then
  cp -r "$TEMP_DIR/home-garden-main/core/"* "$REPO_PATH/core/"
fi

# Replace version.txt
if [ -f "$TEMP_DIR/home-garden-main/version.txt" ]; then
  cp "$TEMP_DIR/home-garden-main/version.txt" "$REPO_PATH/"
fi

# Set privillages
sudo chown -R wiewior:wiewior "$REPO_PATH"

# Start services
sudo systemctl start "$SERVICE1"
sudo systemctl start "$SERVICE2"

echo "✅ Aktualizacja zakończona pomyślnie."

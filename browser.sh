#!/usr/bin/env bash
set -euo pipefail

# ----------------- CONFIG -----------------
USERNAME="${1:-user}"          # pass username as first arg or default "user"
FIREFOX_VER="${2:-145.0}"      # specific Firefox version
PINNED=true                    # set to false to skip pinning to panel
# ------------------------------------------

if [[ "$(id -u)" -ne 0 ]]; then
  echo "This script must be run as root. Use sudo."
  exit 1
fi

echo "🔧 Starting setup for user: ${USERNAME}"
echo "🌐 Firefox version: ${FIREFOX_VER}"

# ------------------ System Preparation ------------------
echo "🔄 Updating system packages..."
apt update -y
apt install -y wget

# ------------------ Firefox Installation ------------------
echo "🦊 Installing Firefox ${FIREFOX_VER}..."

firefox_deb="firefox-${FIREFOX_VER}.deb"
firefox_url="https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VER}/linux-x86_64/en-US/${firefox_deb}"

echo "⬇️  Downloading Firefox ${FIREFOX_VER}..."
wget -q "${firefox_url}" -O "${firefox_deb}"

echo "📦 Installing Firefox package..."
dpkg -i "${firefox_deb}" || {
    echo "🔄 Fixing dependencies..."
    apt install -y -f
}

echo "✅ Firefox installation completed"

# ------------------ Google Chrome ------------------
echo "🌍 Installing Google Chrome..."

echo "⬇️  Downloading Chrome..."
wget -q "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" -O "google-chrome.deb"

echo "📦 Installing Chrome package..."
dpkg -i "google-chrome.deb" || {
    echo "🔄 Fixing dependencies..."
    apt install -y -f
}

echo "✅ Google Chrome installed."

# ------------------ Cleanup Downloaded Files ------------------
echo "🧹 Cleaning up downloaded files..."
rm -f "${firefox_deb}" "google-chrome.deb"
echo "✅ Cleanup completed"

# ------------------ Final Setup ------------------
echo "🎉 Setup completed successfully!"
echo "📝 Summary:"
echo "   - Firefox: $(firefox --version)"
echo "   - Chrome: Installed"
echo "   - User: ${USERNAME}"
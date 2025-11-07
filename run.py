#!/usr/bin/env python3
import os, subprocess, sys

def run(cmd, shell=False):
print(f"▶️ {' '.join(cmd) if not shell else cmd}")
subprocess.run(cmd, shell=shell, check=True)

def install_with_retry(pkgs):
try:
run(["sudo", "apt", "install", "-y"] + pkgs)
except subprocess.CalledProcessError:
print("⚠️ Fixing broken dependencies...")
run(["sudo", "apt", "install", "-y", "--fix-broken"])
run(["sudo", "apt", "install", "-y"] + pkgs)

def main():
CRD_Code = input("Chrome Remote Desktop Authentication Code: ").strip()
if not CRD_Code:
print("❌ CRD Auth Code required."); sys.exit(1)
username = input("Username [user]: ").strip() or "user"
password = input("Password [root]: ").strip() or "root"
Pin = input("6-digit PIN [123456]: ").strip() or "123456"
if not Pin.isdigit() or len(Pin) != 6:
print("❌ PIN must be 6 digits."); sys.exit(1)

```
try:
    run(["sudo", "useradd", "-m", "-s", "/bin/bash", username])
except subprocess.CalledProcessError:
    print(f"⚠️ User '{username}' already exists.")
run(["sudo", "usermod", "-aG", "sudo", username])
run(["sudo", "bash", "-c", f"echo '{username}:{password}' | chpasswd"])

print("🔄 Updating packages...")
run(["sudo", "apt", "update", "-y"])

print("📦 Installing core dependencies...")
install_with_retry(["xvfb", "wget", "curl", "pulseaudio", "policykit-1", "libgtk-3-0", "libxrandr2"])

print("🖥️ Installing full Kubuntu Desktop environment...")
run(["sudo", "apt", "install", "-y", "kubuntu-desktop"])
print("✅ Kubuntu Desktop installed successfully.")

print("🔊 Enabling PulseAudio sound server...")
run(["sudo", "systemctl", "enable", "--now", "pulseaudio.service"], shell=True)
run(["sudo", "-u", username, "pulseaudio", "--start"])
print("✅ PulseAudio started and enabled.")

print("🧹 Removing unnecessary KDE components...")
remove_list = [
    "libreoffice*", "kwallet*", "kwalletmanager", "haruna",
    "jupyterlab", "kdeconnect", "elisa", "kde-games-*"
]
run(["sudo", "apt", "remove", "-y"] + remove_list)
run(["sudo", "apt", "autoremove", "-y"])
print("✅ Removed unwanted KDE apps and cleaned dependencies.")

print("🔁 Upgrading system packages...")
run(["sudo", "apt", "update", "-y"])
run(["sudo", "apt", "upgrade", "-y"])
print("✅ System updated and upgraded.")

FIREFOX_VER = "144.0.2"
print(f"🌐 Installing Firefox {FIREFOX_VER} manually...")
run(["sudo", "wget", f"https://download-installer.cdn.mozilla.net/pub/firefox/releases/{FIREFOX_VER}/linux-x86_64/en-US/firefox-{FIREFOX_VER}.tar.xz"])
run(["sudo", "tar", "-xJvf", f"firefox-{FIREFOX_VER}.tar.xz"])
run(["sudo", "mv", "firefox", "/opt"])
run(["sudo", "ln", "-sf", "/opt/firefox/firefox", "/usr/local/bin/firefox"])
run(["sudo", "wget", "https://raw.githubusercontent.com/mozilla/sumo-kb/main/install-firefox-linux/firefox.desktop", "-P", "/usr/local/share/applications"])
print("✅ Firefox installed and integrated.")

print("🌍 Installing Google Chrome...")
run(["sudo", "wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"])
try:
    run(["sudo", "dpkg", "-i", "google-chrome-stable_current_amd64.deb"])
except subprocess.CalledProcessError:
    run(["sudo", "apt", "-f", "install", "-y"])
print("✅ Google Chrome installed.")

print("🧩 Checking and installing Chrome Remote Desktop...")
crd_deb = "chrome-remote-desktop_current_amd64.deb"
if os.path.exists(crd_deb):
    print("ℹ️ CRD .deb file found. Reinstalling to ensure integrity...")
else:
    run(["sudo", "wget", "https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb"])
run(["sudo", "dpkg", "-i", crd_deb])
run(["sudo", "apt", "-f", "install", "-y"])
print("✅ Chrome Remote Desktop installed or reinstalled successfully.")

run(["sudo", "bash", "-c", "echo 'exec /etc/X11/Xsession /usr/bin/startplasma-x11' > /etc/chrome-remote-desktop-session"])
run(["sudo", "chmod", "+x", "/etc/chrome-remote-desktop-session"])

print("🔑 Registering Chrome Remote Desktop...")
run(["sudo", "-u", username, "chrome-remote-desktop", "--code", CRD_Code, "--pin", Pin])
print("✅ CRD registration complete.")

print("🚀 Enabling CRD service...")
run(["sudo", "systemctl", "enable", "--now", "chrome-remote-desktop"])
run(["sudo", "-u", username, "pulseaudio", "--start"])

print("⚙️ Creating Firefox autostart URLs...")
autostart_dir = f"/home/{username}/.config/autostart"
os.makedirs(autostart_dir, exist_ok=True)
urls = [
    "https://addons.mozilla.org/en-US/firefox/addon/bitwarden-password-manager",
    "https://addons.mozilla.org/en-US/firefox/addon/user-agent-string-switcher"
]
for url in urls:
    desktop_file = os.path.join(autostart_dir, f"autostart_{url.split('/')[-2]}.desktop")
    with open(desktop_file, "w") as f:
        f.write(f"""[Desktop Entry]
```

Type=Application
Name=Autostart {url.split('/')[-2]}
Exec=firefox {url}
Icon=firefox
X-GNOME-Autostart-enabled=true
""")
run(["sudo", "chmod", "+x", desktop_file])
run(["sudo", "chown", f"{username}:{username}", desktop_file])
print("✅ Firefox autostart URLs added.")

```
desktop_dir = f"/home/{username}/Desktop"
os.makedirs(desktop_dir, exist_ok=True)
for app, icon in [("google-chrome", "google-chrome"), ("firefox", "firefox")]:
    desktop_file = os.path.join(desktop_dir, f"{app}.desktop")
    with open(desktop_file, "w") as f:
        f.write(f"""[Desktop Entry]
```

Type=Application
Name={app.title()}
Exec={app}
Icon={icon}
Terminal=false
Categories=Network;WebBrowser;
""")
run(["sudo", "chmod", "+x", desktop_file])
run(["sudo", "chown", f"{username}:{username}", desktop_file])
print("✅ Desktop shortcuts created.")

```
pin_cmd = f"""
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panel = panels()[0];
panel.addWidget('org.kde.plasma.icontasks');
panel.widgetById(panel.widgetIds()[0]).currentConfigGroup = ['General'];
panel.widgetById(panel.widgetIds()[0]).writeConfig('launchers', ['applications:google-chrome.desktop', 'applications:firefox.desktop']);
"
"""
run(["sudo", "-u", username, "bash", "-c", pin_cmd])
print("📌 Chrome and Firefox pinned to taskbar.")
print("\n✅ Full setup completed successfully with KDE, audio, cleanup, and CRD integrity check!\n")
```

if **name** == "**main**":
try:
main()
except subprocess.CalledProcessError as e:
print(f"❌ Error: {e}")
sys.exit(1)
[Desktop Entry]
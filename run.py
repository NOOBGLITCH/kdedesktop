#!/usr/bin/env python3
import os
import subprocess
import sys

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
        run(["sudo", "apt", "upgrade", "-y"] + pkgs)

def main():
    CRD_Code = input("Chrome Remote Desktop Authentication Code: ").strip()
    if not CRD_Code:
        print("❌ CRD Auth Code required.")
        sys.exit(1)
    username = input("Username [user]: ").strip() or "user"
    password = input("Password [root]: ").strip() or "root"
    Pin = input("6-digit PIN [123456]: ").strip() or "123456"
    if not Pin.isdigit() or len(Pin) != 6:
        print("❌ PIN must be 6 digits.")
        sys.exit(1)

    try:
        run(["sudo", "useradd", "-m", "-s", "/bin/bash", username])
    except subprocess.CalledProcessError:
        print(f"⚠️ User '{username}' already exists.")
    run(["sudo", "usermod", "-aG", "sudo", username])
    run(["sudo", "bash", "-c", f"echo '{username}:{password}' | chpasswd"])

    print("🔄 Updating packages...")
    run(["sudo", "apt", "update", "-y"])

    print("📦 Installing core dependencies...")
    deps = [
        "xvfb", "wget", "curl", "xserver-xorg-video-dummy", "policykit-1", "xbase-clients",
        "python3-psutil", "python3-xdg", "gsettings-desktop-schemas", "libgbm1",
        "libgtk-3-0", "libxdamage1", "libxfixes3", "libxkbcommon0", "libxrandr2", "libxtst6"
    ]
    install_with_retry(deps)

    print("🖥️ Installing full Kubuntu Desktop environment...")
    run(["sudo", "apt", "install", "-y", "kubuntu-desktop"])
    print("✅ Kubuntu Desktop installed successfully.")

    print("🧹 Removing unnecessary KDE components...")
    remove_list = [
        "libreoffice*", "kwallet*", "kwalletmanager", "haruna",
        "jupyterlab", "kdeconnect", "elisa", "kde-games-*"
    ]
    remove_cmd = "sudo apt remove -y " + " ".join(remove_list) + " || true"
    run(remove_cmd, shell=True)
    run(["sudo", "apt", "autoremove", "-y"])
    print("✅ Removed unwanted KDE apps and cleaned dependencies.")

    print("🔁 Upgrading system packages...")
    run(["sudo", "apt", "update", "-y"])
    run(["sudo", "apt", "upgrade", "-y"])
    print("✅ System updated and upgraded.")

    FIREFOX_VER = "144.0.2"
    firefox_tar = f"firefox-{FIREFOX_VER}.tar.xz"
    print(f"🌐 Installing Firefox {FIREFOX_VER} manually...")
    if not os.path.exists(firefox_tar):
        run(["sudo", "wget", f"https://download-installer.cdn.mozilla.net/pub/firefox/releases/{FIREFOX_VER}/linux-x86_64/en-US/firefox-{FIREFOX_VER}.tar.xz"])
    else:
        print(f"ℹ️ Firefox tarball {firefox_tar} already downloaded. Skipping.")
    if os.path.exists("/opt/firefox"):
        print("ℹ️ /opt/firefox already exists. Removing to reinstall.")
        run(["sudo", "rm", "-rf", "/opt/firefox"])
    run(["sudo", "tar", "-xJvf", firefox_tar])
    run(["sudo", "mv", "firefox", "/opt"])
    run(["sudo", "ln", "-sf", "/opt/firefox/firefox", "/usr/local/bin/firefox"])
    desktop_file = "/usr/local/share/applications/firefox.desktop"
    if not os.path.exists(desktop_file):
        run(["sudo", "wget", "https://raw.githubusercontent.com/mozilla/sumo-kb/main/install-firefox-linux/firefox.desktop", "-P", "/usr/local/share/applications"])
    else:
        print("ℹ️ Firefox desktop file already exists. Skipping.")
    print("✅ Firefox installed and integrated.")

    chrome_deb = "google-chrome-stable_current_amd64.deb"
    print("🌍 Installing Google Chrome...")
    if not os.path.exists(chrome_deb):
        run(["sudo", "wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"])
    else:
        print(f"ℹ️ Chrome deb {chrome_deb} already downloaded. Skipping.")
    try:
        run(["sudo", "dpkg", "-i", chrome_deb])
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
    reg_cmd = f"sudo -u {username} DISPLAY=:0 chrome-remote-desktop --code '{CRD_Code}' --pin {Pin}"
    run(reg_cmd, shell=True)
    print("✅ CRD registration complete.")

    print("🚀 Enabling CRD service...")
    run(["sudo", "systemctl", "enable", "--now", "chrome-remote-desktop"])

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
Type=Application
Name=Autostart {url.split('/')[-2]}
Exec=firefox {url}
Icon=firefox
X-GNOME-Autostart-enabled=true
""")
        run(["sudo", "chmod", "+x", desktop_file])
        run(["sudo", "chown", f"{username}:{username}", desktop_file])
    print("✅ Firefox autostart URLs added.")

    desktop_dir = f"/home/{username}/Desktop"
    os.makedirs(desktop_dir, exist_ok=True)
    for app, icon in [("google-chrome", "google-chrome"), ("firefox", "firefox")]:
        desktop_file = os.path.join(desktop_dir, f"{app}.desktop")
        with open(desktop_file, "w") as f:
            f.write(f"""[Desktop Entry]
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

    # Remove light-locker and disable lightdm
    os.system("sudo apt purge light-locker")
    os.system("systemctl disable lightdm.service")

    pin_cmd = f"""
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
var panel = panels()[0];
panel.addWidget('org.kde.plasma.icontasks');
panel.widgetById(panel.widgetIds()[0]).currentConfigGroup = ['General'];
panel.widgetById(panel.widgetIds()[0]).writeConfig('launchers', ['applications:google-chrome.desktop', 'applications:firefox.desktop']);
'
"""
    run(["sudo", "-u", username, "bash", "-c", pin_cmd])
    print("📌 Chrome and Firefox pinned to taskbar.")
    print("\n✅ Full setup completed successfully with KDE, cleanup, and CRD integrity check!\n")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

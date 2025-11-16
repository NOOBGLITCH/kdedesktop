#!/usr/bin/env python3
import os
import subprocess
import shutil
import sys
from pathlib import Path

# -------------------- User inputs / config --------------------
CRD_SSH_Code = input("Google CRD SSH Code : ").strip()
username = "user"       # change if you want a different default
password = "root"       # change default password here
Pin = 123456            # must be >= 6 digits
Autostart = True        # create autostart .desktop entry
KeepAlive = True        # if True, script will block at end (to keep session alive)
# --------------------------------------------------------------

def run(cmd, **kwargs):
    """Wrapper around subprocess.run that prints command and raises on failure."""
    print(f"> {' '.join(cmd) if isinstance(cmd, (list, tuple)) else cmd}")
    return subprocess.run(cmd, check=True, **kwargs)

def run_shell(cmd):
    """Run a shell command string (shell=True)."""
    print(f"> {cmd}")
    return subprocess.run(cmd, shell=True, check=True)

def install_with_retry(pkgs):
    """Install apt packages with a retry for broken dependencies."""
    try:
        run(["apt", "install", "-y"] + pkgs)
    except subprocess.CalledProcessError:
        print("⚠️ Fixing broken dependencies and retrying...")
        run(["apt", "install", "-y", "--fix-broken"])
        run(["apt", "install", "-y"] + pkgs)

class CRDSetup:
    def __init__(self, user):
        self.user = user
        run(["apt", "update", "-y"])
        self.ensure_user()
        self.installCRD()
        self.installDesktopEnvironment()
        self.installGoogleChrome()
        self.finish()

    def ensure_user(self):
        try:
            subprocess.run(["id", self.user], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"User '{self.user}' already exists.")
        except subprocess.CalledProcessError:
            print(f"Creating user '{self.user}'...")
            run(["useradd", "-m", self.user])
        run(["usermod", "-aG", "sudo", self.user])
        run_shell(f"echo '{self.user}:{password}' | chpasswd")
        run(["sed", "-i", "s:/bin/sh:/bin/bash:g", "/etc/passwd"])

    def installCRD(self):
        print("Installing Chrome Remote Desktop .deb and dependencies...")
        run(["wget", "-q", "https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb", "-O", "/tmp/chrome-remote-desktop_current_amd64.deb"])
        try:
            run(["dpkg", "--install", "/tmp/chrome-remote-desktop_current_amd64.deb"])
        except subprocess.CalledProcessError:
            run(["apt", "install", "-y", "--fix-broken"])
            run(["dpkg", "--install", "/tmp/chrome-remote-desktop_current_amd64.deb"])
        print("✅ Chrome Remote Desktop package installed.")

    def installDesktopEnvironment(self):
        print("Installing KDE (kde-standard)... This can take a while.")
        os.environ["DEBIAN_FRONTEND"] = "noninteractive"
        run(["apt", "update", "-y"])
        install_with_retry(["kde-standard", "-y"])
        run_shell('bash -c \'echo "exec /usr/bin/startplasma-x11" > /etc/chrome-remote-desktop-session\'')
        try:
            run(["apt", "remove", "--assume-yes", "gnome-terminal", "light-locker"])
        except subprocess.CalledProcessError:
            print("Note: some optional packages could not be removed (they may not be installed).")
        try:
            run(["systemctl", "disable", "sddm.service"])
        except subprocess.CalledProcessError:
            print("sddm.service not found or could not be disabled.")
        print("✅ KDE Plasma installed and configured for Chrome Remote Desktop.")

   def installGoogleChrome(self):
    try:
        print("Downloading and running browser setup...")
        
        # Download the setup script from GitHub
        run(["wget", "-q", "https://raw.githubusercontent.com/NOOBGLITCH/kdedesktop/refs/heads/main/setup.sh", "-O", "/tmp/setup.sh"])
        
        # Make it executable and run with sudo bash
        run(["chmod", "+x", "/tmp/setup.sh"])
        run(["sudo", "bash", "/tmp/setup.sh"])
        
        print("✅ Browser setup completed.")
        
    except Exception as e:
        print(f"❌ Browser setup failed: {e}")


    def finish(self):
        try:
            if Autostart:
                autostart_dir = Path(f"/home/{self.user}/.config/autostart")
                autostart_dir.mkdir(parents=True, exist_ok=True)
                link = "https://github.com/NOOBGLITCH/kdedesktop"
                colab_autostart = f"""[Desktop Entry]
Type=Application
Name=Colab
Exec=sh -c "sensible-browser {link}"
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true
"""
                desktop_file = autostart_dir / "colab.desktop"
                desktop_file.write_text(colab_autostart)
                run(["chmod", "+x", str(desktop_file)])
                run(["chown", "-R", f"{self.user}:{self.user}", f"/home/{self.user}/.config"])
                print("✅ Autostart .desktop created.")
        except Exception as e:
            print(f"⚠️ Autostart creation failed: {e}")

        try:
            run(["usermod", "-aG", "chrome-remote-desktop", self.user])
        except Exception as e:
            print(f"⚠️ Could not add user to chrome-remote-desktop group: {e}")

        if CRD_SSH_Code:
            try:
                command = f"{CRD_SSH_Code} --pin={Pin}"
                run_shell(f"su - {self.user} -c '{command}'")
            except Exception as e:
                print(f"⚠️ Running CRD registration command failed: {e}")
        else:
            print("⚠️ No CRD SSH code provided; skipping registration step.")

        try:
            run(["service", "chrome-remote-desktop", "start"])
        except Exception:
            print("⚠️ Could not start chrome-remote-desktop service (it might not be installed correctly).")

        print("\n..........................................................")
        print(".....Brought By The Disala................................")
        print("..........................................................")
        print("Log in PIN :", Pin)
        print("User Name :", self.user)
        print("User Pass :", password)
        print("..........................................................\n")

        if KeepAlive:
            print("Keeping script alive (press Ctrl+C to exit).")
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                print("\nExiting.")

# --------------------- Main execution ---------------------
def main():
    if os.geteuid() != 0:
        print("Error: This script must be run as root. Please run with sudo or as root.")
        sys.exit(1)

    if CRD_SSH_Code == "":
        print("Please enter authcode from the given link and run again.")
        sys.exit(1)
    elif len(str(Pin)) < 6:
        print("Enter a pin of 6 or more digits.")
        sys.exit(1)

    try:
        CRDSetup(username)
    except Exception as e:
        print(f"Fatal error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

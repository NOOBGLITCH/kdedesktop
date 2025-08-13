import os
import subprocess
import shutil

# ====== Load from environment variables ======
CRD_SSH_Code = os.getenv("CRD_SSH_CODE", "")
username = os.getenv("CRD_USERNAME", "user")
password = os.getenv("CRD_PASSWORD", "root")
Pin = int(os.getenv("CRD_PIN", "123456"))
Autostart = os.getenv("CRD_AUTOSTART", "true").lower() == "true"

# ====== Basic validation ======
if not CRD_SSH_Code:
    raise ValueError("CRD_SSH_CODE environment variable is required.")
if len(str(Pin)) < 6:
    raise ValueError("CRD_PIN must be at least 6 digits.")

# ====== Create user ======
os.system(f"useradd -m {username}")
os.system(f"adduser {username} sudo")
os.system(f"echo '{username}:{password}' | sudo chpasswd")
os.system("sed -i 's/\\/bin\\/sh/\\/bin\\/bash/g' /etc/passwd")

class CRDSetup:
    def __init__(self, user):
        os.system("apt update")
        self.installCRD()
        self.installDesktopEnvironment()
        self.changewall()
        self.installGoogleChrome()
        self.installTelegram()
        self.installQbit()
        self.finish(user)

    @staticmethod
    def installCRD():
        subprocess.run(['wget', 'https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb'])
        subprocess.run(['dpkg', '--install', 'chrome-remote-desktop_current_amd64.deb'])
        subprocess.run(['apt', 'install', '--assume-yes', '--fix-broken'])
        print("Chrome Remote Desktop Installed!")

    @staticmethod
    def installDesktopEnvironment():
        os.environ["DEBIAN_FRONTEND"] = "noninteractive"
        os.system("apt install --assume-yes xfce4 desktop-base xfce4-terminal")
        os.system("bash -c 'echo \"exec /etc/X11/Xsession /usr/bin/xfce4-session\" > /etc/chrome-remote-desktop-session'")
        os.system("apt remove --assume-yes gnome-terminal")
        os.system("apt install --assume-yes xscreensaver")
        os.system("sudo apt purge light-locker")
        os.system("sudo apt install --reinstall xfce4-screensaver")
        os.system("systemctl disable lightdm.service")
        print("XFCE4 Desktop Environment Installed!")

    @staticmethod
    def installGoogleChrome():
        subprocess.run(["wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"])
        subprocess.run(["dpkg", "--install", "google-chrome-stable_current_amd64.deb"])
        subprocess.run(['apt', 'install', '--assume-yes', '--fix-broken'])
        print("Google Chrome Installed!")

    @staticmethod
    def installTelegram():
        subprocess.run(["apt", "install", "--assume-yes", "telegram-desktop"])
        print("Telegram Installed!")

    @staticmethod
    def changewall():
        os.system("curl -s -L -k -o xfce-verticals.png https://gitlab.com/chamod12/changewallpaper-win10/-/raw/main/CachedImage_1024_768_POS4.jpg")
        current_directory = os.getcwd()
        custom_wallpaper_path = os.path.join(current_directory, "xfce-verticals.png")
        destination_path = '/usr/share/backgrounds/xfce/'
        shutil.copy(custom_wallpaper_path, destination_path)
        print("Wallpaper Changed!")

    @staticmethod
    def installQbit():
        subprocess.run(["sudo", "apt", "update"])
        subprocess.run(["sudo", "apt", "install", "-y", "qbittorrent"])
        print("Qbittorrent Installed!")

    @staticmethod
    def finish(user):
        if Autostart:
            os.makedirs(f"/home/{user}/.config/autostart", exist_ok=True)
            link = "https://www.youtube.com/@The_Disala"
            colab_autostart = f"""[Desktop Entry]
Type=Application
Name=Colab
Exec=sh -c "sensible-browser {link}"
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true
"""
            with open(f"/home/{user}/.config/autostart/colab.desktop", "w") as f:
                f.write(colab_autostart)
            os.system(f"chmod +x /home/{user}/.config/autostart/colab.desktop")
            os.system(f"chown {user}:{user} /home/{user}/.config")

        os.system(f"adduser {user} chrome-remote-desktop")
        command = f"{CRD_SSH_Code} --pin={Pin}"
        os.system(f"su - {user} -c '{command}'")
        os.system("service chrome-remote-desktop start")

        print("Setup Complete!")
        print(f"Log in PIN: {Pin}")
        print(f"User Name: {username}")
        print(f"User Pass: {password}")
        while True:
            pass

# ====== Run setup ======
CRDSetup(username)

import os
import subprocess
CRD = input("Google CRD SSH Code :")
username = "user" #@param {type:"string"}
password = "root" #@param {type:"string"}
os.system(f"useradd -m {username}")
os.system(f"adduser {username} sudo")
os.system(f"echo '{username}:{password}' | sudo chpasswd")
os.system("sed -i 's/\/bin\/sh/\/bin\/bash/g' /etc/passwd")

Pin = 123456 #@param {type: "integer"}
Autostart = True #@param {type: "boolean"}

class CRD:
    def __init__(self, user):
        os.system("apt update")
        self.installCRD()
        self.installDesktopEnvironment()
        self.installGoogleChrome()
        self.installTelegram()
        self.finish(user)

    @staticmethod
    def installCRD():
        subprocess.run(['wget', 'https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb'])
        subprocess.run(['dpkg', '--install', 'chrome-remote-desktop_current_amd64.deb'])
        subprocess.run(['apt', 'install', '--assume-yes', '--fix-broken'])
        print("************************************************************************************")

    @staticmethod
    def installDesktopEnvironment():
        os.system("export DEBIAN_FRONTEND=noninteractive")
        os.system("apt install --assume-yes xfce4 desktop-base xfce4-terminal")
        os.system("bash -c 'echo \"exec /etc/X11/Xsession /usr/bin/xfce4-session\" > /etc/chrome-remote-desktop-session'")
        os.system("apt remove --assume-yes gnome-terminal")
        os.system("apt install --assume-yes xscreensaver")
        os.system("systemctl disable lightdm.service")
        print("************************************************************************************")

    @staticmethod
    def installGoogleChrome():
        subprocess.run(["wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"])
        subprocess.run(["dpkg", "--install", "google-chrome-stable_current_amd64.deb"])
        subprocess.run(['apt', 'install', '--assume-yes', '--fix-broken'])
        print("************************************************************************************")
    
    @staticmethod
    def installTelegram():
        subprocess.run(["apt", "install", "--assume-yes", "telegram-desktop"])
        print("************************************************************************************")

    @staticmethod
    def finish(user):
        if Autostart:
            os.makedirs(f"/home/{user}/.config/autostart", exist_ok=True)
            link = "www.youtube.com/@The_Disala"
            colab_autostart = """[Desktop Entry]
            print("************************************************************************************")

Type=Application
Name=Colab
Exec=sh -c "sensible-browser {}"
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true""".format(link)
            with open(f"/home/{user}/.config/autostart/colab.desktop", "w") as f:
                f.write(colab_autostart)
            os.system(f"chmod +x /home/{user}/.config/autostart/colab.desktop")
            os.system(f"chown {user}:{user} /home/{user}/.config")

        os.system(f"adduser {user} chrome-remote-desktop")
        command = f"{CRD} --pin={Pin}"
        os.system(f"su - {user} -c '{command}'")
        os.system("service chrome-remote-desktop start")

        print("..........................................................") 
        print(".....Brought By The Disala................................") 
        print("..........................................................") 
        print("......#####...######...####....####...##.......####.......") 
        print("......##..##....##....##......##..##..##......##..##......")  
        print("......##..##....##.....####...######..##......######......") 
        print("......##..##....##........##..##..##..##......##..##......") 
        print("......#####...######...####...##..##..######..##..##......") 
        print("..........................................................") 
        print("..Youtube Video Tutorial - https://youtu.be/xqpCQCJXKxU ..") 
        print("..........................................................") 
        print("Log in PIN : 123456") 
        print("User Name : user") 
        print("User Pass : root") 
        while True:
            pass

try:
    if CRD == "":
        print("Please enter authcode from the given link")
    elif len(str(Pin)) < 6:
        print("Enter a pin more or equal to 6 digits")
    else:
        CRD(username)
except NameError as e:
    print("'username' variable not found, Create a user first")
